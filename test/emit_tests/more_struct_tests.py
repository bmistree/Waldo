#!/usr/bin/env python

from more_struct_tests_v4 import SideA,SideB

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


def run_test():

    sideA, sideB = (
        Waldo.same_host_create(SideA).same_host_create(SideB))

    sideX, sideY=(
        Waldo.same_host_create(SideA).same_host_create(SideB))
    
    
    in_val = 320
    if sideA.get_struct_from_other_side(sideX,in_val) != in_val:
        print '\nErr: getting struct from endpoint call'
        return False

    gotten_val = sideA.get_partner_struct(in_val)
    if gotten_val != in_val:    
    # if sideA.get_partner_struct(in_val) != in_val:
        print '\nErr: getting struct from partner'
        print gotten_val
        print in_val
        print '\n\n'
        return False
        

    # test changes to input struct across sequences
    inc1 = 39
    inc2 = 5
    if sideA.input_struct_sequence(inc1,inc2) != (inc1 + inc2):
        print '\nErr: input struct sequence did not increment correctly'
        return False
    

    # test that can insert a struct into a map and access its fields
    # from within map
    expected_num = 390
    if sideA.test_struct_map('hello',expected_num) != expected_num:
        print '\nErr: structs in maps is broken'
        return False

    # test that can serialize maps of structs
    sideA.test_sequence_struct_map()
    
    return True

if __name__ == '__main__':
    run_test()
