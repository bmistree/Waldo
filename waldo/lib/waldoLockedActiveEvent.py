import threading
import util
from waldoEventSubscribedTo import EventSubscribedTo
from waldoCallResults import _BackoutBeforeEndpointCallResult
from waldoCallResults import _SequenceMessageCallResult
from waldoCallResults import _BackoutBeforeReceiveMessageResult

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
        
        # FIXME: maybe can unmake this reentrant, but get deadlock
        # from serializing data when need to add to touched objects.
        self.mutex = threading.RLock()
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

    def begin_first_phase_commit(self,from_partner=False):
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

        self.event_map.remove_event(self.uuid)
        
        # FIXME: which should happen first, notifying others or
        # releasing locks locally?
        
        # notify other endpoints to also complete their commits
        self.event_parent.second_phase_transition_success(
            self.other_endpoints_contacted,self.partner_contacted)    

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

        @returns {bool} --- True if did not get backed out in the
        middle.
        '''

        # FIXME: actually fill this method in
        return True
        
        
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
        '''
        To provide blocking, whenever issue an endpoint call or
        partner call, thread of execution blocks, waiting on a read
        into a threadsafe queue.  When we rollback, we must put a
        sentinel into the threadsafe queue indicating that the event
        has been rolled back and to not proceed further.
        '''

        for msg_queue_to_unblock in self.message_listening_queues_map.values():
            msg_queue_to_unblock.put(_BackoutBeforeReceiveMessageResult())
        
        for subscribed_to_element in self.other_endpoints_contacted.values():
            for res_queue in subscribed_to_element.result_queues:
                res_queue.put(_BackoutBeforeEndpointCallResult())
                    
        
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

    def issue_partner_sequence_block_call(
        self,ctx,func_name,threadsafe_unblock_queue, first_msg):
        '''
        @param {String or None} func_name --- When func_name is None,
        then sending to the other side the message that we finished
        performing the requested block.  In this case, we do not need
        to add result_queue to waiting queues.

        @param {bool} first_msg --- True if this is the first message
        in a sequence that we're sending.  Necessary so that we can
        tell whether or not to force sending sequence local data.

        @param {Queue or None} threadsafe_unblock_queue --- None if
        this was the last message sent in a sequence and we're not
        waiting on a reply.
        
        The local endpoint is requesting its partner to call some
        sequence block.
        '''
        partner_call_requested = False
        self._lock()

        if self.state == self.STATE_RUNNING:
            partner_call_requested = True
            self.partner_contacted = True

            # code is listening on threadsafe result_queue.  when we
            # receive a response, put it inside of the result queue.
            # put result queue in map so that can demultiplex messages
            # from partner to determine which result queue is finished
            reply_with_uuid = util.generate_uuid()

            if threadsafe_unblock_queue != None:
                # may get None for result queue for the last message
                # sequence block requested.  It does not need to await
                # a response.
                self.message_listening_queues_map[
                    reply_with_uuid] = threadsafe_unblock_queue
                
            # here, the local endpoint uses the connection object to
            # actually send the message.
            self.event_parent.local_endpoint._send_partner_message_sequence_block_request(
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
        if ((self.state == LockedActiveEvent.STATE_FIRST_PHASE_COMMIT) or
            (self.state == LockedActiveEvent.STATE_SECOND_PHASE_COMMITTED)):
            # when we have been requested to commit, it means that all
            # events should have run to completion.  Therefore, it
            # would not make sense to receive an endpoint call when we
            # were in the request commit state (it would mean that all
            # events had not run to completion).
            util.logger_assert(
                'Should not be requesting to issue an endpoint ' +
                'object call when in request commit phase.')
        #### END DEBUG

        if self.state == LockedActiveEvent.STATE_RUNNING:
            # we can only execute endpoint object calls if we are
            # currently running.  Note: we may issue an endpoint call
            # when we are in the backout phase (if, for instance, we
            # detected a conflict early and wanted to backout).  In
            # this case, do not make additional endpoint calls.  
            
            endpoint_call_requested = True

            # perform the actual endpoint function call.  note that this
            # does not block until it completes.  It just schedules the 
            endpoint_calling._receive_endpoint_call(
                self.event_parent.local_endpoint,self.uuid,func_name,result_queue,
                *args)


            # add the endpoint to subscribed to
            if endpoint_calling._uuid not in self.other_endpoints_contacted:
                self.other_endpoints_contacted[endpoint_calling._uuid] = EventSubscribedTo(
                    endpoint_calling,result_queue)
            else:
                self.other_endpoints_cnotacted[endpoint_calling._uuid].add_result_queue(
                    result_queue)

        self._unlock()
        return endpoint_call_requested
        

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

        '''
        self.event_parent.receive_successful_first_phase_commit_msg(
            event_uuid,msg_originator_endpoint_uuid,
            children_event_endpoint_uuids)

    def complete_commit_and_forward_complete_msg(
        self,request_from_partner):
        '''
        @param {bool} request_from_partner --- @see
        waldoEndpointServiceThread
        complete_commit_and_forward_complete_msg.
        '''
        self.second_phase_commit()

        
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
        # FIXME: may be needlessly forwarding backouts to partners and
        # back to the endpoints that requested us to back out.
        self.backout(None)


    def handle_first_sequence_msg_from_partner(
        self,msg,name_of_block_to_exec_next):
        '''        
        ASSUMES ALREADY WITHIN LOCK

        @param {PartnerMessageRequestSequenceBlock.proto} msg ---

        @param {string} name_of_block_to_exec_next --- the name of the
        sequence block to execute next.

        @returns {Executing event}
        
        means that the other side has generated a first message create
        a new context to execute that message and do so in a new
        thread.
        '''
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
            self.event_parent.local_endpoint,block_to_exec_internal_name):
            util.logger_assert(
                'Error in _ActiveEvent.  Received a request to ' +
                'perform an unknown sequence step.')
        #### END MAYBE DEBUG

        to_exec = getattr(self.event_parent.local_endpoint,block_to_exec_internal_name)

        ### SET UP CONTEXT FOR EXECUTING
        # FIXME: re-arrange code to avoid this import
        import waldoVariableStore
        seq_local_var_store = waldoVariableStore._VariableStore(
            self.event_parent.local_endpoint._host_uuid)

        # FIXME: eventually, want to remove pickle-ing here
        seq_local_var_store.incorporate_deltas(
            self,msg.sequence_local_var_store_deltas)

        # FIXME: super ugly
        from waldoExecutingEvent import _ExecutingEventContext
        from waldoExecutingEvent import _ExecutingEvent

        
        evt_ctx = _ExecutingEventContext(
            # already incorporated deltas for global_var_store
            # above.
            self.event_parent.local_endpoint._global_var_store,
            seq_local_var_store)

        evt_ctx.set_to_reply_with(msg.reply_with_uuid.data)

        # used to actually start execution of context thread at end
        # of loop.  must start event outside of locks.  That way,
        # if the exec event leads to and endpoint call, etc., we
        # don't block waiting on its return.
        exec_event = _ExecutingEvent(
            to_exec,self,evt_ctx,
            None # using None here means that we do not need to
                 # bother with waiting for modified peered-s to
                 # update.
            )

        return exec_event


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
        self.event_parent.local_endpoint._global_var_store.incorporate_deltas(
            self,msg.peered_var_store_deltas)

        exec_event = None

        self._lock()
        if not msg.HasField('reply_to_uuid'):
            exec_event = self.handle_first_sequence_msg_from_partner(
                msg,name_of_block_to_exec_next)
        else:
            self.handle_non_first_sequence_msg_from_partner(
                msg,name_of_block_to_exec_next)
        self._unlock()

        if exec_event != None:
            ### ACTUALLY START EXECUTION CONTEXT THREAD
            exec_event.run()

            

    def handle_non_first_sequence_msg_from_partner(
        self,msg,name_of_block_to_exec_next):
        '''
        ASSUMES ALREADY WITHIN LOCK
        @param {PartnerMessageRequestSequenceBlock.proto} msg ---

        @param {string or None} name_of_block_to_exec_next --- the
        name of the sequence block to execute next. None if nothing to
        execute next (ie, last sequence message).
        '''
        #### DEBUG
        if msg.reply_to_uuid.data not in self.message_listening_queues_map:
            util.logger_assert(
                'Error: partner response message responding to ' +
                'unknown _ActiveEvent message.')
        #### END DEBUG

        # unblock waiting listening queue.
        self.message_listening_queues_map[msg.reply_to_uuid.data].put(
            _SequenceMessageCallResult(
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

