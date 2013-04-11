import util
import waldoEndpointServiceThread
import pickle
import waldoActiveEventMap
import waldoMessages
from util import Queue
import threading
import logging

class _Endpoint(object):
    '''
    All methods that begin with _receive, are called by other
    endpoints or from connection object's receiving a message from
    partner endpoint.

    All methods that begin with _forward or _send are called from
    active events on this endpoint.
    '''

    def __init__(self,waldo_classes,host_uuid,conn_obj,global_var_store):
        '''
        @param {dict} waldo_classes --- Contains common utilities
        needed by emitted code, such as WaldoNumVariable
        
        @param {uuid} host_uuid --- The uuid of the host this endpoint
        lives on.
        
        @param {ConnectionObject} conn_obj --- Used to write messages
        to partner endpoint.

        @param {_VariableStore} global_var_store --- Contains the
        peered and endpoint global data for this endpoint.  Will not
        add or remove any peered or endpoint global variables.  Will
        only make calls on them.
        '''
        self._uuid = util.generate_uuid()

        self._endpoint_uuid_str = str(self._uuid)
        
        self._waldo_classes = waldo_classes
        
        self._act_event_map = waldoActiveEventMap._ActiveEventMap(self)
        self._conn_obj = conn_obj
        
        # whenever we create a new _ExecutingEvent, we point it at
        # this variable store so that it knows where it can retrieve
        # variables.
        self._global_var_store = global_var_store

        self._endpoint_service_thread = waldoEndpointServiceThread._EndpointServiceThread(self)
        self._endpoint_service_thread.start()

        self._host_uuid = host_uuid
        
        # When go through first phase of commit, may need to forward
        # partner's endpoint uuid back to the root, so the endpoint
        # needs to keep track of its partner's uuid.  FIXME: right
        # now, manually setting partner uuids in connection object.
        # And not checking to ensure that the partner endpoint is set
        # before doing additional work. should create a proper
        # handshake instead.
        self._partner_uuid = None

        
        # both sides should run their onCreate methods to entirety
        # before we can execute any additional calls.
        self._ready_lock_ = threading.Lock()
        self._this_side_ready_bool = False
        self._other_side_ready_bool = False

        self._ready_waiting_list_mutex = threading.Lock()
        self._ready_waiting_list = []

        self._conn_obj.register_endpoint(self)


    def _ready_waiting_list_lock(self,additional):
        self._ready_waiting_list_mutex.acquire()

    def _ready_waiting_list_unlock(self,additional):
        self._ready_waiting_list_mutex.release()        
        
    def _block_ready(self):
        '''
        Returns True if both sides are initialized.  Otherwise, blocks
        until initialization is complete
        '''
        waiting_queue = None
        self._ready_waiting_list_lock('block_ready')
        if self._ready_waiting_list != None:
            waiting_queue = Queue.Queue()
            # when this endpoint becomes ready, every queue in this
            # list gets written into, this will unblock the method
            # below.
            self._ready_waiting_list.append(waiting_queue)

        self._ready_waiting_list_unlock('block_ready')

        if waiting_queue != None:
            waiting_queue.get()

        return True


    def _ready_lock(self,additional):
        self._ready_lock_.acquire()
            
    def _ready_unlock(self,additional):
        self._ready_lock_.release()
    
    def _other_side_ready(self):
        '''
        Gets called when the other side sends a message that its
        ready.
        '''
        self._ready_lock('other_side_ready')
        self._other_side_ready_bool = True
        set_ready = self._this_side_ready_bool and self._other_side_ready_bool
        self._ready_unlock('other_side_ready')

        if set_ready:
            self._set_ready()
        
    
    def _this_side_ready(self):
        '''
        Gets called when this side finishes its initialization
        '''
        self._ready_lock('this_side_ready')
        self._this_side_ready_bool = True
        set_ready = self._this_side_ready_bool and self._other_side_ready_bool
        self._ready_unlock('this_side_ready')

        # send message to the other side that we are ready
        self._notify_partner_ready()
        
        if set_ready:
            self._set_ready()


    def _swapped_in_block_ready(self):
        return True
            
    def _set_ready(self):
        # any future events that try to check if ready, will get True
        setattr(
            self,'_block_ready',self._swapped_in_block_ready)

        self._ready_waiting_list_lock('set_ready')        
        for queue in self._ready_waiting_list:
            queue.put(True)
        self._ready_waiting_list = None
        self._ready_waiting_list_unlock('set_ready')
        
    def _set_partner_uuid(self,uuid):
        '''
        FIXME: @see note above _partner_uuid.
        '''
        self._partner_uuid = uuid

        
    def _request_commit(self,uuid,requesting_endpoint):
        '''
        @see _EndpointServiceThread.request_commit
        '''
        self._endpoint_service_thread.request_commit(
            uuid,requesting_endpoint)

    def _receive_request_backout(self,uuid,requesting_endpoint):
        '''
        @see _EndpointServiceThread.receive_request_backout
        '''
        self._endpoint_service_thread.receive_request_backout(
            uuid,requesting_endpoint)

    def _receive_request_commit(self,uuid,requesting_endpoint):
        '''
        Called by another endpoint on the same host as this endpoint
        to begin the first phase of the commit of the active event
        with uuid "uuid."
        '''
        self._endpoint_service_thread.receive_request_commit_from_endpoint(
            uuid,requesting_endpoint)
        
    def _receive_request_complete_commit(self,uuid):
        '''
        Called by another endpoint on the same host as this endpoint
        to finish the second phase of the commit of active event with
        uuid "uuid."
        '''
        self._endpoint_service_thread.receive_request_complete_commit(
            uuid,
            False # complete commit request was not from partner
                  # endpoint.
            )

    def _receive_msg_from_partner(self,string_msg):
        '''
        Called by the connection object.

        @param {String} string_msg --- A raw byte string sent from
        partner.  Should be able to deserialize it, convert it into a
        message, and dispatch it as an event.

        Can receive a variety of messages from partner: request to
        execute a sequence block, request to commit a change to a
        peered variable, request to backout an event, etc.  In this
        function, we dispatch depending on message we receive.
        '''
        counter = 0
        while True:
            try:
                msg_map = pickle.loads(string_msg)
                break
            except:
                # import pdb
                # pdb.set_trace()
                counter +=1
                # util.get_logger().critical('error',extra=self._logging_info)
                if counter > 10:
                    raise 
        msg = waldoMessages._Message.map_to_msg(msg_map)
            
        if isinstance(msg,waldoMessages._PartnerRequestSequenceBlockMessage):
            self._endpoint_service_thread.receive_partner_request_message_sequence_block(
                msg)
        elif isinstance(msg,waldoMessages._PartnerCommitRequestMessage):
            self._endpoint_service_thread.receive_partner_request_commit(msg)
            
        elif isinstance(msg,waldoMessages._PartnerCompleteCommitRequestMessage):
            self._endpoint_service_thread.receive_partner_request_complete_commit(msg)
        elif isinstance(msg,waldoMessages._PartnerBackoutCommitRequestMessage):
            self._receive_request_backout(msg.event_uuid,util.PARTNER_ENDPOINT_SENTINEL)
        elif isinstance(msg,waldoMessages._PartnerRemovedSubscriberMessage):
            self._receive_removed_subscriber(
                msg.event_uuid, msg.removed_subscriber_uuid,
                msg.host_uuid,msg.resource_uuid)

        elif isinstance(msg,waldoMessages._PartnerAdditionalSubscriberMessage):
            self._receive_additional_subscriber(
                msg.event_uuid, msg.additional_subscriber_uuid,
                msg.host_uuid,msg.resource_uuid)

        elif isinstance(msg,waldoMessages._PartnerFirstPhaseResultMessage):
            if msg.successful:
                self._receive_first_phase_commit_successful(
                    msg.event_uuid,msg.sending_endpoint_uuid,
                    msg.children_event_endpoint_uuids)
            else:
                self._receive_first_phase_commit_unsuccessful(
                    msg.event_uuid,msg.sending_endpoint_uuid)

        elif isinstance(msg,waldoMessages._PartnerNotifyOfPeeredModified):
            self._endpoint_service_thread.receive_partner_notify_of_peered_modified_msg(msg)
            
        elif isinstance(msg,waldoMessages._PartnerNotifyOfPeeredModifiedResponse):
            self._endpoint_service_thread.receive_partner_notify_of_peered_modified_rsp_msg(msg)

        elif isinstance(msg,waldoMessages._PartnerNotifyReady):
            self._receive_partner_ready(msg.endpoint_uuid)
            
        else:
            #### DEBUG
            util.logger_assert(
                'Do not know how to convert message to event action ' +
                'in _receive_msg_from_partner.')
            #### END DEBUG

    def _receive_partner_ready(self,partner_uuid = None):
        self._endpoint_service_thread.receive_partner_ready()
        self._set_partner_uuid(partner_uuid)
        
    def _notify_partner_ready(self):
        '''
        Tell partner endpoint that I have completed my onReady action.
        '''
        msg = waldoMessages._PartnerNotifyReady(self._uuid)
        self._conn_obj.write(pickle.dumps(msg.msg_to_map()),self)

            
    def _notify_partner_removed_subscriber(
        self,event_uuid,removed_subscriber_uuid,host_uuid,resource_uuid):
        '''
        Send a message to partner that a subscriber is no longer
        holding a lock on a resource to commit it.
        '''
        msg = waldoMessages._PartnerRemovedSubscriberMessage(
            event_uuid,removed_subscriber_uuid,host_uuid,resource_uuid)
        self._conn_obj.write(pickle.dumps(msg.msg_to_map()),self)

    def _forward_first_phase_commit_unsuccessful(
        self,event_uuid,endpoint_uuid):
        '''
        @param {uuid} event_uuid
        @param {uuid} endpoint_uuid
        
        Partner endpoint is subscriber of event on this endpoint with
        uuid event_uuid.  Send to partner a message that the first
        phase of the commit was unsuccessful on endpoint with uuid
        endpoint_uuid (and therefore, it and everything along the path
        should roll back their commits).
        '''
        msg = waldoMessages._PartnerFirstPhaseResultMessage(
            event_uuid,endpoint_uuid,False)
        self._conn_obj.write(pickle.dumps(msg.msg_to_map()),self)

    def _forward_first_phase_commit_successful(
        self,event_uuid,endpoint_uuid,children_event_endpoint_uuids):
        '''
        @param {uuid} event_uuid

        @param {uuid} endpoint_uuid
        
        @param {array} children_event_endpoint_uuids --- 
        
        Partner endpoint is subscriber of event on this endpoint with
        uuid event_uuid.  Send to partner a message that the first
        phase of the commit was successful for the endpoint with uuid
        endpoint_uuid, and that the root can go on to second phase of
        commit when all endpoints with uuids in
        children_event_endpoint_uuids have confirmed that they are
        clear to commit.
        '''
        msg = waldoMessages._PartnerFirstPhaseResultMessage(
            event_uuid,endpoint_uuid,True,
            children_event_endpoint_uuids)
        self._conn_obj.write(pickle.dumps(msg.msg_to_map()),self)
        
    def _notify_partner_of_additional_subscriber(
        self,event_uuid,additional_subscriber_uuid,host_uuid,resource_uuid):
        '''
        Send a message to partner that a subscriber has just started
        holding a lock on a resource to commit it.
        '''
        msg = waldoMessages._PartnerAdditionalSubscriberMessage(
            event_uuid,additional_subscriber_uuid,host_uuid,resource_uuid)
        self._conn_obj.write(pickle.dumps(msg.msg_to_map()),self)
        
        
    def _receive_additional_subscriber(
        self,event_uuid,subscriber_event_uuid,host_uuid,resource_uuid):
        '''
        @param {uuid} event_uuid --- The uuid of the event that also
        exists on this endpoint that is trying to subscribe to a
        resource (with uuid resource_uuid) that subscriber_event_uuid
        is also subscribed for.

        @param {uuid} subscriber_event_uuid --- UUID for an event that
        is not necesarilly on this host that holds a subscription on
        the same resource that we are trying to subscribe to.

        @see notify_additional_subscriber (in _ActiveEvent.py)
        '''
        self._endpoint_service_thread.receive_additional_subscriber(
            event_uuid,subscriber_event_uuid,host_uuid,resource_uuid)

    def _receive_removed_subscriber(
        self,event_uuid,removed_subscriber_event_uuid,host_uuid,resource_uuid):
        '''
        @see _receive_additional_subscriber
        '''
        self._endpoint_service_thread.receive_removed_subscriber(
            event_uuid,removed_subscriber_event_uuid,host_uuid,resource_uuid)

    def _receive_endpoint_call(
        self,endpoint_making_call,event_uuid,func_name,result_queue,*args):
        '''
        For params, @see _EndpointServiceThread.endpoint_call
        
        Non-blocking.  Requests the endpoint_service_thread to perform
        the endpoint function call listed as func_name.
        '''
        self._endpoint_service_thread.receive_endpoint_call(
            endpoint_making_call,event_uuid,func_name,result_queue,*args)


    def _receive_first_phase_commit_successful(
        self,event_uuid,endpoint_uuid,children_event_endpoint_uuids):
        '''
        One of the endpoints, with uuid endpoint_uuid, that we are
        subscribed to was able to complete first phase commit for
        event with uuid event_uuid.

        @param {uuid} event_uuid
        
        @param {uuid} endpoint_uuid --- The uuid of the endpoint that
        was able to complete the first phase of the commit.  (Note:
        this may not be the same uuid as that for the endpoint that
        called _receive_first_phase_commit_successful on this
        endpoint.  We only keep track of the endpoint that originally
        committed.)
        
        Forward the message on to the root.  
        '''
        self._endpoint_service_thread.receive_first_phase_commit_message(
            event_uuid,endpoint_uuid,True,children_event_endpoint_uuids)
        

    def _receive_first_phase_commit_unsuccessful(
        self,event_uuid,endpoint_uuid):
        '''
        @see _receive_first_phase_commit_successful
        '''
        self._endpoint_service_thread.receive_first_phase_commit_message(
            event_uuid,endpoint_uuid,False)


    def _send_partner_message_sequence_block_request(
        self,block_name,event_uuid,reply_with_uuid,reply_to_uuid,
        invalidation_listener,sequence_local_store,first_msg):
        '''
        Sends a message using connection object to the partner
        endpoint requesting it to perform some message sequence
        action.
        
        @param {String or None} block_name --- The name of the
        sequence block we want to execute on the partner
        endpoint. (Note: this is how that sequence block is named in
        the source Waldo file, not how it is translated by the
        compiler into a function.)  It can also be None if this is the
        final message sequence block's execution.  

        @param {uuid} event_uuid --- The uuid of the requesting event.

        @param {uuid} reply_with_uuid --- When the partner endpoint
        responds, it should place reply_with_uuid in its reply_to
        message field.  That way, we can determine which message the
        partner endpoint was replying to.

        @param {uuid or None} reply_to_uuid --- If this is the
        beginning of a sequence of messages, then fill the reply_to
        field of the message with None (the message is not a reply to
        anything that we have seen so far).  Otherwise, put the
        reply_with message field of the last message that the partner
        said as part of this sequence in.

        @param {_InvalidationListener} invalidation_listener --- The
        invalidation listener that is requesting the message to be
        sent.

        @param {_VariableStore} sequence_local_store --- We convert
        all changes that we have made to both peered data and sequence
        local data to maps of deltas so that the partner endpoint can
        apply the changes.  We use the sequence_local_store to get
        changes that invalidation_listener has made to sequence local
        data.  (For peered data, we can just use
        self._global_var_store.)

        @param {bool} first_msg --- If we are sending the first
        message in a sequence block, then we must force the sequence
        local data to be transmitted whether or not it was modified.
        
        '''
        glob_deltas = self._global_var_store.generate_deltas(
            invalidation_listener)
        sequence_local_deltas = sequence_local_store.generate_deltas(
            invalidation_listener,first_msg)
        
        msg_to_send = waldoMessages._PartnerRequestSequenceBlockMessage(
            event_uuid,block_name,reply_with_uuid,reply_to_uuid,
            glob_deltas,sequence_local_deltas)

        msg_map = msg_to_send.msg_to_map()

        sending_msg_str = pickle.dumps(msg_map)
        msg_len = len(sending_msg_str)
        self._conn_obj.write(sending_msg_str,self)

        
    def _forward_commit_request_partner(self,active_event):
        '''
        @param {_ActiveEvent} active_event --- Has the same uuid as
        the event we will forward a commit to our partner for.
        '''
        # FIXME: may be a way to piggyback commit with final event in
        # sequence.

        msg = waldoMessages._PartnerCommitRequestMessage(active_event.uuid)
        msg_map = msg.msg_to_map()
        self._conn_obj.write(pickle.dumps(msg_map),self)


    def _notify_partner_peered_before_return(
        self,event_uuid,reply_with_uuid,peered_deltas):
        '''
        @see waldoActiveEvent.wait_if_modified_peered
        '''
        msg = waldoMessages._PartnerNotifyOfPeeredModified(
            event_uuid,reply_with_uuid,peered_deltas)
        msg_map = msg.msg_to_map()
        self._conn_obj.write(pickle.dumps(msg_map),self)
        
    def _notify_partner_peered_before_return_response(
        self,event_uuid,reply_to_uuid,invalidated):
        '''
        @see waldoMessages._PartnerNotifyOfPeeredModifiedResponse
        '''
        msg = waldoMessages._PartnerNotifyOfPeeredModifiedResponse(
            event_uuid,reply_to_uuid,invalidated)
        msg_map = msg.msg_to_map()
        self._conn_obj.write(pickle.dumps(msg_map),self)
        

    def _forward_complete_commit_request_partner(self,active_event):
        '''
        Active event on this endpoint has completed its commit and it
        wants you to tell partner endpoint as well to complete its
        commit.
        '''
        msg = waldoMessages._PartnerCompleteCommitRequestMessage(active_event.uuid)
        msg_map = msg.msg_to_map()
        self._conn_obj.write(pickle.dumps(msg_map),self)
        
    def _forward_backout_request_partner(self,active_event):
        '''
        @param {_ActiveEvent} active_event --- Has the same uuid as
        the event we will forward a backout request to our partner
        for.
        '''
        msg = waldoMessages._PartnerBackoutCommitRequestMessage(active_event.uuid)
        msg_map = msg.msg_to_map()
        self._conn_obj.write(pickle.dumps(msg_map),self)

