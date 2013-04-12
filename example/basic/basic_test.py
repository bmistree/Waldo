#!/usr/bin/env python

from basic_v4 import Requester, Incrementer
import os,sys

# set path to import Waldo lib
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)

# contains Waldo utilities
from lib import Waldo

INCREMENTER_HOST = '127.0.0.1'
INCREMENTER_PORT = 6929



def incrementer_connected(incrementer_endpoint):
    print 'Incrementer connected!'



def run():

    # listen on <INCREMENTER_HOST:INCREMENTER_PORT> for TCP
    # connections.  For each new connection, create an Incrementer.
    # Non-blocking.
    Waldo.tcp_accept(
        Incrementer, INCREMENTER_HOST, INCREMENTER_PORT,
        # the argument to Incrementer's onCreate
        55,
        # a callback that executes whenever a new incrementer is
        # created
        connected_callback=incrementer_connected )

    # connect to <INCREMENTER_HOST:INCREMENTER_PORT> and create a
    # requester object.  Blocks until connection is created.
    requester = Waldo.tcp_connect(
        Requester,INCREMENTER_HOST,INCREMENTER_PORT)

    
    num_incremented = requester.increment(5)
    print '\nFinal value of number: %s\n' % str(num_incremented)



if __name__ == '__main__':
    run()
