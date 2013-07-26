import threading
import util

class EventParent(object):
    '''
    Each event has an event parent.  The parent serves as a connection
    to whatever it was that began the event locally.  For instance, if
    this event was started by an event's partner, then, EventParent
    object would keep a reference to endpoint object so that it can
    forward responses back to partner.
    '''
    def get_uuid(self):
        '''
        The uuid of the event
        '''
        util.logger_assert('get_uuid is pure virtual in EventParent')

    def first_phase_transition_success(
        self,same_host_endpoints_contacted_dict,partner_contacted,event):
        '''
        @param {dict} same_host_endpoints_contacted_dict --- Keys are
        uuids.  Values are endpoint objects.  

        @param {bool} partner_contacted --- True if the event has sent
        a message as part of a sequence to partner.  False otherwise.

        Sends a message back to parent that the first phase lock was
        successful.  Message also includes a list of endpoints uuids
        that this endpoint may have called.  The root event cannot
        proceed to second phase of commit until it hears that each of
        the endpoints in this list have affirmed that they got into
        first phase.

        Also forwards a message on to other endpoints that this
        endpoint called/touched as part of its computation.  Requests
        each of them to enter first phase commit as well.
        '''
        util.logger_warn(
            'first_phase_transition_success is pure virtual in EventParent')

    def second_phase_transition_success(
        self,same_host_endpoints_contacted_dict,partner_contacted):
        '''
        @param {dict} same_host_endpoints_contacted_dict --- Keys are
        uuids.  Values are endpoint objects.  

        @param {bool} partner_contacted --- True if the event has sent
        a message as part of a sequence to partner.  False otherwise.

        Forwards a message on to other endpoints that this endpoint
        called/touched as part of its computation.  Requests each of
        them to enter complete commit.
        '''
        util.logger_warn(
            'second_phase_transition_success is pure virtual in EventParent')

        
    def rollback(
        self,backout_requester_endpoint_uuid,
        same_host_endpoints_contacted_dict,partner_contacted):
        '''
        @param {uuid or None} backout_requester_endpoint_uuid --- If
        None, means that the call to backout originated on local
        endpoint.  Otherwise, means that call to backout was made by
        either endpoint's partner, an endpoint that we called an
        endpoint method on, or an endpoint that called an endpoint
        method on us.
        
        @param {dict} same_host_endpoints_contacted_dict --- Keys are
        uuids.  Values are endpoint objects.  

        @param {bool} partner_contacted --- True if the event has sent
        a message as part of a sequence to partner.  False otherwise.

        Tells all endpoints that we have contacted to rollback their
        events as well.  
        '''
        util.logger_warn('rollback is pure virtual in EventParent')
        
        
# FIXME: must overload rollback, first_phase_transition_success,
# second_phase_transition_success
        
class RootEventParent(EventParent):
    def __init__(self,partner_uuid):
        '''
        @param{uuid} partner_uuid --- UUID of the attached neighbor
        endpoint
        '''
        self.uuid = util.generate_uuid()

        self.partner_uuid = partner_uuid
        # indices are event uuids.  Values are bools.  When all values
        # are true in this dict, then we can transition into second
        # phase commit.
        self.endpoints_waiting_on_commit = {}
        
    def get_uuid(self):
        return self.uuid

    def first_phase_transition_success(
        self,same_host_endpoints_contacted_dict,partner_contacted,event):
        '''
        For arguments, @see EventParent.
        '''
        self.event = event
        
        # first keep track of all events that we are waiting on
        # hearing that first phase commit succeeded.
        if partner_contacted:
            self.endpoints_waiting_on_commit[self.partner_uuid] = False
            # send message to partner telling it to enter first phase
            # commit
            self.local_endpoint._forward_commit_request_partner(self.uuid)

        for waiting_on_uuid in same_host_endpoints_contacted_dict.keys():
            self.endpoints_waiting_on_commit[waiting_on_uuid] = False
            # send message to all other endpoints that we made direct
            # endpoint calls on that they should attempt first phase
            # commit
            endpoint = same_host_endpoints_contacted_dict[waiting_on_uuid]
            endpoint._receive_request_commit(self.uuid,self.local_endpoint)

        self.check_transition()
        
    def check_transition(self):
        '''
        If we are no longer waiting on any endpoint to acknowledge
        first phase commit, then transition into second phase commit.
        '''
        for endpt_transitioned in self.endpoints_waiting_on_commit.values():
            if not endpt_transitioned:
                return
        
        self.event.second_phase_commit()

    def rollback(
        self,backout_requester_endpoint_uuid,other_endpoints_contacted,
        partner_contacted):

        # tell any endpoints that we had called endpoint methods on to
        # back out their changes.
        for endpoint_to_rollback in other_endpoints_contacted.values():
            if endpoint_to_rollback.uuid != backout_requester_endpoint_uuid:
                endpoint_to_rollback._receive_request_backout(self.uuid,self.local_endpoint)

        # tell partner to backout its changes too
        if (partner_contacted and
            (backout_requester_endpoint_uuid != self.local_endpoint._partner_uuid)):
            self.local_endpoint._forward_backout_request_partner(self.uuid)
        

class PartnerEventParent(EventParent):
    def __init__(self,uuid,local_endpoint):
        self.uuid = uuid
        self.local_endpoint = local_endpoint
    def get_uuid(self):
        return self.uuid

class EndpointEventParent(EventParent):
    def __init__(self,uuid,parent_endpoint):
        self.uuid = self.parent_endpoint
    def get_uuid(self):
        return self.uuid

    

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


        # a dict containing all endpoints that this event has issued
        # commands to while executing.  On commit, must run through
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
