class EventSubscribedTo(object):
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

