#!/usr/bin/env python

from self_oncreate_list_v4 import SingleSide

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from lib import Waldo


'''
Tests all the binary operators in the system.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    wlist = Waldo._waldo_classes['WaldoListVariable']('some list',host_uuid)

    single_side = Waldo.no_partner_create(SingleSide, wlist)

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
