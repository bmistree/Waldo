#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib import Waldo
from waldo.lib.waldoLockedVariables import LockedMapVariable
from waldo.lib.waldoLockedVariables import LockedListVariable
from locked_test_util import DummyEndpoint

def check_len (active_event,container_var,err_string_msg,expected_val):
    if container_var.get_len(active_event) != expected_val:
        print '\nIncorrect %s len' % err_string_msg
        return False

    return True


'''
Creates two readers.  That each check length of a created map.  Both
should be able to commit
'''
def run_test():
    
    endpoint = DummyEndpoint()
    init_map_val = {}
    map_var = LockedMapVariable(Waldo._host_uuid,False,init_map_val)

    init_list_val = []
    list_var = LockedListVariable(Waldo._host_uuid,False,init_list_val)

    
    ### Check that each can read initial value
    read_event_1 = endpoint._act_event_map.create_root_event()
    read_event_2 = endpoint._act_event_map.create_root_event()


    if not check_len(read_event_1,map_var,'map',0):
        return False
    if not check_len(read_event_1,list_var,'list',0):
        return False
    
    if not check_len(read_event_2,map_var,'map',0):
        return False
    if not check_len(read_event_2,list_var,'list',0):
        return False
    
    # try to commit both events
    read_event_1.begin_first_phase_commit()
    read_event_2.begin_first_phase_commit()

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
