#!/usr/bin/env python

from two_sided_modify_peer_check_update_test_v4 import Modifier
from two_sided_modify_peer_check_update_test_v4 import DataReader

import sys,os,Queue
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from lib import Waldo

'''
Partner of two_sided_modify_peer_check_update_test, except uses a TCP
connection object instead.
'''

MODIFIER_HOST = '127.0.0.1'
MODIFIER_PORT = 6928


modifier_wait_queue = Queue.Queue()

def modifier_connected(modifier_endpoint):
    modifier_wait_queue.put(modifier_endpoint)


def run_test():
    accept_stoppable = Waldo.tcp_accept(
        Modifier, MODIFIER_HOST, MODIFIER_PORT,
        connected_callback=modifier_connected)
    
    data_reader = Waldo.tcp_connect(
        DataReader,MODIFIER_HOST,MODIFIER_PORT)

    modifier = modifier_wait_queue.get()
    
    # check peered value is initialized properly
    if modifier.read_peered_num() != 22:
        print '\nErr: incorrect modifier initial val of peered num'
        return False

    if data_reader.read_peered_num() != 22:
        print '\nErr: incorrect data reader initial val of peered num'
        return False

    # check modifier can increment
    if modifier.increment_peered_num() != 23:
        print '\nErr: incorrect modifier return from peered num increment'
        return False

    
    # check modifier sees increment
    if modifier.read_peered_num() != 23:
        print '\nErr: incorrect modifier return from peered num read'
        return False

    # check data reader sees increment
    if data_reader.read_peered_num() != 23:
        print '\nErr: incorrect data reader return from peered num read'
        return False

    accept_stoppable.stop()
    
    return True


if __name__ == '__main__':
    run_test()
