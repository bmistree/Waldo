#!/usr/bin/env python
from endpoint_as_library_test_v4 import SingleSide

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from lib import Waldo

    
def run_test():
    math_endpoint = Waldo.math_endpoint_lib()
    single_side = Waldo.no_partner_create(SingleSide, math_endpoint)

    # to mod between
    mod_tuples_list = [
        (6,2),
        (5,3),
        (100,3),
        (38, 7)]

    for mod_tuple in mod_tuples_list:
        lhs = mod_tuple[0]
        rhs = mod_tuple[1]
        if single_side.test_mod(lhs,rhs) != (lhs % rhs):
            print '\nErr with mod call'
            return False


    # to max
    max_min_list_list = [
        list(range(205,150, -1)),
        [-1, 52,1,0],
        [73, 13.25,100,239]]

    for max_min_list in max_min_list_list:
        if single_side.test_max(max_min_list) != max(max_min_list):
            print '\nErr with max call'
            return False

    # to min
    for max_min_list in max_min_list_list:
        if single_side.test_min(max_min_list) != min(max_min_list):
            print '\nErr with min call'
            return False

    return True


if __name__ == '__main__':
    run_test()
