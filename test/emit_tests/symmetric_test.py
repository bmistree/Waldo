#!/usr/bin/env python

from symmetric_test_v4 import SideA,SideB


import sys,os,Queue
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from lib import Waldo


'''
Test to ensure that 
'''

SIDEA_HOST = '127.0.0.1'
SIDEA_PORT = 6921


sidea_wait_queue = Queue.Queue()

def sidea_connected(sidea_endpoint):
    sidea_wait_queue.put(sidea_endpoint)


def run_test():
    original_sidea_num = 13
    original_sideb_num = 135.1
    
    accept_stoppable = Waldo.tcp_accept(
        SideA, SIDEA_HOST, SIDEA_PORT,original_sidea_num,
        connected_callback=sidea_connected)
    
    sideb = Waldo.tcp_connect(
        SideB,SIDEA_HOST,SIDEA_PORT,original_sideb_num)

    sidea = sidea_wait_queue.get()

    # check if each  initialized correctly
    if sidea.get_other_val() != original_sideb_num:
        print '\nErr: symmetric did not initialize correctly'
        return False
    if sideb.get_other_val() != original_sidea_num:
        print '\nErr: symmetric did not initialize correctly'
        return False
    
    
    sidea_num = 39
    sideb_num = 41
    # write endpoint number to each side
    sidea.set_other_val(sideb_num)
    sideb.set_other_val(sidea_num)

    if sidea.get_other_val() != sideb_num:
        print '\nErr: symmetric did not set other side correctly'
        return False
    if sideb.get_other_val() != sidea_num:
        print '\nErr: symmetric did not set other side correctly'
        return False
    
    
    accept_stoppable.stop()
    
    return True


if __name__ == '__main__':
    run_test()
