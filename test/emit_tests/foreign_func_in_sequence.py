#!/usr/bin/env python

from foreign_func_in_sequence_v4 import Pt1
from foreign_func_in_sequence_v4 import Pt2
import time
import sys
import os
import Queue

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

PORT = 5929
HOST = '127.0.0.1'

pt2_wait_queue = Queue.Queue()

def pt2_connected(pt2_endpoint):
    pt2_wait_queue.put(pt2_endpoint)

list_to_return = ['hello', 'hi']
    
#This function creates a simple list with two arguments. This as a
#foreign function causes the program to crash.
def createList(endpoint):
    return list_to_return

        
def run_test():
    Waldo.tcp_accept(Pt2, HOST, PORT, connected_callback=pt2_connected)
    pt1 = Waldo.tcp_connect(Pt1, HOST, PORT,createList);

    pt2 = pt2_wait_queue.get()
    returned_list = pt1.start_seq()
    time.sleep(1)
    list_to_return.append('wo')
    if returned_list != list_to_return:
        return False

    return True

        
if __name__ == '__main__':
    if run_test():
        print '\nSuccess\n'
    else:
        print '\nFailed\n'
    
