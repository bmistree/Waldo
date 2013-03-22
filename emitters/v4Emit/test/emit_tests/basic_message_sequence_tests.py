#!/usr/bin/env python

from basic_message_sequence_tests_v4 import SideA
from basic_message_sequence_tests_v4 import SideB

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

    initial_val = 22
    # check peered value is initialized properly
    if sideA.read_peered_num() != initial_val:
        print '\nErr: incorrect initial val of peered num on SideA'
        return False
    
    if sideB.read_peered_num() != initial_val:
        print '\nErr: incorrect initial val of peered num on SideB'
        return False

    #### Testing that when send a 2-long sequence message, both sides update peered
    #### value
    
    NUM_BASIC_EXCHANGES = 20
    for i in range(0,NUM_BASIC_EXCHANGES):
        # when we initiate a basic sequence, peered number should end up
        # +2 of what it was before it started.
        expected_new_val = initial_val + (i+1)*2
        
        if sideA.basic_exchange_test() != expected_new_val:
            err_msg = '\nErr: incorrect value after basic message '
            err_msg += 'seq on peered data'
            print err_msg
            return False

        if sideB.read_peered_num() != expected_new_val:
            err_msg = '\nErr: B did not receive updated peered '
            err_msg += 'data from basic message seq'
            print err_msg
            return False

        
    #### Now testing a longer sequence message.  Also ends on where we started
    val_after_basics = expected_new_val
    NUM_EXTENDED_EXCHANGES = 20
    for i in range(0,NUM_EXTENDED_EXCHANGES):
        # when we initiate a basic sequence, peered number should end up
        # +2 of what it was before it started.
        expected_new_val = val_after_basics + (i+1)*28

        # gotten_val = sideA.extended_exchange_test()

        # import pdb
        # pdb.set_trace()
        if sideA.extended_exchange_test() != expected_new_val:
            err_msg = '\nErr: incorrect value after ext message '
            err_msg += 'seq on peered data'
            print err_msg
            return False

        if sideB.read_peered_num() != expected_new_val:
            err_msg = '\nErr: B did not receive updated peered '
            err_msg += 'data from ext message seq'
            print err_msg
            return False

        
    return True


if __name__ == '__main__':
    run_test()
