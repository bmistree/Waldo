import time
import Queue
import socket
import threading
from waldo.lib.proto_compiled.generalMessage_pb2 import GeneralMessage

class Heartbeat:
    '''
    Implementation of a simple endpoint to endpoint heartbeat.
    Periodically sends heartbeats to the partner endpoint and listens for
    heartbeats from the partner endpoint.

    It is meant to be integrated within the Waldo endpoint and to use
    the same socket being used by the endpoint to communicate with its
    partner.
    '''

    def __init__(self, socket, timeout_cb, send_period=1, timeout=15):
        '''
        Initializes the Heartbeat object. 

        @param  socket      Python socket object. Should already be connected.
        @param  timeout_cb  Callback function which is invoked upon timeout.
        @param  send_period Time (in seconds) representing how often to send 
                            heartbeats to the partner endpoint. The default 
                            period is 5 seconds.
        @param  timeout     Time (in seconds) to wait between partner heartbeats
                            before assuming node or network failure and calling
                            timeout_cb. The default period is 15 seconds.
        '''
        self._sock = socket
        self._timeout_cb = timeout_cb
        self._send_period = send_period
        self._timeout = timeout
        self._lock = threading.Lock()
        self._partner_alive = True

    def start(self):
        '''
        Starts the heartbeat's sending thread. Before this is called, the class
        will only be listening 
        '''
        self._time_since_last_beat = time.time()
        self._send_thread = threading.Thread(target=self._send_heartbeats)
        self._send_thread.daemon = True
        self._send_thread.start()
        self._timeout_thread = threading.Thread(target=self._check_timeout)
        self._timeout_thread.daemon = True
        self._timeout_thread.start()

    def receive_heartbeat(self, msg):
        '''
        Must be called when a heartbeat is received from the partner endpoint.

        @param  msg     The pong message received by the endpoint.
        '''
        self._lock.acquire()
        self._partner_alive = True
        self._lock.release()

    def _send_heartbeats(self):
        '''
        Periodically sends heartbeats to the partner endpoint to indicate that this
        endpoint is still alive and reachable.
        '''
        while True:
            time.sleep(self._send_period)
            general_message = GeneralMessage()
            general_message.message_type = GeneralMessage.HEARTBEAT
            heartbeat_message = general_message.heartbeat
            heartbeat_message.msg = 'ping' ### FIXME: This should probably be a constant,
                  ### whether or not it needs to be a string is debatable.
            try:
                self._sock.write(general_message.SerializeToString(),self)
            except socket.error as err:
                self._sock.close()
                break

    def _check_timeout(self):
        '''
        Periodically check that we have received one or more heartbeats from
        the partner in the last self._timeout seconds. 
        '''
        while True:
            time.sleep(self._timeout)
            self._lock.acquire()
            if self._partner_alive:
                self._partner_alive = False
                self._lock.release()
            else:
                self._lock.release()
                self._timeout_cb()
                break
