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
Adds elements to lists and maps.  Commits, then reads elements to
ensure that lists and maps hold correct values.
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
        map_var.get_val(load_event).add_key(load_event,map_index,init_map_val[map_index])

    for list_index in range(0,len(init_list_val)):
        list_var.get_val(load_event).append_val(load_event,init_list_val[list_index])
        
    load_event.begin_first_phase_commit()
        
    
    ### Check that each can read initial value
    read_event_1 = endpoint._act_event_map.create_root_event()
    read_event_2 = endpoint._act_event_map.create_root_event()


    if not check_len(read_event_1,map_var,'map',len(init_map_val)):
        return False
    if not check_len(read_event_1,list_var,'list',len(init_list_val)):
        return False
    
    if not check_len(read_event_2,map_var,'map',len(init_map_val)):
        return False
    if not check_len(read_event_2,list_var,'list',len(init_list_val)):
        return False
    
    # try to commit both events
    read_event_1.begin_first_phase_commit()
    read_event_2.begin_first_phase_commit()

    # now try to read each value from list and map
    read_element_event = endpoint._act_event_map.create_root_event()
    for list_val_index in range(0,len(init_list_val)):
        list_val = list_var.get_val(read_element_event).get_val_on_key(read_element_event,list_val_index)
        if list_val != init_list_val[list_val_index]:
            print 'Incorrect internal val in list'
            return False

    for map_val_index in init_map_val.keys():
        map_val = map_var.get_val(read_element_event).get_val_on_key(read_element_event,map_val_index)
        if map_val != init_map_val[map_val_index]:
            print 'Incorrect internal val in map'
            return False

    read_element_event.begin_first_phase_commit()
        
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
