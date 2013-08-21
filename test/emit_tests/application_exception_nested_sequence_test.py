#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from exception_nested_sequence_inner_v4 import InnerPing, InnerPong
from exception_nested_sequence_outer_v4 import OuterPing, OuterPong

HOST = 'localhost'
PORT_INNER = 8777
PORT_OUTER = 8778

def throw_func():
    '''
    Throws an ApplicationException in Waldo.
    '''
    1 / 0

def run_test():
    '''
    Tests Waldo's capability of propagating an exception back through nested
    sequences. Here we have two pairs of endpoints: (a,b), (c,d). Endpoint a 
    begins a sequence with b, which makes and endpoint call to c, which 
    initiates a sequence with d, which raises an exception.

    Returns true if the exception is propagated back to the root of the
    event and handled and false otherwise.
    '''
    Waldo.tcp_accept(InnerPong, HOST, PORT_INNER, throw_func)
    inner_ping = Waldo.tcp_connect(InnerPing, HOST, PORT_INNER)
    Waldo.tcp_accept(OuterPong, HOST, PORT_OUTER, inner_ping)
    outer_ping = Waldo.tcp_connect(OuterPing, HOST, PORT_OUTER)
    return outer_ping.testNestedSequencePropagation()

if __name__ == "__main__":
    print run_test()
