import util
import waldoConnectionObj
import Queue
import wVariables
import waldoCallResults
import waldoEndpoint
import waldoExecutingEvent
import waldoVariableStore
import threading
# import shim.get_math_endpoint


_host_uuid = util.generate_uuid()
_threadsafe_stoppable_cleanup_queue = Queue.Queue()

_waldo_classes = {
    # waldo variables
    'WaldoNumVariable': wVariables.WaldoNumVariable,
    'WaldoTextVariable': wVariables.WaldoTextVariable,
    'WaldoTrueFalseVariable': wVariables.WaldoTrueFalseVariable,
    'WaldoMapVariable': wVariables.WaldoMapVariable,
    'WaldoListVariable': wVariables.WaldoListVariable,
    'WaldoUserStructVariable': wVariables.WaldoUserStructVariable,
    'WaldoFunctionVariable': wVariables.WaldoFunctionVariable,
    
    'WaldoEndpointVariable': wVariables.WaldoEndpointVariable,
    'WaldoExtNumVariable': wVariables.WaldoExtNumVariable,
    'WaldoExtTrueFalseVariable': wVariables.WaldoExtTrueFalseVariable,
    'WaldoExtTextVariable': wVariables.WaldoExtTextVariable,
    
    # call results
    'CompleteRootCallResult': waldoCallResults._CompleteRootCallResult,
    'BackoutBeforeReceiveMessageResult': waldoCallResults._BackoutBeforeReceiveMessageResult,
    'EndpointCallResult': waldoCallResults._EndpointCallResult,

    # misc
    'Endpoint': waldoEndpoint._Endpoint,
    'Queue': Queue,
    'ExecutingEventContext': waldoExecutingEvent._ExecutingEventContext,
    'VariableStore': waldoVariableStore._VariableStore,
    'BackoutException': util.BackoutException,
    }


def tcp_connect(constructor,host,port,*args):

    tcp_connection_obj = waldoConnectionObj._WaldoTCPConnectionObj(
        host,port)

    endpoint = constructor(
        _waldo_classes,_host_uuid,tcp_connection_obj,*args)
    return endpoint

def tcp_accept(constructor,host,port,*args,**kwargs):
    '''
    @returns {Stoppable object} --- Can call stop method on this to
    stop listening for additional connections.  Note: listeners will
    not stop instantly, but probably within the next second or two.
    '''
    
    connected_callback = kwargs.get('connected_callback',None)

    stoppable = waldoConnectionObj._TCPListeningStoppable()

    # TCP listenener starts in a separate thread.  We must wait for
    # the calling thread to actually be listening for connections
    # before returning.
    synchronization_queue = Queue.Queue()
    
    tcp_accept_thread = waldoConnectionObj._TCPAcceptThread(
        stoppable, constructor,_waldo_classes,host,port,
        connected_callback,
        _host_uuid,synchronization_queue,*args)
    tcp_accept_thread.start()

    # once this returns, we know that we are listening on the
    # host:port pair.
    synchronization_queue.get()

    
    # the user can call stop directly on the returned object, but we
    # still put it into the cleanup queue.  This is because there is
    # no disadvantage to calling stop multiple times.
    _threadsafe_stoppable_cleanup_queue.put(stoppable)
    return stoppable

def same_host_create(constructor,*args):
    '''
    @returns {EndpointCreater object} --- Call same_host_create on
    SecondCreater, passing in constructor of second endpoint and any
    args its onCreate takes.  It will return both endpoints created.
    '''

    class EndpointCreater(object):
        '''
        Creates two separate threads in case one side needs to
        initialize peered data: in this case, both sides need to be
        running and listening for initialization messages.
        '''
                
        def same_host_create(self,constructor2,*args2):

            class CreateEndpoint(threading.Thread):
                def __init__(self,threadsafe_queue, same_host_conn_obj,constructor, *args):
                    self.threadsafe_queue = threadsafe_queue
                    self.same_host_conn_obj = same_host_conn_obj
                    self.constructor = constructor
                    self.args = args

                    threading.Thread.__init__(self)
                    self.daemon = True
                    
                def run(self):
                    endpoint = self.constructor(
                        _waldo_classes,_host_uuid,self.same_host_conn_obj,*self.args)
                    self.threadsafe_queue.put(endpoint)

            
            same_host_conn_obj = waldoConnectionObj._WaldoSameHostConnectionObject()

            q1 = Queue.Queue()
            ce1 = CreateEndpoint(q1,same_host_conn_obj,constructor,*args)
            ce1.start()

            q2 = Queue.Queue()
            ce2 = CreateEndpoint(q2,same_host_conn_obj,constructor2,*args2)
            ce2.start()

            first_endpoint = q1.get()
            second_endpoint = q2.get()
            
            return first_endpoint, second_endpoint

    return EndpointCreater()


    

# def math_endpoint_lib():
#     return shim.get_math_endpoint.math_endpoint(no_partner_create)

def no_partner_create(constructor,*args):
    '''
    @returns{Waldo endpoint} --- Calls constructor with args for an
    endpoint that has no partner.
    '''
    return constructor(
        _waldo_classes,_host_uuid,
        waldoConnectionObj._WaldoSingleSideConnectionObject(),
        *args)
        

def stop():
    '''
    Tells all connection listeners to stop listening for new
    connections and begins safely closing all open connections on this
    server.
    '''
    # FIXME: does not actually begin safely closing connections.
    
    try:
        stoppable_item = _threadsafe_stoppable_cleanup_queue.get_nowait()
        stoppable_item.stop()
        stop()
    except:
        return
