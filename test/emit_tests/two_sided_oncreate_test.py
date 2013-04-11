#!/usr/bin/env python

from two_sided_oncreate_test_v4 import SideA
from two_sided_oncreate_test_v4 import SideB

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from lib import Waldo

'''
Test that when have oncreate on two sides, 
'''

def run_test():

    new_peered_num = 30
    new_end_text = 'hoi'
    
    sideA, sideB = (
        Waldo.same_host_create(SideA,new_peered_num).same_host_create(SideB,new_end_text))

    
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
