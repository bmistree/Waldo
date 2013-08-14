import sys,os,threading

# pickup local dependencies instead of system dependencies.
deps_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','deps')
sys.path.insert(0,deps_dir)

import util
import waldoConnectionObj
from util import Queue
import wVariables
import waldoCallResults
import waldoEndpoint
import waldoExecutingEvent
import waldoVariableStore
import shim.get_math_endpoint
import waldoReferenceBase
import WaldoSSL
from WaldoSSL import secure
from WaldoSSL import keymanager
import shutil

StoppedException = util.StoppedException


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

    # single thread variables
    'WaldoSingleThreadNumVariable': wVariables.WaldoSingleThreadNumVariable,
    'WaldoSingleThreadTextVariable': wVariables.WaldoSingleThreadTextVariable,
    'WaldoSingleThreadTrueFalseVariable': wVariables.WaldoSingleThreadTrueFalseVariable,
    'WaldoSingleThreadMapVariable': wVariables.WaldoSingleThreadMapVariable,
    'WaldoSingleThreadListVariable': wVariables.WaldoSingleThreadListVariable,
    'WaldoSingleThreadUserStructVariable': wVariables.WaldoSingleThreadUserStructVariable,
    'WaldoSingleThreadEndpointVariable': wVariables.WaldoSingleThreadEndpointVariable,
    
    
    # call results
    'CompleteRootCallResult': waldoCallResults._CompleteRootCallResult,
    'StopRootCallResult' : waldoCallResults._StopRootCallResult,

    'BackoutBeforeReceiveMessageResult': waldoCallResults._BackoutBeforeReceiveMessageResult,
    'EndpointCallResult': waldoCallResults._EndpointCallResult,

    # misc
    'Endpoint': waldoEndpoint._Endpoint,
    'Queue': Queue,
    'ExecutingEventContext': waldoExecutingEvent._ExecutingEventContext,
    'VariableStore': waldoVariableStore._VariableStore,
    'BackoutException': util.BackoutException,
    'StoppedException': util.StoppedException
    }

def uuid():
  '''
  Params:
  None


  Returns the uuid (probability says this should be unique)
  '''
  return _host_uuid

def get_key():
  '''
  Call this to get a key pair

  IMPORTANT: The key pair shouldn't be passed around. The public key should be extracted then passed around.

  Returns a key object
  '''
  return secure.get_key()

def get_certificate(CN, host, port, key):
  '''
  Params:
  host and port are the address that certificate authority is running on
  key is the keyobject that you want to register
  CN is the common name that you want

  Returns:
  The certificate object

  Call get_cert_text if you need a keytext version
  '''
  return secure.get_certificate(CN, host, port, key)

def start_ca(generate=False, certfile="cacertificate.pem", keyfile="cakey.pem", host=None, port=None, start_time=None, end_time=None, cert_start = None, cert_end = None, authentication_function=None):
  '''
  Params:
  Call this to start a CA running on the host and port specified.

  Generate says whether or not 
  to create a new certificate or not. If True, it will save the certificate in the address specified by the certfile, and the key in the keyfile path specified.
  If Generate is False, then it will load up the certificate and key from the path specified.

  The start_time and the end_time says how when the certificates should start and how long they should last. The start_time is seconds from now, and the end_time is seconds from the start_time.
  By defauly, it starts now and ends in 3 months. 

  The cert_start and cert_end say how long the ca_certificate generated should last and function the same way as the start_time and end_time

  The authentication function is a callback function that will called everytime a request for a certificate comes in. It should accept a string. It is up the developer
  to create their own authentication function to know if the CN being asked for is valid.

  '''
  keymanager.start_ca(generate, certfile, keyfile, host, port,start_time, end_time, cert_start, cert_end, authentication_function)

def get_ca_endpoint(host, port):
  '''
  This used to past back an endpoint so you can ask for certificates through Waldo.
  '''
  return secure.connect_to_ca(host, port)


def get_certificate(client, CN, key):
  '''
  Params:
  client is the endpoint that we will call to get the certificate. Get it from get_ca_endpoint.

  CN, key are the common name and key that we respectively want saved

  Return:
  returns the certificate object
  '''

  req = secure.generate_request(CN, key)
  cert = client.req_to_cert(req)
  import OpenSSL
  from OpenSSL import crypto
  cert = crypto.load_certificate(crypto.FILETYPE_PEM,cert)
  return cert

