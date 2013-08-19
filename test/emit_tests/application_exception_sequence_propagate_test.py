#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from application_exception_sequence_propagate_test_v4 import Ping, Pong

HOST = '127.0.0.1'
PORT = 7979
SLEEP_TIME = .25

def run_test():
    '''
    Tests Waldo's ability to detect an application exception on the partner
    endpoint mid-sequence and propagate that exception back to the root endpoint
    for handling.
    
    Returns true if the exception is caught and handled, and false otherwise.
    '''
    Waldo.tcp_accept(Pong,HOST,PORT)
    connector = Waldo.tcp_connect(Ping,HOST,PORT)
    return connector.testPropagateException()

if __name__ == "__main__":
    print run_test()
