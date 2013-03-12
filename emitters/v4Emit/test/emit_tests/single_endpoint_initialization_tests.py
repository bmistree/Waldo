#!/usr/bin/env python

from single_endpoint_initialization_tests_v4 import SingleSide


'''
Tests that local variables and endpoint global variables get
initialized correctly.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)

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
