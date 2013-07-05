import threading
import waldoCallResults
import waldoReferenceBase
import waldoReferenceContainerBase
import numbers
import wVariables
import util
import waldoEndpoint, waldoInternalMap, waldoInternalList
from util import Queue
from waldoObj import WaldoObj


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

        # if this function were called via an endpoint call on another
        # endpoint, then from_endpoint_call will be true.  We check
        # whether this function was called from another endpoint so
        # that we know whether we need to copy in reference
        # containers.  Pass lists, maps, and user structs by value
        # type across endpoint calls unless they're declared external.
        self.from_endpoint_call = False


    def set_from_endpoint_true(self):
        self.from_endpoint_call = True

    def check_and_set_from_endpoint_call_false (self):
        to_return = self.from_endpoint_call
        self.from_endpoint_call = False
        return to_return
        
    def set_to_reply_with (self,to_reply_with_uuid):
        '''
        @param {uuid} to_reply_with_uuid --- @see comments above
        self.to_reply_with_uuid in __init__ method.
        '''
        self.to_reply_with_uuid = to_reply_with_uuid

    def reset_to_reply_with(self):
        '''
        Each time we finish a message sequence, we reset
        set_to_reply_with.  This is so that if we start any new
        message sequences, the calls to the message sequences will be
        started fresh instead of viewed as a continuation of the
        previous sequence.
        '''
        self.set_to_reply_with(None)
        

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

    def write_val(self,to_write_to,to_write,active_event):
        if isinstance(to_write_to, WaldoObj):
            to_write_to.write_val(active_event,to_write)
            return to_write_to
        return to_write



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

        if isinstance(val,wVariables._WaldoExternalValueType):
            return val.get_val(active_event).get_val(active_event)
        elif isinstance(val,WaldoObj):
            return val.get_val(active_event)
        return val


    def turn_into_waldo_var_if_was_var(
        self,val,force_copy,active_event, host_uuid,
        new_peered,new_multi_threaded):
        '''
        @see turn_into_waldo_var, except that we will only turn into a
        Waldo variable if the previous value had been a Waldo variable.

        Otherwise, return the value and variable keeps Python form.
        '''
        if (isinstance(val,WaldoObj) or
            isinstance(val,dict) or
            isinstance(val,list)):
            # note: when converting from external, we may need to copy
            # list and dict reference types so that changes to them do
            # not interfere with actual values in Python.
            return self.turn_into_waldo_var(
                val,force_copy,active_event,host_uuid,new_peered,
                new_multi_threaded)

        return val
        

    def turn_into_waldo_var(
        self,val,force_copy,active_event, host_uuid,new_peered,
        new_multi_threaded):
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

        # FIXME: Start using some of the single threaded constructors
        # as well.
        
        if isinstance(val,WaldoObj):
            if force_copy:
                # means that it was a WaldoVariable: just call its copy
                # method
                return val.copy(active_event,new_peered,new_multi_threaded)
            # otherwise, just return val
            return val

        # means that val was not a reference object.... turn it into one.
        constructor = None

        if new_multi_threaded:

            if util.is_string(val):
                # not using isinstance here because python 3 and python
                # 2.7 have different ways of testing for string.
                constructor = wVariables.WaldoTextVariable
            elif isinstance(val,numbers.Number):
                constructor = wVariables.WaldoNumVariable
            elif isinstance(val,bool):
                constructor = wVariables.WaldoTrueFalseVariable
            elif isinstance(val,dict):
                constructor = wVariables.WaldoMapVariable
            elif isinstance(val,list):
                constructor = wVariables.WaldoListVariable
            elif isinstance(val,waldoEndpoint._Endpoint):
                constructor = wVariables.WaldoEndpointVariable
            #### DEBUG
            elif hasattr(val,'__call__'):
                # checks if is function
                util.logger_assert(
                    'Should use special call func_turn_into_waldo_var for function objects')
            else:
                util.logger_assert(
                    'Unknown object type to call turn_into_waldo_var on')
            #### END DEBUG

                
        else:
            if util.is_string(val):
                # not using isinstance here because python 3 and python
                # 2.7 have different ways of testing for string.
                constructor = wVariables.WaldoSingleThreadTextVariable
            elif isinstance(val,numbers.Number):
                constructor = wVariables.WaldoSingleThreadNumVariable
            elif isinstance(val,bool):
                constructor = wVariables.WaldoSingleThreadTrueFalseVariable
            elif isinstance(val,dict):
                constructor = wVariables.WaldoSingleThreadMapVariable
            elif isinstance(val,list):
                constructor = wVariables.WaldoSingleThreadListVariable
            elif isinstance(val,waldoEndpoint._Endpoint):
                constructor = wVariables.WaldoSingleThreadEndpointVariable
            #### DEBUG
            elif hasattr(val,'__call__'):
                # checks if is function
                util.logger_assert(
                    'Should use special call func_turn_into_waldo_var for function objects')
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

    def func_turn_into_waldo_var(
        self,val,force_copy,active_event, host_uuid,new_peered,
        ext_args_array,new_multi_threaded):
        '''
        turn_into_waldo_var works for all non-function types.
        function-types require additional information (which arguments
        are and are not external) to populate their ext_args_array.
        This is passed in in this function.
        '''
        if isinstance(val,wVariables.WaldoFunctionVariable):
            if force_copy:
                # means that it was a WaldoVariable: just call its copy
                # method
                return val.copy(active_event,new_peered,new_multi_threaded)
            # otherwise, just return val
            return val
        elif hasattr(val,'__call__'):
            # python function
            pass
        #### DEBUG
        else:
            util.logger_assert(
                'incorrect type passed into func_turn_into_waldo_var')
        #### END DEBUG

        waldo_func = wVariables.WaldoFunctionVariable(
            'garbage',
            host_uuid,
            new_peered,
            val).set_external_args_array(ext_args_array)

        return waldo_func
    
    
    def call_func_obj(
        self,active_event,func_obj,*args):
        '''
        @param {wVariable.WaldoFunctionVariable} func_obj --- The
        wrapped function that we are calling.

        @param {*args} --- The actual arguments that get passed to the
        function.
        '''
        # {list} external_arg_list --- Each element is a number.
        # If a number is in this list, then that means that the
        # corresponding argument to func_obj is external and therefore
        # should not be de_waldo-ified.  If an argument does not have
        # its corresponding index in the array, then dewaldo-ify it.
        external_arg_list = func_obj.ext_args_array

        if external_arg_list == None:
            util.logger_assert(
                'No external arg array for function object')
        
        call_arg_list = []
        for counter in range(0,len(args)):
            to_append = args[counter]
            if counter not in external_arg_list:
                to_append = self.de_waldoify(to_append,active_event)

            call_arg_list.append(to_append)

        internal_func = func_obj.get_val(active_event)
        returned_val = internal_func(
            active_event.local_endpoint,*call_arg_list)

        if isinstance(returned_val,list):
            return wVariables.WaldoSingleThreadListVariable(
                'garbage', # actual name of variable isn't important
                active_event.local_endpoint._host_uuid,
                False, # not peered
                returned_val# used as initial value
                )

        elif isinstance(returned_val,dict):
            return wVariables.WaldoSingleThreadMapVariable(
                'garbage', # actual name of variable isn't important
                active_event.local_endpoint._host_uuid,
                False, # not peered
                returned_val# used as initial value
                )        
        
        return returned_val

    
    def convert_for_seq_local(self,val,active_event,host_uuid):
        '''
        Take whatever is in val and copy it into a sequence local
        piece of data (ie, change peered to True).  Return the copy.

        Used when loading arguments to message send into sequence
        local data space.
        '''
        return self.turn_into_waldo_var(
            val,True,active_event,host_uuid,
            # will be peered because used between both sides
            True,
            # will not be multi-threaded, because only can be accessed
            # from one thread of control at a time.
            False)


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

    def assign(self,lhs,rhs,active_event):
        '''
        If lhs is a Waldo variable, then write_val rhs's value into it
        and return True.  Otherwise, return False.  (if return False,
        then should do assignment in function calling from directly.)

        Note: to assign into a specific index of a map, list, or
        struct, use assign_on_key, below.
        
        @returns{bool} --- True if after this method lhs contains rhs.
        False otherwise.
        '''
        
        if not isinstance(lhs,WaldoObj):
            return False

        lhs.write_val(active_event,self.get_val_if_waldo(rhs,active_event))
        return True


    def assign_on_key(self,lhs,key,rhs,active_event):
        '''
        For bracket statements + struct statements
        '''
        if not isinstance(lhs,WaldoObj):
            return False

        raw_key = self.get_val_if_waldo(key,active_event)

        if wVariables.is_non_ext_text_var(lhs):
            raw_rhs = self.get_val_if_waldo(rhs,active_event)            
            to_overwrite_string = lhs.get_val(active_event)
            to_overwrite_string[raw_key] = raw_rhs
            lhs.write_val(active_event,to_overwrite_string)
        elif isinstance(lhs,wVariables.WaldoExtTextVariable):
            raw_rhs = self.get_val_if_waldo(rhs,active_event)            
            to_overwrite_string = lhs.get_val(active_event).get_val(active_event)
            to_overwrite_string[raw_key] = raw_rhs
            lhs.get_val(active_event).write_val(active_event,to_overwrite_string)
        elif waldoReferenceContainerBase.is_reference_container(lhs):
            # just write the value explicitly for now.  Later, will
            # need to check if we need to wrap it first.
            lhs.write_val_on_key(active_event,raw_key,rhs)
        else:
            # just write the value explicitly for now.  Later, will
            # need to check if we need to wrap it first.
            lhs.get_val(active_event).write_val_on_key(active_event,raw_key,rhs)

        return True

    def get_val_on_key(self,to_get_from,key,active_event):
        raw_key = self.get_val_if_waldo(key,active_event)
        
        if not isinstance(to_get_from,WaldoObj):
            return to_get_from[raw_key]

        # handle text + ext text
        if wVariables.is_non_ext_text_var(lhs):
            return to_get_from.get_val(active_event)[raw_key]

        if isinstance(lhs,wVariables.WaldoExtTextVariable):
            return to_get_from.get_val(active_event).get_val(active_event)[raw_key]

        # handle internals containers
        if waldoReferenceContainerBase.is_reference_container(lhs):
            return to_get_from.get_val_on_key(active_event,raw_key)

        # handle map, list, struct
        return to_get_from.get_val(active_event).get_val_on_key(active_event,raw_key)
        
    def get_for_iter(self,to_iter_over,active_event):
        '''
        When call for loop on Waldo variables, need to get item to
        iterate over
        '''

        if (isinstance(to_iter_over,dict) or
            isinstance(to_iter_over,list) or
            util.is_string(to_iter_over)):
            return iter(to_iter_over)

        if wVariables.is_non_ext_text_var(to_iter_over):
            return iter(to_iter_over.get_val(active_event))

        if wVariables.is_non_ext_map_var(to_iter_over):
            return iter(to_iter_over.get_val(active_event).get_keys(active_event))

        if wVariables.is_non_ext_list_var(to_iter_over):
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
                if (wVariables.is_non_ext_list_var(to_append) or
                    wVariables.is_non_ext_map_var(to_append)):
                    to_append = to_append.get_val(active_event)
                
                to_return.append(to_append)

            return iter(to_return)

        util.logger_assert(
            'Calling get_for_iter on an object that does not support iteration')

        
        
    def to_text(self,what_to_call_to_text_on,active_event):
        '''
        @returns {Python String}
        '''
        if not isinstance(what_to_call_to_text_on,WaldoObj):
            return str(what_to_call_to_text_on)

        # strings for waldo variable value types
        if (wVariables.is_non_ext_text_var(what_to_call_to_text_on) or
            wVariables.is_non_ext_num_var(what_to_call_to_text_on) or
            wVariables.is_non_ext_true_false_var(what_to_call_to_text_on)):
            return str(what_to_call_to_text_on.get_val(active_event))

        # strings for reference types
        # lists
        if wVariables.is_non_ext_list_var(what_to_call_to_text_on):
            to_return_arg = ''
            waldo_internal_list = what_to_call_to_text_on.get_val(active_event)
            # get each element separately from the list and call
            # to_text on it.
            for i in range(0,waldo_internal_list.get_len(active_event)):
                list_val = waldo_internal_list.get_val_on_key(active_event,i)
                to_return_arg += self.to_text(list_val,active_event) + ', '
            
            return '[%s]' % to_return_arg

        # maps
        if wVariables.is_non_ext_map_var(what_to_call_to_text_on):
            to_return_arg = ''
            waldo_internal_map = what_to_call_to_text_on.get_val(active_event)
            # get each element separately from the list and call
            # to_text on it.
            waldo_key_list = waldo_internal_map.get_keys(active_event)
            waldo_internal_key_list = waldo_key_list.get_val(active_event)
            
            for i in range(0,waldo_internal_key_list.get_len(active_event)):
                key_val = waldo_internal_key_list.get_val_on_key(active_event,i)

                # get item from map
                item_val = waldo_internal_map.get_val_on_key(active_event,key_val)

                
                to_return_arg += (
                    self.to_text(key_val,active_event) + ': ' +
                    self.to_text(item_val,active_event) + ', ')

            
            return '{%s}' % to_return_arg

    def signal_call(self,active_event,func,*args):
        class Signal(object):
            def __init__(self,func,*args):
                self.func = de_waldoify(func,active_event)
                self.args = []
                for arg in args:
                    self.args.append(de_waldoify(arg,active_event))
            def call(self):
                self.func(active_event.local_endpoint,*self.args)

        active_event.add_signal_call(Signal(func,*args))
                
                
    def handle_len(self,what_calling_len_on, active_event):
        '''
        Can support python lists, dicts, strings, or waldo lists, waldo maps,
        waldo texts.
        
        @returns {int}
        '''
        if (isinstance(what_calling_len_on, dict) or
            isinstance(what_calling_len_on, list) or
            util.is_string(what_calling_len_on)):
            return len(what_calling_len_on)

        if wVariables.is_non_ext_text_var(what_calling_len_on):
            return len(what_calling_len_on.get_val(active_event))


        if (wVariables.is_non_ext_list_var(what_calling_len_on) or
            wVariables.is_non_ext_map_var(what_calling_len_on)):
            return what_calling_len_on.get_val(active_event).get_len(active_event)

        util.logger_assert(
            'Calling len on an object that does not support the function')
        

    def hide_endpoint_call(
        self,active_event,context,endpoint_obj,method_name,*args):

        threadsafe_result_queue = Queue.Queue()
        
        active_event.issue_endpoint_object_call(
            endpoint_obj,method_name,threadsafe_result_queue,*args)

        queue_elem = threadsafe_result_queue.get()

        # FIXME: there may be other errors that are not from
        # backout...we shouldn't treat all cases of not getting a
        # result as a backout exception
        if not isinstance(queue_elem, waldoCallResults._EndpointCallResult):
            raise util.BackoutException()
        
        return queue_elem.result_array
        
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
        if util.is_string(rhs):
            return lhs_val in rhs

        elif wVariables.is_non_ext_text_var(rhs):
            return lhs_val in rhs.get_val(active_event)

        elif wVariables.is_non_ext_map_var(rhs):
            return rhs.get_val(active_event).contains_key_called(
                active_event,lhs_val)

        elif wVariables.is_non_ext_list_var(rhs):
            return rhs.get_val(active_event).contains_val_called(
                active_event,lhs_val)

        util.logger_assert(
            'Error when calling in: unknown right hand side of expression')
        
    
def de_waldoify(val,active_event):
    '''
    When returning a value to non-Waldo code, need to convert the
    value to a regular python type.  This function handles that.
    '''
    if isinstance(val,WaldoObj):
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
class _ExecutingEvent(object):

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

        # threading.Thread.__init__(self)
        # self.daemon = True
        

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
        


