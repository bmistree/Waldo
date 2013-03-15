#!/usr/bin/env python

from sequence_local_data_tests_v4 import SideA
from sequence_local_data_tests_v4 import SideB

# going through all this trouble to re-use test_util's
# DummyConnectionObj.
import sys,os
ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util
    

'''
Tests that arguments to sequences get put into sequence local data.
Checks that these arguments get put into sequence global data space.
And can be accessed from outside.  Also checks returns.
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

    initial_num = 22
    initial_text = 'a'
    initial_tf = True


    # check that peereds are initialized properly on both ends
    if sideA.read_peered_value_types() != (initial_num,initial_text,initial_tf):
        print '\nErr: incorrect initial val of peered on SideA'
        return False

    if sideB.read_peered_value_types() != (initial_num,initial_text,initial_tf):    
        print '\nErr: incorrect initial val of peered on SideB'
        return False

    #### Testing that when send a 2-long sequence message, both sides
    #### can read peered args.
    
    NUM_ARGUMENTS_CHECK_EXCHANGE = 20
    expected_new_text = initial_text
    expected_new_num = initial_num
    expected_tf = initial_tf
    for i in range(0,NUM_ARGUMENTS_CHECK_EXCHANGE):
        # the values that we expect to be returned
        expected_new_num += i
        expected_new_text += 'b'
        expected_tf = ((i % 2) == 0)
        
        if sideA.arguments_check(i,'b',expected_tf) != (expected_new_num,expected_new_text,expected_tf):
            err_msg = '\nErr: incorrect value types after argument '
            err_msg += 'check message seq'
            print err_msg
            return False

        if sideB.read_peered_value_types() != (expected_new_num,expected_new_text,expected_tf):
            err_msg = '\nErr: B has incorrect value types after argument '
            err_msg += 'check message seq'
            print err_msg
            return False

    #### Testing that can return values from sequence
    NUM_RETURNS_CHECK_EXCHANGE = 20
    for i in range(0,NUM_RETURNS_CHECK_EXCHANGE):
        expected_returned_num = 55
        expected_returned_text = 'sideA';
        expected_returned_tf = True

        if sideA.returns_check() != (expected_returned_num,expected_returned_text,expected_returned_tf):
            err_msg = '\nErr: A got incorrect returns while '
            err_msg += 'in returns check.'
            print err_msg
            return False


    #### Testing that can declare and manipulate sequence local
    #### data not in arguments or return nodes
    expecting_seq_local_num = 62
    expecting_seq_local_text = 'wowwow'

    if (expecting_seq_local_num, expecting_seq_local_text) != sideA.non_arg_return_seq_local_data_check():
        err_msg = '\nErr: A could not declare and manipulate '
        err_msg += 'additional sequence local data.'
        print err_msg
        return False

    #### Test to ensure that sequence local data do not affect 
    if not sideA.arguments_check_references():
        err_msg = '\nErr: incorrect behavior for references'
        print err_msg
        return False
    
    return True


if __name__ == '__main__':
    run_test()
