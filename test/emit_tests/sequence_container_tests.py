#!/usr/bin/env python

from sequence_container_tests_v4 import A,B

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo



def run_test():
    sideA, sideB = (
        Waldo.same_host_create(A).same_host_create(B))

    index = 'hi'
    val = 30
    if sideA.map_test(index,val) != val:
        return False

    # val = 30
    # if sideA.struct_test(val) != val:
    #     return False    

    return True

if __name__ == '__main__':
    if run_test() is True:
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
        
        
    
