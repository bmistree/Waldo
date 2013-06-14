#!/usr/bin/env python

import os, sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import wVariables, waldoExecutingEvent, util
import test_util
host_uuid = util.generate_uuid()

'''
When we return Waldo data to non-Waldo code, we need to unwrap it into
Python code.  This test checks to ensure that we unrwap into Python
correctly.
'''


def create_two_events(dummy_endpoint):
    evt1 = dummy_endpoint._act_event_map.create_root_event()
    evt2 = dummy_endpoint._act_event_map.create_root_event()
    return evt1,evt2

def create_map(dummy_endpoint,to_populate_with):
    '''
    @param {map} to_populate_with --- Each element gets inserted into
    the map that we return.
    '''
    new_map = wVariables.WaldoMapVariable('some map',host_uuid)
    evt1,evt2 = create_two_events(dummy_endpoint)
    for key in to_populate_with:
        element = to_populate_with[key]
        new_map.get_val(evt1).add_key(evt1,key,element)

    evt1.hold_can_commit()
    evt1.complete_commit()

    return new_map
        
def create_peered_list(dummy_endpoint,to_populate_with):
    '''
    @param {list} to_populate_with --- Runs through the entire list
    appending them to a peered Waldo list that this returns.
    '''
    new_list = wVariables.WaldoListVariable('some list',host_uuid,True)
    evt1,evt2 = create_two_events(dummy_endpoint)
    for element in to_populate_with:
        new_list.get_val(evt1).append_val(evt1,element)

    evt1.hold_can_commit()
    evt1.complete_commit()
    return new_list
    


def run_test():
    dummy_endpoint = test_util.DummyEndpoint(
        test_util.SingleEndpointConnectionObj(),host_uuid)

    map_vals = {
        'a': 1,
        'b': 2        
        }
    el1_map = create_map(dummy_endpoint,map_vals)
    peered_list = create_peered_list(dummy_endpoint,[el1_map])

    # try to de-waldoify the peered list... check that each element
    # turns into a separate python map.
    evt1, evt2 = create_two_events(dummy_endpoint)
    de_waldoified = waldoExecutingEvent.de_waldoify(peered_list,evt1)

    if ((len(de_waldoified) != 1) or (de_waldoified[0]['a'] != 1) or
        (de_waldoified[0]['b'] != 2)):
        print '\nIncorrect value after dewaldoifying nested list map'
        return False

    new_number = wVariables.WaldoNumVariable(
        'some var',host_uuid,False,6)
    de_waldoified = waldoExecutingEvent.de_waldoify(new_number,evt2)
    if de_waldoified != 6:
        print '\nIncorrect value after dewaldoifying number'
        print de_waldoified
        return False


    new_map = wVariables.WaldoMapVariable(
        'some var',host_uuid,False,map_vals)
    de_waldoified = waldoExecutingEvent.de_waldoify(new_map,evt2)
    if ((de_waldoified['a'] != 1) or (de_waldoified['b'] != 2)):
        print '\nIncorrect value after dewaldoifying plain map'
        return False
    

    return True
        
if __name__ == '__main__':
    run_test()


