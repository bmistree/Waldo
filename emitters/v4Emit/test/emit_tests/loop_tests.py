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
