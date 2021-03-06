import sys,os,threading

# pickup local dependencies instead of system dependencies.
deps_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','deps')
sys.path.insert(0,deps_dir)

import waldo.lib.util as util
import waldo.lib.waldoConnectionObj as waldoConnectionObj
from waldo.lib.util import Queue
import waldo.lib.waldoCallResults as waldoCallResults
import waldo.lib.waldoEndpoint as waldoEndpoint
import waldo.lib.waldoExecutingEvent as waldoExecutingEvent
import waldo.lib.waldoVariableStore as waldoVariableStore
import waldo.lib.shim.get_math_endpoint 
import waldo.lib.waldoLockedVariables as waldoLockedVariables
from waldo.lib.waldoClock import Clock
from waldo.lib.waldoThreadPool import ThreadPool
from waldo.lib.waldoAllEndpoints import AllEndpoints

StoppedException = util.StoppedException


_host_uuid = util.generate_uuid()
_threadsafe_stoppable_cleanup_queue = Queue.Queue()

_default_values = {
    'heartbeat_timeout_period': 300,
    'heartbeat_send_period': 30,
    'thread_pool_count': 100
}

_waldo_all_endpoints = AllEndpoints()
_waldo_clock = Clock(_waldo_all_endpoints)
_waldo_thread_pool = ThreadPool(_default_values['thread_pool_count'])


_waldo_classes = {
    # waldo variables
    'WaldoNumVariable': waldoLockedVariables.LockedNumberVariable,
    'WaldoTextVariable': waldoLockedVariables.LockedTextVariable,
    'WaldoTrueFalseVariable': waldoLockedVariables.LockedTrueFalseVariable,
    'WaldoMapVariable': waldoLockedVariables.LockedMapVariable,
    'WaldoListVariable': waldoLockedVariables.LockedListVariable,
    'WaldoEndpointVariable': waldoLockedVariables.LockedEndpointVariable,
    'WaldoUserStructVariable': waldoLockedVariables.LockedStructVariable,
    'WaldoFunctionVariable': waldoLockedVariables.LockedFunctionVariable,

    'WaldoExtNumVariable': waldoLockedVariables.WaldoExternalNumberVariable,
    'WaldoExtTrueFalseVariable': waldoLockedVariables.WaldoExternalTrueFalseVariable,
    'WaldoExtTextVariable': waldoLockedVariables.WaldoExternalTextVariable,

    # single thread variables
    'WaldoSingleThreadNumVariable': waldoLockedVariables.SingleThreadedLockedNumberVariable,
    'WaldoSingleThreadTextVariable': waldoLockedVariables.SingleThreadedLockedTextVariable,
    'WaldoSingleThreadTrueFalseVariable': waldoLockedVariables.SingleThreadedLockedTrueFalseVariable,

    'WaldoSingleThreadMapVariable': waldoLockedVariables.SingleThreadedLockedMapVariable,
    'WaldoSingleThreadListVariable': waldoLockedVariables.SingleThreadedLockedListVariable,
    'WaldoSingleThreadEndpointVariable': waldoLockedVariables.SingleThreadedLockedEndpointVariable,
    'WaldoSingleThreadUserStructVariable': waldoLockedVariables.SingleThreadedLockedStructVariable,
    'WaldoSingleThreadFunctionVariable': waldoLockedVariables.SingleThreadedLockedFunctionVariable,
    
    # call results
    'CompleteRootCallResult': waldoCallResults._CompleteRootCallResult,
    'StopRootCallResult' : waldoCallResults._StopRootCallResult,
    'NetworkFailureCallResult' : waldoCallResults._NetworkFailureCallResult,
    'ApplicationExceptionCallResult' : waldoCallResults._ApplicationExceptionCallResult,
    'BackoutBeforeReceiveMessageResult': waldoCallResults._BackoutBeforeReceiveMessageResult,
    'BackoutDueToNetworkFailure': waldoCallResults._BackoutDueToNetworkFailure,
    'EndpointCallResult': waldoCallResults._EndpointCallResult,

    # misc
    'Endpoint': waldoEndpoint._Endpoint,
    'Queue': Queue,
    'ExecutingEventContext': waldoExecutingEvent._ExecutingEventContext,
    'VariableStore': waldoVariableStore._VariableStore,
    'BackoutException': util.BackoutException,
    'StoppedException': util.StoppedException,
    'NetworkException': util.NetworkException,
    'ApplicationException': util.ApplicationException,
    
    # Not a class, but global variable passed to everything:
    'Clock': _waldo_clock,
    'ThreadPool': _waldo_thread_pool,
    'AllEndpoints': _waldo_all_endpoints,
    }


