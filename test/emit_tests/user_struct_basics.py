#!/usr/bin/env python

from user_struct_basics_v4 import SingleSide

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
    
'''
Tests that can declare and use user structs.
'''

def run_test():
    single_side = Waldo.no_partner_create(SingleSide)

    num_to_assign = 30
    single_side.assign_num_to_number_struct(num_to_assign)
    if single_side.read_num_from_number_struct() != num_to_assign:
        print '\nErr: could not write user struct number'
        return False


    # tests nesting user structs
    outer_nested_num = 52
    inner_nested_num = 31
    single_side.assign_num_to_nested_struct(
        outer_nested_num,inner_nested_num)
    if single_side.get_outer_and_inner_nested_nums() != (outer_nested_num,inner_nested_num):
        print '\nErr with nested user structs'
        return False

    # tests passing struct through argument to method
    new_num = 1
    if single_side.get_endpoint_nested_struct_num(new_num) != new_num:
        print '\nError passing structs through as method args'
        return False
    
    return True


if __name__ == '__main__':
    run_test()
