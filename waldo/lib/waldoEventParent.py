import util
from waldoCallResults import _RescheduleRootCallResult, _CompleteRootCallResult

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
        uuids.  Values are EventSubscribedTo objects (which wrap
        endpoint objects).

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
            endpoint = same_host_endpoints_contacted_dict[waiting_on_uuid].endpoint_object
            endpoint._receive_request_commit(self.uuid,self.local_endpoint)


        
    def second_phase_transition_success(
        self,same_host_endpoints_contacted_dict,partner_contacted):
        '''        
        @param {dict} same_host_endpoints_contacted_dict --- Keys are
        uuids.  Values are EventSubscribedTo objects (which wrap
        endpoint objects).

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
        uuids.  Values are EventSubscribedTo objects (which wrap
        endpoint objects).

        @param {bool} partner_contacted --- True if the event has sent
        a message as part of a sequence to partner.  False otherwise.

        Tells all endpoints that we have contacted to rollback their
        events as well.  
        '''
        util.logger_warn('rollback is pure virtual in EventParent')
        
        
# FIXME: must overload rollback, first_phase_transition_success,
# second_phase_transition_success
        
class RootEventParent(EventParent):
    def __init__(self,local_endpoint,partner_uuid):
        '''
        @param{uuid} partner_uuid --- UUID of the attached neighbor
        endpoint
        '''
        self.uuid = util.generate_uuid()
        self.local_endpoint = local_endpoint
        self.partner_uuid = partner_uuid
        # indices are event uuids.  Values are bools.  When all values
        # are true in this dict, then we can transition into second
        # phase commit.
        self.endpoints_waiting_on_commit = {}

        # when the root tries to commit the event, it blocks while
        # reading the event_complete_queue
        self.event_complete_queue = util.Queue.Queue()

        
    def get_uuid(self):
        return self.uuid

    def first_phase_transition_success(
        self,same_host_endpoints_contacted_dict,partner_contacted,event):
        '''
        For arguments, @see EventParent.
        '''
        super(RootEventParent,self).first_phase_transition_success(
            same_host_endpoints_contacted_dict,partner_contacted,event)
        
        # after first phase has completed, should check if can
        # transition directly to second phase (ie, no other endpoints
        # were involved in event.)
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

    def second_phase_transition_success(
        self,same_host_endpoints_contacted_dict,partner_contacted):
        '''
        @see second_phase_transition_success in EventParent
        '''
        self.event_complete_queue.put(_CompleteRootCallResult())
        # tell any endpoints that we had called endpoint methods on to
        # run second phase of commit
        for endpoint_to_second_phase_commit in same_host_endpoints_contacted_dict.values():
            endpoint_to_second_phase_commit._receive_request_complete_commit(self.uuid)

        if partner_contacted:
            self.local_endpoint._forward_complete_commit_request_partner(self.uuid)
            
        
    def rollback(
        self,backout_requester_endpoint_uuid,other_endpoints_contacted,
        partner_contacted):

        self.event_complete_queue.put(_RescheduleRootCallResult())

        
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
    def __init__(self,uuid,parent_endpoint,local_endpoint,result_queue):
        self.uuid = uuid
        self.parent_endpoint = parent_endpoint
        self.local_endpoint = local_endpoint
        self.result_queue = result_queue
        
    def get_uuid(self):
        return self.uuid

