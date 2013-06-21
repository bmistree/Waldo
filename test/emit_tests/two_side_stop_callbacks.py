#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

from two_side_stop_v4 import SideA,SideB

SIDEA_HOST = '127.0.0.1'
SIDEA_PORT = 16991

sidea_wait_queue = Queue.Queue()

def sidea_connected(sidea_endpoint):
    sidea_wait_queue.put(sidea_endpoint)

sidea_stop_counter = 0
sideb_stop_counter = 0
def sidea_stop_listener():
    global sidea_stop_counter
    sidea_stop_counter += 1


def sideb_stop_listener_1():
    global sideb_stop_counter
    sideb_stop_counter += 1

def sideb_stop_listener_2():
    global sideb_stop_counter
    sideb_stop_counter += 2


def run_test():
    accept_stoppable = Waldo.tcp_accept(
        SideA, SIDEA_HOST, SIDEA_PORT,
        connected_callback=sidea_connected)
    
    sideb = Waldo.tcp_connect(
        SideB,SIDEA_HOST,SIDEA_PORT)

    sidea = sidea_wait_queue.get()

    sidea.add_stop_listener(sidea_stop_listener)
    sideb.add_stop_listener(sideb_stop_listener_1)
    sideb.add_stop_listener(sideb_stop_listener_2)
    listener_id = sideb.add_stop_listener(sideb_stop_listener_2)
    sideb.remove_stop_listener(listener_id)
    sideb.remove_stop_listener(listener_id)
    
    sidea.do_nothing()
    sideb.do_nothing()
    sidea.stop()
    time.sleep(1)

    if sidea_stop_counter != 1:
        return False
    
    if sideb_stop_counter != 3:
        return False

    return True

if __name__ == '__main__':
    run_test()
