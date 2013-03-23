import util
import Queue
import threading
import socket
import re

class _WaldoConnectionObject(object):

    def register_endpoint(self,endpoint):
        util.logger_assert(
            'Error register_endpoint in _WaldoConnectionObject ' +
            'is pure virtual')
    
    def write(self,string_to_write,endpoint_writing):
        util.logger_assert(
            'Error write in _WaldoConnectionObject is pure ' +
            'virtual.')

class _WaldoSingleSideConnectionObject(_WaldoConnectionObject):

    def __init__(self):
        self.endpoint = None
    
    def register_endpoint(self,endpoint):
        self.endpoint = endpoint

        # force a message to other side that fakes saying that the
        # other side's onCreate has completed
        self.endpoint._receive_partner_ready(None)

    def write(self,to_write,endpoint_writing):
        pass

    
class _WaldoSameHostConnectionObject(_WaldoConnectionObject,threading.Thread):
    def __init__(self):
        self.queue = Queue.Queue()

        self.endpoint_mutex = threading.Lock()
        self.endpoint1 = None
        self.endpoint2 = None

        threading.Thread.__init__(self)
        self.daemon = True

    def register_endpoint (self, endpoint):
        self.endpoint_mutex.acquire()
        if self.endpoint1 == None:
            self.endpoint1 = endpoint
        else:
            self.endpoint2 = endpoint
            self.endpoint1._set_partner_uuid(
                self.endpoint2._uuid)
            self.endpoint2._set_partner_uuid(
                self.endpoint1._uuid)

            self.start()

        self.endpoint_mutex.release()
            

    def write(self,msg,endpoint):
        self.queue.put((msg,endpoint))

    def run(self):
        while True:
            msg,msg_sender_endpt = self.queue.get()
            msg_recvr_endpt = self.endpoint1
            if msg_sender_endpt == self.endpoint1:
                msg_recvr_endpt = self.endpoint2

            msg_recvr_endpt._receive_msg_from_partner(msg)
                


class _WaldoTCPConnectionObj(_WaldoConnectionObject):

    DELIMITER_A = 'a'
    DELIMITER_B = 'b'
    # every message ends with this delimiter
    MSG_DELIMITER = DELIMITER_A + DELIMITER_B
    # every message begins with this letter
    MSG_HEAD = 'm'

    # messages are constructed in such a way that we replace every
    # occurrence of the delimiter in the message body with duplicates
    # of the delimiter.  For example, message
    #
    # acb
    #
    # would turn into
    #
    # aacbb
    # 
    # We then glue on the MSG_HEAD and MSG_DELIMITER onto the message:
    #
    # maacbbab
    #
    # To decode, it is not enough that we only check that the message
    # ends with ab.  Consider the following original mesasge:
    # ab
    # translates to
    # maabbab
    # Would decode as a: m(a)ab
    #
    # We need to ensure that ends with ab and there are only an even
    # number of a-s before ab.  We can do this with the following regex:
    # [^a](?aa)*ab
    # Note the inclusion of the [^a] at the beginning will still work
    # for empty messages because we add the MSG_HEAD to the front.

    
    def __init__(self,dst_host,dst_port,sock=None):
        '''
        Either dst_host + dst_port are None or sock is None.
        
        @param {socket} sock --- If not passed in a socket, then
        create a new connection to dst_host, dst_port.
        '''

        if sock == None:
            self.sock = socket.create_connection((dst_host,dst_port))
        else:
            self.sock = sock

        self.received_data = ''
        self.local_endpoint = None

        
    def register_endpoint(self,local_endpoint):
        '''
        @param {_Endpoint object} local_endpoint --- @see the emitted
        code for a list of _Endpoint object methods.
        
        Once we have an attached endpoint, we start listening for data
        to send to that endpoint.
        '''
        self.local_endpoint = local_endpoint
        listening_thread = _TCPListeningThread(self)
        listening_thread.start()

    def _start_listening_loop(self):
        while 1:
            data = self.sock.recv(1024)
            self.received_data += data
            self._decapsulate_msg_and_dispatch()


    @staticmethod
    def _encapsulate_msg_str(str_to_escape):
        '''
        Adds delimiters to message so that when other side's
        TCPConnectionObject receives a byte string, can know when
        received full message to forward on to receiving endpoint.
        Note: _decapsulate_msg(_encapsulate_msg_str(msg_str)) equals
        the original message.
        '''

        to_return = str_to_escape.replace(
            _WaldoTCPConnectionObj.DELIMITER_A,
            _WaldoTCPConnectionObj.DELIMITER_A + _WaldoTCPConnectionObj.DELIMITER_A)

        to_return = to_return.replace(
            _WaldoTCPConnectionObj.DELIMITER_B,
            _WaldoTCPConnectionObj.DELIMITER_B + _WaldoTCPConnectionObj.DELIMITER_B)

        return _WaldoTCPConnectionObj.MSG_HEAD + to_return + _WaldoTCPConnectionObj.MSG_DELIMITER

    @staticmethod
    def _decapsulate_msg_str(to_try_to_decapsulate):
        '''
        @returns {2-tuple} (a,b)

           a{String or None} --- Either the string corresponding to a
           fully read-in message or None if do not have enough data to
           create a message.

           b{String or None} --- Either the string corresponding to
           the rest of the data that we received from the opposite
           side or None if did not have enough data to create a
           message

        '''
            # '[^%s](?:%s%s)*(%s%s)' %
        
        regex = (
            '[^%s](?:%s%s)*%s%s' %
            (_WaldoTCPConnectionObj.DELIMITER_A,_WaldoTCPConnectionObj.DELIMITER_A,
             _WaldoTCPConnectionObj.DELIMITER_A,_WaldoTCPConnectionObj.DELIMITER_A,
             _WaldoTCPConnectionObj.DELIMITER_B))

        match_obj = re.search(regex,to_try_to_decapsulate)

        if match_obj == None:
            return None,None

        # only checking for one message group at a time.
        new_msg_group_index = 0

        
        # Trim off the message header and footer
        new_msg = match_obj.string[
            len(_WaldoTCPConnectionObj.MSG_HEAD):
                match_obj.end(new_msg_group_index) - len(_WaldoTCPConnectionObj.MSG_DELIMITER)]
        
        remaining_msg = match_obj.string[match_obj.end(new_msg_group_index) + 1:]

        
        # de-duplicate replaced characters
        new_msg = new_msg.replace(
            _WaldoTCPConnectionObj.DELIMITER_A + _WaldoTCPConnectionObj.DELIMITER_A,
            _WaldoTCPConnectionObj.DELIMITER_A)
        new_msg = new_msg.replace(
            _WaldoTCPConnectionObj.DELIMITER_B + _WaldoTCPConnectionObj.DELIMITER_B,
            _WaldoTCPConnectionObj.DELIMITER_B)

        
        return new_msg,remaining_msg

        
    def _decapsulate_msg_and_dispatch(self):
        '''
        When receive a full message, fire callback into endpoint code
        to handle the message.

        @returns {Nothing} 
        '''

        msg_str,rest_of_data = self._decapsulate_msg_str(
            self.received_data)

        if msg_str == None:
            # had not received full message
            return

        # dispatch to endpoint
        self.local_endpoint._receive_msg_from_partner(msg_str)

        self.received_data = rest_of_data
        # recurse in case received more than two messages worth of
        # information simultaneously.
        self._decapsulate_msg_and_dispatch()
        

    def write(self,msg_str_to_write,sender_endpoint_obj):
        '''
        @param {String} msg_str_to_write
        @param {Endpoint} sender_endpoint_obj
        
        Gets called from endpoint to send message from one side to the
        other.
        '''
        msg_str_to_send = self._encapsulate_msg_str(msg_str_to_write)
        self.sock.send(msg_str_to_send)


        
