import threading
import waldo.lib.util as util
from waldo.lib.waldoLockedObj import WaldoLockedObj
from waldo.lib.waldoEventUUID import gte_uuid, in_place_sort_uuid_list


class WaitingElement(object):
    def __init__(self,event,read,data_wrapper_constructor,peered):
        '''
        @param {bool} read --- True if the element that is waiting is
        waiting on a read lock (not a write lock).
        '''
        self.event = event
        self.read = read
        self.data_wrapper_consructor = data_wrapper_constructor
        self.peered = peered
        
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
        self.data_wrapper_constructor = data_wrapper_constructor
        self.uuid = util.generate_uuid()
        
        self.host_uuid = host_uuid
        self.peered = peered

        self.val = self.data_wrapper_constructor(init_val,self.peered)
        self.dirty_val = None
        
        # If write_lock_holder is not None, then the only element in
        # read_lock_holders is the write lock holder.  
        self.read_lock_holders = {}
        self.write_lock_holder = None

        # A dict of event ids to WaitingEventTypes
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

        # must be careful to add obj to active_event's touched_objs.
        # That way, if active_event needs to backout, we're guaranteed
        # that the state we've allocated for accounting the
        # active_event is cleaned up here.
        if not self.insert_in_touched_objs(active_event):
            self._unlock()
            raise util.BackoutException()

        # check 0 above
        if ((self.write_lock_holder is not None) and
            (active_event.uuid == self.write_lock_holder.uuid)):
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
            self.read_lock_holders[active_event.uuid] = active_event
            self._unlock()
            return to_return

        # check 2b
        if gte_uuid(active_event.uuid, self.write_lock_holder.uuid):

            # backout write lock if can
            if self.write_lock_holder.can_backout_and_hold_lock():

                # actually back out the event
                self.write_lock_holder.obj_request_backout_and_release_lock()
                
                # add active event as read lock holder and return
                self.dirty_val = None
                self.write_lock_holder = None
                self.read_lock_holders = {}
                self.read_lock_holders[active_event.uuid] = active_event
                to_return = self.val
                self._unlock()
                return to_return

        # Condition 2c + 3
            
        # create a waiting read element
        waiting_element = WaitingElement(
            active_event,True,self.data_wrapper_constructor,self.peered)
        
        self.waiting_events[active_event.uuid] = waiting_element
        self._unlock()

        return waiting_element.queue.get()

    def acquire_write_lock(self,active_event):
        '''
        0) If already holding a write lock, then return the dirty value

        1) If there are no read or write locks, then just copy the
           data value and set read and write lock holders for it.

        2) There are existing read and/or write lock holders.  Check
           if our uuid is larger than their uuids.
        
        '''
        self._lock()

        # must be careful to add obj to active_event's touched_objs.
        # That way, if active_event needs to backout, we're guaranteed
        # that the state we've allocated for accounting the
        # active_event is cleaned up here.
        if not self.insert_in_touched_objs(active_event):
            self._unlock()
            raise util.BackoutException()

        
        # case 0 above
        if ((self.write_lock_holder is not None) and
            (active_event.uuid == self.write_lock_holder.uuid)):
            to_return = self.dirty_val
            self._unlock()
            return to_return
        
        # case 1 above
        if ((self.write_lock_holder is None) and
            (len(self.read_lock_holders) == 0)):
            self.dirty_val = self.data_wrapper_constructor(self.val,self.peered)
            self.write_lock_holder = active_event
            self.read_lock_holders[active_event.uuid] = active_event
            to_return = self.dirty_val
            self._unlock()
            return to_return
            

        if self.is_gte_than_lock_holding_events(active_event.uuid):
            # Stage 2 from above
            if self.test_and_backout_all(active_event.uuid):
                # Stage 3 from above
                # actually update the read/write lock holders
                self.read_lock_holders[active_event.uuid] = active_event
                self.write_lock_holder = active_event

                self.dirty_val = self.data_wrapper_constructor(self.val,self.peered)
                to_return = self.dirty_val
                self._unlock()
                return to_return


        # case 3: add to wait queue and wait
        write_waiting_event = WaitingElement(
            active_event,False,self.data_wrapper_constructor,self.peered)
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
            if self.write_lock_holder.uuid == active_event.uuid:
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
            (active_event.uuid == self.write_lock_holder.uuid)):
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
            (self.write_lock_holder.uuid == active_event.uuid)):
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
        read_lock_holder_uuids = list(self.read_lock_holders.keys())
        in_place_sort_uuid_list(read_lock_holder_uuids)
        
        to_backout_list = []
        can_backout_all = True
        for read_uuid in read_lock_holder_uuids:
            if read_uuid != event_to_not_backout_uuid:
                event = self.read_lock_holders[read_uuid]
                if event.can_backout_and_hold_lock():
                    to_backout_list.append(event)
                else:
                    can_backout_all = False
                    break

        # Phase 2:
        if can_backout_all:
            for event_to_backout in to_backout_list:
                event_to_backout.obj_request_backout_and_release_lock()

            event = self.read_lock_holders.get(event_to_not_backout_uuid,None)
            self.read_lock_holders = {}
            self.write_lock_holder = None
            if event is not None:
                self.read_lock_holders[event.uuid] = event
                
        else:
            for event_not_to_backout in to_backout_list:
                event_not_to_backout.obj_request_no_backout_and_release_lock()
                
        return can_backout_all

    
    def is_gte_than_lock_holding_events(self,waiting_event_uuid):
        '''
        @param {uuid} waiting_event_uuid --- 
        
        @returns {bool} --- Returns True if waiting_event_uuid is
        greater than or equal to all other events that are currently
        holding read or read/write locks on data.
        '''

        # check write lock
        if ((self.write_lock_holder is not None) and
            (not gte_uuid(waiting_event_uuid,self.write_lock_holder.uuid))):
            
            return False

        # check read locks
        for read_lock_uuid in self.read_lock_holders:
            if not gte_uuid(waiting_event_uuid,read_lock_uuid):
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
            self.read_lock_holders[waiting_event.event.uuid] = waiting_event.event
            waiting_event.unwait(self)
            return True

        # CASE 2
        #   b) If it is younger and it's not in two phase commit, 
        #      then go ahead and revoke it.

        # 2 a --- check if write lock holder is younger (ie, it should be
        #         preempted).
        if gte_uuid(self.write_lock_holder.uuid,waiting_event.event.uuid):
            # do not preempt write lock: it has been around longer
            return False

        # 2 b --- If it is younger and it's not in two phase commit, 
        #         then go ahead and revoke it.
        if not self.write_lock_holder.can_backout_and_hold_lock():
            # cannot backout write lock holder
            return False

        # Can backout write lock holder:
        #    1) Actually perform backout of writing event
        #    2) Clean up write lock holder and read lock holder state
        #       associated with write lock
        #    3) Waiting event gets included in read lock holder
        #    4) Unjam waiting event's read queue, which returns value.

        # 1
        self.write_lock_holder.obj_request_backout_and_release_lock()
        # 2
        self.write_lock_holder = None
        self.read_lock_holders = {}
        # 3
        self.read_lock_holders[waiting_event.event.uuid] = waiting_event.event        
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
        if self.is_gte_than_lock_holding_events(waiting_event.event.uuid):
            # Stage 2 from above
            if self.test_and_backout_all(waiting_event.event.uuid):
                # Stage 3 from above
                # actually update the read/write lock holders
                self.read_lock_holders[waiting_event.event.uuid] = waiting_event.event
                self.write_lock_holder = waiting_event.event
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
        waiting_event_uuids = list(self.waiting_events.keys())
        in_place_sort_uuid_list(waiting_event_uuids)


        # Phase 2 from above
        # Run through all waiting events.  If the waiting event is a
        # write, first check that
        
        for waiting_event_uuid in waiting_event_uuids:
            waiting_event = self.waiting_events[waiting_event_uuid]

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
                
    

