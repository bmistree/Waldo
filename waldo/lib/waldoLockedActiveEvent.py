import threading
import util

class LockedActiveEvent(object):

    STATE_RUNNING = 1
    STATE_FIRST_PHASE_COMMIT = 2
    STATE_SECOND_PHASE_COMMITTED = 3
    STATE_BACKED_OUT = 4
    
    def __init__(self,event_parent,event_map):
        '''
        @param {EventParent} event_parent
        
        @param {WaldoActiveEventMap} event_map
        '''
        self.uuid = event_parent.get_uuid()
        self.mutex = threading.Lock()
        self.state = LockedActiveEvent.STATE_RUNNING

        self.event_map = event_map
        
        # a dict containing all local objects that this event has
        # touched while executing.  On commit, must run through each
        # and complete commit.  On backout, must run through each and
        # call backout.
        self.touched_objs = {}


        # a dict.  keys are uuids, values are EventSubscribedTo
        # objects, which contain all endpoints that this event has
        # issued commands to while executing as well as the queues
        # they may be waiting on to free.  On commit, must run through
        # each and tell it to enter first phase commit.
        self.other_endpoints_contacted = {}
        self.partner_contacted = False
        
        self.event_parent = event_parent
        
        
    def _lock(self):
        self.mutex.acquire()
    def _unlock(self):
        self.mutex.release()

    def add_touched_obj(self,obj):
        '''
        @param {WaldoLockedObj} obj --- Whenever we try to perform a
        read or a write on a Waldo object, if this event has not
        previously performed a read or write on that object, then we
        check to ensure that this event hasn't already begun to
        backout.

        @returns {bool} --- Returns True if have not already backed
        out.  Returns False otherwise.
        '''
        self._lock()

        still_running = (self.state == LockedActiveEvent.STATE_RUNNING)
        if still_running:
            self.touched_objs[obj.uuid] = obj
        self._unlock()
        
        return still_running
        
        
    def can_backout_and_hold_lock(self):
        '''
        @returns {bool} --- True if not in the midst of two phase
        commit.  False otherwise.

        If it is not in the midst of two phase commit, then does not
        return the lock that it is holding.  The lock must be released
        in obj_request_backout_and_release_lock or
        obj_request_no_backout_and_release_lock.
        
        '''
        self._lock()
        if self.state != LockedActiveEvent.STATE_RUNNING:
            self._unlock()
            return False

        return True

    def begin_first_phase_commit(self):
        '''
        If can enter Should send a message back to parent that 
        '''
        self._lock()

        if self.state != LockedActiveEvent.STATE_RUNNING:
            self._unlock()
            # note: do not need to respond negatively to first phase
            # commit request if we already are backing out.  This is
            # because we should have sent a message to all partners,
            # etc. as soon as we backed out telling them that they
            # should also back out.  Do not need to send the same
            # message again.
            return
        
        # transition into first phase commit state        
        self.state = LockedActiveEvent.STATE_FIRST_PHASE_COMMIT
        self._unlock()

        # forwards message on to others and affirmatively replies that
        # now in first pahse of commit.
        self.event_parent.first_phase_transition_success(
            self.other_endpoints_contacted,self.partner_contacted,self)

        

    def second_phase_commit(self):
        self._lock()

        if self.state == LockedActiveEvent.STATE_SECOND_PHASE_COMMITTED:
            # already committed, already forwarded names along.
            # nothing left to do.
            self._unlock()
            return

        self.state = LockedActiveEvent.STATE_SECOND_PHASE_COMMITTED
        # complete commit on each individual object that we touched
        for obj in self.touched_objs.values():
            obj.complete_commit(self)
            
        self.touched_objs = {}
        
        self._unlock()

        # FIXME: which should happen first, notifying others or
        # releasing locks locally?
        
        # notify other endpoints to also complete their commits
        self.event_parent.second_phase_transition_success(
            self.other_endpoints_contacted,self.partner_contacted)    
    
    def complete_commit_local(self):
        '''
        Runs through all touched objects and calls their
        complete_commit methods.  These just remove this event from
        list of lock holders, and, if we wrote, to the object,
        exchanges the dirty cell holding the write with a clean cell.
        '''
        # note that by the time we get here, we know that we will not
        # be modifying touched_objs dict.  Therefore, we do not need
        # to take any locks.
        for obj in self.touched_objs.values():
            obj.complete_commit(self)


    def _backout(self,backout_requester_endpoint_uuid):
        '''
        MUST BE CALLED FROM WITHIN LOCK
        
        @param {uuid or None} backout_requester_endpoint_uuid --- If
        None, means that the call to backout originated on local
        endpoint.  Otherwise, means that call to backout was made by
        either endpoint's partner, an endpoint that we called an
        endpoint method on, or an endpoint that called an endpoint
        method on us.
        
        0) If we're already in backed out state, do nothing: we've
           already taken appropriate action.
        
        1) Change state to backed out.
        
        2) Run through all objects that this event has touched and
           backout from them.

        3) Unblock any queues that are waiting on results, with a
           message to quit.

        4) Remove from active event map

        5) Forward messages to all other endpoints in event to roll
           back.
        '''

        # 0
        if self.state == LockedActiveEvent.STATE_BACKED_OUT:
            # Can get multiple backout requests if, for instance,
            # multiple partner endpoints get preempted and forward
            # message to this node.  Do nothing: cannot backout twice.
            return

        # 1
        self.state = LockedActiveEvent.STATE_BACKED_OUT

        # 2
        for touched_obj in self.touched_objs.values():
            touched_obj.backout(self)
            
        # 3
        self.rollback_unblock_waiting_queues()

        # 4
        self.event_map.remove_event(self.uuid)

        # 5
        self.event_parent.rollback(
            backout_requester_endpoint_uuid,self.other_endpoints_contacted,
            self.partner_contacted)

        
    def rollback_unblock_waiting_queues(self):
        util.logger_warn(
            'Unfinished method for unblocking waiting queues in waldoLockedActiveEvent.')
        
    def backout(self,backout_requester_endpoint_uuid):
        '''
        @param {uuid or None} backout_requester_endpoint_uuid --- If
        None, means that the call to backout originated on local
        endpoint.  Otherwise, means that call to backout was made by
        either endpoint's partner, an endpoint that we called an
        endpoint method on, or an endpoint that called an endpoint
        method on us.
        '''
        self._lock()
        self._backout(backout_requester_endpoint_uuid)
        self._unlock()

        
    def obj_request_backout_and_release_lock(self):
        '''
        Either this or obj_request_no_backout_and_release_lock
        are called after can_backout_and_hold_lock returns
        True.  

        Called by a WaldoLockedObject to preempt this event.

        '''
        self._backout(None)
        # unlock after method
        self._unlock()

        
        
    def obj_request_no_backout_and_release_lock(self):
        '''
        Either this or obj_request_backout_and_release_lock
        are called after can_backout_and_hold_lock returns
        True.  

        Called by a WaldoLockedObject.  WaldoLockedObject will not
        preempt this event.
        
        Do not have backout event.  Just release lock.
        '''
        self._unlock()


