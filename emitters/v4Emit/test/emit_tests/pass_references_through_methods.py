#!/usr/bin/env python

from pass_references_through_methods_v4 import SingleSide


'''
Checks passing reference types (maps, lists) through returns of
function calls.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)


    if not test_maps(single_side):
        return False

    if not test_lists(single_side):
        return False
    
    return True


def test_lists(single_side):
    expected_list = [5,7,9]
    
    #### Testing lists
    if expected_list != single_side.create_list_return_literal():
        print '\nErr: Incorrect map returned from create list literal'
        return False
    
    if expected_list != single_side.create_list_return_var():
        print '\nErr: Incorrect list returned from create map return var'
        return False


    #### Testing that Waldo code can use a list generated through a
    #### Waldo function call
    if expected_list[1] != single_side.get_element_from_list_call(1):
        print '\nErr: received incorrect val from list 1'
        return False
    
    if expected_list[2] != single_side.get_element_from_list_call(2):
        print '\nErr: received incorrect val from list 2'
        return False

    if expected_list[1] != single_side.get_element_from_list_literal_call(1):
        print '\nErr: received incorrect val from list literal 1'
        return False
    
    if expected_list[2] != single_side.get_element_from_list_literal_call(2):
        print '\nErr: received incorrect val from list literal 2'
        return False

    if expected_list[1] != single_side.get_element_from_list_var(1):
        print '\nErr: received incorrect val from list var 1'
        return False
    
    if expected_list[2] != single_side.get_element_from_list_var(2):
        print '\nErr: received incorrect val from list var 2'
        return False
    
    return True
        
    


def test_maps(single_side):
    expected_map = {
        1: 2,
        3: 4
        }

    #### Ensures that maps are being constructed properly and returned
    #### to non-Waldo code.
    if expected_map != single_side.create_map_return_literal():
        print '\nErr: Incorrect map returned from create map literal'
        return False
    
    if expected_map != single_side.create_map_return_var():
        print '\nErr: Incorrect map returned from create map return var'
        return False


    #### Testing that Waldo code can use a map generated through a
    #### Waldo function call
    if expected_map[1] != single_side.get_element_from_map_call(1):
        print '\nErr: received incorrect val from map 1'
        return False
    
    if expected_map[3] != single_side.get_element_from_map_call(3):
        print '\nErr: received incorrect val from map 2'
        return False

    if expected_map[1] != single_side.get_element_from_map_literal_call(1):
        print '\nErr: received incorrect val from map literal 1'
        return False
    
    if expected_map[3] != single_side.get_element_from_map_literal_call(3):
        print '\nErr: received incorrect val from map literal 2'
        return False

    if expected_map[1] != single_side.get_element_from_map_var(1):
        print '\nErr: received incorrect val from map var 1'
        return False
    
    if expected_map[3] != single_side.get_element_from_map_var(3):
        print '\nErr: received incorrect val from map var 2'
        return False
    
    return True




if __name__ == '__main__':
    run_test()
