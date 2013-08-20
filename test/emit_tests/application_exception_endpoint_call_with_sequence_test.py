#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from application_exception_endpoint_call_with_sequence_test_v4 import Ping, Pong
from application_exception_endpoint_call_with_sequence_test_catcher_v4 import Catcher

HOST = '127.0.0.1'
PORT = 8001

def run_test():
    '''
    Tests Waldo's ability to detect an application exception on the partner
    endpoint mid-sequence and propagate that exception back to the root endpoint
    for handling.
    
    Returns true if the exception is caught and handled, and false otherwise.
    '''
    Waldo.tcp_accept(Pong,HOST,PORT)
    connector = Waldo.tcp_connect(Ping,HOST,PORT)
    catcher = Waldo.no_partner_create(Catcher)
    catcher.addEndpoint(connector)
    return catcher.testCatchApplicationExceptionFromSequence()

if __name__ == "__main__":
    print run_test()
