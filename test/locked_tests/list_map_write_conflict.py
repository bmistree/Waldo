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
Load data into a map and a list...
Creates two readers.  That each check length of a created map.  Both
should be able to commit
'''
def run_test():
    
    endpoint = DummyEndpoint()
    init_map_val = {
        'a': 'hi',
        'b': 'hello'
        }
    map_var = LockedMapVariable(Waldo._host_uuid,False,{})

    init_list_val = [1,3,3,4,5]
    list_var = LockedListVariable(Waldo._host_uuid,False,[])

    ### load each container with elements
    load_event = endpoint._act_event_map.create_root_event()
    for map_index in init_map_val.keys():
        map_var.add_key(load_event,map_index,init_map_val[map_index])

    for list_index in range(0,len(init_list_val)):
        list_var.append_val(load_event,init_list_val[list_index])
        
    load_event.begin_first_phase_commit()
        

    ### create conflicting events: both try to write
    older_event,younger_event = endpoint.create_older_and_younger_root_events()

    should_commit = 57
    should_not_commit = should_commit + 1
    list_var.append_val(younger_event,should_not_commit)
    list_var.append_val(older_event,should_commit)

    older_event.begin_first_phase_commit()

    read_event = endpoint._act_event_map.create_root_event()
    if list_var.get_len(read_event) != (len(init_list_val) + 1):
        print 'Error did not commit anything'
        return False

    if list_var.get_val_on_key(read_event,len(init_list_val)) != should_commit:
        print 'Error did not commit correct value'
        return False
    
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
