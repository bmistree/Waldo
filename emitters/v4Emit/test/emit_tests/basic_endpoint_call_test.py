#!/usr/bin/env python

from basic_endpoint_call_test_v4 import SideA
from basic_endpoint_call_test_v4 import SideB

# going through all this trouble to re-use test_util's
# DummyConnectionObj.
import sys,os
ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util
    

'''
Tests that changes to a peered type on one side get updated to partner side.
'''

def run_test():
    conn_obj = test_util.DummyConnectionObj()
    # just must insure that modifier and data reader appear to be on
    # different hosts.
    mod_host = 10
    data_reader_host = mod_host + 1
    
    sideA = SideA(mod_host,conn_obj)
    sideB = SideB(data_reader_host,conn_obj)
    conn_obj.register_endpoint(sideA)
    conn_obj.register_endpoint(sideB)
    conn_obj.start()

    
    # assign endpoint into a
    sideA.assign_endpoint(sideB)


    base_num = 20
    increment_num = 30
    if sideA.test_assigned_number(base_num,increment_num) != (base_num+increment_num):
        print '\nErr: with basic endpoint call'
        return False


    if sideA.check_value_type_argument(base_num,increment_num) != (base_num,base_num+increment_num):
        print '\nErr: incorrectly modified value type data'
        return False

    
    return True


if __name__ == '__main__':
    run_test()
