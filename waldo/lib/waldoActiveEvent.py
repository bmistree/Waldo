from invalidationListener import _InvalidationListener
import util
import threading, pickle, time
import waldoCallResults
import waldoExecutingEvent
from abc import abstractmethod
from util import Queue
import waldoDeadlockDetector



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


# FIXME: never actually running oncompletes
        
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

    # A very temporary state.  After completing, we remove the event
    # from the endpoint's active event map.  However, before removing,
    # we may have received another request to complete the commit (in
    # the case of having loops in the endpoint call graph).  In these
    # cases, we may have already read the active event from the
    # active_event_map.  To prevent a second commit in this case,
    # enter STATE_COMPLETED_COMMIT and check for being in
    # STATE_COMPLETED_COMMIT before completing the commit the second
    # time.  @see complete_commit_and_forward_complete_msg
    STATE_COMPLETED_COMMIT = 4

    # If our subscriber is our partner, then this is what
    # self.subscriber will be equal to.
    SUBSCRIBER_PARTNER_FLAG = -1
    
    
    def __init__(self,uuid,local_endpoint):
        '''
        @param {Endpoint object} local_endpoint --- The local endpoint
        the event is running on.

        @param {UUID or None} uuid --- If None, will generate a new
        one.
        '''
        _InvalidationListener.__init__(
            self,uuid)

        self.str_uuid = str(self.uuid)
        
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


        # keeps a list of functions that we should exec when we
        # complete.  Starts as None, because unlikely to use.  If we
        # do use, then turn it into a proper Queue.Queue().  
        # self.signal_queue = Queue.Queue()
        self.signal_queue = None

        
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
        self._mutex = threading.RLock()


        # When in first phase of commit, run through every object that
        # this event has touched, and try to hold a lock on it for
        # commit.  Hold this lock until told to backout or told to
        # complete commit.  To avoid deadlock, if there's contention
        # for a lock, that this active event is trying to acquire,
        # checks breakout.  If breakout is True, it means we've been
        # told to backout and should release all the locks on objects
        # that we have already acquired (object ids of these are
        # contained in self.holding_locks_on)
        self._breakout_mutex = threading.Lock()
        self.holding_locks_on = []
        self.breakout = False


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

    def in_state_completed_commit_phase(self):
        return self._state == _ActiveEvent.STATE_COMPLETED_COMMIT
    
    def set_request_commit_holding_locks_phase(self):
        #### DEBUG
        if not self.in_running_phase():
            util.logger_assert(
                'Cannot move into request commit phase if ' +
                'not in running sate.')
        #### END DEBUG
        self._state = _ActiveEvent.STATE_COMMIT_REQUEST_HOLDING_LOCKS

    def set_request_commit_not_holding_locks_phase(self):
        self._state = _ActiveEvent.STATE_COMMIT_REQUEST_NOT_HOLDING_LOCKS
        
    def set_request_backout_phase(self):
        self._state = _ActiveEvent.STATE_BACKOUT_REQUEST
        
    def set_state_completed_commit_phase(self):
        #### DEBUG
        # can only transition into completed commit phase from holding
        # locks phase.
        if not self.in_commit_request_holding_locks_phase():
            util.logger_assert(
                'Can only transition into completed commit phase ' +
                'from holding locks phase.')
        #### END DEBUG

        self._state = _ActiveEvent.STATE_COMPLETED_COMMIT

    def stop(self,skip_partner):
        '''
        If not in first or second phase of commit, then backout.
        '''
        self._lock()

        if not self.in_running_phase():
            # do not stop an event unless it is in the running phase.
            # (if it's midway through 2-phase commit, then if we stop
            # ourselves, we could screw up the entire commit on all
            # committers.
            self._unlock()
            return

        self.forward_backout_request_and_backout_self(
            skip_partner,
            # already_backed_out,
            False,
            # stop message
            True )
        
        self._unlock()

        
        
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
        return self.message_sent or self.peered_modified

    def notify_invalidated(self,wld_obj):
        '''
        When another event commits and that commit conflicts with a
        read/write to a data element that this event makes, then we
        set is_invalidated to True so that when we try to commit this
        event, we can short-circuit attempt to hold resources.
        '''
        # FIXME: are reads and writes on bools atomic in Python?
        self.is_invalidated = True
        self.set_breakout()
        
        
    def issue_partner_sequence_block_call(
        self,ctx,func_name,result_queue,first_msg):
        '''
        @param {String or None} func_name --- When func_name is None,
        then sending to the other side the message that we finished
        performing the requested block.  In this case, we do not need
        to add result_queue to waiting queues.

        @param {bool} first_msg --- True if this is the first message
        in a sequence that we're sending.  Necessary so that we can
        tell whether or not to force sending sequence local data.

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

            if result_queue != None:
                # may get None for result queue for the last message
                # sequence block requested.  It does not need to await
                # a response.
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
                ctx.sequence_local_store,
                first_msg)
            
        self._unlock()
        return partner_call_requested


    def generate_partner_modified_peered_response(self,msg):
        '''
        @param {PartnerNotifyOfPeeredModified.proto} msg

        Should attempt to update peered and sequence global data
        contained in message and reply with a partner modified peered
        response.
        '''
        self.local_endpoint._global_var_store.incorporate_deltas(
            self,msg.glob_deltas)

        # FIXME: should check here whether the delta changes have
        # already been invalidated.

        # FIXME: ensure that I really do not need locks around
        # incorporate deltas.
        
        self.local_endpoint._notify_partner_peered_before_return_response(
            self.uuid,msg.reply_with_uuid.data, False)


    def add_signal_call(self,signaler):
        if self.signal_queue == None:
            self.signal_queue = Queue.Queue()
        self.signal_queue.put(signaler)
    
    def receive_partner_modified_peered_response(self,resp_msg):
        '''
        @param {PartnerNotifyOfPeeredModifiedResponse.proto} resp_msg
        
        @see wait_if_modified_peered.  Unlocks queue being waited on
        in that function.
        '''
        self._lock()
        queue_waiting_on =  (
            self.message_listening_queues_map[resp_msg.reply_to_uuid.data])
        del self.message_listening_queues_map[resp_msg.reply_to_uuid.data]

        self._unlock()

        if resp_msg.invalidated:
            queue_waiting_on.put(
                waldoCallResults._BackoutBeforeReceiveMessageResult())
        else:
            queue_waiting_on.put(
                waldoCallResults._ModifiedUpdatedMessageResult())

        
    def wait_if_modified_peered(self):
        '''
        For certain topologies, can have a problem with updating
        peered data:

        root <------> root partner
        a    <------> a partner
        
        root and a are on the same host.  root_partner and a_partner
        are on the same host.  Could get into a situation in which do
        not update partner data.  Specifically, if root updates peered
        data and makes an endpoint call to a, which makes a message
        call to a partner, which makes an endpoint call to root
        partner, which modifies peered data, we need a mechanism for
        root and root partner to exchange the peered data updates.  If
        we wait until first phase of commit, then can get into trouble
        because root locks its variables before knowing it also needs
        to lock root partner's peered variables.  Which could lead to
        deadlock.

        To avoid this, after every endpoint call and root call, we
        send a message to our partners with all updated data.  We then
        wait until we recieve an ack of that message before returning
        back to the endpoint that called us.

        This function checks if we've modified any peered data.  If we
        have, then it sends that message to partner and blocks,
        waiting on a response from partner.

        FIXME: there are (hopefully) better ways to do this.

        FIXME: do I also need to update sequence local data (eg., for
        oncompletes?)
        
        '''

        must_send_update = False
        self._lock()
        
        if self.peered_modified:
            # FIXME: could probably be less conservative here.  For
            # instance, it's more important to know if peered data
            # have been modified after the last sequence message we
            # sent to partner.
            
            # send update message 
            must_send_update = True

        self._unlock()

        
        if must_send_update:
            # send update message and block until we receive a
            # response
            waiting_queue = Queue.Queue()
            reply_with_uuid = util.generate_uuid()
            self.message_listening_queues_map[
                reply_with_uuid] = waiting_queue

            self.local_endpoint._notify_partner_peered_before_return(
                self.uuid,reply_with_uuid,self)
            
            peered_mod_get = waiting_queue.get()
            if isinstance(
                peered_mod_get,waldoCallResults._BackoutBeforeReceiveMessageResult):
                # means that the other side has already invalidated
                # those changes to peered variables.  
                return False

        return True
            

    def complete_commit_and_forward_complete_msg(self,skip_partner=False):
        '''
        @param {bool} skip_partner --- True if we should not forward
        the complete request on to our partner (because our partner
        was the one who sent it to us in the first place).
        
        Removes self as an active event from local endpoint's active
        event map.  Completes the commit, and forwards the complete
        request on to others
        '''
        self._lock()
        if not self.in_state_completed_commit_phase():

            self.set_state_completed_commit_phase()

            ##### remove event from active event map
            self.local_endpoint._act_event_map.remove_event(self.uuid)

            ##### notify other endpoints

            #   notify endpoints we've made endpoint calls on
            for endpoint_uuid in self.subscribed_to.keys():
                subscribed_to_element = self.subscribed_to[endpoint_uuid]
                endpoint = subscribed_to_element.endpoint_object
                endpoint._receive_request_complete_commit(self.uuid)

            #   notify our partner endpoint
            if ((not skip_partner) and self.must_check_partner()):
                self.local_endpoint._forward_complete_commit_request_partner(self)
                
            ##### actually complete the commit
            self.complete_commit()
            
        self._unlock()

    
    def issue_endpoint_object_call(
        self,endpoint_calling,func_name,result_queue,*args):
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
            endpoint_calling._receive_endpoint_call(
                self.local_endpoint,self.uuid,func_name,result_queue,
                *args)

            # add the endpoint to subscribed to
            if endpoint_calling._uuid not in self.subscribed_to:
                self.subscribed_to[endpoint_calling._uuid] = _SubscribedToElement(
                    endpoint_calling,result_queue)
            else:
                self.subscribed_to[endpoint_calling._uuid].add_result_queue(
                    result_queue)

        self._unlock()
        return endpoint_call_requested

    def forward_backout_request_and_backout_self(
        self,skip_partner=False,already_backed_out=False,stop_request=False):
        '''
        @param {bool} skip_partner --- @see forward_commit_request

        @param {bool} already_backed_out --- Caller has already backed
        out the commit through commit manager, and is calling this
        function primarily to forward the backout message.  No need to
        do so again inside of function.

        @param {bool} stop_request --- True if this backout is a
        product of a stop request.  False otherwise.
        
        When this is called, we want to disable all further additions
        to self.subscribed_to and self.message_sent.  (Ie, after we
        have requested to backout, we should not execute any further
        endpoint object calls or request partner to do any additional
        work for this event.)
        '''
        self.set_breakout()
        self._lock()

        if self.in_request_backout_phase():
            self._unlock()
            return

        ##### remove event from active event map
        self.local_endpoint._act_event_map.remove_event_if_exists(
            self.uuid)
        
        if not already_backed_out:
            self.backout_commit()
        self.set_request_backout_phase()
        
        for endpoint_uuid in self.subscribed_to.keys():
            subscribed_to_element = self.subscribed_to[endpoint_uuid]

            # first: notify the associated endpoint that it should
            # also backout.
            endpoint = subscribed_to_element.endpoint_object
            endpoint._receive_request_backout(
                self.uuid,self.local_endpoint)
            
            # second: we may still be waiting for a response to our
            # endpoint call.  put a sentinel in that tells us to stop
            # waiting and not to perform any more operations.
            res_queues_array = subscribed_to_element.result_queues
            for res_queue in res_queues_array:
                if stop_request:
                    queue_feeder = waldoCallResults._StopAlreadyCalledEndpointCallResult()
                else:
                    queue_feeder = waldoCallResults._BackoutBeforeEndpointCallResult()

                res_queue.put(queue_feeder)

        for reply_with_uuid in self.message_listening_queues_map.keys():
            message_listening_queue = self.message_listening_queues_map[reply_with_uuid]
            if stop_request:
                queue_feeder =  waldoCallResults._StopRootCallResult()
            else:
                queue_feeder = waldoCallResults._BackoutBeforeReceiveMessageResult()
            message_listening_queue.put(queue_feeder)


        if ((not skip_partner) and self.must_check_partner()):
            self.local_endpoint._forward_backout_request_partner(self)

        self._unlock()


    def recv_partner_sequence_call_msg(self,msg):
        '''
        @param {PartnerMessageRequestSequenceBlock.proto} msg --- 
        '''
        # can be None... if it is means that the other side wants us
        # to decide what to do next (eg, the other side performed its
        # last message sequence action)
        name_of_block_to_exec_next = None
        if msg.HasField('name_of_block_requesting'):
            name_of_block_to_exec_next = msg.name_of_block_requesting
        
        # update peered data based on data contents of message.
        # (Note: still must update sequence local data from deltas
        # below.)

        # FIXME: pretty sure that do not need to incorporate deltas within
        # lock, but should check
        self.local_endpoint._global_var_store.incorporate_deltas(
            self,msg.peered_var_store_deltas)

        
        exec_event = None

        self._lock()
        if not msg.HasField('reply_to_uuid'):
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
                self.local_endpoint,block_to_exec_internal_name):
                util.logger_assert(
                    'Error in _ActiveEvent.  Received a request to ' +
                    'perform an unknown sequence step.')
            #### END MAYBE DEBUG

            to_exec = getattr(self.local_endpoint,block_to_exec_internal_name)

            ### SET UP CONTEXT FOR EXECUTING
            # FIXME: re-arrange code to avoid this import
            import waldoVariableStore
            seq_local_var_store = waldoVariableStore._VariableStore(
                self.local_endpoint._host_uuid)

            # FIXME: eventually, want to remove pickle-ing here
            seq_local_var_store.incorporate_deltas(
                self,msg.sequence_local_var_store_deltas)
            
            evt_ctx = waldoExecutingEvent._ExecutingEventContext(
                # already incorporated deltas for global_var_store
                # above.
                self.local_endpoint._global_var_store,
                seq_local_var_store)

            evt_ctx.set_to_reply_with(msg.reply_with_uuid.data)
            
            # used to actually start execution of context thread at end
            # of loop.  must start event outside of locks.  That way,
            # if the exec event leads to and endpoint call, etc., we
            # don't block waiting on its return.
            exec_event = waldoExecutingEvent._ExecutingEvent(
                to_exec,self,evt_ctx,
                None # using None here means that we do not need to
                     # bother with waiting for modified peered-s to
                     # update.
                )

        else:
            #### DEBUG
            if msg.reply_to_uuid.data not in self.message_listening_queues_map:
                util.logger_assert(
                    'Error: partner response message responding to ' +
                    'unknown _ActiveEvent message.')
            #### END DEBUG
                
            # unblock waiting listening queue.
            self.message_listening_queues_map[msg.reply_to_uuid.data].put(
                waldoCallResults._SequenceMessageCallResult(
                    msg.reply_with_uuid.data,
                    name_of_block_to_exec_next,
                    # as soon as read from the listening message
                    # queue, populate sequence local data from context
                    # using sequence_local_var_store_deltas.

                    # FIXME: eventaully, want to move away from
                    # pickle-ing here.
                    msg.sequence_local_var_store_deltas))
            
            # no need holding onto queue waiting on a message response.
            del self.message_listening_queues_map[msg.reply_to_uuid.data]

        self._unlock()

        if exec_event != None:
            ### ACTUALLY START EXECUTION CONTEXT THREAD
            exec_event.run()


        
    def notify_removed_subscriber(
        self,removed_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber, except for removals instead
        of additions.
        '''
        util.logger_assert(
            'notify_removed_subscriber is purely virtual in ' +
            'base class _ActiveEvent.')

    def notify_additional_subscriber(
        self,additional_subscriber_uuid,host_uuid,resource_uuid):
        '''
        When we are asked to perform the first phase of a commit, we
        subscribe for events simultaneously trying to commit to the
        same resources. This is to detect and avoid deadlocks: if two
        events are both listening for subscribers on different hosts
        for the same piece of data, then there's a chance for
        deadlock, and we must back one of the events out.  (In this
        case, we backout the event that has the lower uuid.)

        To determine if there is the potential for deadlock, each time
        we try to acquire a lock for the first phase of a variable's
        commit, subscribe for others doing the same, and forward these
        subscribers ids and the resource id back to the root.  The
        root can detect and backout commits as described in the
        previous paragraph.
        '''
        util.logger_assert(
            'notify_additional_subscriber is purely virtual in ' +
            'base class _ActiveEvent.')
        
    def notify_existing_subscribers(
        self,list_of_existing_subscriber_uuids,host_uuid,resource_uuid):
        '''
        @see notify_existing_subscriber
        
        @param {array} list_of_existing_subscriber_uuids --- Each
        element is a uuid of an invalidation listener that is trying
        to hold a commit lock on the Waldo reference with uuid
        resource_uuid.
        '''
        
        # FIXME: probably, eventually, want to create separate
        # messages for each
        for existing_subscriber_uuid in list_of_existing_subscriber_uuids:
            self.notify_additional_subscriber(
                existing_subscriber_uuid,host_uuid,resource_uuid)
        

    def forward_commit_request_and_try_holding_commit_on_myself(
        self,skip_partner=False):
        '''
        Note: gets extended in each base class.
        
        @param {bool} skip_partner --- If our partner issued the
        commit request to us, then we do not need to forward the
        request onto it, ie, skip_partner will be True.  Otherwise,
        check if we need to check with partner (must_check_partner).
        If do, then also request commit from partner.

        Go through all endpoints that this ActiveEvent made endpoint
        calls on while processing and tell them to try committing
        their changes.

        @returns {bool} --- False if know that the commit cannot
        proceed (ie, has a conflict with something that has already
        committed).  True otherwise.  (Note: True does not guarantee
        that we'll be able to commit.  A dependent endpoint may not be
        able to commit its data.  Or, we may have already been told to
        commit.  It just means that the commit *may* still be proceeding.)
        '''
        self._lock()

        if not self.in_running_phase():
            # there was a cycle in endpoint calls.  Ignore to avoid
            # loops.
            self._unlock()
            return True, True, None

        who_forwarded_to = None
        cannot_commit = False
        if self.is_invalidated:
            self.set_request_commit_not_holding_locks_phase()
            cannot_commit = True
            # FIXME: forward the backout message on to those that
            # we are subscribed to?  If we do, then we can also
            # remove the active event here....
            self.backout_commit()
        else:
            self.set_request_commit_holding_locks_phase()
            if self.hold_can_commit():
                # we know that the data that we are trying to
                # commit has not been modified out from under us;
                # go ahead and notify all others that they should
                # also begin commit.

                # when we can commit, we reply back to our subscriber
                # with a set of all those endpoint uuids that we
                # performed endpoint calls on (and therefore that we
                # will forward our first phase commit request on to).
                # When the root endpoint has a record of all of these
                # endpoints' having responded affirmatively to the
                # first phase commit request, it begins trying to
                # complete the commit (second phase of commit).  If
                # any of the endpoints respond negatively, the root
                # backs out the full first phase and restarts.
                who_forwarded_to = [] # a set of uuids
                for endpoint_uuid in self.subscribed_to.keys():
                    subscribed_to_element = self.subscribed_to[endpoint_uuid]
                    endpoint = subscribed_to_element.endpoint_object
                    
                    who_forwarded_to.append(endpoint_uuid)
                    endpoint._receive_request_commit(
                        self.uuid,self.local_endpoint)

                if ((not skip_partner) and self.must_check_partner()):
                    self.local_endpoint._forward_commit_request_partner(self)
                    who_forwarded_to.append(self.local_endpoint._partner_uuid)

            else:
                # if we know that data have been modified before our
                # commit, then we do not need to keep forwarding on the
                # commit request.
                
                # FIXME: forward the backout message on to those that
                # we are subscribed to?  If we do, then we can also
                # remove the active event here....
                self.set_request_commit_not_holding_locks_phase()                
                self.backout_commit()
                cannot_commit = True


        # FIXME: unclear if need to hold this lock up until here.  May
        # be able to let go of it earlier.  Reason through whether it
        # is incorrect for root condition to manage
        # waiting_on_commit_map outside of lock.
        self._unlock()

        return (not cannot_commit), False, who_forwarded_to


    @abstractmethod
    def receive_successful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid,
        children_event_endpoint_uuids):
        '''
        Using two phase commit.  All committers must report to root
        that they were successful in first phase of commit before root
        can tell everyone to complete the commit (second phase).

        In this case, received a message from endpoint that this
        active event is subscribed to that endpoint with uuid
        msg_originator_endpoint_uuid was able to commit.  If we have
        not been told to backout, then forward this message on to the
        root.  (Otherwise, no point in sending it further and doing
        wasted work: can just drop it.)

        Note: this gets overridden in each subclass --- in
        RootActiveEvent, check whether or not to transition to
        complete commit; in other two, determines how to forward
        message (via network or endpoint).
        '''
        util.logger_assert(
            'Call to purely virtual ' +
            'receive_successful_first_phase_commit_msg in '  +
            '_ActiveEvent.')


    def receive_unsuccessful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid):        
        '''
        @see receive_successful_first_phase_commit_msg
        
        Should rollback event if we were completing it and forwards message
        towards root.
        '''
        util.logger_assert(
            'Call to purely virtual ' +
            'receive_unsuccessful_first_phase_commit_msg in ' +
            '_ActiveEvent.')


    def hold_can_commit(self):
        '''
        ASSUMES ALREADY HOLDING LOCK

        Returns True if can commit.  False if cannot commit, which can
        happen for two reasons:
        
            1) The piece of data that we are trying to update has
               already committed a conflicting event
               
            2) We received a notice to backout the event (eg., due to
               deadlock or another node's trying to commit dirty
               state)

        Challenge is to avoid deadlock when acquiring the locks of all
        objects that we have touched.

        We can guarantee that will not get deadlock if all invalidation
        listeners try to acquire locks on the resources that they have
        modified in order of their uuids.  For example, consider two
        invalidation listeners, A and B.

        A's read/write set is {beta, alpha, gamma}
        B's read/write set is {gamma, beta, alpha}

        If, before acquiring locks, we order each's read/write set, and
        attempt to acquire locks in sorted order, we can guarantee no
        deadlock.

        A acquires in order alpha, beta, gamma
        B acquires in order alpha, beta, gamma
        '''
        sorted_touched_obj_ids = (
            sorted(list(self.priority_touched_objs.keys() ) + sorted(list(self.objs_touched.keys()))))
        self.holding_locks_on = []
        for obj_id in sorted_touched_obj_ids:

            touched_obj = self.objs_touched.get(obj_id,None)
            if touched_obj is None:
                touched_obj = self.priority_touched_objs[obj_id]

            obj_can_commit = None

            while obj_can_commit == None:
                obj_can_commit = touched_obj.check_commit_hold_lock(self,False)

                if obj_can_commit == False:
                    # could not perform first phase of commit because
                    # another event already has committed a conflict
                    self.holding_locks_on.append(obj_id)
                    return False
                elif obj_can_commit == True:
                    # could perform first phase of commit
                    self.holding_locks_on.append(obj_id)
                else:
                    # obj_can_commit == None
                    # we were not able to acquire the lock for this
                    # object.  backoff for a bit.  Check that while we
                    # were backed off, we were not told that we needed
                    # to back out.

                    # FIXME: make this time settable, or use some form
                    # of backoff for checking.
                    time.sleep(
                        util.TIME_TO_SLEEP_BEFORE_ATTEMPT_TO_ACQUIRE_VAR_FIRST_PHASE_LOCK)
                    if self.check_breakout():
                        # while we tried to acquire the lock, someone
                        # else told us to backout.  do so.
                        return False

        return True

    def backout_commit(self):
        '''
        CALLED FROM WITHIN LOCK
        '''
        self.set_breakout()
        for obj_id in self.holding_locks_on:
            to_backout_obj = self.objs_touched.get(obj_id,None)
            if to_backout_obj is None:
                to_backout_obj = self.priority_touched_objs[obj_id]
            to_backout_obj.backout(self)
        self.holding_locks_on = []

        
    def complete_commit(self):
        '''
        Should only be called if hold_can_commit returned True.  Runs
        through all touched objects and completes their commits.
        '''
        for touched_obj in self.priority_touched_objs.values():
            touched_obj.complete_commit(self)
        
        for touched_obj in self.objs_touched.values():
            touched_obj.complete_commit(self)

        if self.signal_queue != None:
            while True:
                try:
                    signaler = self.signal_queue.get_nowait()
                    self.local_endpoint._signal_queue.put(signaler)
                except Queue.Empty:
                    break

                
    def set_breakout(self):
        self._breakout_mutex.acquire()
        self.breakout = True
        self._breakout_mutex.release()
        
    def check_breakout(self):
        self._breakout_mutex.acquire()
        to_return = self.breakout
        self._breakout_mutex.release()
        return to_return
        
