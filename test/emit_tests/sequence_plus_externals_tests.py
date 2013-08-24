#!/usr/bin/env python

from sequence_plus_externals_tests_v4 import SideA
from sequence_plus_externals_tests_v4 import SideB


import sys,os
lib_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    '..')
sys.path.append(lib_dir)
from waldo.lib import Waldo

'''
Tests coercing externals to value types when passing into sequence
data and functions.
'''

def run_test():
    sideA, sideB = (
        Waldo.same_host_create(SideA).same_host_create(SideB))

    
    original_num = 30
    ext_num = Waldo._waldo_classes['WaldoExtNumVariable'](
        sideA._host_uuid,False,original_num)


    sideA.load_ext_num(ext_num)


    # sequences + externals
    amt_to_increment = 6
    a,b = sideA.test_seq_arg(amt_to_increment)
    if a != (b + amt_to_increment):
        print '\nErr: incorrect numbers from sequence'
        return False
    
    
        
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
