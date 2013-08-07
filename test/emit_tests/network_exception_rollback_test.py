#!/usr/bin/env python
import os
import sys
import time

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
#from network_exception_mid_sequence_test_v4 import Ping, Pong
from emitted import Ping, Pong
from multiprocessing import Process

HOST = '127.0.0.1'
PORT = 7781
SLEEP_TIME = .5
VALUE = 42

def spawn_acceptor():
    '''
    Starts the TCP accept thread and spins as connections are brought up.
    '''
    Waldo.tcp_accept(Pong,HOST,PORT)
    while True:
        pass

# Waldo TCP accept process
acceptor_process = Process(target=spawn_acceptor,args=())

def signal_func(endpoint):
    '''
    Python function which terminates the acceptor process
    '''
    global acceptor_process
    acceptor_process.terminate()

def run_test():
    '''
    Tests Waldo's ability to detect a network failure between two endpoints
    mid-sequence, thrown a NetworkException, and catch that exception using
    a try-catch.
    
    Returns true if the exception is caught and handled, and false otherwise.
    '''
    Waldo.set_default_heartbeat_period(1)
    Waldo.set_default_partner_timeout(4)
    acceptor_process.start()
    time.sleep(SLEEP_TIME)
    connector = Waldo.tcp_connect(Ping,HOST,PORT,signal_func)
    print connector.testNetworkExceptionRollback(VALUE)
    if connector.getValue() == VALUE:
        return True
    else:
        return False

if __name__ == "__main__":
    run_test()
