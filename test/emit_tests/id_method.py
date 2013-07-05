#!/usr/bin/env python

from id_method_v4 import IdTester, Manager
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
    manager = Waldo.no_partner_create(Manager)
    manager_id = manager.id()
    manager.add_endpoint(id_tester)
    if id != id_tester._uuid or manager_id != manager._uuid:
        return False
    elif id_tester.get_id() != id_tester.id() or manager.get_id() != manager.id():
        return False
    elif id != manager.get_managed_endpoint_id():
        return False
    else:
        return True
    
    
    

if __name__ == '__main__':
    print 'Testing id method...\t\t\t'
    if run_test():
        print 'Success.\n'
    else:
        print 'Failure.\n'
