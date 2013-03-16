#!/usr/bin/env python

from loop_tests_v4 import SingleSide

'''
Tests that range, while, for, break, and continue work correctly
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)

    if not test_range(single_side):
        return False

    if not test_while(single_side):
        return False

    if not test_for(single_side):
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
    run_test()