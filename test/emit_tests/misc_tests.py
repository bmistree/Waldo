#!/usr/bin/env python

from misc_tests_v4 import SingleSide
import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


'''
Tests all the binary operators in the system.
'''

def run_test():
    single_side = Waldo.no_partner_create(SingleSide)    

    if not test_to_text(single_side):
        return False

    if not test_misc_list(single_side):
        return False

    if not test_nested_map(single_side):
        return False

    if not test_user_struct_returns(single_side):
        return False
    
    return True

def test_user_struct_returns(single_side):

    # can we return a single user struct at a time from waldo
    fields_to_test = [
        ('a','b'),
        ('m','n'),
        ('wowo', 'oo'),
        ]
    for fielda, fieldb in fields_to_test:
        user_struct = single_side.test_return_user_struct(fielda,fieldb)
        if ('fielda' not in user_struct) or ('fieldb' not in user_struct):
            print '\nErr: missing key for user struct'
            return False

        if (user_struct['fielda'] != fielda) or (user_struct['fieldb'] != fieldb):
            print '\nErr: incorrect value in user struct field'
            return False


    # can we return user structs nested in a map
    for fielda, fieldb in fields_to_test:
        # just going to reuse fields for indices of map that should return
        map_index = fielda

        expecting = { map_index: { 'fielda': fielda, 'fieldb': fieldb}}
        
        if single_side.test_return_user_struct_in_map(map_index,fielda,fieldb) != expecting:
            print '\nErr: got back incorrect nested user struct'
            return False
                
    return True


def test_nested_map(single_side):
    expected_num = 3
    if expected_num != single_side.nested_map('hello',expected_num):
        print '\nErr with nested map'
        return False

    # test can get a nested map returned from Waldo
    to_test_on = [
        {},
        {
            'a': {'b': 'c'},
            'd': {},
            'e': {'f' : 'g', 'h' : 'i'}
            }]
    for map_to_test_on in to_test_on:
        if map_to_test_on != single_side.test_return_nested_map(map_to_test_on):
            print '\nErr with returning nested map'
            return False
        
    
    return True

def test_misc_list(single_side):

    single_side.nested_list_append()

    # test remove
    to_test_on = [
        (['a','b','m','d','r','q'], 3),
        (['a','b','m','d','r','q'], 1),
        (['a','b','m','d','r','q'], 5)
        ]
    for to_test in to_test_on:
        list_to_test = to_test[0]
        index_to_test = to_test[1]
        returned_list = single_side.test_list_remove(list_to_test,index_to_test)
        del list_to_test[index_to_test]
        if returned_list != list_to_test:
            print '\nError with remove statement'
            return False
        
    # test insert
    to_test_on = [
        ([True,False,True,False,True,False], 3, True),
        ([True,False,False,False,True,True], 3, True),
        ([True,False,False,False,True,True], 0, False),
        ([True,False,False,False,True,True], 2, False),
        ([True,False,False,False,True,True], 5, False),
        ]
    for to_test in to_test_on:
        list_to_test = to_test[0]
        index_to_test = to_test[1]
        to_insert_to_test = to_test[2]
        returned_list = single_side.test_list_insert(
            list_to_test,index_to_test,to_insert_to_test)
        
        list_to_test.insert(index_to_test, to_insert_to_test)
        
        if returned_list != list_to_test:
            print '\nError with insert statement'
            return False
    
    return True
    

def test_to_text(single_side):

    # test number
    for i in range(0, 100):
        if single_side.to_text_number(i) != str(i):
            print '\nErr in number to str'
            return False
        
    # test string
    expected_str = 'bmaief'
    for i in range(0,100):
        expected_str += 'a'
        if single_side.to_text_text(expected_str) != expected_str:
            print '\nErr in text to str'
            return False
        
    # test true false
    for i in [True,False]:
        if single_side.to_text_true_false(i) != str(i):
            print '\nErr in tf to str'
            return False
        
    # maps
    # map_on = {
    #     1: 'two',
    #     3: 'fifty',
    #     385: 'thousand'}

    # print '\n\n'
    # print single_side.to_text_map(map_on)
    # print '\n\n'

    # nested_map_on = {
    #     35: {
    #         'hi': 30,
    #         'I': 3920
    #         }
    #     50: {},
    #     -32: {
    #         'b': 103,
    #         'm': 3
    #         }
    #     }
    # print '\n\n'
    # print single_side.to_text_nested_map(nested_map_on)
    # print '\n\n'

        
    # lists
    return True



if __name__ == '__main__':
    run_test()
