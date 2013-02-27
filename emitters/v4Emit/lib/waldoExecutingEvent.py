import threading



class _ExecutingEventContext(object):
    def __init__(self,global_store,sequence_local_store):
        '''
        @param {_WaldoVariableStore} global_store --- Keeps track of
        endpoint globals and peered data.

        @param {_WaldoVariableStore} sequence_local_store --- Keeps
        track of sequence local data.
        '''
        
        # We can be listening to more than one open threadsafe message
        # queue.  If endpoint A waits on its partner, and, while
        # waiting, its partner executes a series of endpoint calls so
        # that another method on A is invoked, and that method calls
        # its partner again, we could be waiting on 2 different
        # message queues, each held by the same active event.  To
        # ensure that we can correctly demultiplex which queue a
        # message was intended for, each message that we send has two
        # fields, reply_with and reply_to.  reply_with tells the
        # partner endpoint that when it is done, send back a message
        # with uuid reply_with in the message's reply_to field.  (The
        # first message sent has a reply_to field of None.)  We use
        # the reply_to field to index into a map of message listening
        # queues in waldoActiveEvent._ActiveEvent.
        self.to_reply_with_uuid = None

        self.global_store = global_store
        self.sequence_local_store = sequence_local_store
        
        
        
    def set_to_reply_with (self,to_reply_with_uuid):
        '''
        @param {uuid} to_reply_with_uuid --- @see comments above
        self.to_reply_with_uuid in __init__ method.
        '''
        self.to_reply_with_uuid = to_reply_with_uuid


'''
When either external code or another endpoint asks us to execute a
function, we create an active event to use to execute that function.
We want to execute it in its own separate thread.  This class provides
that separate thread and executes the function.
'''
class _ExecutingEvent(threading.Thread):

    def __init__(self,to_exec,active_event,ctx,result_queue,*to_exec_args):
        '''
        @param {Closure} to_exec --- The closure

        @param {_ActiveEvent object} active_event --- The active event
        object that to_exec should use for accessing endpoint data.

        @param {_ExecutingEventContext} ctx ---

        @param {result_queue or None} --- This value should be
        non-None for endpoint-call initiated events.  For endpoint
        call events, we wait for the endpoint to check if any of the
        peered data that it modifies also need to be modified on the
        endpoint's partner (and wait for partner to respond).  (@see
        discussion in waldoActiveEvent.wait_if_modified_peered.)  When
        finished execution, put wrapped result in result_queue.  This
        way the endpoint call that is waiting on the result can
        receive it.  Can be Null only for events that were initiated
        by messages (in which the modified peered data would already
        have been updated).

        FIXME: what if re-used a message-initiated event as an
        endpoint initiated called event?
        
        @param {*args} to_exec_args ---- Any additional arguments that
        get passed to the closure to be executed.
        '''

        self.to_exec = to_exec
        self.active_event = active_event
        self.to_exec_args = to_exec_args
        self.ctx = ctx

        self.result_queue = result_queue
        
        threading.Thread.__init__(self)
        self.daemon = True
        

    def run(self):
        result = self.to_exec(self.active_event,self.ctx,*self.to_exec_args)

        if self.result_queue == None:
            return
        
        # check if the active event has touched any peered data.  if
        # have, then send an update message to partner and wait for
        # ack of message before returning.
        completed = self.active_event.wait_if_modified_peered()

        if not completed:
            self.result_queue.put(
                waldoCallResults._BackoutBeforeEndpointCallResult())

        else:
            self.result_queue.put(
                waldoCallResults._EndpointCallResult(result))
        


