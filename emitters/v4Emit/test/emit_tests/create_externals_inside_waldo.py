#!/usr/bin/env python

from create_externals_inside_waldo_v4 import SingleSide


import os,sys
lib_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    '..','lib')
sys.path.append(lib_dir)
import Waldo



'''
Tests creating externals within Waldo code
'''

def run_test():
    # for single side tests, these values do not really matter.
    internal_num = 35
    index_num = 31

    single_side = Waldo.no_partner_create(
        SingleSide,internal_num,index_num)

    
    if single_side.get_external_vals(index_num) != (internal_num,internal_num):
        print '\nErr: got an incorrect external val'
        return False


    internal_num = 22
    single_side.change_external_num(internal_num)

    if single_side.get_external_vals(index_num) != (internal_num,internal_num):
        print '\nErr: got an incorrect external val after changing'
        return False

    
    return True



if __name__ == '__main__':
    run_test()
