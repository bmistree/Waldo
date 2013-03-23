#!/usr/bin/env python

from two_sided_oncreate_test_v4 import SideA
from two_sided_oncreate_test_v4 import SideB

import threading

# going through all this trouble to re-use test_util's
# DummyConnectionObj.
import sys,os
ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util


conn_obj = test_util.DummyConnectionObj()
# just must insure that modifier and data reader appear to be on
# different hosts.
side_a_host = 10
side_b_host = side_a_host + 1


new_peered_num = 30
new_end_text = 'hoi'


# each of these are in separate threads so that both oncreates can
# run.
sideA = None
sideB = None
class CreateSideA(threading.Thread):
    def run(self):
        global sideA
        sideA = SideA(side_a_host,conn_obj,new_peered_num)
        
class CreateSideB(threading.Thread):
    def run(self):
        global sideB
        sideB = SideB(side_b_host,conn_obj,new_end_text)


'''
Test that when have oncreate on two sides, 
'''

def run_test():

    create_a = CreateSideA()
    create_b = CreateSideB()

    create_a.start()
    create_b.start()

    create_a.join()
    create_b.join()

    if sideB.read_peered_num() != new_peered_num:
        print '\nErr: B has incorrect peered number'
        return False
        
    if sideA.read_peered_num() != new_peered_num:
        print '\nErr: A has incorrect peered number'
        return False
        
    if sideA.read_b_text() != new_end_text:
        print '\nErr: A read incorrect text from B'
        return False

    return True


if __name__ == '__main__':
    run_test()
