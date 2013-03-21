#!/usr/bin/env python

from misc_tests_v4 import SingleSide


'''
Tests all the binary operators in the system.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)

    if not test_to_text(single_side):
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

    single_side.nested_list_append()
        
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
