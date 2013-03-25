#!/usr/bin/env python

from external_tests_v4 import SingleSide
import _waldo_libs

import os,sys
lib_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    '..','lib')
sys.path.append(lib_dir)
import Waldo


ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util


'''
Tests externals
'''

def run_test():
    single_side = Waldo.no_partner_create(SingleSide)

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


    # test that can assign into map index from function call
    map_ext_index_2 = 1
    single_side.test_assign_from_map_index(map_ext_index_2,ext_num)
    if ext_num.get_val(None).get_val(None) != single_side.get_endpoint_map_ext_value(map_ext_index_2):
        print '\nErr: could not assign external into a function call'
        return False

    # creating another external number.  using it to test whether can
    # assign after a function call
    ext_num2 = _waldo_libs.WaldoExtNumVariable(
        'garbage',single_side._host_uuid,False,original_num)
    single_side.test_assign_from_func_call(ext_num2)
    if single_side.get_endpoint_ext_value() != original_num:
        print '\nErr: did not overwrite previous with new value'

    # test to ensure overwriting one external's reference did not
    # change other externals' values.
    if ext_num.get_val(None).get_val(None) != single_side.get_endpoint_map_ext_value(map_ext_index_2):
        print '\nErr: could not assign external into a function call'
        return False


    # test extCopy can handle it when what assigning to is a function call
    expected_num = 58
    if single_side.test_ext_copy_single_function_call(expected_num) != expected_num:
        print '\nErr: could not copy into single function call'
        return False

    
    # testing that extCopy can handle indexing into function calls
    amt_to_add = 3
    expected_num = amt_to_add + single_side.get_endpoint_map_ext_value(
        map_ext_index_2)
    
    if single_side.test_ext_copy_dual_function_call(map_ext_index_2,amt_to_add) != expected_num:
        print '\nErr: extcopy method call failure'
        return False


    # test that can ext copy into a non-function element call of map
    expected_num = 50
    single_side.test_ext_copy_map(map_ext_index_2,expected_num)
    if single_side.get_endpoint_map_ext_value(map_ext_index_2) != expected_num:
        print '\nErr: could not copy into indexed structure'
        return False

    
    
    return True




if __name__ == '__main__':
    run_test()
