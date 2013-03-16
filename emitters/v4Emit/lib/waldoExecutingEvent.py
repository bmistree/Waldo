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
    def get_val_if_waldo(self,val,active_event):
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

        @param {InvalidationListener or None} --- If None, then this
        is used during initialization of variables.  Means that the
        Waldo Reference should just return the actual committed value
        of the variable.  Don't wait for commit or anything else.
        
        '''
        if isinstance(val,waldoReferenceBase._ReferenceBase):
            return val.get_val(active_event)
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

        if isinstance(val,waldoReferenceBase._ReferenceBase):
            if force_copy:
                # means that it was a WaldoVariable: just call its copy
                # method
                return val.copy(active_event,new_peered)
            # otherwise, just return val
            return val

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


    def de_waldoify(self,val,active_event):
        return de_waldoify(val,active_event)


    def flatten_into_single_return_tuple(self,*args):
        '''
        @param *args 

        @returns {tuple or a single value}

        Take something like this: 
        1, (2,3), 4, ((5), (6))
        or
        (1, (2,3), 4, ((5), (6)))
        and turn it into
        (1, 2, 3, 4, 5, 6)

        If the length of the return tuple is just one, then just
        return that value directly.  This is so that when we are
        returning a single value, instead of returning a tuple
        containing a single value, we return the value.

        Ie, if we take in
        (1,)
        we return
        1
        '''
        to_return_list = []

        for arg in args:
            if isinstance(arg,tuple):
                for item in arg:
                    # recursive call returns either a tuple or a
                    # single value....in either case, we want to
                    # incorporate it into the master to_return_list.
                    recursive_val = self.flatten_into_single_return_tuple(item)
                    if isinstance(recursive_val,tuple):
                        item = list(recursive_val)
                    else:
                        item = [recursive_val]
                    to_return_list += item
            else:
                to_return_list.append(arg)

        to_return_tuple = tuple(to_return_list)
        if len(to_return_list) == 1:
            return to_return_tuple[0]
        return to_return_tuple

    def get_for_iter(self,to_iter_over,active_event):
        '''
        When call for loop on Waldo variables, need to get item to
        iterate over
        '''

        if (isinstance(to_iter_over,dict) or
            isinstance(to_iter_over,list) or
            isinstance(to_iter_over,basestring)):
            return iter(to_iter_over)

        if isinstance(to_iter_over,wVariables.WaldoTextVariable):
            return iter(to_iter_over.get_val(active_event))

        if isinstance(to_iter_over,wVariables.WaldoMapVariable):
            return iter(to_iter_over.get_val(active_event).get_keys(active_event))

        if isinstance(to_iter_over,wVariables.WaldoListVariable):
            # FIXME: This is an inefficient way of reading all values
            # over list.
            to_return = []
            for i in range(0, to_iter_over.get_val(active_event).get_len(active_event)):
                to_append = to_iter_over.get_val(active_event).get_val_on_key(active_event,i)

                # The reason that we do this here is that in a for
                # loop, the operation we perform in the compiled code
                # immediately following the actual for header is
                # assign to another Waldo variable the variable being
                # held by to_append.  (We do this through a write_val
                # call.  write_val must take in InternalMaps or
                # InternalLists.  Therefore, get_val on the
                # WaldoList/WaldoMap first.  Note this is unnecessary
                # for all other for iterations because none of the
                # others possibly return a WaldoObject to iterate over.
                if (isinstance(to_append,wVariables.WaldoListVariable) or
                    isinstance(to_append,wVariables.WaldoMapVariable)):
                    to_append = to_append.get_val(active_event)
                
                to_return.append(to_append)


            return iter(to_return)
        
        util.emit_assert(
            'Calling get_for_iter on an object that does not support iteration')
        

    def handle_len(self,what_calling_len_on, active_event):
        '''
        Can support python lists, dicts, strings, or waldo lists, waldo maps,
        waldo texts.
        
        @returns {int}
        '''
        if (isinstance(what_calling_len_on, dict) or
            isinstance(what_calling_len_on, list) or
            isinstance(what_calling_len_on, basestring)):
            return len(what_calling_len_on)

        if isinstance(what_calling_len_on,wVariables.WaldoTextVariable):
            return len(what_calling_len_on.get_val(active_event))


        if (isinstance(what_calling_len_on,wVariables.WaldoListVariable) or
            isinstance(what_calling_len_on,wVariables.WaldoListVariable)):
            return what_calling_len_on.get_val(active_event).get_len(active_event)

        util.emit_assert(
            'Calling len on an object that does not support the function')
        
    
    def handle_in_check(self,lhs,rhs,active_event):
        '''
        Call has form:
            lhs in rhs
        
        rhs can have three basic types: it can be a list, a map, or a
        string.  That means that it can either be a WaldoMapVariable,
        a WaldoListVariable, a WaldoStringVariable, or a Python
        string.

        Instead of using static type inference at compile time to
        determine, for sake of development, just doing dynamic check
        to determine which type it is and do the in processing here.

        FIXME: it is faster to do the static checks with type
        inference, etc. at compile time rather than at run time.
        '''
        lhs_val = self.get_val_if_waldo(lhs,active_event)

        # handles Python string case
        if isinstance(rhs,basestring):
            return lhs_val in rhs

        elif isinstance(rhs,wVariables.WaldoTextVariable):
            return lhs_val in rhs.get_val(active_event)

        elif isinstance(rhs,wVariables.WaldoMapVariable):
            return rhs.get_val(active_event).contains_key_called(
                active_event,lhs_val)

        elif isinstance(rhs,wVariables.WaldoListVariable):
            return rhs.get_val(active_event).contains_val_called(
                active_event,lhs_val)

        util.emit_assert(
            'Error when calling in: unknown right hand side of expression')
        
    
def de_waldoify(val,active_event):
    '''
    When returning a value to non-Waldo code, need to convert the
    value to a regular python type.  This function handles that.
    '''
    if isinstance(val,waldoReferenceBase._ReferenceBase):
        return val.de_waldoify(active_event)
    if isinstance(val,tuple):
        # means that we are trying to dewaldoify a function call's
        # return.  Need to dewaldo-ify each element of tuple
        return_list = []
        for item in val:
            return_list.append(de_waldoify(item,active_event))
        return tuple(return_list)

    return val
    
    
    
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
        


