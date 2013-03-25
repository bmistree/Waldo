import util
import waldoConnectionObj
import Queue
import wVariables
# import shim.get_math_endpoint


_host_uuid = util.generate_uuid()
_threadsafe_stoppable_cleanup_queue = Queue.Queue()

def tcp_connect(constructor,host,port,*args):

    tcp_connection_obj = waldoConnectionObj._WaldoTCPConnectionObj(
        host,port)

    endpoint = constructor(_host_uuid,tcp_connection_obj,*args)
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
        stoppable, constructor,host,port,connected_callback,
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


# def math_endpoint_lib():
#     return shim.get_math_endpoint.math_endpoint(no_partner_create)

def no_partner_create(constructor,*args):
    '''
    @returns{Waldo endpoint} --- Calls constructor with args for an
    endpoint that has no partner.
    '''
    return constructor(
        _host_uuid,
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
