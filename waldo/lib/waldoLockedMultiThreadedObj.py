import threading
import waldo.lib.util as util
from waldo.lib.waldoLockedObj import WaldoLockedObj
from waldo.lib.waldoEventPriority import gte_priority

def in_place_sort_event_cached_priority_list_by_priority(list_to_sort):
    '''
    @param {list} ---
    
    Sorts the list in place.  Lower indices will contain higher
    priorities.

    @returns sorted list
    '''
    list_to_sort.sort(key=get_priority_key_from_event_cached_priority_obj,reverse=True)
    return list_to_sort

def get_priority_key_from_event_cached_priority_obj(evt_cached_priority_obj):
    return evt_cached_priority_obj.cached_priority


def in_place_sort_event_cached_priority_list_by_uuid(list_to_sort):
    '''
    @param {list} ---
    
    Sorts the list in place.  Lower indices will contain higher uuids

    @returns sorted list
    '''
    list_to_sort.sort(key=get_uuid_key_from_event_cached_priority_obj,reverse=True)
    return list_to_sort

def get_uuid_key_from_event_cached_priority_obj(evt_cached_priority_obj):
    return evt_cached_priority_obj.event.uuid



def in_place_sort_waiting_event_list_by_priority(list_to_sort):
    list_to_sort.sort(key=get_priority_key_from_waiting_element,reverse=True)
    return list_to_sort

def get_priority_key_from_waiting_element(el):
    return el.cached_priority


class EventCachedPriorityObj(object):
    def __init__(self,event,cached_priority):
        self.event = event
        self.cached_priority = cached_priority

    
class WaitingElement(object):
    def __init__(self,event,priority,read,data_wrapper_constructor,peered):
        '''
        @param {bool} read --- True if the element that is waiting is
        waiting on a read lock (not a write lock).
        '''
        self.event = event
        self.read = read
        self.data_wrapper_constructor = data_wrapper_constructor
        self.peered = peered

        # Each event has a priority associated with it.  This priority
        # can change when an event gets promoted to be boosted.  To
        # avoid the read/write conflicts this might cause, instead of
        # operating on an event's real-time priority, when trying to
        # acquire read and write locks on events, we initially request
        # their priorities and use them for the main body of that
        # operation.  This priority gets cached in WaitingElements and
        # can get updated, asynchronously, when an event requests
        # promotion.
        self.cached_priority = priority

        
        # when add a waiting element, that waiting element's read or
        # write blocks.  The way that it blocks is by listening at a
        # threadsafe queue.  This is that queue.
        self.queue = util.Queue.Queue()
        
    def is_read(self):
        return self.read
    
    def is_write(self):
        return not self.read

    def unwait(self,locked_obj):
        '''
        Called from within locked_obj's lock.

        Call to set_val and get_val are blocking.  They wait on a
        threadsafe queue, self.queue.  This method writes to
        threadsafe queue to unjam the waiting events.  
        '''
        if self.read:
            # read expects updated value returned in queue
            self.queue.put(locked_obj.val)
        else:
            # FIXME: it may be that we don't want to copy over initial
            # value when acquiring a lock (eg., if we're just going to
            # write over it anyways).  Add a mechanism for that?
            
            # update dirty val with value asked to write with
            locked_obj.dirty_val = self.data_wrapper_constructor(locked_obj.val.val,self.peered)
            self.queue.put(locked_obj.dirty_val)


import time, random
class Monitor(threading.Thread):
    def __init__(self,multi_threaded_obj):
        self.multi_threaded_obj = multi_threaded_obj
        super(Monitor,self).__init__()
    def run(self):
        time.sleep(6 + random.random())

        if self.multi_threaded_obj.write_lock_holder is None:
            return
        
        print (
            '\nOn ' +
            str(int(self.multi_threaded_obj.write_lock_holder.event.event_parent.local_endpoint._uuid)) +
            ' with obj ' +  str(int(self.multi_threaded_obj.uuid)))

        print 'Multi-threaded object read lock holders: '
        print('\n'.join(self.multi_threaded_obj.read_lock_holders.keys()))
        if self.multi_threaded_obj.write_lock_holder is None:
            print 'No write holders'
        else:
            print 'Write lock holder ' + self.multi_threaded_obj.write_lock_holder.event.uuid
        print 'Waiting elements: '
        print ('\n'.join(self.multi_threaded_obj.waiting_events.keys()))
        print '\n\n'
            

