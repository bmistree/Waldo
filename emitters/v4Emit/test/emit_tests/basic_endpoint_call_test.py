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
import _waldo_libs

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

    # check to ensure that one side can make an endpoint call to the
    # other side and receive a result.
    base_num = 20
    increment_num = 30
    if sideA.test_assigned_number(base_num,increment_num) != (base_num+increment_num):
        print '\nErr: with basic endpoint call'
        return False


    if sideA.check_value_type_argument(base_num,increment_num) != (base_num,base_num+increment_num):
        print '\nErr: incorrectly modified value type data'
        return False


    # Test to ensure that passing an external variable through an
    # endpoint call can change its value.
    original_num = 32
    ext_num = _waldo_libs.WaldoExtNumVariable(
        'garbage',sideA._host_uuid,False,original_num)
    sideA.assign_external_number(ext_num)
    new_num = 50
    if sideA.test_updated_val(new_num) != new_num:
        print '\nErr: external should have global change'
        return False


    # test that lists and maps are copied across endpoint calls
    original_list = ['eiof','ff','efeio']
    if sideA.hide_list(original_list) != len(original_list):
        print '\nErr: list passed by reference across endpoint call'
        return False
    
    return True


if __name__ == '__main__':
    run_test()
