#!/usr/bin/env python
import os
import sys
import time

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from exception_nested_sequence_inner_v4 import InnerPing, InnerPong
from network_exception_nested_sequence_outer_v4 import OuterPing, OuterPong
from multiprocessing import Process

HOST = 'localhost'
PORT_INNER = 8788
PORT_OUTER = 8789
SLEEP_TIME = 1

def throw_func(endpoint):
    '''
    Throws an ApplicationException in Waldo.
    '''
    os.kill(os.getpid(),1)


def spawn_acceptor():
    '''
    Starts the TCP accept thread and spins as connections are brought up.
    '''
    Waldo.tcp_accept(InnerPong, HOST, PORT_INNER, throw_func)
    while True:
        pass

# Waldo TCP accept process
acceptor_proc = Process(target=spawn_acceptor, args=())

def run_test():
    '''
    Tests Waldo's capability of propagating a network exception back through
    a sequence. Here we have two pairs of endpoints: (a,b), (c,d). Endpoint a 
    begins a sequence with b, which makes and endpoint call to c, which 
    initiates a sequence with d. Endpoint d is in a separate process which is
    manually terminated mid-sequence, thus a network exception should be
    detected by c and propagated back to a.

    Returns true if the exception is propagated back to the root of the
    event and handled and false otherwise.
    '''
    global acceptor_proc
    Waldo.set_default_heartbeat_period(1)
    Waldo.set_default_partner_timeout(2)
    acceptor_proc.start()
    time.sleep(SLEEP_TIME) # make sure process is ready for tcp_connect
    inner_ping = Waldo.tcp_connect(InnerPing, HOST, PORT_INNER)
    Waldo.tcp_accept(OuterPong, HOST, PORT_OUTER, inner_ping)
    outer_ping = Waldo.tcp_connect(OuterPing, HOST, PORT_OUTER)
    result = outer_ping.testNestedSequencePropagation()
    acceptor_proc.terminate()
    return result

if __name__ == "__main__":
    print run_test()
