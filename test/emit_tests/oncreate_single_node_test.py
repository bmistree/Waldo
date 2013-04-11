#!/usr/bin/env python

from oncreate_single_node_test_v4 import SingleSide

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from lib import Waldo

'''
Tests that oncreate gets called on a single node.
'''

def run_test():
    # for single side tests, these values do not really matter.

    init_num = 50
    init_text = 'hello'
    init_list = [ [True,False], [False]]
    init_map = {
        2: 'wow',
        6: 'this'}
    
    host_uuid = 10
    single_side = Waldo.no_partner_create(
        SingleSide, 
        init_num,init_text,init_list,init_map)


    if (single_side.get_endpoint_values() !=
        (init_num,init_text,init_list,init_map)):
        print '\nErr when initializing'
        return False

    
    return True





if __name__ == '__main__':
    run_test()
