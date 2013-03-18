#!/usr/bin/env python

from external_tests_v4 import SingleSide
import _waldo_libs

'''
Tests externals
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)


    if not test_ext_num(single_side):
        return False
    
    return True

def test_ext_num(single_side):

    original_num = 32
    
    ext_num = _waldo_libs.WaldoExtNumVariable(
        'garbage',single_side._host_uuid,False,original_num)

    single_side.input_ext_num(ext_num)
    map_ext_index = 3
    single_side.input_ext_num_to_map(ext_num,map_ext_index)

    NUM_INCREMENTS = 50
    for i in range(1,NUM_INCREMENTS):
        expected_num = original_num + i
        if expected_num != single_side.increment_ext_num():
            print '\nErr: in increment ext number'
            return False

        if expected_num != single_side.get_endpoint_ext_value():
            print '\nErr: getting value'
            return False

        if expected_num != single_side.get_endpoint_map_ext_value(map_ext_index):
            print '\nErr: external value was not mirrored on map'
            return False


    # test that can still get the original external back
    if ext_num.get_val(None) != single_side.get_endpoint_ext().get_val(None):
        print '\nErr: getting external back'
        return False

    
    return True




if __name__ == '__main__':
    run_test()
