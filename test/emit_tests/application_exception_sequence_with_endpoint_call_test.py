#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from application_exception_sequence_with_endpoint_call_test_v4 import Ping, Pong

HOST = '127.0.0.1'
PORT = 7888

def run_test():
    '''
    Tests Waldo's ability to propagate an ApplicationException back through an
    endpoint call on the remote partner in a sequence. The exception should be
    passed back to the root endpoint which initiates the sequence.
    
    Returns true if the exception is caught and handled, and false otherwise.
    '''
    thrower = Waldo.no_partner_create(Pong,None)
    catcher_partner = Waldo.tcp_accept(Pong,HOST,PORT,thrower)
    catcher = Waldo.tcp_connect(Ping,HOST,PORT)
    return catcher.testExceptionPropagation()

if __name__ == "__main__":
    print run_test()
