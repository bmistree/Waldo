#!/usr/bin/env python

from sequence_plus_externals_tests_v4 import SideA
from sequence_plus_externals_tests_v4 import SideB
import _waldo_libs

# going through all this trouble to re-use test_util's
# DummyConnectionObj.
import sys,os
ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util
    

'''
   Tests coercing externals to value types when passing into sequence
   data and functions.
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

    original_num = 30
    ext_num = _waldo_libs.WaldoExtNumVariable(
        'garbage',sideA._host_uuid,False,original_num)


    sideA.load_ext_num(ext_num)


    # sequences + externals
    amt_to_increment = 6
    a,b = sideA.test_seq_arg(amt_to_increment)
    if a != (b + amt_to_increment):
        print '\nErr: incorrect numbers from sequence'
        return False
    
    
        
    return True


if __name__ == '__main__':
    run_test()