# FIXME: are there any cases where we need to flush threadsafe queues
# when completing a commit?
            
        
class RootActiveEvent(_ActiveEvent):
    def __init__(self,local_endpoint):

        _ActiveEvent.__init__(self,None,local_endpoint)
        self.subscriber = None

        # from endpoint uuid to bool.  bool value is True if still
        # waiting on the commit, false otherwise.  After we initiate
        # first phase of commit and all values in this map are False,
        # can move on to second phase of commit.
        self.waiting_on_commit_map = {}

        self.deadlock_detector = waldoDeadlockDetector._DeadlockDetector(self)
        
        # The code that initiates a RootActiveEvent should block
        # until the RootActiveEvent completes.  It does so by
        # listening on a threadsafe queue for a result.  If the result
        # is a backout result, then reschedules the event.
        self.event_complete_queue = Queue.Queue()
        
        
        # When an active event is asked to perform the first phase of
        # the commit, it:
        #   1) Tries to commit itself
        #   2) If that is successful, it tells all the endpoints that
        #      it is subscribed to (potentially including its partner)
        #      to try committing as well.
        #   3) To its subscriber, it sends back a list of uuids for
        #      all the endpoints that it forwarded the first phase
        #      message on to.
        #   4) For any non-root active event that receives another
        #      endpoint's message containing the endpoint uuids from
        #      #3, forward on to subscriber.
        #   5) The root keeps track of everyone that has sent in that
        #      their first phases were successful and the outstanding
        #      endpoints that they brought into the global event.
        #      When all have responded affirmatively, can complete the
        #      commit.

    def request_commit(self):
        '''
        Only the root event can begin the entire commit phase.
        '''
        # if we know that data have been modified before our commit,
        # then

        # FIXME: there may be instances/topologies where do not have
        # to issue this call.
        self.wait_if_modified_peered()
        self.forward_commit_request_and_try_holding_commit_on_myself()

    def receive_unsuccessful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid):
        '''
        @see receive_unsuccessful_first_phase_commit_msg in base class
        '''
        self.set_breakout()
        to_broadcast_backout = False
        self._lock()

        if (self.in_commit_request_holding_locks_phase() or
            self.in_commit_request_not_holding_locks_phase()):
            # okay to make calls because of re-entrantness
            self.forward_backout_request_and_backout_self()
            
        self._unlock()

    def forward_backout_request_and_backout_self(
        self,skip_partner=False,already_backed_out=False,stop_request=False):
        
        # whenever we backout, we must also reschedule
        super(RootActiveEvent,self).forward_backout_request_and_backout_self(
            skip_partner,already_backed_out)

        if stop_request:
            # notify queue that we have stopped and are not processing
            # any more
            self.event_complete_queue.put(
                waldoCallResults._StopRootCallResult())
        else:
            self.reschedule()
        
        
    def receive_successful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid,
        children_event_endpoint_uuids):
        '''
        @see base class' receive_successful_first_phase_commit_msg
        '''
        self._lock()
        # ordering of additions/changes to self.waiting_on_commit_map
        # is important.  if flipped order, root could think that it
        # was not waiting on any additional endpoints to confirm first
        # phase commit completed and begin second phase of commit
        # (even though children_event_endpoint contains uuids of more
        # events that may not have completed first phase of commit.)
        self.add_waiting_on_first_phase(children_event_endpoint_uuids)
        self.add_received_first_phase(msg_originator_endpoint_uuid)
        self._unlock()

    def forward_commit_request_and_try_holding_commit_on_myself(
        self,skip_partner=False):
        self._lock()

        can_commit, early_abort,who_forwarded_to = super(
            RootActiveEvent,self).forward_commit_request_and_try_holding_commit_on_myself(
            skip_partner)
    
        if not early_abort:

            if can_commit:
                # We are a _RootActiveEvent.  The _RootActiveEvent can
                # get here from its first call to begin committing.
                # Load the waiting_on_commit_map so that know when to
                # proceed to second phase of commit.

                # handles case of loops in the endpoint call graph.
                self.add_waiting_on_first_phase(who_forwarded_to)
                self.add_received_first_phase(
                    self.local_endpoint._uuid)
            else:
                # active event was invalidated
                # this _ActiveEvent is the RootActiveEvent.  Forward
                # to all to backout and reschedule
                self.forward_backout_request_and_backout_self(
                    False,True)
        self._unlock()
        return can_commit
        
        
    def add_waiting_on_first_phase(self,endpoint_uuid_array):
        '''
        ASSUMES ALREADY HOLDING LOCK
        
        @param {list} endpoint_uuid_array --- Each element is a uuid
        for an endpoint.  We cannot transition into second phase of
        two phase commit until every uuid element in the
        endpoint_uuid_array has responded that it is clear to commit.
        
        Note: because of loops in the endpoint call graph, we may
        receive endpoint uuids.  If the uuid already exists in the
        map, we *should not* overwrite its value.  If we do, we might
        lose track of an endpoint that has already responded that it
        was clear to commit in its first phase.
        '''
        
        for uuid in endpoint_uuid_array:
            self.waiting_on_commit_map.setdefault(uuid,True)
            

    def add_received_first_phase(self,endpoint_uuid):
        '''
        ASSUMES ALREADY HOLDING LOCK

        Tells us that endpoint with uuid endpoint_uuid has
        completed the first phase of the commit with no conflicts.

        waiting_on_commit_map keeps track of endpoints that have
        and have not gone through the first phase of the commit.

        (An endpoint has gone through the first phase of the
        commit successfully if its uuid is a key in the map to
        False.  The root does not know if an endpoint has
        completed its first phase of the commit if the key in the
        map points to true.)

        As endpoints we are subscribed to attempt the first phase
        of their commits, they forward back whether their attempt
        to commit would conflict with existing commits or whether
        they do not.  In the case that they do not, the endpoints
        also forward back a list of additional endpoint uuids that
        we must also wait for before completing commit.

        Note: if at the end of this function all values are false,
        we can begin completing the commit.
        '''
        if not self.in_commit_request_holding_locks_phase():
            # may get duplicates for certain endpoints (eg, if there's
            # a loop in the endpoint graph).  Duplicates might lead to
            # getting additional first_phase_complete messages.  We do
            # not need to process these and can return.
            return
        
        self.waiting_on_commit_map[endpoint_uuid] = False

        can_transition_to_complete_commit = True
        for waiting_value in self.waiting_on_commit_map.values():
            if waiting_value:
                can_transition_to_complete_commit = False
                break

        if can_transition_to_complete_commit:
            self._request_complete_commit()

    def reschedule(self):
        '''
        When root backs out, we must attempt to reschedule the event.
        This function writes into 
        '''
        # FIXME: may eventually want to put some additional metadata
        # in, for instance, the uuid of the event so that may increase
        # event priority for next go around.
        self.event_complete_queue.put(
            waldoCallResults._RescheduleRootCallResult())

            
    def _request_complete_commit(self):
        '''
        Should automatically happen.  Completes its commit and
        forwards a message to all others to complete their commits.

        Can be called while holding locks or while not holding locks
        '''
        self.complete_commit_and_forward_complete_msg()

        self.event_complete_queue.put(
            waldoCallResults._CompleteRootCallResult())
        
    def notify_additional_subscriber(
        self,additional_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber in _ActiveEvent for a general
        description.

        This class is the root of the event, it must check that these
        conflicts will not cause a deadlock.
        '''
        potential_deadlock = False
        self._lock()
        if (self.in_request_backout_phase() or
            self.in_state_completed_commit_phase()):
            # do not do anything.  there cannot be deadlock because
            # we're about to release our locks anyways.
            pass
        else:
            potential_deadlock = self.deadlock_detector.add_subscriber(
                additional_subscriber_uuid,host_uuid,resource_uuid)
        self._unlock()

        if potential_deadlock and (self.uuid < additional_subscriber_uuid):
            # backout changes if this event's uuid is less than
            # the additional subscriber's uuid.
            self.forward_backout_request_and_backout_self()

    def notify_removed_subscriber(
        self,removed_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber, except for removals instead of
        additions.
        '''
        self.deadlock_detector.remove_subscriber(
            removed_subscriber_uuid,host_uuid,resource_uuid)
                        
        
class PartnerActiveEvent(_ActiveEvent):
    def __init__(self,uuid,local_endpoint):
        _ActiveEvent.__init__(self,uuid,local_endpoint)
        
        # we received a message, which caused us to create this event.
        # That means that we must check with our partner before we can
        # commit/backout.
        self.message_sent = True
        self.subscriber = _ActiveEvent.SUBSCRIBER_PARTNER_FLAG


    def notify_additional_subscriber(
        self,additional_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber in _ActiveEvent for a general
        description.

        This event was initiated by the endpoint's partner.
        Therefore, forward the resource subscriber on to partner.
        '''
        
        # FIXME: should use separate locking for state variables.
        # This actually needs a lock around it (writes and reads are
        # not atomic to the value)...but cannot use self._lock,
        # becuase could get into this function by calling
        # hold_can_commit, which holds the active event's global lock.
        if not self.in_commit_request_holding_locks_phase():
            # do not need to forward the notification on: we aren't
            # actually holding the lock any more (could mean that we
            # had a conflict and therefore backed out holding the lock).
            return

        self.local_endpoint._notify_partner_of_additional_subscriber(
            self.uuid,additional_subscriber_uuid,host_uuid,resource_uuid)
        
    def notify_removed_subscriber(
        self,removed_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber, except for removals instead of
        additions.
        '''
        if not self.in_commit_request_holding_locks_phase():
            return

        self.local_endpoint._notify_partner_removed_subscriber(
            self.uuid,removed_subscriber_uuid,host_uuid,resource_uuid)

    def receive_successful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid,
        children_event_endpoint_uuids):
        '''
        @see base class' receive_successful_first_phase_commit_msg
        '''
        
        self._lock()
        if self.in_commit_request_holding_locks_phase():
            # forward message towards root
            self.local_endpoint._forward_first_phase_commit_successful(
                self.uuid,msg_originator_endpoint_uuid,
                children_event_endpoint_uuids)
        self._unlock()


    # FIXME: seems to be quite a bit of code duplication between
    # EndpointCalledActiveEvent and PartnerCalledActiveEvent.  (For
    # instance, this method and
    # receive_usccessful_first_phase_commit_msg.)  Think about a way
    # to reduce this.
    def receive_unsuccessful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid):
        '''
        @see receive_unsuccessful_first_phase_commit_msg in base class
        '''

        self.set_breakout()
        to_forward = False
        self._lock()
        if self.in_commit_request_holding_locks_phase():
            to_forward = True
            self.backout_commit()
            self.set_request_backout_phase()

        if self.in_commit_request_not_holding_locks_phase():
            to_forward = True
            self.set_request_backout_phase()
            
        self._unlock()

        if to_forward:
            self.local_endpoint._forward_first_phase_commit_unsuccessful(
                event_uuid,msg_originator_endpoint_uuid)


    def forward_commit_request_and_try_holding_commit_on_myself(
        self,skip_partner=False):
        '''
        @see _ActiveEvent.forward_commit_rquest_and_try_holding_commit_on_myself
        '''
        can_commit, early_abort,who_forwarded_to = super(
            PartnerActiveEvent,self).forward_commit_request_and_try_holding_commit_on_myself(
            skip_partner)
    
        if not early_abort:
            if can_commit:
                # Tell partner (our subscriber) that we were able to
                # commit, and the root should wait for messages from
                # the endpoint uuids in who_forwarded_to before
                # transitioning to second state of commit.                
                self.local_endpoint._forward_first_phase_commit_successful(
                    self.uuid,self.local_endpoint._uuid,who_forwarded_to)
            else:
                # Tell partner to back out (and forward that back out
                # to root)                
                self.local_endpoint._forward_first_phase_commit_unsuccessful(
                    self.uuid,self.local_endpoint._uuid)

        return can_commit
        


    
