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
    if container_var.get_val(active_event).get_len(active_event) != expected_val:
        print '\nIncorrect %s len' % err_string_msg
        return False

    return True

'''
Adds elements to maps.  Commits, the additions.  Then checks to ensure
that can do concurrent writes to different elements of same map.
'''
def run_test():
    
    endpoint = DummyEndpoint()
    init_map_val = {
        'a': 'hi',
        'b': 'hello'
        }
    map_var = LockedMapVariable(Waldo._host_uuid,False,{})

    ### load each container with elements
    load_event = endpoint._act_event_map.create_root_event()
    for map_index in init_map_val.keys():
        map_var.get_val(load_event).add_key(load_event,map_index,init_map_val[map_index])

    load_event.begin_first_phase_commit()
        
    
    ### Check that each can read initial value
    # concurrent map changes:
    map_change_event_1 = endpoint._act_event_map.create_root_event()
    map_change_event_2 = endpoint._act_event_map.create_root_event()

    a_val = 'test it'
    b_val = 'test other'
    map_var.get_val(map_change_event_1).set_val_on_key(map_change_event_1,'a',a_val)
    map_var.get_val(map_change_event_2).set_val_on_key(map_change_event_2,'b',b_val)
    
    # try to commit both events
    map_change_event_1.begin_first_phase_commit()
    map_change_event_2.begin_first_phase_commit()

    ### Check values
    map_read_event = endpoint._act_event_map.create_root_event()
    if a_val != map_var.get_val(map_read_event).get_val_on_key(map_read_event,'a'):
        print '\nDid not concurrently write a\n'
        return False
    if b_val != map_var.get_val(map_read_event).get_val_on_key(map_read_event,'b'):
        print '\nDid not concurrently write b\n'
        return False

    
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
