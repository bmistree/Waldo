#!/usr/bin/env python
import os
import sys
import time

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from network_exception_test_propagate_endpoint_call_v4 import Ping, Pong
from network_exception_test_propagate_endpoint_call_catcher_v4 import Catcher
from multiprocessing import Process

HOST = '127.0.0.1'
PORT = 12345
SLEEP_TIME = 1

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
    Tests that Waldo can detect a network exception mid-sequence and propagate
    that exception back through an endpoint call.

    Returns true if the test passes and false otherwise.
    '''
    Waldo.set_default_heartbeat_period(1)
    Waldo.set_default_partner_timeout(2)
    acceptor_process.start()
    time.sleep(SLEEP_TIME)
    endpt = Waldo.tcp_connect(Ping, HOST, PORT)
    endpt.addTerminationFunction(signal_func)
    catcher = Waldo.no_partner_create(Catcher)
    catcher.addEndpoint(endpt)
    return catcher.testPropagateNetworkExceptionOnEndpointCall()

if __name__ == "__main__":
    print run_test()
