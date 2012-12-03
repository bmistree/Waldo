#!/usr/bin/env python


CONNECTION_TYPE_TCP = 0
# not yet supported
# CONNECTION_TYPE_LOCAL = 1
# CONNECTION_TYPE_NO_CONNECTION = 2


_DEFAULT_TCP_ACCEPT_WALDO_PORT = 5300
_DEFAULT_TCP_ACCEPT_WALDO_HOST = '127.0.0.1'

from reservationManager import ReservationManager
import connObj
import externalObjects as Externals
import random

class WaldoModuleExcep (Exception):
    def __init__(self,err_msg):
        self.value = err_msg
    def __str__(self):
        return repr(self.value)

# used to synchronize all external variables
_reservation_manager = None
_initialized_called = False
_waldo_id = None

def initialize(**kwargs):
    global _reservation_manager
    _reservation_manager = ReservationManager()

    global _waldo_id
    _waldo_id = _generate_uuid()
    
    global _initialized_called
    if _initialized_called:
        excep_msg = 'Can only initialize Waldo module once'
        WaldoModuleExcep(excep_msg)
    
    _initialized_called = True

    
def connect(*args,**kwargs):
    '''
    @param{int} port --- The port to connect to on the listening host
    (ie, the host that's running accept).  Defaults to 5300.

    @parma{String} host_name --- The IP address or host name of the
    host that we're trying to connect to.  Defaults to 127.0.0.1.
    
    @param{int} connection_type --- @see accept
    
    @param {WaldoEndpoint Class} constructor --- @see accept

    @param {Function} connected_callback --- @see accept

    @param *args --- All other args will be passed into the endpoint
    constructor in the order they are provided.

    @returns {Waldo Endpoint Object} --- Connected Waldo endpoint.
    
    '''
    _check_init('connect')

    if not ('constructor' in kwargs):
        excep_msg = 'Waldo.connect requires keyword arg "constructor" '
        excep_msg += 'to be passed in.'
        raise WaldoModuleExcep(excep_msg)
        
    connection_obj_type = kwargs.get('connection_type',CONNECTION_TYPE_TCP)
    constructor = kwargs['constructor']
    connected_callback = kwargs.get('connected_callback',None)
    
    
    if connection_obj_type == CONNECTION_TYPE_TCP:
        port = kwargs.get('port',_DEFAULT_TCP_ACCEPT_WALDO_PORT)
        host_name = kwargs.get('host',_DEFAULT_TCP_ACCEPT_WALDO_HOST)

        tcp_conn_obj = connObj.TCPConnectionObject(host_name,port,None)
        _endpoint_id = _generate_uuid()
        
        new_obj = constructor(
            tcp_conn_obj,_reservation_manager,
            _waldo_id,_endpoint_id,*args)
        
        return new_obj
        
    excep_msg = 'Waldo.connect only allows TCP connections.  Other '
    excep_msg += 'connection types may be added in the future.'
    raise WaldoModuleExcep(excep_msg)

def _generate_uuid():
    # FIXME: may want a little more control over probability of uniqueness
    return random.random()
    
def accept(*args,**kwargs):
    '''
    @param {Waldo Endpoint Class} constructor --- Required.  Specifies
    what endpoint to create when receive a connection.

    @param {int} connection_type --- Specifies whether to create a TCP
    connection between endpoints (Waldo.CONNECTION_TYPE_TCP).  Other
    connection types may later be added.  Defaults to tcp connection.

    @param{int} port --- Port to listen on for connections.  Defaults
    to 5300.

    @param{String} host_name --- The IP address or host name to listen
    for connections on.  Defaults to 127.0.0.1.

    @param{Function} connected_callback --- Optional.  If provided, as
    soon as the connection is made, executes this function, passing in
    the new endpoint object as an argument.
    
    @param *args --- All other args will be passed into the endpoint
    constructor in the order they are provided.
    '''

    _check_init('accept')
    global _reservation_manager


    if not ('constructor' in kwargs):
        excep_msg = 'Waldo.accept requires keyword arg "constructor" '
        excep_msg += 'to be passed in.'
        raise WaldoModuleExcep(excep_msg)

    
    connection_obj_type = kwargs.get('connection_type',CONNECTION_TYPE_TCP)
    constructor = kwargs['constructor']
    connected_callback = kwargs.get('connected_callback',None)
    
    
    if connection_obj_type == CONNECTION_TYPE_TCP:
        port = kwargs.get('port',_DEFAULT_TCP_ACCEPT_WALDO_PORT)
        host_name = kwargs.get('host',_DEFAULT_TCP_ACCEPT_WALDO_HOST)


        # listen for incoming client connections on host_name:port_no
        connObj.TCPConnectionObject.accept(
            host_name,port,connected_callback,
            constructor,_reservation_manager,_waldo_id,
            _generate_uuid,*args)
    else:
        excep_msg = 'Waldo.accept only allows TCP connections.  Other '
        excep_msg += 'connection types may be added in the future.'
        raise WaldoModuleExcep(excep_msg)






    
########################
#    
# Thin wrappers around external objects.  @see externalObjects.py
# for actuall definitions of each.
#
########################
    
def ExternalTrueFalse(initial_val):
    _check_init('ExternalTrueFalse')
    global _reservation_manager
    return Externals.ExternalTrueFalse(
        initial_val,_reservation_manager)

def ExternalNumber(initial_val):
    _check_init('ExternalNumber')
    global _reservation_manager
    return Externals.ExternalNumber(
        initial_val,_reservation_manager)

def ExternalText(initial_val):
    _check_init('ExternalText')
    global _reservation_manager
    return Externals.ExternalText(
        initial_val,_reservation_manager)

def ExternalList(initial_val):
    _check_init('ExternalList')
    global _reservation_manager
    return Externals.ExternalList(
        initial_val,_reservation_manager)
    
def ExternalMap(initial_val):
    _check_init('ExternalMap')
    global _reservation_manager
    return Externals.ExternalMap(
        initial_val,_reservation_manager)
    
def ExternalFile(filename):
    _check_init('ExternalFile')
    global _reservation_manager
    return Externals.ExternalFile(
        filename,_reservation_manager)
    
def ExternalFs(folder_name):
    _check_init('ExternalFs')
    global _reservation_manager
    return Externals.ExternalFs(
        folder_name,_reservation_manager)


#################
# Helper functions
#################    
def _check_init(function_name):
    '''
    @raises {WaldoModuleExcep} --- If the function named function_name
    is accessed before Waldo.initialize has been called, raise exception.
    '''
    global _initialized_called
    if not _initialized_called:
        excep_msg = 'Cannot call Waldo.' + function_name
        excep_msg += ' until have already have called ' 
        excep_msg += 'Waldo.initialize.'
        raise WaldoModuleExcep(excep_msg)        
    