def add_ca_to_list(ca_file, host, port):
  '''
  This is used to add a custom CA to your CA list.
  Params:
  ca_file is a pathname to where the file is stored.

  host and port is the address of the CA that we want to add to the list
  '''
  ca_cert = secure.get_cacert(host, port)
  f = open("temp.pem", "w+")
  f.write(ca_cert)
  f.close()
  destination = open(ca_file,'wb')
  shutil.copyfileobj(open(ca_file,'rb'), destination)
  shutil.copyfileobj(open("temp.pem",'rb'), destination)
  destination.close()

def encrypt_keytext(key, passphrase, cipher=None):
  '''
  This is the function used to encrypt text
  Params:
  The key is the key object.

  The passphrase is the password we're using to encrypt it.

  The cipher is the encryption algorithm. "DES3" is the default.

  Returns: 
  The ciphertext in a text form
  '''
  import OpenSSL
  from OpenSSL import crypto
  if cipher is None:
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, key, "DES3", passphrase)
  else:
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, key, cipher, passphrase)

def decrypt_keytext(keytext, passphrase):
  '''
  Params:
  This is the function used to decrypt the keytext.

  The keytext is the encrypted text.

  The passphrase is the phrase we're using to decode the cipher text
  
  Returns:
  A PKey object.
  '''
  import OpenSSL
  from OpenSSL import crypto
  return crypto.load_privatekey(crypto.FILETYPE_PEM, keytext, passphrase)

def cleanup(certfile, keyfile=None):
  '''
  Helper function called to cleanup the certfile and keyfile so they aren't kept on disk.

  certfile and keyfile are pathnames
  '''
  os.remove(certfile)
  os.remove(keyfile)

def salt():
  '''
  Returns a randomly generated uuid to use as salt
  '''
  return util.generate_uuid()

def hash(password, salt):
  '''
  Param:
  Hashes the password
  password is keytext of the password
  salt is the randomly generated string passed to randomize it

  Returns:
  The hash digest in string format
  '''
  import hashlib
  h = hashlib.new("sha256")
  h.update(password + str(salt))
  return h.hexdigest()

def get_cert_text(cert):
  '''
  Params:
  cert

  Returns:
  The certificate text dump of a certificate object
  '''
  import OpenSSL
  from OpenSSL import crypto
  return crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

def get_cert_from_text(certtext):
  '''
  Params:

  certtext is the text dump of a certificate object

  Returns: 
  A certificate object from a certificate text
  '''
  import OpenSSL
  from OpenSSL import crypto
  return crypto.load_certificate(crypto.FILETYPE_PEM, certtext)

def stcp_connect(constructor,host,port,*args, **kwargs):
    '''
    Tries to connect an endpoint to another endpoint via a TCP
    connection though SSL.

    Args:
    
      constructor (Endpoint Constructor): The constructor of the endpoint to
      create upon connection.  Should be imported from the compiled Waldo file.

      host (String): The name of the host to connect to.

      port (int): The TCP port to try to connect to.

      certfile (String): The file path of the certificate file

      keyfile (String): The file path of the keyfile

      *args (*args):  Any arguments that should get passed to
      the endpoint's onCreate method for initialization.

    Returns:

      Endpoint object: --- Can call any Public method of this
      object.
    '''


    stcp_connection_obj = waldoConnectionObj._WaldoSTCPConnectionObj(
        host,port, **kwargs)

    endpoint = constructor(
        _waldo_classes,_host_uuid,stcp_connection_obj,*args)
    return endpoint

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


def stcp_accept(constructor, host, port, *args, **kwargs):
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

      certfile (String): The file path of the certificate file

      keyfile (String): The file path of the keyfile. Leave as None if key is in certfile

      ca_certs (String): List of CAs you trust. If your certificates aren't verified, leave as None.

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
    
    tcp_accept_thread = waldoConnectionObj._STCPAcceptThread(
        stoppable, constructor,_waldo_classes,host,port,
        connected_callback,
        _host_uuid,synchronization_queue,*args,**kwargs)
    tcp_accept_thread.start()

    # once this returns, we know that we are listening on the
    # host:port pair.
    synchronization_queue.get()

    
    # the user can call stop directly on the returned object, but we
    # still put it into the cleanup queue.  This is because there is
    # no disadvantage to calling stop multiple times.
    _threadsafe_stoppable_cleanup_queue.put(stoppable)
    return stoppable

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
    return shim.get_math_endpoint.math_endpoint(no_partner_create)

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
