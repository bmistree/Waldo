#!/usr/bin/env python

from more_struct_tests_v4 import SideA,SideB

import os,sys
lib_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    '..','lib')
sys.path.append(lib_dir)
import Waldo


def run_test():

    sideA, sideB = (
        Waldo.same_host_create(SideA).same_host_create(SideB))

    sideX, sideY=(
        Waldo.same_host_create(SideA).same_host_create(SideB))
    
    
    in_val = 320
    if sideA.get_struct_from_other_side(sideX,in_val) != in_val:
        print '\nErr: getting struct from endpoint call'
        return False

    if sideA.get_partner_struct(in_val) != in_val:
        print '\nErr: getting struct from partner'
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


    # test that can write over a map in a message sequence
    to_test = [
        {'a': {'c': 'd'}},
        {'m': { 'o': 'q'}}]

    for map_to_test in to_test:
        if sideA.test_write_over_map(map_to_test) != map_to_test:
            print '\nErr: got incorrect map value'
            return False
    
    
    # # test that can serialize maps of structs
    struct_index_name = 'a'
    to_test = [
        ('hi',3, 'm', 1),
        ('hi',3, 'n', 1),
        ('hoiwei',100, 'n', 1),
        ]
    for index1_to_insert, number1_to_insert, index2_to_insert, number2_to_insert in to_test:
        expected = { index1_to_insert: { struct_index_name: number1_to_insert},
                     index2_to_insert: { struct_index_name: number2_to_insert}}

        got_val = sideA.test_sequence_struct_map(
            index1_to_insert,number1_to_insert, index2_to_insert, number2_to_insert)

        import pdb
        pdb.set_trace()
        
        if (sideA.test_sequence_struct_map(
            index1_to_insert,number1_to_insert, index2_to_insert, number2_to_insert) !=
            expected):
            print '\nErr: got incorrect struct map from passing across sequence.'
            return False
    
    return True

if __name__ == '__main__':
    run_test()