class EndpointCalledActiveEvent(_ActiveEvent):
    def __init__(
        self,uuid,local_endpoint,
        endpoint_making_call,result_queue):
        
        _ActiveEvent.__init__(self,uuid,local_endpoint)
        self.subscriber = endpoint_making_call

    def receive_successful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid,
        children_event_endpoint_uuids):
        '''
        @see base class' receive_successful_first_phase_commit_msg
        '''
        
        self._lock()
        if self.in_commit_request_holding_locks_phase():
            # forward message towards root
            self.subscriber._receive_first_phase_commit_successful(
                self.uuid,msg_originator_endpoint_uuid,
                children_event_endpoint_uuids)
        self._unlock()

        
    def notify_additional_subscriber(
        self,additional_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber in _ActiveEvent for a general
        description.

        This event was initiated by an endpoint caller on the same
        host as this event is currently on.  Forward, the subscription
        on to it.
        '''
        # FIXME: should use separate locking for state variables.
        # This actually needs a lock around it (writes and reads are
        # not atomic to the value)...but cannot use self._lock,
        # becuase could get into this function by calling
        # hold_can_commit, which holds the active event's global lock.
        if not self.in_commit_request_holding_locks_phase():
            # do not need to forward the notification on: we aren't
            # actually holding the lock any more (could mean that we
            # had a conflict and therefore backed out holding the lock).
            return

        self.subscriber._receive_additional_subscriber(
            self.uuid,additional_subscriber_uuid,host_uuid,resource_uuid)


    def notify_removed_subscriber(
        self,removed_subscriber_uuid,host_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber, except for removals instead of
        additions.
        '''
        if not self.in_commit_request_holding_locks_phase():
            return

        self.subscriber._receive_removed_subscriber(
            self.uuid,removed_subscriber_uuid,host_uuid,resource_uuid)


    def receive_unsuccessful_first_phase_commit_msg(
        self,event_uuid,msg_originator_endpoint_uuid):
        '''
        @see receive_unsuccessful_first_phase_commit_msg in base class
        '''
        self.set_breakout()
        
        to_forward = False
        self._lock()
        if self.in_commit_request_holding_locks_phase():
            to_forward = True
            self.backout_commit()
            self.set_request_backout_phase()

        if self.in_commit_request_not_holding_locks_phase():
            to_forward = True
            self.set_request_backout_phase()
            
        self._unlock()

        if to_forward:
            self.subscriber._receive_first_phase_commit_unsuccessful(
                event_uuid,msg_originator_endpoint_uuid)

    def forward_commit_request_and_try_holding_commit_on_myself(
        self,skip_partner=False):
        '''
        @see _ActiveEvent.forward_commit_rquest_and_try_holding_commit_on_myself
        '''
        can_commit, early_abort,who_forwarded_to = super(
            EndpointCalledActiveEvent,self).forward_commit_request_and_try_holding_commit_on_myself(
            skip_partner)
    
        if not early_abort:
            if can_commit:
                # this was an EndpointCalledActiveEvent, which means
                # that we can just call the subscriber directly to
                # receive the successful message.
                self.subscriber._receive_first_phase_commit_successful(
                    self.uuid,self.local_endpoint._uuid,who_forwarded_to)
            else:
                # this was an EndpointCalledActiveEvent, which means
                # that we can call subscriber directly to forward the
                # message.                
                self.subscriber._receive_first_phase_commit_unsuccessful(
                    self.uuid,self.local_endpoint._uuid)
