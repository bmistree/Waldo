import util
import waldoConnectionObj
from util import Queue
import wVariables
import waldoCallResults
import waldoEndpoint
import waldoExecutingEvent
import waldoVariableStore
import threading
import shim.get_math_endpoint
import logging

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
    'logger': util.get_logger()
    }

def setup_logging():
    '''
    Internal function.  Not to be used by programmer.
    '''
    DEFAULT_LOG_FILENAME = 'log.txt'
    DEFAULT_LOGGING_LEVEL = logging.CRITICAL
    
    format_ = (
        '%(levelname)s : %(asctime)s.%(msecs)f: %(endpoint_string)s : %(mod)s \n     %(message)s')
        # '%(levelname)s : %(asctime)s.%(msecs).03d: %(endpoint_string)s : %(mod)s \n     %(message)s')
    logging.basicConfig(
        format=format_, filename=DEFAULT_LOG_FILENAME, level=DEFAULT_LOGGING_LEVEL,
        datefmt='%I:%M:%S')

    util.get_logger().critical(
        '***** New *****', extra={'mod': 'NEW', 'endpoint_string': 'NEW'})

    util.lock_log('***** New *****')

    
setup_logging()
    
def set_logging_level(level):
    '''
    @param {int} level --- See Python's internal logging module.
    Options are logging.CRITICAL, logging.INFO, logging.DEBUG, etc.
    
    User can set level of logging he/she desires.  Note: mostly used
    internally for compiler development.
    '''
    util.get_logger().setLevel(level)
    

def tcp_connect(constructor,host,port,*args):
    '''
    @param {Endpoint Constructor} constructor --- The constructor of
    the endpoint to create upon connection.  Should be imported from
    the compiled Waldo file.

    @param {String} host --- The name of the host to connect to.

    @param {int} port --- The TCP port to try to connect to.

    @param {*args} *args --- Any arguments that should get passed to
    the endpoint's onCreate method for initialization.

    @returns {Endpoint object} --- Can call any Public method of this
    object.

    Tries to connect an endpoint to another endpoint via a TCP
    connection.
    '''
    
    tcp_connection_obj = waldoConnectionObj._WaldoTCPConnectionObj(
        host,port)

    endpoint = constructor(
        _waldo_classes,_host_uuid,tcp_connection_obj,*args)
    return endpoint

def tcp_accept(constructor,host,port,*args,**kwargs):
    '''
    @param {Endpoint Constructor} constructor --- The constructor of
    the endpoint to create upon connection.  Should be imported from
    the compiled Waldo file.

    @param {String} host --- The name of the host to listen for
    connections on.

    @param {int} port --- The TCP port to listen for connections on.

    @param {*args} *args --- Any arguments that should get passed to
    the endpoint's onCreate method for initialization.

    @param {connected_callback} function --- Use kwarg
    "connected_callback."  When a connection is received and we create
    an endpoint, callback gets executed, passing in newly-created
    endpoint object as argument.
    
    @returns {Stoppable object} --- Can call stop method on this to
    stop listening for additional connections.  Note: listeners will
    not stop instantly, but probably within the next second or two.

    Non-blocking function that listens for TCP connections and creates
    endpoints for each new connection.
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
    @param {Endpoint Constructor} constructor --- The constructor of
    the endpoint to create.  Should be imported from
    the compiled Waldo file.

    @param {*args} *args --- Arguments to be passed to the new host's constructor.
    
    @returns {EndpointCreater object} --- Call same_host_create on
    SecondCreater, passing in constructor of second endpoint and any
    args its onCreate takes.  It will return both endpoints created.

    Example usage:
    endpointA, endpointB = (
        Waldo.same_host_create(ConstructorA,5).same_host_create(ConstructorB))

    if ConstructorA's onCreate method took in a Number and
    ConstructorB's onCreate method took no arguments.
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
    @returns {Endpoint object} --- Can pass this endpoint into Waldo code and
    make endpoint calls on it to provide several math operations that otherwise
    would be missing from the Waldo langauge.

    The enpdoint returned has the following public methods:
    
    Public Function min_func(List(element: Number) in_nums) returns Number
    Public Function max_func(List(element: Number) in_nums) returns Number
    Public Function mod_func(Number lhs, Number rhs) returns Number
    /**
     * @returns {Number} --- Returns random integer in the range [a,b]
     */
    Public Function rand_int_func(Number a, Number b) returns Number
    '''
    return shim.get_math_endpoint.math_endpoint(no_partner_create)

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