class _TCPListeningStoppable(object):
    '''
    Need a way to escape from listening for TCP connections.  Every
    second, a TCP listener will poll a stoppable object to check if it
    should stop listening for connections.
    '''
    
    def __init__(self):
        self._mutex = threading.Lock()
        self._uuid = util.generate_uuid()
        self._stopped = False

    def stop(self):
        self._mutex.acquire()
        self._stopped = True
        self._mutex.release()

    def is_stopped(self):
        self._mutex.acquire()
        to_return = self._stopped
        self._mutex.release()
        return to_return
        
        
class _TCPListeningThread(threading.Thread):
    '''
    Just starts the "_start_listening_loop" on the
    tcp_connection_object.  Whenever this loop receives sufficient
    data, it spins off another thread TCPFireEvent, which calls
    msg_receive on connection's local endpoint
    '''
    def __init__(self,tcp_connection_object):
        self.tcp_connection_object = tcp_connection_object
        threading.Thread.__init__(self)
        self.setDaemon(True)
        
    def run(self):
        self.tcp_connection_object._start_listening_loop()


class _TCPAcceptThread(threading.Thread):

    def __init__(
        self, stoppable, endpoint_constructor, host_listen_on,
        port_listen_on, cb, host_uuid,synchronization_listening_queue,
        *args):
        '''
        @param{_TCPListeningStoppable object} stoppable --- Every 1s,
        breaks out of listening for new connections and checks if
        should stop waiting on connections.
        
        @param{function}endpoint_constructor --- An _Endpoint object's
        constructor.  It takes in a tcp connection object, reservation
        manager object, and any additional arguments specified in its
        oncreate method.
        
        @param{String} host_listen_on --- The ip/host to listen for
        new connections on.

        @param{int} port_listen_on --- The prot to listen for new
        connections on.

        @param {function or Non} cb --- When receive a new connection,
        execute the callback, passing in a new Endpoint object in its
        callback.  

        @param{UUID} host_uuid ---

        
        @param {Queue.Queue} synchronization_listening_queue --- The
        thread that began this thread blocks waiting for a value on
        this queue so that it does not return before this thread has
        started to listen for the connection.
        
        @param{*args} --- Any other arguments to pass into the
        oncreate argument of the endpoint constructor.

        '''
        
        self.stoppable= stoppable
        self.endpoint_constructor = endpoint_constructor
        self.host_listen_on = host_listen_on
        self.port_listen_on = port_listen_on
        self.cb = cb
        self.host_uuid = host_uuid
        
        self.synchronization_listening_queue = synchronization_listening_queue
        
        self.args = args

        threading.Thread.__init__(self)
        self.daemon = True

        
    def run(self):

        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # we do not want to listen for the connection forever.  every
        # 1s, if we do not get a connection check if we should stop listening
        sock.settimeout(1)
        
        sock.bind((self.host_listen_on, self.port_listen_on))
        sock.listen(1)
        self.synchronization_listening_queue.put(True)
        while True:

            try:

                conn, addr = sock.accept()
                tcp_conn_obj = _WaldoTCPConnectionObj(None,None,conn)

                created_endpoint = self.endpoint_constructor(
                    self.host_uuid,tcp_conn_obj,*self.args)

                if self.cb != None:
                    self.cb(created_endpoint)

                if self.stoppable.is_stopped():
                    break
                    
            except socket.timeout:
                if self.stoppable.is_stopped():
                    break
                
