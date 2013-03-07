import threading
import waldoCallResults
import waldoReferenceBase
import numbers
import wVariables
import util

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

        self.msg_send_initialized_bit = False
        
        
    def set_to_reply_with (self,to_reply_with_uuid):
        '''
        @param {uuid} to_reply_with_uuid --- @see comments above
        self.to_reply_with_uuid in __init__ method.
        '''
        self.to_reply_with_uuid = to_reply_with_uuid


    def set_msg_send_initialized_bit_false(self):
        '''
        @see emitter.emit_statement._emit_msg_seq_begin_call

        Essentially, it is difficult to keep track of whether we have
        initialized sequence local data in the presence of jumps.
        (What happens if we jump back into a message send function
        that was already initializing data?)  Use this value to test
        whether we need to initialize sequence local data or not.
        '''
        self.msg_send_initialized_bit = False
        return True

    def set_msg_send_initialized_bit_true(self):
        '''
        @see set_msg_send_initialized_bit_false

        @returns {Bool} --- The previous state of the initialized bit.
        Can use this to test whether to initialize sequence local data.
        '''
        prev_initialized_bit = self.msg_send_initialized_bit
        self.msg_send_initialized_bit = True
        return prev_initialized_bit


    #### UTILITY FUNCTIONS  ####
    # all of these could be static: they don't touch any internal
    # state.
    def get_val_if_waldo(self,val):
        '''
        @param {Anything} val --- If val is a waldo reference object,
        call get_val on it.  Otherwise, return val itself.

        Assume that we are emitting for 
        a = b
        and
        a = 4

        In the first case, we do not want to assign the reference of b
        to a, we want to assign its value.  In the second case, we
        want to assign the value of 4 to a.  We want to emit the
        following for each:

        a.write_val(_active_event,b.get_val(_active_event))
        a.write_val(_active_event,4)

        At compile time, we *do* have information on whether the rhs
        of the expression is a literal or a WaldoReference object.
        However, it's a pain to keep track of this information.
        Therefore, the compiler just uses this function at *runtime.*
        This function will either call get_val on the oject (if it's a
        WaldoReference) or just pass it through otherwise.
        '''
        if isinstance(val,waldoReferenceBase._ReferenceBase):
            return val.get_val()
        return val

    def turn_into_waldo_var(
        self,val,force_copy,active_event, host_uuid,new_peered=False):
        '''
        @param {Anything} val

        @param {bool} force_copy

        @param {_ActiveEvent object} active_event
        
        @param {uuid} host_uuid

        @param {bool} new_peered --- True if in the case that we have
        to copy a value, the copy should be peered.  Used for loading
        arguments into sequence local data when message send is
        called.  @see convert_for_seq_local.
        
        @returns {WaldoVariable}

        Used when copying arguments in to function.  Compiler's caller
        can pass in Python literals or WaldoReference objects when it
        emits a function call.  However, the emitted function
        definition requires all arguments to be WaldoVariables.
        Therefore, at the beginning of each emitted function, copy all
        arguments in to WaldoVariables if they are not already.  

        If val is not a WaldoReference, then based on its type, assign
        it as the initial value of a Waldo Variable and return.

        If val is a WaldoReference, then check force_copy.  force_copy
        represents whether or not we want to make a copy of the
        WaldoReference object.  (It would be True for instance if we
        were passed in a WaldoNumber because numbers are passed by
        value; it would be false if the arg was external or if we were
        passed in a reference type.)

        If it is false, then just return val.  Otherwise, make copy.
        
        '''
        if (isinstance(val,waldoReferenceBase._ReferenceBase) and
            (not force_copy)):
            return val

        if force_copy:
            # means that it was a WaldoVariable: just call its copy
            # method
            return val.copy(active_event,new_peered)


        # means that val was not a reference object.... turn it into one.
        constructor = None
        if isinstance(val,basestring):
            constructor = wVariables.WaldoTextVariable
        elif isinstance(val,numbers.Number):
            constructor = wVariables.WaldoNumVariable
        elif isinstance(val,bool):
            constructor = wVariables.WaldoTrueFalseVariable
        elif isinstance(val,dict):
            constructor = wVariables.WaldoMapVariable
        elif isinstance(val,list):
            constructor = wVariables.WaldoListVariable
        #### DEBUG
        else:
            util.logger_assert(
                'Unknown object type to call turn_into_waldo_var on')
        #### END DEBUG
        
        return constructor(
            'garbage', # actual name of variable isn't important
            host_uuid,
            new_peered, # not peered
            val # used as initial value
            )

    def convert_for_seq_local(self,val,active_event,host_uuid):
        '''
        Take whatever is in val and copy it into a sequence local
        piece of data (ie, change peered to True).  Return the copy.

        Used when loading arguments to message send into sequence
        local data space.
        '''
        return self.turn_into_waldo_var(
            val,True,active_event,host_uuid,True)

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
        receive it.  Can be None only for events that were initiated
        by messages (in which the modified peered data would already
        have been updated).
        
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
        


