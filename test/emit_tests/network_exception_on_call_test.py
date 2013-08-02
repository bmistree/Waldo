#!/usr/bin/env python
import os
import sys
import time

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
from network_exception_on_call_test_v4 import Ping, Pong
from multiprocessing import Process

HOST = '127.0.0.1'
PORT = 7779
KILL_WAIT_TIME = .5
TIMEOUT_DETECT_TIME = 6 # should be enough time for network exception to be
                        # thrown

def spawn_acceptor():
    '''
    Starts the TCP accept thread and spins as connections are brought up.
    '''
    Waldo.tcp_accept(Pong,HOST,PORT)
    while True:
        pass


def run_test():
    '''
    Tests Waldo's ability to detect a network failure between two endpoints
    mid-sequence, thrown a NetworkException, and catch that exception using
    a try-catch.
    
    Returns true if the exception is caught and handled, and false otherwise.
    '''
    acceptor_process = Process(target=spawn_acceptor,args=())
    Waldo.set_default_heartbeat_period(1)
    Waldo.set_default_partner_timeout(3)
    acceptor_process.start()
    time.sleep(KILL_WAIT_TIME)
    connector = Waldo.tcp_connect(Ping,HOST,PORT)
    time.sleep(KILL_WAIT_TIME)
    acceptor_process.terminate()
    time.sleep(TIMEOUT_DETECT_TIME)
    return connector.testNetworkException()

if __name__ == "__main__":
    run_test()
