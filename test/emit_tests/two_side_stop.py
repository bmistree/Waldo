#!/usr/bin/env python
import os,sys, Queue
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

from two_side_stop_v4 import SideA,SideB

SIDEA_HOST = '127.0.0.1'
SIDEA_PORT = 6961

sidea_wait_queue = Queue.Queue()

def sidea_connected(sidea_endpoint):
    sidea_wait_queue.put(sidea_endpoint)


def run_test():
    accept_stoppable = Waldo.tcp_accept(
        SideA, SIDEA_HOST, SIDEA_PORT,
        connected_callback=sidea_connected)
    
    sideb = Waldo.tcp_connect(
        SideB,SIDEA_HOST,SIDEA_PORT)

    sidea = sidea_wait_queue.get()


    lkjs;
    
    single_side = Waldo.no_partner_create(SingleSide)
    single_side.do_nothing()
    single_side.stop()
    try:
        single_side.do_nothing()
    except Waldo.StoppedException as inst:
        return True

    return False

if __name__ == '__main__':
    run_test()
