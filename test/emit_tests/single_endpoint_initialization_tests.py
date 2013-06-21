#!/usr/bin/env python

from single_endpoint_initialization_tests_v4 import SingleSide

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

'''
Tests that local variables and endpoint global variables get
initialized correctly.
'''

def run_test():
    single_side = Waldo.no_partner_create(SingleSide)
    
    expected_txt = 'a'
    expected_num = 30
    expected_tf = False
    expected_list = [2,4,6]
    expected_map = {
        True: 100,
        False: 93
        }
    expected_other_num = 30
    expected_other_list = [2,4,6]
    

    if (single_side.return_local_vars() !=
        (expected_txt,
         expected_num,
         expected_tf,
         expected_list,
         expected_map,
         expected_other_num,
         expected_other_list)):
        print '\nErr getting locally initialized'
        return False
    

    if (single_side.return_global_vars() !=
        (expected_txt,
         expected_num,
         expected_tf,
         expected_list,
         expected_map,
         expected_other_num,
         expected_other_list)):
        print '\nErr getting globally initialized'
        return False

    return True


if __name__ == '__main__':
    run_test()
