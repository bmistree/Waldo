#!/usr/bin/env python

from oncreate_single_node_test_v4 import SingleSide

import os,sys
ind_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    'ind_tests')
sys.path.append(ind_test_dir)
import test_util


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
    single_side = SingleSide(
        host_uuid,
        test_util.SingleEndpointConnectionObj(),
        init_num,init_text,init_list,init_map)


    if (single_side.get_endpoint_values() !=
        (init_num,init_text,init_list,init_map)):
        print '\nErr when initializing'
        return False

    
    return True





if __name__ == '__main__':
    run_test()
