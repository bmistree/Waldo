#!/usr/bin/env python

from self_oncreate_list_v4 import SingleSide

import os,sys
ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util
import _waldo_libs

'''
Tests all the binary operators in the system.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    wlist = _waldo_libs.WaldoListVariable('some list',host_uuid)
    single_side = SingleSide(
        host_uuid,
        test_util.SingleEndpointConnectionObj(),
        wlist)

    internal_list = wlist.get_val(None)
    raw_internal_list = internal_list.val
    
    if len(raw_internal_list) != 1:
        print '\nErr: did not append self to list'
        return False

    if raw_internal_list[0] != single_side:
        print '\nErr: incorrect endpoint value appended to list'
        return False
    
    return True




if __name__ == '__main__':
    run_test()