def tcp_connect(constructor,host,port,*args):
    '''
    Tries to connect an endpoint to another endpoint via a TCP
    connection.

    Args:
    
      constructor (Endpoint Constructor): The constructor of the endpoint to
      create upon connection.  Should be imported from the compiled Waldo file.

      host (String): The name of the host to connect to.

      port (int): The TCP port to try to connect to.

      *args (*args):  Any arguments that should get passed to
      the endpoint's onCreate method for initialization.

    Returns:

      Endpoint object: --- Can call any Public method of this
      object.
    '''
    tcp_connection_obj = waldoConnectionObj._WaldoTCPConnectionObj(
        host,port)

    endpoint = constructor(
        _waldo_classes,_host_uuid,tcp_connection_obj,*args)
    return endpoint


def tcp_accept(constructor,host,port,*args,**kwargs):
    '''
    Non-blocking function that listens for TCP connections and creates
    endpoints for each new connection.

    Args:
    
      constructor(Endpoint Constructor): The constructor of
      the endpoint to create upon connection.  Should be imported from
      the compiled Waldo file.

      host (String): The name of the host to listen for
      connections on.

      port(int): The TCP port to listen for connections on.

      *args(*args): Any arguments that should get passed to
      the endpoint's onCreate method for initialization.

    Kwargs:

      connected_callback(function): Use kwarg "connected_callback."  When a
      connection is received and we create an endpoint, callback gets executed,
      passing in newly-created endpoint object as argument.

    Returns:
    
      Stoppable object: Can call stop method on this to stop listening for
      additional connections.  Note: listeners will not stop instantly, but
      probably within the next second or two.
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
    Used when trying to create endpoints on the same host.
    Example usage:
    endpointA, endpointB = (
        Waldo.same_host_create(ConstructorA,5).same_host_create(ConstructorB))

    if ConstructorA's onCreate method took in a Number and
    ConstructorB's onCreate method took no arguments.


    Args:

      constructor(Endpoint Constructor): The constructor of the endpoint to
      create.  Should be imported from the compiled Waldo file.

      *args (*args): Arguments to be passed to the new host's constructor.

    Returns:

      EndpointCreater object: Call same_host_create on SecondCreater, passing in
      constructor of second endpoint and any args its onCreate takes.  It will
      return both endpoints created.

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


    
def math_endpoint_lib():
    '''
    Can pass returned endpoint object into Waldo code and make endpoint
    calls on it to provide several math operations that otherwise would be
    missing from the Waldo langauge.

    The enpdoint returned has the following public methods:
    
    Public Function min_func(List(element: Number) in_nums) returns Number
    Public Function max_func(List(element: Number) in_nums) returns Number
    Public Function mod_func(Number lhs, Number rhs) returns Number
    /**
     * @returns {Number} --- Returns random integer in the range [a,b]
     */
    Public Function rand_int_func(Number a, Number b) returns Number    

    Returns:
    
      Endpoint object: Can pass this endpoint into Waldo code and make endpoint
      calls on it to provide several math operations that otherwise would be
      missing from the Waldo langauge.

    '''
    return waldo.lib.shim.get_math_endpoint.math_endpoint(no_partner_create)


def no_partner_create(constructor,*args):
    '''
    Creates an endpoint without its partner.

    Returns:
    
      Waldo endpoint: Calls constructor with args for an endpoint that has no
      partner.
    '''
    return constructor(
        _waldo_classes,_host_uuid,
        waldoConnectionObj._WaldoSingleSideConnectionObject(),
        *args)
        

def stop():
    '''
    Tells all TCP connection listeners to stop listening for new
    connections and begins safely closing all open connections on this
    server.

    Warning: FIXME: does not actually begin safely closing connections.
    
    '''
    # FIXME: does not actually begin safely closing connections.
    
    try:
        stoppable_item = _threadsafe_stoppable_cleanup_queue.get_nowait()
        stoppable_item.stop()
        stop()
    except:
        return


def set_default_partner_timeout(timeout_period):
    '''
    Sets the default timeout period for connections between endpoints. 
    When a heartbeat from a partner endpoint is not received within the
    timeout window an exception is thrown to indicate connection failure.

    Must be called before tcp_connect or tcp_accept for the period passed
    in to be used correctly.

    Args:
    
      timeout_period(number): Length of timeout in seconds.

    '''
    _default_values['heartbeat_timeout_period'] = timeout_period


def set_default_heartbeat_period(heartbeat_period):
    '''
    Sets the default heartbeat period for connections between endpoints. 
    The heartbeat period indicates how often each endpoint should send a
    heartbeat message to its partner endpoint 

    Must be called before tcp_connect or tcp_accept for the period passed
    in to be used correctly.

    Args:
    
      heartbeat_period(number): Length of heartbeat period in seconds.

    '''
    _default_values['heartbeat_send_period'] = heartbeat_period
