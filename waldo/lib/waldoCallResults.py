
# FIXME: probably a lot of overhead using classes here instead of just
# named tuples.

####### ENDPOINT CALL RESULTS ########

# When an active event issues an endpoint call, it blocks on reading a
# threadsafe queue.  If the invalidation event has been backed out
# before the endpoint call completes, we put a
# _BackoutBeforeEndpointCallResult into the queue so that the event
# knows not to perform any additional work.  Otherwise, put an
# _EndpointCallResult in, which contains the returned values.
class _EndpointCallResult(object):
    def __init__(self,result_array):
        self.result_array = result_array
        
class _BackoutBeforeEndpointCallResult(object):
    pass

class _StopAlreadyCalledEndpointCallResult(object):
    pass



class _EndpointCallError(object):
    '''
    If we get an error in the midst of an endpoint call, then we
    return a subtype of this class into an endpoint's result queue.
    '''
    def __init__(self,err):
        self.err = err

class _NoMethodEndpointCallError(_EndpointCallError):
    def __init__(self,func_name):
        _EndpointCallError.__init__(
            self, 'No func name named ' + func_name + ' on endpoint.')



####### MESSAGE CALL RESULTS ########
class _SequenceMessageCallResult(object):
    def __init__(
        self,reply_with_msg_field,to_exec_next_name_msg_field,
        sequence_local_var_store_deltas):
        '''
        @param {UUID} reply_with_msg_field --- @see comment above
        self.message_listening_queues_map in
        waldoActiveEvent._ActiveEvent.

        @param {String or None} to_exec_next_name_msg_field --- In a
        message sequence, tells us the next internal function to
        execute in the sequence.  If it is None, then it means that
        there is no more to execute in the sequence.

        @param {dict} sequence_local_var_store_deltas --- Should be
        able to put this map directly into a _VariableStore object
        to update each of an event's pieces of peered data.  @see
        waldoVariableStore._VariableStore.incorporate_deltas
        
        We must update the event context with the new
        reply_with_msg_field when complete.
        '''
        self.reply_with_msg_field = reply_with_msg_field
        self.to_exec_next_name_msg_field = to_exec_next_name_msg_field
        self.sequence_local_var_store_deltas =  sequence_local_var_store_deltas
        
        
        
class _BackoutBeforeReceiveMessageResult(object):
    pass

class _ModifiedUpdatedMessageResult(object):
    '''
    @see waldoActiveEvent.wait_if_modified_peered
    '''
    pass


######### ROOT EVENT QUEUE CALL RESULTS ######
# the requester of a root event listens on a threadsafe queue until
# the event completes.  it listens for objects of these types.
class _RescheduleRootCallResult(object):
    pass

class _StopRootCallResult(object):
    pass

class _CompleteRootCallResult(object):
    pass
