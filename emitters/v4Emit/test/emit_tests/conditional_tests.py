#!/usr/bin/env python

from conditional_tests_v4 import SingleSide


'''
Tests if, else, elseIf 
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)


    # basic if test
    if single_side.test_if(True,1,2) != 1:
        print '\nErr: error of conditional of if 1'
        return False

    if single_side.test_if(False,1,2) != 2:
        print '\nErr: error of conditional of if 2'
        return False

    # basic if, else, elseIf tests
    if single_side.test_else_if(
        True,1,
        True,-1,
        True,-1,
        True,-1,
        True,-1,
        True,-1,
        True,-1,
        -1,-1) != 1:

        print '\nErr of if condition of test else if'
        return False
    
    if single_side.test_else_if(
        False,-1,
        True,1,
        True,-1,
        True,-1,
        True,-1,
        True,-1,
        True,-1,
        -1,-1) != 1:

        print '\nErr of elseIf1 condition of test else if'
        return False
        

    if single_side.test_else_if(
        False,-1,
        False,-1,
        True,1,
        True,-1,
        True,-1,
        True,-1,
        True,-1,
        -1,-1) != 1:

        print '\nErr of elseIf2 condition of test else if'
        return False

    if single_side.test_else_if(
        False,-1,
        False,-1,
        False,-1,
        True,1,
        True,-1,
        True,-1,
        True,-1,
        -1,-1) != 1:

        print '\nErr of elseIf3 condition of test else if'
        return False

    if single_side.test_else_if(
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        True,1,
        True,-1,
        True,-1,
        -1,-1) != 1:

        print '\nErr of elseIf4 condition of test else if'
        return False
    
    if single_side.test_else_if(
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        True,1,
        True,-1,
        -1,-1) != 1:

        print '\nErr of elseIf5 condition of test else if'
        return False

    if single_side.test_else_if(
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        True,1,
        -1,-1) != 1:

        print '\nErr of elseIf6 condition of test else if'
        return False

    if single_side.test_else_if(
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        False,-1,
        1,-1) != 1:

        print '\nErr of elseIf7 condition of test else if'
        return False

    
    # test if else
    if single_side.test_if_else(True,1,-1,-1) != 1:
        print '\nErr of ifElse 1'
        return False

    if single_side.test_if_else(False,-1,1,-1) != 1:
        print '\nErr of ifElse 2'
        return False

    # test boolean logic
    # Public Function test_boolean_logic(
    #     TrueFalse a_or1, TrueFalse a_or2,TrueFalse b_and1,
    #     TrueFalse b_and2, Number return_if, Number return_else) returns Number
    # {
    #     if ((a_or1 or a_or2) and (b_and1 and b_and2))
    #     {
    #         return return_if;
    #     }
    #     return return_else;
    # }
    if single_side.test_boolean_logic(
        False, False, True, True, -1, 1) != 1:
        print '\nErr on test_boolean_logic1'
        return False
    
    if single_side.test_boolean_logic(
        False, True, True, True, 1, -1) != 1:
        print '\nErr on test_boolean_logic2'
        return False

    if single_side.test_boolean_logic(
        True, True, True, False, -1, 1) != 1:
        print '\nErr on test_boolean_logic3'
        return False


    # Test many statements if_else_if_else
    if single_side.many_statements_in_if_else_if_else(
        True,True,1,-1,-1,-1) != 21:
        print '\nErr on many if 1'
        return False
    
    if single_side.many_statements_in_if_else_if_else(
        False,True,-1,1,-1,-1) != 21:
        print '\nErr on many if 2'
        return False

    if single_side.many_statements_in_if_else_if_else(
        False,False,-1,-1,1,-1) != 21:
        print '\nErr on many if 3'
        return False
    
    return True



if __name__ == '__main__':
    run_test()
