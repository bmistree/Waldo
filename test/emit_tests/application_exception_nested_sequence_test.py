#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from application_exception_nested_sequence_inner_v4 import InnerPing, InnerPong
from application_exception_nested_sequence_outer_v4 import OuterPing, OuterPong

HOST = 'localhost'
PORT_INNER = 8777
PORT_OUTER = 8778

def run_test():
    Waldo.tcp_accept(InnerPong, HOST, PORT_INNER)
    inner_ping = Waldo.tcp_connect(InnerPing, HOST, PORT_INNER)
    Waldo.tcp_accept(OuterPong, HOST, PORT_OUTER, inner_ping)
    outer_ping = Waldo.tcp_connect(OuterPing, HOST, PORT_OUTER)
    return outer_ping.testNestedSequencePropagation()

if __name__ == "__main__":
    print run_test()
