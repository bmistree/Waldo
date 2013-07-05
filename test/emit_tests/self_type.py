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
    firstEndpoint = Waldo.no_partner_create(SelfTester)
    secondEndpoint = firstEndpoint.get_self()
    if firstEndpoint != secondEndpoint:
        return False
    elif secondEndpoint.test_input_output(NUM) != NUM:
        return False
    else:
        return True

if __name__ == "__main__":
    print 'Testing self type...\t\t\t'
    if run_test():
        print 'Success.\n'
    else:
        print 'Failure.\n'
