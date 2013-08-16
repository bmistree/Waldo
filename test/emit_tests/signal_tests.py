#!/usr/bin/env python

from signal_tests_v4 import SideA,SideB

import os,sys,Queue,time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


num_queue = Queue.Queue()
def num_func(endpoint, num):
    num_queue.put(num)


def run_test():

    sideA, sideB = (
        Waldo.same_host_create(SideA,num_func).same_host_create(SideB,num_func))

    for i in range(0,20):
        sideA.run_signal(i)
        sideA.service_signal()
        time.sleep(.1)
        sideB.service_signal()
        time.sleep(.1)

        try:
            for j in range(0,2):
                read_num = num_queue.get_nowait()
                if (read_num != i) and (read_num != (i+1)):
                    print '\nUnexpected num read from queue\n'
                    return False
                
        except Queue.Empty:
            print '\nNever received signal to execute\n'
            return False

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
