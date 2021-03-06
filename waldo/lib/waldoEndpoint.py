import waldo.lib.util as util
import waldo.lib.waldoActiveEventMap as waldoActiveEventMap
import waldo.lib.waldoCallResults as waldoCallResults
from util import Queue
import threading
import time
import traceback
from waldo.lib.waldoHeartbeat import Heartbeat
from waldo.lib.proto_compiled.generalMessage_pb2 import GeneralMessage
from waldo.lib.waldoEndpointBase import EndpointBase
from waldo.lib.proto_compiled.partnerError_pb2 import PartnerError
import waldo.lib.waldoServiceActions as waldoServiceActions

HEARTBEAT_TIMEOUT = 30

class _Endpoint(EndpointBase):
    '''
    All methods that begin with _receive, are called by other
    endpoints or from connection object's receiving a message from
    partner endpoint.

    All methods that begin with _forward or _send are called from
    active events on this endpoint.
    '''

    def __init__(self,waldo_classes,host_uuid,conn_obj,global_var_store,*args):
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

        self._clock = waldo_classes['Clock']
        self._act_event_map = waldoActiveEventMap._ActiveEventMap(
            self,self._clock)

        self._conn_obj = conn_obj
        
        # whenever we create a new _ExecutingEvent, we point it at
        # this variable store so that it knows where it can retrieve
        # variables.
        self._global_var_store = global_var_store

        # put service actions into thread pool to be executed
        self._thread_pool = waldo_classes['ThreadPool']

        self._all_endpoints = waldo_classes['AllEndpoints']
        self._all_endpoints.add_endpoint(self)
        
        
        self._host_uuid = host_uuid

        self._signal_queue = Queue.Queue()
        
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

        self._stop_mutex = threading.Lock()
        # has stop been called locally, on the partner, and have we
        # performed cleanup, respectively
        self._stop_called = False
        self._partner_stop_called = False
        self._stop_complete = False
        
        self._stop_blocking_queues = []

        # holds callbacks to call when stop is complete
        self._stop_listener_id_assigner = 0
        self._stop_listeners = {}

        self._conn_failed = False
        self._conn_mutex = threading.Lock()

        # start heartbeat thread
        self._heartbeat = Heartbeat(socket=self._conn_obj, 
            timeout_cb=self.partner_connection_failure,*args)
        self._heartbeat.start()
        self._send_clock_update()
        
        
    def _stop_lock(self):
        self._stop_mutex.acquire()
        
    def _stop_unlock(self):
        self._stop_mutex.release()

    def _ready_waiting_list_lock(self,additional):
        self._ready_waiting_list_mutex.acquire()

    def _ready_waiting_list_unlock(self,additional):
        self._ready_waiting_list_mutex.release()        

    def partner_connection_failure(self):
        '''
        Called when it has been determined that the connection to the partner
        endpoint has failed prematurely. Closes the socket and raises a network
        exception, thus backing out from all current events, and sets the 
        conn_failed flag, but only if this method has not been called before.
        '''
        # notify all_endpoints to remove this endpoint because it has
        # been stopped
        self._all_endpoints.network_exception(self)
        
        self._conn_mutex.acquire()
        self._conn_obj.close()
        self._raise_network_exception()
        self._conn_failed = True
        self._conn_mutex.release()

    def get_conn_failed(self):
        '''
        Returns true if the runtime has detected a network failure and false
        otherwise.
        '''
        self._conn_mutex.acquire()
        conn_failed = self._conn_failed    
        self._conn_mutex.release()
        return conn_failed


    def _send_clock_update(self):
        '''
        Grab timestamp from clock and send it over to partner.
        '''
        current_clock_timestamp = self._clock.get_timestamp()
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.TIMESTAMP_UPDATE
        timestamp_updated = general_message.timestamp_updated
        timestamp_updated.data = current_clock_timestamp
        self._conn_obj.write(general_message.SerializeToString(),self)


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
        

    def service_signal(self):
        try:
            signaler = self._signal_queue.get_nowait()
            signaler.call()            
        except Queue.Empty:
            pass
                
            
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


    def _receive_request_backout(self,uuid,requesting_endpoint):
        '''
        @param {uuid} uuid --- The uuid of the _ActiveEvent that we
        want to backout.

        @param {either Endpoint object or
        util.PARTNER_ENDPOINT_SENTINEL} requesting_endpoint ---
        Endpoint object if was requested to backout by endpoint objects
        on this same host (from endpoint object calls).
        util.PARTNER_ENDPOINT_SENTINEL if was requested to backout
        by partner.
        
        Called by another endpoint on this endpoint (not called by
        external non-Waldo code).
        '''
        req_backout_action = waldoServiceActions._ReceiveRequestBackoutAction(
            self,uuid,requesting_endpoint)
        self._thread_pool.add_service_action(req_backout_action)

    def _receive_request_commit(self,uuid,requesting_endpoint):
        '''
        Called by another endpoint on the same host as this endpoint
        to begin the first phase of the commit of the active event
        with uuid "uuid."

        @param {uuid} uuid --- The uuid of the _ActiveEvent that we
        want to commit.

        @param {Endpoint object} requesting_endpoint --- 
        Endpoint object if was requested to commit by endpoint objects
        on this same host (from endpoint object calls).
        
        Called by another endpoint on this endpoint (not called by
        external non-Waldo code).

        Forward the commit request to any other endpoints that were
        touched when the event was processed on this side.
        '''
        endpoint_request_commit_action = (
            waldoServiceActions._ReceiveRequestCommitAction(
                self,uuid,False))
        self._thread_pool.add_service_action(endpoint_request_commit_action)

    def _receive_request_complete_commit(self,event_uuid):
        '''
        Called by another endpoint on the same host as this endpoint
        to finish the second phase of the commit of active event with
        uuid "uuid."

        Another endpoint (either on the same host as I am or my
        partner) asked me to complete the second phase of the commit
        for an event with uuid event_uuid.
        
        @param {uuid} event_uuid --- The uuid of the event we are
        trying to commit.

        '''
        req_complete_commit_action = (
            waldoServiceActions._ReceiveRequestCompleteCommitAction(
                self,event_uuid,False))

        self._thread_pool.add_service_action(req_complete_commit_action)


    def _raise_network_exception(self):
        '''
        Called by the connection object when a network error is detected.

        Sends a message to each active event indicating that the connection
        with the partner endpoint has failed. Any corresponding endpoint calls
        waiting on an event involving the partner will throw a NetworkException,
        which will result in a backout (and be re-raised) if not caught by
        the programmer.
        '''
        self._act_event_map.inform_events_of_network_failure()

    def _propagate_back_exception(self,event_uuid,priority,exception):
        '''
        Called by the active event when an exception has occured in
        the midst of a sequence and it needs to be propagated back
        towards the root of the active event. Sends a partner_error
        message to the partner containing the event and endpoint
        uuids.
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_ERROR
        error = general_message.error
        error.event_uuid.data = event_uuid

        error.host_uuid.data = self._uuid
        if isinstance(exception, util.NetworkException):
            error.type = PartnerError.NETWORK
            error.trace = exception.trace
        elif isinstance(exception, util.ApplicationException):
            error.type = PartnerError.APPLICATION
            error.trace = exception.trace
        else:
            error.trace = traceback.format_exc()
            error.type = PartnerError.APPLICATION
        self._conn_obj.write(general_message.SerializeToString(),self)

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
        general_msg = GeneralMessage()
        general_msg.ParseFromString(string_msg)

        if general_msg.HasField('notify_ready'):
            endpoint_uuid = general_msg.notify_ready.endpoint_uuid
            self._receive_partner_ready(endpoint_uuid.data)
        elif general_msg.HasField('notify_of_peered_modified_resp'):
            service_action = waldoServiceActions._ReceivePeeredModifiedResponseMsg(
                self,general_msg.notify_of_peered_modified_resp)
            self._thread_pool.add_service_action(service_action)

        elif general_msg.HasField('timestamp_updated'):
            clock_timestamp = general_msg.timestamp_updated.data
            self._clock.got_partner_timestamp(clock_timestamp)            
            
        elif general_msg.HasField('request_sequence_block'):
            service_action =  waldoServiceActions._ReceivePartnerMessageRequestSequenceBlockAction(
                self,general_msg.request_sequence_block)
            self._thread_pool.add_service_action(service_action)
            
        elif general_msg.HasField('notify_of_peered_modified'):
            service_action = waldoServiceActions._ReceivePeeredModifiedMsg(
                self,general_msg.notify_of_peered_modified)
            self._thread_pool.add_service_action(service_action)

        elif general_msg.HasField('stop'):
            t = threading.Thread(target= self._handle_partner_stop_msg,args=(general_msg.stop,))
            t.start()

        elif general_msg.HasField('first_phase_result'):
            if general_msg.first_phase_result.successful:
                self._receive_first_phase_commit_successful(
                    general_msg.first_phase_result.event_uuid.data,
                    general_msg.first_phase_result.sending_endpoint_uuid.data,
                    [x.data for x  in general_msg.first_phase_result.children_event_endpoint_uuids])
            else:
                self._receive_first_phase_commit_unsuccessful(
                    general_msg.first_phase_result.event_uuid.data,
                    general_msg.first_phase_result.sending_endpoint_uuid.data)

        elif general_msg.HasField('additional_subscriber'):
            self._receive_additional_subscriber(
                general_msg.additional_subscriber.event_uuid.data,
                general_msg.additional_subscriber.additional_subscriber_uuid.data,
                general_msg.additional_subscriber.host_uuid.data,
                general_msg.additional_subscriber.resource_uuid.data)

        elif general_msg.HasField('promotion'):
            self._receive_promotion(
                general_msg.promotion.event_uuid.data,
                general_msg.promotion.new_priority.data)
            
        elif general_msg.HasField('removed_subscriber'):
            self._receive_removed_subscriber(
                general_msg.removed_subscriber.event_uuid.data,
                general_msg.removed_subscriber.removed_subscriber_uuid.data,
                general_msg.removed_subscriber.host_uuid.data,
                general_msg.removed_subscriber.resource_uuid.data)

        elif general_msg.HasField('backout_commit_request'):
            self._receive_request_backout(
                general_msg.backout_commit_request.event_uuid.data,
                util.PARTNER_ENDPOINT_SENTINEL)

        elif general_msg.HasField('complete_commit_request'):
            service_action = (
                waldoServiceActions._ReceiveRequestCompleteCommitAction(
                    self,general_msg.complete_commit_request.event_uuid.data,True))
            self._thread_pool.add_service_action(service_action)

        elif general_msg.HasField('commit_request'):
            service_action = (
                waldoServiceActions._ReceiveRequestCommitAction(
                    self,general_msg.commit_request.event_uuid.data,True))
            self._thread_pool.add_service_action(service_action)
            
        elif general_msg.HasField('error'):
            event = self._act_event_map.get_event(general_msg.error.event_uuid.data)
            event.send_exception_to_listener(general_msg.error)

        elif general_msg.HasField('heartbeat'):
            self._heartbeat.receive_heartbeat(general_msg.heartbeat.msg)

        #### DEBUG
        else:
            util.logger_assert(
                'Do not know how to convert message to event action ' +
                'in _receive_msg_from_partner.')
        #### END DEBUG


    def _receive_promotion(self,event_uuid,new_priority):
        promotion_action = waldoServiceActions._ReceivePromotionAction(
            self,event_uuid,new_priority)
        self._thread_pool.add_service_action(promotion_action)

        
    def _receive_partner_ready(self,partner_uuid = None):
        service_action = waldoServiceActions._ReceivePartnerReadyAction(self)
        self._thread_pool.add_service_action(service_action)
        self._set_partner_uuid(partner_uuid)

        
    def _notify_partner_ready(self):
        '''
        Tell partner endpoint that I have completed my onReady action.
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_NOTIFY_READY
        partner_notify_ready = general_message.notify_ready

        # endpoint uuid
        endpoint_uuid = partner_notify_ready.endpoint_uuid
        endpoint_uuid.data = self._uuid

        self._conn_obj.write(general_message.SerializeToString(),self)

    def _forward_promotion_message(self,uuid,new_priority):
        '''
        Send partner message that event has been promoted
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PROMOTION
        promotion_message = general_message.promotion
        promotion_message.event_uuid.data = uuid
        promotion_message.new_priority.data = new_priority
        self._conn_obj.write(general_message.SerializeToString(),self)
        
    def _notify_partner_removed_subscriber(
        self,event_uuid,removed_subscriber_uuid,host_uuid,resource_uuid):
        '''
        Send a message to partner that a subscriber is no longer
        holding a lock on a resource to commit it.
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_REMOVED_SUBSCRIBER
        
        removed_subscriber = general_message.removed_subscriber
        removed_subscriber.event_uuid.data = event_uuid
        removed_subscriber.removed_subscriber_uuid.data = removed_subscriber_uuid
        removed_subscriber.host_uuid.data = host_uuid
        removed_subscriber.resource_uuid.data = resource_uuid
        self._conn_obj.write(general_message.SerializeToString(),self)

        

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
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_FIRST_PHASE_RESULT
        first_phase_result = general_message.first_phase_result
        first_phase_result.event_uuid.data = event_uuid
        first_phase_result.sending_endpoint_uuid.data = endpoint_uuid
        first_phase_result.successful = False
        self._conn_obj.write(general_message.SerializeToString(),self)


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
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_FIRST_PHASE_RESULT
        first_phase_result = general_message.first_phase_result
        first_phase_result.event_uuid.data = event_uuid
        first_phase_result.sending_endpoint_uuid.data = endpoint_uuid
        first_phase_result.successful = True

        for child_event_uuid in children_event_endpoint_uuids:
            child_event_uuid_msg = first_phase_result.children_event_endpoint_uuids.add()
            child_event_uuid_msg.data = child_event_uuid
        
        self._conn_obj.write(general_message.SerializeToString(),self)

        
    def _notify_partner_of_additional_subscriber(
        self,event_uuid,additional_subscriber_uuid,host_uuid,resource_uuid):
        '''
        Send a message to partner that a subscriber has just started
        holding a lock on a resource to commit it.
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_ADDITIONAL_SUBSCRIBER

        additional_subscriber = general_message.additional_subscriber
        additional_subscriber.event_uuid.data = event_uuid
        additional_subscriber.additional_subscriber_uuid.data = additional_subscriber_uuid
        additional_subscriber.host_uuid.data = host_uuid
        additional_subscriber.resource_uuid.data = resource_uuid

        self._conn_obj.write(general_message.SerializeToString(),self)

        
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
        service_action = waldoServiceActions._ReceiveSubscriberAction(
            self,event_uuid,subscriber_event_uuid,
            host_uuid,resource_uuid,False)
        self._thread_pool.add_service_action(service_action)

        
    def _receive_removed_subscriber(
        self,event_uuid,removed_subscriber_event_uuid,host_uuid,resource_uuid):
        '''
        @see _receive_additional_subscriber
        '''
        service_action = waldoServiceActions._ReceiveSubscriberAction(
            self,event_uuid,removed_subscriber_event_uuid,
            host_uuid,resource_uuid,True)
        self._thread_pool.add_service_action(service_action)
        
        
    def _receive_endpoint_call(
        self,endpoint_making_call,event_uuid,priority,func_name,
        result_queue,*args):
        '''
        @param{_Endpoint object} endpoint_making_call --- The endpoint
        that made the endpoint call into this endpoint.

        @param {uuid} event_uuid --- 

        @param {priority} priority
        
        @param {string} func_name --- The name of the Public function
        to execute (in the Waldo source file).

        @param {Queue.Queue} result_queue --- When the function
        returns, wrap it in a
        waldoEndpointCallResult._EndpointCallResult object and put it
        into this threadsafe queue.  The endpoint that made the call
        is blocking waiting for the result of the call. 

        @param {*args} *args --- additional arguments that the
        function requires.

        Called by another endpoint on this endpoint (not called by
        external non-Waldo code).
        
        Non-blocking.  Requests the endpoint_service_thread to perform
        the endpoint function call listed as func_name.
        '''
        self._stop_lock()
        # check if should short-circuit processing 
        if self._stop_called:
            result_queue.push(
                waldoCallResults._StopAlreadyCalledEndpointCallResult())
            self._stop_unlock()
            return
        self._stop_unlock()

        endpt_call_action = waldoServiceActions._ReceiveEndpointCallAction(
            self,endpoint_making_call,event_uuid,priority,
            func_name,result_queue,*args)
        self._thread_pool.add_service_action(endpt_call_action)


    def _receive_first_phase_commit_successful(
        self,event_uuid,endpoint_uuid,children_event_endpoint_uuids):
        '''
        One of the endpoints, with uuid endpoint_uuid, that we are
        subscribed to was able to complete first phase commit for
        event with uuid event_uuid.

        @param {uuid} event_uuid --- The uuid of the event associated
        with this message.  (Used to index into local endpoint's
        active event map.)
        
        @param {uuid} endpoint_uuid --- The uuid of the endpoint that
        was able to complete the first phase of the commit.  (Note:
        this may not be the same uuid as that for the endpoint that
        called _receive_first_phase_commit_successful on this
        endpoint.  We only keep track of the endpoint that originally
        committed.)

        @param {None or list} children_event_endpoint_uuids --- None
        if successful is False.  Otherwise, a set of uuids.  The root
        endpoint should not transition from being in first phase of
        commit to completing commit until it has received a first
        phase successful message from endpoints with each of these
        uuids.
        
        Forward the message on to the root.  
        '''
        service_action = waldoServiceActions._ReceiveFirstPhaseCommitMessage(
            self,event_uuid,endpoint_uuid,True,children_event_endpoint_uuids)
        self._thread_pool.add_service_action(service_action)
        
    def _receive_first_phase_commit_unsuccessful(
        self,event_uuid,endpoint_uuid):
        '''
        @param {uuid} event_uuid --- The uuid of the event associated
        with this message.  (Used to index into local endpoint's
        active event map.)

        @param {uuid} endpoint_uuid --- The endpoint
        that tried to perform the first phase of the commit.  (Other
        endpoints may have forwarded the result on to us.)


        '''
        service_action = waldoServiceActions._ReceiveFirstPhaseCommitMessage(
            self,event_uuid,endpoint_uuid,False,None)
        self._thread_pool.add_service_action(service_action)

        

    def _send_partner_message_sequence_block_request(
        self,block_name,event_uuid,priority,reply_with_uuid,reply_to_uuid,
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
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_REQUEST_SEQUENCE_BLOCK

        request_sequence_block_msg = general_message.request_sequence_block

        # event uuid
        request_sequence_block_msg.event_uuid.data = event_uuid
        request_sequence_block_msg.priority.data = priority
        
        # name of block requesting
        if block_name != None:
            request_sequence_block_msg.name_of_block_requesting = block_name
            
        # reply with uuid
        reply_with_uuid_msg = request_sequence_block_msg.reply_with_uuid
        reply_with_uuid_msg.data = reply_with_uuid

        # reply to uuid
        if reply_to_uuid != None:
            reply_to_uuid_msg = request_sequence_block_msg.reply_to_uuid
            reply_to_uuid_msg.data = reply_to_uuid

        sequence_local_deltas = sequence_local_store.generate_deltas(
            invalidation_listener,first_msg,request_sequence_block_msg.sequence_local_var_store_deltas)
                
        glob_deltas = self._global_var_store.generate_deltas(
            invalidation_listener,False,request_sequence_block_msg.peered_var_store_deltas)

        self._conn_obj.write(general_message.SerializeToString(),self)


        
    def _forward_commit_request_partner(self,active_event_uuid):
        '''
        @param {UUID} active_event_uuid --- The uuid of the event we
        will forward a commit to our partner for.
        '''
        # FIXME: may be a way to piggyback commit with final event in
        # sequence.
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_COMMIT_REQUEST
        general_message.commit_request.event_uuid.data = active_event_uuid
        self._conn_obj.write(general_message.SerializeToString(),self)


    def _notify_partner_peered_before_return(
        self,event_uuid,reply_with_uuid,active_event):
        '''
        @see waldoActiveEvent.wait_if_modified_peered
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_NOTIFY_OF_PEERED_MODIFIED
        notify_of_peered_modified = general_message.notify_of_peered_modified

        glob_deltas = notify_of_peered_modified.glob_deltas
        self._global_var_store.generate_deltas(
            active_event,False,glob_deltas)

        notify_of_peered_modified.event_uuid.data = event_uuid
        notify_of_peered_modified.reply_with_uuid.data = reply_with_uuid
        self._conn_obj.write(general_message.SerializeToString(),self)

    def _notify_partner_peered_before_return_response(
        self,event_uuid,reply_to_uuid,invalidated):
        '''
        @see PartnerNotifyOfPeeredModifiedResponse.proto
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_NOTIFY_OF_PEERED_MODIFIED_RESPONSE

        notify_of_peered_modified_resp = general_message.notify_of_peered_modified_resp

        # load event uuid
        msg_event_uuid = notify_of_peered_modified_resp.event_uuid
        msg_event_uuid.data = event_uuid

        # load reply_to_uuid
        msg_reply_to_uuid = notify_of_peered_modified_resp.reply_to_uuid
        msg_reply_to_uuid.data = reply_to_uuid

        # load invalidated
        notify_of_peered_modified_resp.invalidated = invalidated
        
        self._conn_obj.write(general_message.SerializeToString(),self)
        

    def _forward_complete_commit_request_partner(self,active_event_uuid):
        '''
        Active event uuid on this endpoint has completed its commit
        and it wants you to tell partner endpoint as well to complete
        its commit.
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_COMPLETE_COMMIT_REQUEST
        general_message.complete_commit_request.event_uuid.data = active_event_uuid
        self._conn_obj.write(general_message.SerializeToString(),self)

    def _forward_backout_request_partner(self,active_event_uuid):
        '''
        @param {UUID} active_event_uuid --- The uuid of the event we
        will forward a backout request to our partner for.
        '''
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_BACKOUT_COMMIT_REQUEST
        general_message.backout_commit_request.event_uuid.data = active_event_uuid
        self._conn_obj.write(general_message.SerializeToString(),self)

    def _notify_partner_stop(self):
        general_message = GeneralMessage()
        general_message.message_type = GeneralMessage.PARTNER_STOP
        general_message.stop.dummy = False

        self._conn_obj.write_stop(general_message.SerializeToString(),self)

    def add_stop_listener(self, to_exec_on_stop):
        '''
        @param {callable} to_exec_on_stop --- When this endpoint
        stops, we execute to_exec_on_stop and any other
        stop listeners that were waiting.

        @returns {int or None} --- int id should be passed back inot
        remove_stop_listener to remove associated stop
        listener.
        '''
        self._stop_lock()
        if self._stop_called:
            self._stop_unlock()
            return None

        stop_id = self._stop_listener_id_assigner
        self._stop_listener_id_assigner += 1
        self._stop_listeners[stop_id] = to_exec_on_stop
        self._stop_unlock()

        return stop_id
        
    def remove_stop_listener(self, stop_id):
        '''
        int returned from add_stop_listener
        '''
        self._stop_lock()
        self._stop_listeners.pop(stop_id,None)
        self._stop_unlock()

    def is_stopped(self):
        '''
        Returns whether the endpoint is stopped.
        '''
        return self._stop_complete

    def stop(self,_skip_partner=False):
        '''
        Called from python or called when partner requests stop
        '''
        self._stop_lock()
        if self._stop_complete:
            # means that user called stop after we had already
            # stopped.  Do nothing
            self._stop_unlock()
            return

        # call to stop from external code should block until all
        # queues have unblocked
        blocking_queue = util.Queue.Queue()

        self._stop_blocking_queues.append(blocking_queue)

        stop_already_called = self._stop_called
        self._stop_called = True

        # if we have stopped and our partner has stopped, then request callback
        request_callback = self._partner_stop_called and self._stop_called
            
        self._stop_unlock()

        # act event map filters duplicate stop calls automatically
        self._act_event_map.initiate_stop(_skip_partner)

        if not stop_already_called:
            # we do not want to send multiple stop messages to our
            # partner.  just one.  this check ensures that we don't
            # infinitely send messages back and forth.
            self._notify_partner_stop()
            
        # 4 from above as well
        if request_callback:
            self._act_event_map.callback_when_stopped(self._stop_complete_cb)

        # blocking wait until ready to shut down.
        blocking_queue.get()

            
    def _stop_complete_cb(self):
        '''
        Passed in as callback arugment to active event map, which calls it.
        
        When this is executed:
           1) Stop was called on this side
           
           2) Stop was called on the other side
           
           3) There are no longer any running events in active event
              map

        Close the connection between both sides.  Unblock the stop call.
        '''
        # FIXME: chance of getting deadlock if one of the stop
        # listeners tries to remove itself.
        self._stop_lock()
        if self._stop_complete:
            self._stop_unlock()
            return
        
        self._stop_complete = True
        self._stop_unlock()

        for stop_listener in self._stop_listeners.values():
            stop_listener()
        self._conn_obj.close()
            
        # flush stop queues so that all stop calls unblock.  Note:
        # does not matter what value put into the queues.
        for q in self._stop_blocking_queues:
            q.put(None)


    def _handle_partner_stop_msg(self,msg):
        '''
        @param {PartnerStop message object} --- Has a single boolean
        field, which is meaningless.
                
        Received a stop message from partner:
          1) Label partner stop as having been called
          2) Initiate stop locally
          3) If have already called stop myself then tell active event
             map we're ready for a shutdown when it is
        '''

        # notify all_endpoints to remove this endpoint because it has
        # been stopped
        self._all_endpoints.endpoint_stopped(self)
        
        self._stop_lock()

        # 2 from above
        self._partner_stop_called = True

        # 3 from above
        t = threading.Thread(target = self.stop, args=(True,))
        t.start()

        # 4 from above
        request_callback = self._partner_stop_called and self._stop_called
        
        self._stop_unlock()

        # 4 from above as well
        if request_callback:
            self._act_event_map.callback_when_stopped(self._stop_complete_cb)

    # Builtin Endpoint Functions
    def _endpoint_func_call_prefix__waldo__id(self, *args):
        '''
        Builtin id method. Returns the endpoint's uuid.

        For use within Waldo code.
        '''
        return self._uuid

    def id(self):
        '''
        Builtin id method. Returns the endpoint's uuid.

        For use on endpoints within Python code.
        '''
        return self._uuid
        
