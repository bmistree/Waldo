#!/usr/bin/env python

from external_reference_tests_v4 import SideA
from external_reference_tests_v4 import SideB

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


'''
Want to test that can put self endpoint into maps and lists and then
make endpoint calls on them.  See comments in Waldo source.
'''


def run_test():

    a_num = 3902
    a_index = 133

    b_num = 302
    b_index = 33

    side_a, side_b = (
        Waldo.same_host_create(SideA,a_num,a_index).same_host_create(SideB,b_num))

    list_of_endpoints, map_of_endpoints = side_a.get_self_holders()

    # load sideb into external list and map
    side_b.append_self_to_list(list_of_endpoints)
    side_b.append_self_to_map(b_index,map_of_endpoints)

    # make endpoint calls on all endpoints in the list (ie, sideA and
    # sideB) and test that their values are what should be expected
    # for sidea's and sideb's internal numbers
    endpoint_num_list = side_a.get_numbers_from_list()
    if len(endpoint_num_list) != 2:
        print '\nErr: incorrect number of numbers returned in endpoint list'
        return False

    if (endpoint_num_list[0] != a_num) or (endpoint_num_list[1] != b_num):
        print '\nErr: incorrect numbers returned in endpoint list'
        return False

    # make endpoint calls on all endpoints in the list (ie, sideA and
    # sideB) and test that their values are what should be expected
    # for sidea's and sideb's internal numbers
    endpoint_num_map = side_a.get_numbers_from_map()
    if len(endpoint_num_map) != 2:
        print '\nErr: incorrect number of numbers returned in endpoint map'
        return False

    if (a_index not in endpoint_num_map) or (b_index not in endpoint_num_map):
        print '\nErr: missing indices in endpoint number map'
        return False

    if (endpoint_num_map[a_index] != a_num) or (endpoint_num_map[b_index] != b_num):
        print '\nErr: incorrect values returned in endpoint map'
        return False
    
    return True


if __name__ == '__main__':
    run_test()