class MultiThreadedObj(WaldoLockedObj):
    '''
    This object can be accessed by multiple transactions at once.
    (eg., it's an endpoint global or peered variable.)

    '''
    
    def __init__(self,data_wrapper_constructor,host_uuid,peered,init_val):
        '''
        @param {DataWrapper object} --- Used to store dirty values.
        For value types, can just use ValueTypeDataWrapper.  For
        reference types, should use ReferenceTypeDataWrpper.
        '''
        # m = Monitor(self)
        # m.start()
        
        self.data_wrapper_constructor = data_wrapper_constructor
        self.uuid = util.generate_uuid()

        
        self.host_uuid = host_uuid
        self.peered = peered

        self.val = self.data_wrapper_constructor(init_val,self.peered)
        self.dirty_val = None
        
        # If write_lock_holder is not None, then the only element in
        # read_lock_holders is the write lock holder.
        # read_lock_holders maps from uuids to EventCachedPriorityObj.
        self.read_lock_holders = {}
        # write_lock_holder is EventCachedPriorityObj
        self.write_lock_holder = None

        
        # A dict of event uuids to WaitingEventTypes
        self.waiting_events = {}

        # In try_next, can cause events to backout.  If we do cause
        # other events to backout, then backout calls try_next.  This
        # (in some cases) can invalidate state that we're already
        # dealing with in the parent try_next.  Use this flag to keep
        # track of whether already in try next.  If are, then return
        # out immediately from future try_next calls.
        self.in_try_next = False
        
        # FIXME: do not have to use reentrant lock here.  The reason
        # that I am is that when we request an event to release locks
        # on an object, we do so from within a lock.  Following that,
        # the event calls into a lock-protected method to remove
        # itself from the dict.  Could re-write code to trak which obj
        # requested backout and skip backing that obj out instead.
        self._mutex = threading.RLock()

    def _lock(self):
        self._mutex.acquire()
    def _unlock(self):
        self._mutex.release()

    def de_waldoify(self,active_event):
        wrapped_val = self.acquire_read_lock(active_event)
        return wrapped_val.de_waldoify(active_event)

    def update_event_priority(self,uuid,new_priority):
        '''
        Called when an event with uuid "uuid" is promoted to boosted
        with priority "priority"
        '''
        self._lock()
        may_require_update = False
        if ((self.write_lock_holder is not None) and
            (self.write_lock_holder.event.uuid == uuid)):
            self.write_lock_holder.cached_priority = new_priority

        if uuid in self.read_lock_holders:
            self.read_lock_holders[uuid].cached_priority = new_priority

        if uuid in self.waiting_events:
            self.waiting_events[uuid].cached_priority = new_priority
            may_require_update = True

        self._unlock()
        
        if may_require_update:
            update_thread = threading.Thread(target=self.try_next)
            update_thread.start()

        
    
    def acquire_read_lock(self,active_event):
        '''
        DOES NOT ASSUME ALREADY WITHIN LOCK

        @returns {DataWrapper object}

        Algorithms:

           0) If already holds a write lock on the variable, then
              return the dirty value associated with event.
           
           1) If already holds a read lock on variable, returns the value
              immediately.

           2) If does not hold a read lock on variable, then attempts
              to acquire one.  If worked, then return the variable.
              When attempting to acquire read lock:

                 a) Checks if there is any event holding a write lock.
                    If there is not, then adds itself to read lock
                    holder dict.
              
                 b) If there is another event holding a write lock,
                    then check if uuid of the read lock requester is
                    >= uuid of the write lock.  If it is, then try to
                    backout the holder of write lock.

                 c) If cannot backout or have a lesser uuid, then
                    create a waiting event and block while listening
                    to queue.  (same as #3)
              
           3) If did not work, then create a waiting event and a queue
              and block while listening on that queue.

        Blocks until has acquired.
              
        '''
        self._lock()

        # Each event has a priority associated with it.  This priority
        # can change when an event gets promoted to be boosted.  To
        # avoid the read/write conflicts this might cause, at the
        # beginning of acquring read lock, get priority and use that
        # for majority of time trying to acquire read lock.  If cached
        # priority ends up in WaitingElement, another thread can later
        # update it.
        cached_priority = active_event.get_priority()

        
        # must be careful to add obj to active_event's touched_objs.
        # That way, if active_event needs to backout, we're guaranteed
        # that the state we've allocated for accounting the
        # active_event is cleaned up here.
        if not self.insert_in_touched_objs(active_event):
            self._unlock()
            raise util.BackoutException()

        # check 0 above
        if ((self.write_lock_holder is not None) and
            (active_event.uuid == self.write_lock_holder.event.uuid)):
            to_return = self.dirty_val
            self._unlock()
            return to_return


        # also check 1 above
        if active_event.uuid in self.read_lock_holders:
            # already allowed to read the variable
            to_return = self.val
            self._unlock()
            return to_return

        # must be careful to add obj to active_event's touched_objs.
        # That way, if active_event needs to backout, we're guaranteed
        # that the state we've allocated for accounting the
        # active_event is cleaned up here.
        if not self.insert_in_touched_objs(active_event):
            self._unlock()
            raise util.BackoutException()

        # Check 2 from above
        
        # check 2a
        if self.write_lock_holder is None:
            to_return = self.val
            self.read_lock_holders[active_event.uuid] = (
                EventCachedPriorityObj(active_event,cached_priority))
            
            self._unlock()
            return to_return

        # check 2b
        if gte_priority(cached_priority, self.write_lock_holder.cached_priority):

            # backout write lock if can
            if self.write_lock_holder.event.can_backout_and_hold_lock():
                # actually back out the event
                self.obj_request_backout_and_release_lock(self.write_lock_holder.event)

                # add active event as read lock holder and return
                self.dirty_val = None
                self.write_lock_holder = None
                self.read_lock_holders = {}
                self.read_lock_holders[active_event.uuid] = (
                    EventCachedPriorityObj(active_event,cached_priority))
                to_return = self.val
                self._unlock()
                return to_return

        # Condition 2c + 3

        # create a waiting read element
        waiting_element = WaitingElement(
            active_event,cached_priority,True,self.data_wrapper_constructor,self.peered)
        
        self.waiting_events[active_event.uuid] = waiting_element
        self._unlock()

        return waiting_element.queue.get()


    def obj_request_backout_and_release_lock(self,active_event):
        '''
        ASSUMES CALLED FROM WITHIN LOCK
        
        When preempting a lock holder, we first call
        can_backout_and_hold_lock on the method.  If this returns
        True, then it means that the active event is holding its lock
        on the event and preparing for a command to complete its
        backout (via obj_request_backout_and_release_lock).

        The active event's obj_request_backout_and_release_lock method
        will not call backout back on this object.  This means that we
        must remove active_event from the read lock holders, write
        lock holders, and waiting elements.

        Note: Previously, immediately after calling
        request_and_release_lock on each obj, we just overwrote
        write_lock_holders and read_lock holders.  This is
        insufficient however because the active event may also be a
        waiting element.  Consider the case where we have a read lock
        holder that is waiting to become a write lock holder.  If we
        then backout of the read lock holder, we should also back out
        of its waiting element.  Otherwise, the waiting element will
        eventually be scheduled.
        
        '''
        active_event.obj_request_backout_and_release_lock(self)

        # remove write lock holder if it was one
        self.read_lock_holders.pop(active_event.uuid,None)
        if ((self.write_lock_holder is not None) and 
            (self.write_lock_holder.event.uuid == active_event.uuid)):
            self.write_lock_holder = None

        # un-jam threadsafe queue waiting for event
        waiting_event = self.waiting_events.pop(active_event.uuid,None)
        if waiting_event is not None:
            waiting_event.unwait(self)


            
    def acquire_write_lock(self,active_event):
        '''
        0) If already holding a write lock, then return the dirty value

        1) If there are no read or write locks, then just copy the
           data value and set read and write lock holders for it.

        2) There are existing read and/or write lock holders.  Check
           if our uuid is larger than their uuids.
        
        '''        
        self._lock()
        # Each event has a priority associated with it.  This priority
        # can change when an event gets promoted to be boosted.  To
        # avoid the read/write conflicts this might cause, at the
        # beginning of acquring write lock, get priority and use that
        # for majority of time trying to acquire read lock.  If cached
        # priority ends up in WaitingElement, another thread can later
        # update it.
        cached_priority = active_event.get_priority()


        # must be careful to add obj to active_event's touched_objs.
        # That way, if active_event needs to backout, we're guaranteed
        # that the state we've allocated for accounting the
        # active_event is cleaned up here.
        if not self.insert_in_touched_objs(active_event):
            self._unlock()
            raise util.BackoutException()

        
        # case 0 above
        if ((self.write_lock_holder is not None) and
            (active_event.uuid == self.write_lock_holder.event.uuid)):
            to_return = self.dirty_val
            self._unlock()
            return to_return
        
        # case 1 above
        if ((self.write_lock_holder is None) and
            (len(self.read_lock_holders) == 0)):
            self.dirty_val = self.data_wrapper_constructor(self.val,self.peered)
            self.write_lock_holder = (
                EventCachedPriorityObj(active_event,cached_priority))
            
            self.read_lock_holders[active_event.uuid] = (
                EventCachedPriorityObj(active_event,cached_priority))
            to_return = self.dirty_val
            self._unlock()
            return to_return
            

        if self.is_gte_than_lock_holding_events(cached_priority):
            # Stage 2 from above
            if self.test_and_backout_all(active_event.uuid):
                # Stage 3 from above
                # actually update the read/write lock holders
                self.read_lock_holders[active_event.uuid] = (
                    EventCachedPriorityObj(active_event,cached_priority))
                self.write_lock_holder = (
                    EventCachedPriorityObj(active_event,cached_priority))

                self.dirty_val = self.data_wrapper_constructor(self.val,self.peered)
                to_return = self.dirty_val
                self._unlock()
                return to_return


        # case 3: add to wait queue and wait
        write_waiting_event = WaitingElement(
            active_event,cached_priority,False,self.data_wrapper_constructor,
            self.peered)
        self.waiting_events[active_event.uuid] = write_waiting_event
        
        self._unlock()
        return write_waiting_event.queue.get()

    def get_dirty_wrapped_val(self,active_event):
        '''
        When serializing data to send to other side for peered
        variables, need to get deltas across lifetime of variable,
        this method returns a data wrapper that can be used to get
        those deltas.
        '''
        util.logger_assert(
            'Have not determined how to serialize multithreaded peered data.')

    
    def get_and_reset_has_been_written_since_last_msg(self,active_event):
        '''
        @returns {bool} --- True if the object has been written to
        since we sent the last message.  False otherwise.  (Including
        if event has been preempted.)
        '''
        has_been_written = False
        self._lock()

        # check if active event even has ability to write to variable
        if self.write_lock_holder is not None:
            if self.write_lock_holder.event.uuid == active_event.uuid:
                has_been_written = self.dirty_val.get_and_reset_has_been_written_since_last_msg()
        
        self._unlock()
        return has_been_written
    
        
    def complete_commit(self,active_event):
        '''
        Both readers and writers can complete commits.  If it's a
        reader, we do not update the internal value of the object.  If
        it's a writer, we do.  In either case, we remove the event
        from holding a lock and check if any other events can be
        scheduled.
        '''
        self._lock()
        if ((self.write_lock_holder is not None) and 
            (active_event.uuid == self.write_lock_holder.event.uuid)):
            self.val.write(self.dirty_val.val)
            
            self.write_lock_holder = None
            self.read_lock_holders = {}
        else:
            val = self.read_lock_holders.pop(active_event.uuid,None)
            #### DEBUG
            if val is None:
                util.logger_assert(
                    'Should not be completing a commit on a missing event')
            #### END DEBUG
        self._unlock()

        # FIXME: may want to actually check whether the change could
        # have caused another read/write to be scheduled.
        self.try_next()

    def is_peered(self):
        return self.peered
        
    def backout(self,active_event):
        '''
        When an event backs out, it calls this method on all the
        objects it holds read/write locks on.  This just removes
        active_event from our lists of read/write lock holders.
        
        If not already holding lock, then delete it from waiting
        events
        '''
        
        # FIXME: Are there chances that could process a stale backout?
        # I think so.
        self._lock()
        # note: there are cases where an active event may try to
        # backout after it's
        self.read_lock_holders.pop(active_event.uuid,None)
        if ((self.write_lock_holder is not None) and 
            (self.write_lock_holder.event.uuid == active_event.uuid)):
            self.write_lock_holder = None

        # un-jam threadsafe queue waiting for event
        waiting_event = self.waiting_events.pop(active_event.uuid,None)
        if waiting_event is not None:
            waiting_event.unwait(self)
        self._unlock()
        
        # check if removal might have freed up preforming another
        # operation that had blocked on it.
        
        # FIXME: may want to actually check whether the change could
        # have caused another read/write to be scheduled.
        self.try_next()
        

    def test_and_backout_all(self,event_to_not_backout_uuid = None):
        '''
        ASSUMES ALREADY WITHIN LOCK

        Checks if can backout all events that currently hold
        read/write locks on this object.
        
        @param {uuid} event_to_not_backout_uuid --- If we had an event
        that was going from being a reader of the data to a writer on
        the data, it might call this method to upgrade itself.  In
        that case, we do not want to back it out itself.  So we skip
        over it.
        
        Happens in two phases:
        
          Phase 1: Iterate through each event holding a lock.  Request
          that event to take a lock on itself so that the event cannot
          transition into a different state (eg., begin two phase
          commit).  Then it returns a bool for whether it's
          backout-able.  (True, if it had not started 2-phase commit,
          False otherwise).

          Note: it is important to sort the list of events by uuid
          before iterating through them.  This is so that we can
          prevent deadlock when two different objects are iterating
          through their lists.
          

          Phase 2:
          
            * If any return that they are not backout-able, then break
              there and tell any that we had already held locks for to
              release their locks and continue on about their
              business.

           * If all return that they are backout-able, then run
             through all and back them out.

           Return True if all were backed out.  False if they weren't.
        '''
        
        # Phase 1:
        
        # note: do not have to explicitly include the write lock key
        # here because the event that is writing will be included in
        # read locks

        # Note: it is important to sort the list of events by uuid
        # before iterating through them.  This is so that we can
        # prevent deadlock when two different objects are iterating
        # through their lists.
        read_lock_holder_event_cached_priorities = list(self.read_lock_holders.values())
        in_place_sort_event_cached_priority_list_by_uuid(
            read_lock_holder_event_cached_priorities)

        to_backout_list = []
        can_backout_all = True
        for event_cached_priority_obj in read_lock_holder_event_cached_priorities:
            read_event = event_cached_priority_obj.event
            read_uuid = read_event.uuid
            if read_uuid != event_to_not_backout_uuid:
                if read_event.can_backout_and_hold_lock():
                    to_backout_list.append(read_event)
                else:
                    can_backout_all = False
                    break

        # Phase 2:
        if can_backout_all:
            for event_to_backout in to_backout_list:
                self.obj_request_backout_and_release_lock(event_to_backout)
                
            event_cached_priority = self.read_lock_holders.get(event_to_not_backout_uuid,None)
            self.read_lock_holders = {}
            self.write_lock_holder = None
            if event_cached_priority is not None:
                self.read_lock_holders[event_cached_priority.event.uuid] = event_cached_priority

        else:
            for event_not_to_backout in to_backout_list:
                event_not_to_backout.obj_request_no_backout_and_release_lock()
                
        return can_backout_all



    def is_gte_than_lock_holding_events(self,waiting_event_priority):
        '''
        @param {priority} waiting_event_priority --- 
        
        @returns {bool} --- Returns True if waiting_event_uuid is
        greater than or equal to all other events that are currently
        holding read or read/write locks on data.
        '''

        # check write lock
        if ((self.write_lock_holder is not None) and
            (not gte_priority(waiting_event_priority,self.write_lock_holder.cached_priority))):
            
            return False

        # check read locks
        for read_lock_uuid in self.read_lock_holders:
            read_lock_holder_event_cached_priority = self.read_lock_holders[read_lock_uuid]
            if not gte_priority(
                waiting_event_priority,read_lock_holder_event_cached_priority.cached_priority):
                return False
            
        return True

    

    def try_schedule_read_waiting_event(self,waiting_event):
        '''
        CALLED FROM WITHIN LOCK
        
        Check if can schedule the read event waiting_event

        Should be able to schedule if:

          1) There is not a write lock holder or 

          2) There is a write lock holder that is not currently in two
             phase commit, and has a uuid that is less than our uuid.

              a) check if write lock holder is younger (ie, it should
                 be preempted).
                 
              b) If it is younger and it's not in two phase commit,
                 then go ahead and revoke it.
             
        @returns {bool} --- Returns True if could schedule read
        waiting event.  False if could not.
        '''
        # CASE 1
        if self.write_lock_holder is None:
            self.read_lock_holders[waiting_event.event.uuid] = (
                EventCachedPriorityObj(waiting_event.event,waiting_event.cached_priority))
            waiting_event.unwait(self)
            return True

        # CASE 2
        #   b) If it is younger and it's not in two phase commit, 
        #      then go ahead and revoke it.

        # 2 a --- check if write lock holder is younger (ie, it should be
        #         preempted).
        if gte_priority(
            self.write_lock_holder.cached_priority,waiting_event.cached_priority):
            # do not preempt write lock: it has been around longer
            return False

        # 2 b --- If it is younger and it's not in two phase commit, 
        #         then go ahead and revoke it.
        if not self.write_lock_holder.event.can_backout_and_hold_lock():
            # cannot backout write lock holder
            return False

        # Can backout write lock holder:
        #    1) Actually perform backout of writing event
        #    2) Clean up write lock holder and read lock holder state
        #       associated with write lock
        #    3) Waiting event gets included in read lock holder
        #    4) Unjam waiting event's read queue, which returns value.

        # 1
        self.obj_request_backout_and_release_lock(write_lock_holder.event)
        
        # following code will remove all write lock holders and read
        # lock holders.
        
        # 2
        self.write_lock_holder = None
        self.read_lock_holders = {}
        # 3
        self.read_lock_holders[waiting_event.event.uuid] = (
            EventCachedPriorityObj(waiting_event.event,waiting_event.cached_priority))
        # 4
        waiting_event.unwait(self)
        return True


    def set_val(self,active_event,new_val):
        '''
        Called as an active event runs code.
        '''
        to_write_on = self.acquire_write_lock(active_event)
        to_write_on.write(new_val)

    
    def try_schedule_write_waiting_event(self,waiting_event):
        '''
        CALLED FROM WITHIN LOCK HOLDER
        
        Gets called when an event that had not been holding a write
        lock tries to begin holding a write lock.

        Three things must happen.
        
          1) Check that the event that is trying to assume the write
             lock has a higher uuid than any other event that is
             currently holding a lock (read or read/write).  

          2) If 1 succeeded, then try to backout all events that
             currently hold locks.  (May not be able to if an event is
             in the midst of a commit.)  If can, roll back changes to
             events that currently hold locks.
        
          3) If 1 and 2 succeeded, then updates self.write_lock_holder
             and self.read_lock_holders.  Also, unjams
             waiting_event's queue.

        @param {Waiting Event object} --- Should be 
        
        @returns {bool} --- True if could successfully schedule the
        waiting write.  False otherwise.
        '''
        #### DEBUG
        if not waiting_event.is_write():
            util.logger_assert(
                'Should only pass writes into try_schedule_write_waiting_event')
        #### END DEBUG

            
        # Stage 1 from above
        if self.is_gte_than_lock_holding_events(waiting_event.cached_priority):
            # Stage 2 from above
            if self.test_and_backout_all(waiting_event.event.uuid):
                # Stage 3 from above
                # actually update the read/write lock holders
                self.read_lock_holders[waiting_event.event.uuid] = (
                    EventCachedPriorityObj(waiting_event.event,waiting_event.cached_priority))
                self.write_lock_holder = (
                    EventCachedPriorityObj(waiting_event.event,waiting_event.cached_priority))
                waiting_event.unwait(self)
                return True

        return False
    
        
    def try_next(self):
        '''
        Check if any events that have been waiting on read/write locks
        can now be scheduled.
        
        All events that are not currently running, but waiting to be
        scheduled on the Waldo object are in the self.waiting_events
        dict.

          #1: Sort all waiting events by uuid (part of time/wait
              algo).

          #2: Keep grabbing elements from the sorted list and trying
              to apply them until:

                a) We hit a write (we know that reads+writes cannot
                   function simultaneously) or

                b) The waiting event that we try to schedule fails to
                   schedule.  (Eg., it is blocked by a higher-priority
                   event that is holding a write lock.)
        
        '''
        self._lock()

        
        if len(self.waiting_events) == 0:
            self._unlock()
            return

        # see comment in class' __init__ for in_try_next.
        if self.in_try_next:
            self._unlock()
            return
        self.in_try_next = True

        
        # Phase 1 from above:
        # sort event uuids from high to low to determine if should add
        # them.
        waiting_events = list(self.waiting_events.values())
        in_place_sort_waiting_event_list_by_priority(waiting_events)


        # Phase 2 from above
        # Run through all waiting events.  If the waiting event is a
        # write, first check that

        for waiting_event in waiting_events:
            if waiting_event.is_write():
                if self.try_schedule_write_waiting_event(waiting_event):
                    del self.waiting_events[waiting_event.event.uuid]
                break
                        
            else:
                if self.try_schedule_read_waiting_event(waiting_event):
                    del self.waiting_events[waiting_event.event.uuid]
                else:
                    break

        self.in_try_next = False
        self._unlock()


    def get_val(self,active_event):
        if active_event is None:
            # used for debugging: allows python code to read into and
            # check the value of an external reference.
            return self.val.val
        
        data_wrapper = self.acquire_read_lock(active_event)
        return data_wrapper.val


    def insert_in_touched_objs(self,active_event):
        '''
        ASSUMES ALREADY HOLDING LOCK

        @param {WaldoLockedActiveEvent} active_event --- 

        @returns {bool} --- True if obj has been inserted into
        active_event's touched_obj dict or already existed there.
        False if did not exist there and the event has been backed
        out.

        This method ensures that this object is in the dict,
        touched_objs, that the event active_event is holding.  It
        tries to add self to that dict.  If the event has already been
        backed out and we try to add self to event's touched_objs, we
        do not add to touched objs and return false.
        
        '''
        if ((active_event.uuid in self.waiting_events) or
            (active_event.uuid in self.read_lock_holders)):
            return True

        in_running_state = active_event.add_touched_obj(self)
        return in_running_state

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        The runtime automatically synchronizes data between both
        endpoints.  When one side has updated a peered variable, the
        other side needs to attempt to apply those changes before
        doing further work.  This method grabs the val and version
        object of the dirty element associated with invalid_listener.
        Using these data, plus var_name, it constructs a named tuple
        for serialization.  (@see
        util._generate_serialization_named_tuple)

        Note: if the val of this object is another Reference object,
        then we recursively keep generating named tuples and embed
        them in the one we return.

        Note: we only serialize peered data.  No other data gets sent
        over the network; therefore, it should not be serialized.

        @param {*Delta or VarStoreDeltas} parent_delta --- Append any
        message that we create here to this message.
        
        @param {String} var_name --- Both sides of the connection need
        to agree on a common name for the variable being serialized.
        This is to ensure that when the data are received by the other
        side we know which variable to put them into.  This value is
        only really necessary for the outermost wrapping of the named
        type tuple, but we pass it through anyways.

        @param {bool} force --- True if regardless of whether modified
        or not we should serialize.  False otherwise.  (We migth want
        to force for instance the first time we send sequence data.)
        
        @returns {bool} --- True if some subelement was modified,
        False otherwise.

        '''
        util.logger_assert(
            'Serializable var tuple for network is pure virtual ' +
            'in waldoLockedObj.')
                
    

