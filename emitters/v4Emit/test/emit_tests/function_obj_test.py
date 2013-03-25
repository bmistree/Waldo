#!/usr/bin/env python

from function_obj_test_v4 import SingleSide

import os,sys
lib_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    '..','lib')
sys.path.append(lib_dir)
import Waldo


'''
Tests function objects
'''

def text_identity(endpoint,input_txt):
    return input_txt

def text_len(endpoint,input_txt):
    return len(input_txt)

def list_sum(endpoint,input_list):
    return reduce(
        lambda x,y: x+y,
        input_list,
        0)

def no_return(endpoint):
    pass

def sum_three_args(endpoint, arg_a,arg_b,arg_c):
    return arg_a + arg_b + arg_c

def return_three_args(endpoint,arg_a,arg_b,arg_c):
    return arg_a, arg_b, arg_c

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    single_side = Waldo.no_partner_create(
        SingleSide, text_identity,text_len,list_sum,no_return,
        sum_three_args,return_three_args)


    test_strings_list = ['hello','wow','my','good','this is it']
    # test identity text call
    for string in test_strings_list:
        if not single_side.execute_identity_endpoint_func (string):
            print '\nErr in identity func call'
            return False

    # test len text call
    for string in test_strings_list:
        if not single_side.execute_len_endpoint_func (string):
            print '\nErr in len func call'
            return False


    test_nums_list = [
        list(range(0,13)),
        list(range(50,500,2)),
        [1.2,3.9,-1.3]]

    # test sum list call
    for num_list in test_nums_list:
        if not single_side.execute_sum_list_endpoint_func (num_list):
            print '\nErr in sum list func call'
            return False


    # execute no return
    single_side.execute_no_return_endpoint_func()

    # test multiple arguments
    mult_args_array = [
        (1,3,5),
        (38,10,1000),
        (-1.4,-50,10)
        ]
    for arg_tuple in mult_args_array:
        if not single_side.execute_sum_three_args_endpoint_func(*arg_tuple):
            print '\nErr: with multiple arguments to functions'
            return False

    # test multiple return arguments
    for arg_tuple in mult_args_array:
        if single_side.execute_return_three_args_endpoint_func(*arg_tuple) != arg_tuple:
            print '\nErr could not return tuple'
            return False
        
    return True



if __name__ == '__main__':
    run_test()
