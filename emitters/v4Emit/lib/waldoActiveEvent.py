from invalidationListener import _InvalidationListener
import util
import threading
import waldoCallResults
import waldoExecutingEvent
import waldoVariableStore

class _SubscribedToElement(object):
    '''
    @see add_result_queue.
    '''
    
    # FIXME: could easily turn this into a named tuple.
    def __init__(self,endpoint_object,result_queue):
        '''
        @param {_Endpoint object} --- The endpoint object that we are
        subscribed to.

        @param {Queue.Queue} result_queue --- @see add_result_queue
        '''
        self.endpoint_object = endpoint_object
        self.result_queues = []
        self.add_result_queue(result_queue)

    def add_result_queue(self,result_queue):
        '''
        @param {Queue.Queue} result_queue --- Whenever we make an
        endpoint call on another endpoint object, we listen for the
        call's return value on result_queue.  When we backout an
        event, we put a backout sentinel value into the result queue
        so that any code that was waiting on the result of the
        endpoint call knows to stop executing.  We maintain all
        result_queues in SubscribedToElement so that we can write this
        sentinel into them if we backout.  (Note: the sentinel is
        waldoCallResults._BackoutBeforeEndpointCallResult)
        '''
        self.result_queues.append(result_queue)

    
class _ActiveEvent(_InvalidationListener):

    # when executing (or when it's finished executing but has not
    # committed or backed out yet).  Can only transition into
    # STATE_COMMIT_REQUEST_HOLDING_LOCKS state from STATE_RUNNING.
    STATE_RUNNING = 0

    # we were asked to hold locks on variables for committing to them.
    # we did so, we know that there was no intervening commit and we
    # forwarded on the commit request
    STATE_COMMIT_REQUEST_HOLDING_LOCKS = 1

    # we were asked to hold locks on variables for committing to them.
    # we discovered that we could not commit because state got changed
    # in the intervening time.  We backed out our changes and are no
    # longer holding locks on the variables.  We did not forward on
    # the commit request.
    STATE_COMMIT_REQUEST_NOT_HOLDING_LOCKS = 2

    # We received a backout request, backed our own changes out and
    # forwarded the request on.
    STATE_BACKOUT_REQUEST = 3

    
    def __init__(self,commit_manager,uuid,local_endpoint):
        '''
        @param {Endpoint object} local_endpoint --- The local endpoint
        the event is running on.
        '''
        _InvalidationListener.__init__(
            self,commit_manager,uuid)

        
        self.local_endpoint = local_endpoint
        
        # If we hit any sequences that have oncomplete handlers, we
        # keep track of each that we must fire.
        self.on_completes_to_fire = []

        # keyed by the uuids of all endpoints that we made endpoint
        # calls on. values are _SubscribedToElements.  We want
        # to avoid making additional endpoint calls after we've been
        # told to backout.  (This may happen if we receive an
        # invalidation notification and decide that we want to cancel
        # the event as it is firing.)
        self.subscribed_to = {}
        
        # if we have received a request to commit our changes, then
        # set to True.  This is used so that 
        self._state = _ActiveEvent.STATE_RUNNING

        # a shortcut (that isn't always accurate) to determine whether
        # or not we can commit.  If this value is true, then it means
        # we will not be able to commit.  If it is false, it means
        # that we *may* be able to commit our changes.
        self.is_invalidated = False

        # True if this event initiated a sequence between both sides,
        # or received a message sequence from its partner.  (If it,
        # did, or if the event has modified peered state, then we need
        # to involve the other side in the commit.)
        self.message_sent = False
        # When an active event sends a message to the partner
        # endpoint, it blocks until the response.  The way it blocks
        # is by calling get on an empty threadsafe queue.  There are
        # two ways that data get put into the queue.  The first is if
        # the partner endpoint completes its computation and replies.
        # In this case, _Endpoint updates the associated ActiveEvent
        # and puts a waldoCallResults._MessageFinishedCallResult
        # object into the queue.  When the listening endpoint receives
        # this result, it continues processing.  The other way is if
        # the event is backed out while we're waiting.  In that case,
        # the runtime puts a
        # waldoCallResults._BackoutBeforeReceiveMessageResult object
        # into the queue.
        #
        # We can be listening to more than one open threadsafe message
        # queue.  If endpoint A waits on its partner, and, while
        # waiting, its partner executes a series of endpoint calls so
        # that another method on A is invoked, and that method calls
        # its partner again, we could be waiting on 2 different
        # message queues, each held by the same active event.  To
        # determine which queue a message is a reply to, we read the
        # message's reply_to field.  If the reply_to field matches one
        # of the indices in the map below, we know the matching
        # waiting queue.  If it does not match and is None, that means
        # that it is the first message in a message sequence.  If it
        # does not match and is not None, there must be some error.
        # (@see
        # waldoExecutingEvent._ExecutingEventContext.to_reply_with_uuid.)
        self.message_listening_queues_map = {}

        
        # used to lock subscribed_to and message_sent.  Essentially,
        # if we receive a request to backout, then we need to: notify
        # all those that we are subscribed to to back out as well and
        # lock the subscribed_to list so that no others can subscribe
        # after.  (Same with message_sent.)
        self._mutex = threading.Lock()

    def _lock(self):
        self._mutex.acquire()
    def _unlock(self):
        self._mutex.release()

    ##### STATE CHANGERS AND ACCESSERS #####
        
    # @see comments at top of class about meaning of each state and
    # state transitions.
    def in_running_phase(self):
        return self._state == _ActiveEvent.STATE_RUNNING

    def in_commit_request_holding_locks_phase(self):
        return self._state == _ActiveEvent.STATE_COMMIT_REQUEST_HOLDING_LOCKS

    def in_commit_request_not_holding_locks_phase(self):
        return self._state == _ActiveEvent.STATE_COMMIT_REQUEST_NOT_HOLDING_LOCKS

    def in_request_backout_phase(self):
        return self._state == _ActiveEvent.STATE_BACKOUT_REQUEST

    def set_request_commit_holding_locks_phase(self):
        #### DEBUG
        if self._state != _ActiveEvent.STATE_RUNNING:
            util.logger_assert(
                'Cannot move into request commit phase if ' +
                'not in running sate.')
        #### END DEBUG
        self._state = _ActiveEvent.STATE_COMMIT_REQUEST_HOLDING_LOCKS

    def set_request_commit_not_holding_locks_phase(self):
        self._state = _ActiveEvent.STATE_COMMIT_REQUEST_NOT_HOLDING_LOCKS
        
    def set_request_backout_phase(self):
        self._state = _ActiveEvent.STATE_BACKOUT_REQUEST


        
    def must_check_partner(self):
        '''
        If we have modified peered state or if we received or sent a
        message to our partner, then:

          1) Before committing, we must check with our partner whether
             it can commit
             
          2) When backing out, we must tell our partner to back out.

        This method just tells us whether it is necessary to contact
        our partner.
          
        @returns {bool}
        '''
        return self.message_sent or self.peered_modified()

    def notify_invalidated(self,wld_obj):
        '''
        When another event commits and that commit conflicts with a
        read/write to a data element that this event makes, then we
        set is_invalidated to True so that when we try to commit this
        event, we can short-circuit attempt to hold resources.
        '''
        # FIXME: are reads and writes on bools atomic in Python?
        self.is_invalidated = True
        

    def issue_partner_sequence_block_call(
        self,ctx,func_name,result_queue):
        '''
        The local endpoint is requesting its partner to call some
        sequence block.
        
        For other params, @see issue_endpoint_object_call
        '''
        partner_call_requested = False
        self._lock()
        if self.in_running_phase():
            partner_call_requested = True
            self.message_sent = True

            # code is listening on threadsafe result_queue.  when we
            # receive a response, put it inside of the result queue.
            # put result queue in map so that can demultiplex messages
            # from partner to determine which result queue is finished
            reply_with_uuid = util.generate_uuid()
            self.message_listening_queues_map[
                reply_with_uuid] = result_queue

            # here, the local endpoint uses the connection object to
            # actually send the message.
            self.local_endpoint._send_partner_message_sequence_block_request(
                func_name, self.uuid, reply_with_uuid,
                ctx.to_reply_with_uuid, self,
                # sending sequence_local_store so that can determine
                # deltas in sequence local state made from this call.
                # do not need to add global store, because
                # self.local_endpoint already has a copy of it.
                ctx.sequence_local_store)
            
            
        self._unlock()
        return partner_call_requested

    
    def issue_endpoint_object_call(
        self,endpooint_calling,func_name,result_queue,*args):
        '''
        @param {Endpoint object} endpoint_calling --- The endpoint to
        execute the endpoint object call on.

        @param {String} func_name --- The name of the function to
        execute on the endpoint object.

        @param {Queue.Queue} result_queue --- Threadsafe queue that
        stores the result 
        
        @returns {bool} --- True if the endpoint object call could go
        through (ie, we were not already requested to backout the
        event).  False otherwise.

        Adds endpoint as an Endpoint object that we are subscribed to.
        (We need to keep track of all the endpoint objects that we are
        subscribed to [ie, have requested endpoint object calls on] so
        that we know who to forward our commit requests and backout
        requests to.)
        '''
        endpoint_call_requested = False
        self._lock()

        #### DEBUG
        if (self.in_commit_request_holding_locks_phase() or
            self.in_commit_request_not_holding_locks_phase()):
            # when we have been requested to commit, it means that all
            # events should have run to completion.  Therefore, it
            # would not make sense to receive an endpoint call when we
            # were in the request commit state (it would mean that all
            # events had not run to completion).
            util.logger_assert(
                'Should not be requesting to issue an endpoint ' +
                'object call when in request commit phase.')
        #### END DEBUG
        
        if self.in_running_phase():
            # we can only execute endpoint object calls if we are
            # currently running.  Note: we may issue an endpoint call
            # when we are in the backout phase (if, for instance, we
            # detected a conflict early and wanted to backout).  In
            # this case, do not make additional endpoint calls.  
            
            endpoint_call_requested = True

            # perform the actual endpoint function call.  note that this
            # does not block until it completes.  It just schedules the 
            endpoint_calling._endpoint_call(
                self.endpoint,self.uuid,func_name,result_queue,
                *args)

            # add the endpoint to subscribed to
            if endpoint_calling.uuid not in self.subscribed_to:
                self.subscribed_to[endpoint_calling.uuid] = _SubscribedToElement(
                    endpoint_calling,result_queue)
            else:
                self.subscribed_to[endpoint_calling.uuid].add_result_queue(
                    result_queue)
            
        self._unlock()
        return endpoint_call_requested

    def forward_backout_request_and_backout_self(self,skip_partner=False):
        '''
        @param {bool} skip_partner --- @see forward_commit_request

        When this is called, we want to disable all further additions
        to self.subscribed_to and self.message_sent.  (Ie, after we
        have requested to backout, we should not execute any further
        endpoint object calls or request partner to do any additional
        work for this event.)
        '''
        self._lock()
        
        if self.in_request_backout_phase():
            return
        
        let_go_of_commit_locks = False
        if self.in_commit_request_holding_locks_phase():
            let_go_of_commit_locks = True            

        self.backout_commit(let_go_of_commit_locks)
        
        self.set_request_backout_phase()
        for endpoint_uuid in self.subscribed_to.keys():
            subscribed_to_element = self.subscribed_to[endpoint_uuid]

            # first: notify the associated endpoint that it should
            # also backout.
            endpoint = subscribed_to_element.endpoint_object
            endpoint._request_backout(self.uuid)

            # second: we may still be waiting for a response to our
            # endpoint call.  put a sentinel in that tells us to stop
            # waiting and not to perform any more operations.
            res_queues_array = subscribed_to_element.result_queues
            for res_queue in res_queues_array:
                res_queue.put(
                    waldoCallResults._BackoutBeforeEndpointCallResult())


        for reply_with_uuid in self.message_listening_queues_map.keys():
            message_listening_queue.put(
                waldoCallResults._BackoutBeforeReceiveMessageResult())

        if ((not skip_partner) and self.must_check_partner()):
            self.local_endpoint._forward_backout_request_partner(self)

        self._unlock()

    def recv_partner_sequence_call_msg(self,msg):
        '''
        @param {_PartnerMessageRequestSequenceBlockAction} msg --- 
        '''
        reply_to_uuid = msg.reply_to_uuid
        reply_with_uuid = msg.reply_with_uuid
        name_of_block_to_exec_next = msg.name_of_block_requesting

        # update peered data based on data contents of message.
        # (Note: still must update sequence local data from deltas
        # below.)

        # FIXME: pretty sure that do not need to incorporate deltas within
        # lock 
        self.local_endpoint._global_var_store.incorporate_deltas(
            self,msg.global_var_store_deltas)

        
        self._lock()
        if reply_to_uuid == None:
            # means that the other side has generated a first message
            # create a new context to execute that message and do so
            # in a new thread.

            ### FIGURE OUT WHAT TO EXECUTE NEXT

            #### DEBUG
            if name_of_block_to_exec_next == None:
                util.logger_assert(
                    'Error in _ActiveEvent.  Should not receive the ' +
                    'beginning of a sequence message without some ' +
                    'instruction for what to do next.')
            #### END DEBUG
                    
            block_to_exec_internal_name = util.partner_endpoint_msg_call_func_name(
                name_of_block_to_exec_next)

            #### MAYBE DEBUG
            # ("maybe" because we also may want to throw a Waldo error
            # for this instead of just asserting out.)
            if not hasattr(
                self.local_endpoint,to_exec_next_internal_name):
                util.logger_assert(
                    'Error in _ActiveEvent.  Received a request to ' +
                    'perform an unknown sequence step.')
            #### END MAYBE DEBUG
                           
            to_exec = getattr(self.local_endpoint,to_exec_next_internal_name)

            ### SET UP CONTEXT FOR EXECUTING
            seq_local_var_store = waldoVariableStore._VariableStore()
            seq_lcoal_var_store.incorporate_deltas(
                self,msg.sequence_local_var_store_deltas)
            
            evt_ctx = waldoExecutingEvent._ExecutingEventContext(
                # already incorporated deltas for global_var_store
                # above.
                self.local_endpoint._global_var_store,
                seq_local_var_store)

            
            evt_ctx.set_to_reply_with(reply_with_field)

            ### ACTUALLY START EXECUTION CONTEXT THREAD
            # FIXME: may be faster if move this outside of the lock.
            # Probably not much faster though.
            exec_event = waldoExecutingEvent._ExecutingEvent(
                to_exec,act_event,evt_ctx)
            exec_event.start()
            
        else:
            #### DEBUG
            if reply_to_uuid not in self.message_listening_queues_map:
                util.logger_assert(
                    'Error: partner response message responding to ' +
                    'unknown _ActiveEvent message.')
            #### END DEBUG
                
            # unblock waiting listening queue.
            self.message_listening_queues_map[reply_to_uuid].put(
                waldoCallResults._SequenceMessageCallResult(
                    reply_with_field,to_exec_next_name_field,
                    # as soon as read from the listening message
                    # queue, populate sequence local data from context
                    # using sequence_local_var_store_deltas.
                    msg.sequence_local_var_store_deltas))

            # no need holding onto queue waiting on a message response.
            del self.message_listening_queues_map[reply_to_uuid]
            
        self._unlock()
        
        
    def forward_commit_request_and_try_holding_commit_on_myself(
        self,skip_partner=False):
        '''
        @param {bool} skip_partner --- If our partner issued the
        commit request to us, then we do not need to forward the
        request onto it, ie, skip_partner will be True.  Otherwise,
        check if we need to check with partner (must_check_partner).
        If do, then also request commit from partner.

        Go through all endpoints that this ActiveEvent made endpoint
        calls on while processing and tell them to try committing
        their changes.
        '''
        self._lock()
        if not self.in_running_phase():
            # there was a cycle in endpoint calls.  Ignore to avoid
            # loops.
            pass
        else:
            # FIXME: can get deadlock from multiple events trying to
            # commit at same time.
            if self.is_invalidated:
                self.set_request_commit_not_holding_locks_phase()                
                self.backout_commit(False)
            else:
                self.set_request_commit_holding_locks_phase()
                                
                if self.hold_can_commit():
                    # we know that the data that we are trying to
                    # commit has not been modified out from under us;
                    # go ahead and notify all others that they should
                    # also begin commit.

                    for endpoint_uuid in self.subscribed_to.keys():
                        endpoint = self.subscribed_to[endpoint_uuid]
                        endpoint._request_commit(self.uuid)

                    if ((not skip_partner) and self.must_check_partner()):
                        self.local_endpoint._forward_commit_request_partner(self)
                    else:
                        # instantly backout if another change happened
                        self.backout_commit(not self.is_invalidated)
                else:
                    # if we know that data have been modified before our
                    # commit, then we do not need to keep forwarding on the
                    # commit request.
                    self.backout_commit(True)
                    self.set_request_commit_not_holding_locks_phase()                
                    
        self._unlock()


# FIXME: are there any cases where we need to flush threadsafe queues
# when completing a commit?
            
        
class RootActiveEvent(_ActiveEvent):
    def __init__(self,commit_manager):
        ActiveEvent.__init__(self,commit_manager,None)

    def request_commit(self):
        '''
        Only the root event can begin the entire commit phase.

        @returns {bool} --- True if we were able to 
        '''
        # if we know that data have been modified before our commit,
        # then
        forward_commit_request_and_try_holding_commit_on_myself()
        
        if self.hold_can_commit():
            self.forward_commit_request()
            return True

        self.backout_commit(True)
        return False
                    
class PartnerActiveEvent(_ActiveEvent):
    def __init__(self,commit_manager,uuid):
        _ActiveEvent.__init__(self,commit_manager,uuid)

        # we received a message, which caused us to create this event.
        # That means that we must check with our partner before we can
        # commit/backout.
        self.message_sent = True
        
        
class EndpointCalledActiveEvent(_ActiveEvent):
    def __init__(
        self,commit_manager,uuid,local_endpoint,
        endpoint_making_call):
        
        _ActiveEvent.__init__(self,commit_manager,uuid,local_endpoint)
        self.subscriber = endpoint_making_call
        
