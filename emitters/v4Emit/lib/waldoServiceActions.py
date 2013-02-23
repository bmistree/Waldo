import util
import waldoCallResults
import threading

class _Action(object):
    '''
    Any action that we can take from within EndpointServiceThread,
    inherits from Action.  Essentially, we create action objects, with
    all of their relevant data, pass them into a threadsafe queue and
    then service them in a separate thread's event loop.
    '''
    def service(self):
        util.logger_assert(
            'Error.  Action\'s run method is pure virtual.')

        
class _ReceivePartnerMessageRequestSequenceBlockAction(_Action):
    '''
    Corresponds to case when partner endpoint receives a request for
    local endpoint to execute a block sequence.
    '''

    def __init__(self,local_endpoint,partner_request_block_msg):
        '''
        @param {_Endpoint object} local_endpoint --- The endpoint that
        received a message requesting it to execute one of its
        sequence blocks.

        @param {_PartnerRequestSequenceBlockMessage}
        partner_request_block_msg
        '''

        self.local_endpoint = local_endpoint
        self.partner_request_block_msg = partner_request_block_msg
        

    def service(self):
        event_uuid = self.partner_request_block_msg.event_uuid
        
        evt = self.local_endpoint._act_event_map.get_or_create_partner_event(
            event_uuid)

        # FIXME: may eventually want to move this into its own thread
        # a la PartnerRequestCommitAction
        
        evt.recv_partner_sequence_call_msg(self.partner_request_block_msg)


class _ReceiveSubscriberAction(_Action,threading.Thread):
    '''
    To avoid deadlock in the first phase of commit, we forward the
    uuids of any events that try to commit to the same resource
    another event is.  In this case, it's a notification that the
    other event has backed off trying to commit to the same resource.
    '''

    def __int__(
        self,local_endpoint,event_uuid,subscriber_event_uuid,
        resource_uuid, removed):
        '''
        @param {bool} removed --- True if the subscriber_event_uuid
        was removed from listening to resoure, false otherwise.
        '''

        self.local_endpoint = local_endpoint
        self.event_uuid = event_uuid
        self.subscriber_event_uuid = subscriber_event_uuid
        self.resource_uuid = resource_uuid
        self.removed = removed
        
        threading.Thread.__init__(self)
        
    def service(self):
        self.start()

    def run(self):
        evt = self.local_endpoint._act_event_map.get_event(self.event_uuid)

        if self.removed:
            evt.notify_removed_subscriber(
                self.subscriber_event_uuid,self.resource_uuid)
        else:
            evt.notify_additional_subscriber(
                self.subscriber_event_uuid,self.resource_uuid)
    
        
class _ReceivePartnerRequestCommitAction(_Action,threading.Thread):
    '''
    The local endpoint's partner has requested the local endpoint to
    begin the first phase of committing changes (note: not complete
    committing the changes, just begin the first phase) for an event.
    '''
    def __init__(self,local_endpoint,event_uuid):
        self.local_endpoint = local_endpoint
        self.event_uuid = event_uuid

        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        evt = self.local_endpoint._act_event_map.get_event(self.event_uuid)
        
        #### DEBUG
        if evt == None:
            util.logger_assert(
                'Requested committing an event that does not exist')
        #### END DEBUG

        evt.forward_commit_request_and_try_holding_commit_on_myself(
            True)        

    def service(self):
        self.start()

        
class _ReceiveRequestCompleteCommitAction(_Action,threading.Thread):
    '''
    Another endpoint (either on the same host as I am or my
    partner) asked me to complete the second phase of the commit
    for an event with uuid event_uuid.

    @see waldoEndpoint._EndpointServiceThread.request_complete_commit
    '''
    def __init__(self,local_endpoint,event_uuid,request_from_partner):
        '''
        For params, @see
        waldoEndpoint._EndpointServiceThread.request_complete_commit
        '''
        self.local_endpoint = local_endpoint
        self.event_uuid = event_uuid
        self.request_from_partner = request_from_partner
        threading.Thread.__init__(self)
        self.daemon = True
        
        
    def run(self):
        '''
        1.  Grab the endpoint from active event map (if it exists)
        
        2.  Call its complete_commit_and_forward_complete_msg method.  
        '''
        evt = self.local_endpoint._act_event_map.get_event(self.event_uuid)
        
        if evt == None:
            # event may not exist, for instance if got multiple
            # complete commit messages because of loops in endpoint
            # call graph.
            return

        # if the request to complete the commit was from our partner,
        # then we can skip sending a request to our partner to
        # complete the commit.
        evt.complete_commit_and_forward_complete_msg(self.request_from_partner)
        
    def service(self):
        # just start the thread
        self.start()
        
        
class _ReceiveRequestBackoutAction(_Action):
    '''
    We were requested to backout an event.  Check if we have the
    event, back it out if can, and forward the backout message to
    others.
    '''
    def __init__(self,local_endpoint,uuid,requesting_endpoint):
        '''
        @param {_Endpoint object} local_endpoint --- The endpoint
        which was requested to backout.  (Ie, the endpoint on which
        this action will take place.)

        @param{UUID}  uuid --- @see _EndpointServiceThread.request_backout
        
        @param{either Endpoint object or
        util.PARTNER_ENDPOINT_SENTINEL} requesting_endpoint ---
        @see _EndpointServiceThread.request_backout
        '''
        self.local_endpoint = local_endpoint
        self.uuid = uuid
        self.requesting_endpoint = requesting_endpoint


    def service(self):
        evt = self.local_endpoint._act_event_map.get_and_remove_event(
            self.uuid)

        if evt == None:
            # could happen for instance if there are loops in endpoint
            # call graph.  In this case, might get more than one
            # request to backout an event.  However, the first backout
            # has already removed the the active event from the active
            # event map.
             return

        skip_partner = False
        if self.requesting_endpoint == util.PARTNER_ENDPOINT_SENTINEL:
            skip_partner = True

        # FIXME: should probably be in a separate thread
        evt.forward_backout_request_and_backout_self(skip_partner)

        

class _ReceiveEndpointCallAction(_Action):
    '''
    Another endpoint has asked us to execute an action on our own
    endpoint as part of a global event.
    '''

    def __init__(
        self,local_endpoint,endpoint_making_call,
        event_uuid,func_name,result_queue,*args):
        '''
        @param {_Endpoint object} local_endpoint --- The endpoint
        which was requested to backout.  (Ie, the endpoint on which
        this action will take place.)

        For other @params, @see, _EndpointServiceThread._endpointCall.
        '''

        self.local_endpoint = local_endpoint
        self.endpoint_making_call = endpoint_making_call
        self.event_uuid = event_uuid
        self.result_queue = result_queue
        self.args = args

        if not hasattr(
            self.local_endpoint,
            util.endpoint_call_func_name(self.func_name)):
            
            self.to_exec = None
            self.result_queue.put(
                waldoCallResults._NoMethodEndpointCallError(
                    func_name))

        else:
            to_exec = getattr(
                self.local_endpoint,
                util.endpoint_call_func_name(self.func_name))

    def service(self):

        act_event = self.local_endpoint._act_event_map.get_or_create_endpoint_called_event(
            self.endpoint_making_call,self.event_uuid)
        
        evt_ctx = waldoExecutingEvent._ExecutingEventContext(
            self.local_endpoint._global_var_store,
            # should not have any sequence local data from an endpoint
            # call.
            waldoVariableStore._VaribaleStore() )
        
        exec_event = waldoExecutingEvent._ExecutingEvent(
            self.to_exec,act_event,evt_ctx,*self.args)

        exec_event.start()
