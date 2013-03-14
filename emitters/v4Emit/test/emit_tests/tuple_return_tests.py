#!/usr/bin/env python

from tuple_return_tests_v4 import SingleSide


'''
Tests that can receive tuple return types from Waldo code
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


    
    for i in range(1,15):
        if (i,i) != single_side.return_tuple_endpoint_global():
            print '\nErr: incorrect tuple value of mutated state'
            return False

    for j in range(i+1,i+15):
        if (j,j,0) != single_side.wrapped_tuple():
            print '\nErr: incorrect tuple value of wrapped mutated state'
            return False
        
        
    return True


if __name__ == '__main__':
    run_test()
