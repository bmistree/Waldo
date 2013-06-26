#!/usr/bin/env python

from id_method_v4 import IdTester
#from emitted import SelfTester

import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
sys.path.append(os.path.join('..','..',))

ID_LEN = 16

def run_test():
    id_tester = Waldo.no_partner_create(IdTester)
    id = id_tester.id()
    if id != id_tester._uuid:
        return False
    elif id_tester.get_id() != id_tester.id():
        return False
    else:
        return True
    

if __name__ == '__main__':
    print 'Testing id method...\t\t\t'
    if run_test():
        print 'Success.\n'
    else:
        print 'Failure.\n'
