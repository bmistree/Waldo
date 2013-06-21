#!/usr/bin/env python

import os, sys, test_util
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import wVariables, util

host_uuid = util.generate_uuid()

'''
Waldo's semantics disallow sharing references between peered pieces of
data.

To test this, we create a map and put it inside of a peered list.  We
then make changes to the map and try to ensure that the changes are
not reflected in the map when accessed through the list.
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
    

    # first: test that if we delete b from el1_map that we can commit
    # still change b in peered_list's first element.  both should
    # commit.
    
    evt1,evt2 = create_two_events(dummy_endpoint)
    el1_map.get_val(evt1).del_key_called(evt1,'b')
    
    # for peered, we do not need the additional get_val after getting
    # val on key.  This is because we actually aren't holding onto a
    # reference to an internal map, but rather the internal map
    # itself.  For non-peered data, where we do not pass back
    # references from list, struct, and maps.  We pass back copies of
    # them.
    peered_list.get_val(evt2).get_val_on_key(evt2,0).get_val(evt2).write_val_on_key(evt2,'b',15)

    
    if not evt1.hold_can_commit():
        print '\nErr: should be able to hold commit 1\n'
        return False
    evt1.complete_commit()    
    if not evt2.hold_can_commit():
        print '\nErr: should be able to hold commit 2\n'
        return False
    evt2.complete_commit()

    
    # now check that the changes were actually applied: el1_map should
    # be of length 1 and peered_list's first element should have a b
    # value of 15.
    
    evt1,evt2 = create_two_events(dummy_endpoint)
    if el1_map.get_val(evt1).get_len(evt1) != 1:
        err_msg = '\nErr: should have gotten a length of 1 '
        err_msg += 'on map that we deleted from.\n'
        print err_msg
        return False

    if peered_list.get_val(evt2).get_val_on_key(evt2,0).get_val(evt2).get_val_on_key(evt2,'b') != 15:
        err_msg = '\nErr: should have gotten an update from '
        err_msg += 'previous commit.\n'
        print err_msg
        return False
        
    if not evt1.hold_can_commit():
        print '\nerr: should be able to commit\n'
        return False
    evt1.complete_commit()
    
    if not evt2.hold_can_commit():
        print '\nerr: should be able to commit 2 reads\n'
        return False
    evt2.complete_commit()
        

    # now want to ensure that *just* on the peered data we still
    # cannot perform reads and writes using separate events.
    evt1,evt2 = create_two_events(dummy_endpoint)

    # read
    peered_list.get_val(evt1).get_val_on_key(evt1,0).get_val(evt1).get_val_on_key(evt1,'b')
    # write
    peered_list.get_val(evt2).get_val_on_key(evt2,0).get_val(evt2).write_val_on_key(evt2,'b',22)

    if not evt2.hold_can_commit():
        err_msg = '\nerr: should be able to commit write\n'
        print err_msg
        return False
    evt2.complete_commit()

    
    if evt1.hold_can_commit():
        err_msg = '\nerr: should not be able to commit read after write.\n'
        print err_msg
        return False
    evt1.backout_commit()

    return True
    
        
if __name__ == '__main__':
    run_test()


