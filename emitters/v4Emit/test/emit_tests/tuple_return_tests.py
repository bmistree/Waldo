#!/usr/bin/env python

from tuple_return_tests_v4 import SingleSide


'''
Tests all the binary operators in the system.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)


    if (1,2,3) != single_side.return_static_nums():
        print '\nErr getting static numbers'
        return False

    if (1,2,3) != single_side.return_func_call_nums():
        print '\nErr getting func call numbers'
        return False

    if ('a','b') != single_side.return_variable_texts():
        print '\nErr getting variable texts'
        return False
    
    if ('a','b') != single_side.return_func_call_variable_texts():
        print '\nErr getting func call variable texts'
        return False

    if ('a','b','c') != single_side.return_extended_texts():
        print '\nErr getting extended texts'
        return False
    
    return True




if __name__ == '__main__':
    run_test()
