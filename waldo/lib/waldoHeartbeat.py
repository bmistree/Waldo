import time
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

    def __init__(self, socket, timeout_cb, send_period=1, timeout=30):
        '''
        Initializes the Heartbeat object. 

        @param  socket      Python socket object. Should already be connected.
        @param  timeout_cb  Callback function which is invoked upon timeout.
        @param  send_period Time (in seconds) representing how often to send 
                            heartbeats to the partner endpoint.
        @param  timeout     Time (in seconds) to wait between partner heartbeats
                            before assuming node or network failure and calling
                            timeout_cb.
        '''
        self._sock = socket
        self._timeout_cb = timeout_cb
        self._send_period = send_period
        self._timeout = timeout


    def start(self):
        '''
        Starts the heartbeat's sending thread. Before this is called, the class
        will only be listening 
        '''
        self._thread = threading.Thread(target=self._send_heartbeats)
        self._thread.daemon = True
        self._thread.start()

    def _send_heartbeats(self):
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
                print 'caught write error in heartbeat send thread.'
                self._sock.close()
                print 'closed socket...'
                break

    def receive_heartbeat(self, msg):
        '''
        Must be called when a heartbeat is received from the partner endpoint,
        indicating that the partner is still alive and reachable.

        @param  msg     The pong message received by the endpoint.
        '''

#        print 'received heartbeat' ## for testing purposes

        pass
