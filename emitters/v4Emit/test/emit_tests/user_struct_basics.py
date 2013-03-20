#!/usr/bin/env python

from user_struct_basics_v4 import SingleSide


'''
Tests that can declare and use user structs.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)

    num_to_assign = 30
    single_side.assign_num_to_number_struct(num_to_assign)
    if single_side.read_num_from_number_struct() != num_to_assign:
        print '\nErr: could not write user struct number'
        return False

    return True


if __name__ == '__main__':
    run_test()
