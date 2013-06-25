#!/usr/bin/env python

from self_type_v4 import SelfTester
#from emitted import SelfTester

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

NUM = 42

def run_test():
    '''
    Returns true on success.
    '''
    firstEndpoint = Waldo.same_host_create(SelfTester)
    secondEndpoint = firstEndpoint.get_self()
    if firstEndpoint != secondEndpoint:
        return false
    elif secondEndpoint.test_input_output(NUM) != NUM:
        return false
    else:
        return true

if __name__ == "__main__":
    print 'Testing self type...\t\t\t'
    if run_test:
        print 'Success.\n'
    else:
        print 'Failure.\n'
