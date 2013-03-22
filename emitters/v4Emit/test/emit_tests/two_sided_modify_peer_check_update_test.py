#!/usr/bin/env python

from two_sided_modify_peer_check_update_test_v4 import Modifier
from two_sided_modify_peer_check_update_test_v4 import DataReader

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
    
    modifier = Modifier(mod_host,conn_obj)
    data_reader = DataReader(data_reader_host,conn_obj)

    # check peered value is initialized properly
    if modifier.read_peered_num() != 22:
        print '\nErr: incorrect modifier initial val of peered num'
        return False
    
    if data_reader.read_peered_num() != 22:
        print '\nErr: incorrect data reader initial val of peered num'
        return False

    # check modifier can increment
    if modifier.increment_peered_num() != 23:
        print '\nErr: incorrect modifier return from peered num increment'
        return False

    # check modifier sees increment
    if modifier.read_peered_num() != 23:
        print '\nErr: incorrect modifier return from peered num read'
        return False

    # check data reader sees increment
    if data_reader.read_peered_num() != 23:
        print '\nErr: incorrect data reader return from peered num read'
        return False
    
    
    return True


if __name__ == '__main__':
    run_test()
