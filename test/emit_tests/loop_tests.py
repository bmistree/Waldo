#!/usr/bin/env python

from loop_tests_v4 import SingleSide

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo



'''
Tests that range, while, for, break, and continue work correctly
'''

def run_test():
    single_side = Waldo.no_partner_create(SingleSide)

    if not test_range(single_side):
        return False

    if not test_while(single_side):
        return False

    if not test_for(single_side):
        return False

    if not test_break_continue(single_side):
        return False
    
    return True

def test_break_continue(single_side):

    if not single_side.test_break():
        '\nErr in break'
        return False
    
    if not single_side.test_continue():
        '\nErr in continue'
        return False
    
    return True

def test_for(single_side):

    # FOR RANGE TESTS
    NUM_FOR_RANGE_TESTS = 20
    for i in range(0,NUM_FOR_RANGE_TESTS):
        if i != single_side.range_for_test(i):
            print '\nErr in for range test'
            return False

    # EMPTY FOR TEST
    single_side.empty_for_test()

    # ITER FOR TEST
    NUM_FOR_LIST_ITER_TESTS = 20
    expected_str_list = ['a','b']
    for i in range(0,NUM_FOR_LIST_ITER_TESTS):
        expected_str_list.append('c')
        if expected_str_list != single_side.list_iter_for_test(expected_str_list):
            print '\nErr in list iter for test'
            return False

    # iter over map for test
    input_map = {
        'a': 5,
        'v': 3,
        'm': 31,
        'q': 35
        }
    expected_list = list(input_map.values()).sort()
    received_list = single_side.map_iter_for_test(input_map).sort()
    
    if expected_list != received_list:
        print '\nErr in iter for map test'
        return False
    

    # iter over nested list of numbers.  should contain the sum of
    # every number in lists.
    input_list = [ [1,5,6], [2,3,4], [10,11,2]]
    expected_num = reduce(
        lambda x,y:
            x + reduce(lambda a,b: a+b,y,0),
        input_list,
        0)
    if expected_num != single_side.nested_list_iter_test(input_list):
        print '\nErr iterating over nested list'
        return False

    # iter over nested map of map of numbers.  result should contain
    # the sum of every number in the maps
    input_map = {
        'a': {
            'b': 23,
            'c': 34,
            'd': 45
            },
        'e': {
            'f': 67,
            },
        'g': {},
        'h': {
            'i': 0
            }}
        
    expected_num = reduce (
        lambda x,y:
            x + reduce( lambda a,b: a+b, list(y.values()),0),
        list(input_map.values()),
        0)

    if single_side.nested_map_iter_test(input_map) != expected_num:
        print '\nErr with nested map sum'
        return False
    
    return True
    
        

def test_while(single_side):

    # should not have entered the while loop
    if single_side.test_while_less_than(1,1) != 0:
        print '\nWhile fail 1'
        return False
    
    # should not have entered the while loop
    if single_side.test_while_less_than(1,0) != 0:
        print '\nWhile fail 2'
        return False

    if single_side.test_while_less_than(1,5) != 4:
        print '\nWhile fail 3'
        return False
    
    if single_side.test_while_less_than(100,500) != 400:
        print '\nWhile fail 4'
        return False

    single_side.test_empty_while()

    return True


def test_range(single_side):

    # test ternary range, which includes increment
    if single_side.range_test(0,10,1) != list(range(0,10,1)):
        print '\nErr: range test 1'
        return False

    if single_side.range_test(20,10,1) != list(range(20,10,1)):
        print '\nErr: range test 2'
        return False

    if single_side.range_test(10,100,10) != list(range(10,100,10)):
        print '\nErr: range test 3'
        return False

    if single_side.range_test(10,1,-1) != list(range(10,1,-1)):
        print '\nErr: range test 4'
        return False

    # test binary range, default increment of 1
    if single_side.no_increment_range_test(0,10) != list(range(0,10)):
        print '\nErr: no inc range test 1'
        return False

    if single_side.no_increment_range_test(5,8) != list(range(5,8)):
        print '\nErr: no inc range test 2'
        return False

    if single_side.no_increment_range_test(8,5) != list(range(8,5)):
        print '\nErr: no inc range test 3'
        return False

    if single_side.no_increment_range_test(5,5) != list(range(5,5)):
        print '\nErr: no inc range test 4'
        return False
    
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
