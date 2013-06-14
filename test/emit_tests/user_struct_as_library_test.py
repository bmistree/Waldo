#!/usr/bin/env python

from user_struct_as_library_test_v4 import SingleSide

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


'''
Tests calls to function objects in structs
'''

def min_func(endpoint,num_list):
    return min(num_list)

def max_func(endpoint,num_list):
    return max(num_list)

def mod_func(endpoint,lhs,rhs):
    return lhs % rhs


def run_test():
    single_side = Waldo.no_partner_create(
        SingleSide, min_func,max_func,mod_func)

    # to mod between
    mod_tuples_list = [
        (6,2),
        (5,3),
        (100,3),
        (38, 7)]

    for mod_tuple in mod_tuples_list:
        if single_side.test_mod(*mod_tuple) != mod_func(None,*mod_tuple):
            print '\nErr with mod call'
            return False


    # to max
    max_min_list_list = [
        list(range(205,150, -1)),
        [-1, 52,1,0],
        [73, 13.25,100,239]]

    for max_min_list in max_min_list_list:
        if single_side.test_max(max_min_list) != max_func(None,max_min_list):
            print '\nErr with max call'
            return False

    # to min
    for max_min_list in max_min_list_list:
        if single_side.test_min(max_min_list) != min_func(None,max_min_list):
            print '\nErr with min call'
            return False

    return True


if __name__ == '__main__':
    run_test()
