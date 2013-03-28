#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('../../lib/'))

import wVariables
import time
import waldoNetworkSerializer
import util
import test_util

class SingleSide(test_util.DummyEndpoint):
    def __init__(self):
        test_util.DummyEndpoint.__init__(
            self,test_util.SingleEndpointConnectionObj())
        # both sides start at 1
        self.map = wVariables.WaldoMapVariable('some map',self._host_uuid,True)

    def new_event(self):
        return self._act_event_map.create_root_event()

    
def create_waldo_list(single_side_obj,to_put_inside,evt=None):
    wlist = wVariables.WaldoListVariable(
        'some list',single_side_obj._host_uuid,False)

    if evt == None:
        evt = single_side_obj.new_event()
    
    for item in to_put_inside:
        wlist.get_val(evt).append_val(evt,item)

    return wlist,evt
    

def run_test():
    lhs = SingleSide()
    rhs = SingleSide()

    # lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()

    internal_list1,evt = create_waldo_list(lhs,[1,2,3])
    internal_list2,evt = create_waldo_list(lhs,[4,5,6],evt)
    internal_list3,evt = create_waldo_list(lhs,[7,8,9],evt)
    
    lhs.map.get_val(evt).add_key(evt,1,internal_list1)
    lhs.map.get_val(evt).add_key(evt,2,internal_list2)
    lhs.map.get_val(evt).add_key(evt,1,internal_list3)
    # should produce:
    #  { 1: [7,8,9], 2: [4,5,6] }
    
    serializabled = lhs.map.serializable_var_tuple_for_network(
        'some_name',evt)

    
    waldoNetworkSerializer.deserialize_peered_object_into_variable(
        rhs._host_uuid,serializabled,rhs_event,rhs.map)

    
    if not evt.hold_can_commit():
        print '\nError: should be able to commit lhs.\n'
        return False
    evt.complete_commit()


    if not rhs_event.hold_can_commit():
        print '\nError: should be able to commit rhs.\n'
        return False
    rhs_event.complete_commit()


    # now check that cannot do operations in parallel that affect each
    # other. lhs_event will read all values in the map (and ensure
    # that they were set correctly from above).  It also sets one
    # value.  "concurrently" rhs_event1 will delete a value from its
    # map.  similarly, rhs_event2 will try to apply the change made
    # from lhs_event.  Should either be able to commit
    # {lhs_event,rhs_event2} or {rhs_event1}, but not both sets.


    lhs_event = lhs.new_event()
    rhs_event1 = rhs.new_event()
    rhs_event2 = rhs.new_event()

    
    if lhs.map.get_val(lhs_event).get_val_on_key(lhs_event,1).get_val(lhs_event).get_val_on_key(lhs_event,0) != 7:
        print '\nErr: did not get change from previous commit.\n'
        return False
    if lhs.map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_val_on_key(lhs_event,0) != 4:
        print '\nErr: did not get change from previous commit 2.\n'
        return False

    lhs.map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).write_val_on_key(lhs_event,0,20)
    
    serializabled = lhs.map.serializable_var_tuple_for_network(
        'some_name',lhs_event)

    waldoNetworkSerializer.deserialize_peered_object_into_variable(
        rhs._host_uuid,serializabled,rhs_event2,rhs.map)
    
    rhs.map.get_val(rhs_event1).del_key_called(rhs_event1,1)
    

    if not lhs_event.hold_can_commit():
        print '\nError: should be able to commit lhs\'s reads+single write.\n'
        return False
    lhs_event.complete_commit()

    if not rhs_event2.hold_can_commit():
        print '\nError: should be able to commit rhs\'s read+single write update.\n'
        return False
    rhs_event2.complete_commit()

    if rhs_event1.hold_can_commit():
        print '\nError rhs_evt1 and rhs_evt2 should conflict.\n'
        return False
    rhs_event1.backout_commit()
        

    # now check that can do operations in parallel that do not affect
    # each other. lhs_event sets one value.  "concurrently" rhs_event1
    # deletes a different value from its map.  rhs_event2 will try to
    # apply the change made from lhs_event.  Should either be able to
    # commit all events.  lhs_event2 will try to commit the change
    # made by rhs_event1

    lhs_event1 = lhs.new_event()
    lhs_event2 = lhs.new_event()
    rhs_event1 = rhs.new_event()
    rhs_event2 = rhs.new_event()


    lhs.map.get_val(lhs_event1).get_val_on_key(lhs_event1,1).get_val(lhs_event1).write_val_on_key(lhs_event1,2,66)
    
    rhs.map.get_val(rhs_event1).get_val_on_key(rhs_event1,2).get_val(rhs_event1).del_key_called(rhs_event1,2)
    
    serializabled = lhs.map.serializable_var_tuple_for_network(
        'some_name',lhs_event1)

    waldoNetworkSerializer.deserialize_peered_object_into_variable(
        rhs._host_uuid,serializabled,rhs_event2,rhs.map)


    serializabled = rhs.map.serializable_var_tuple_for_network(
        'some_name',rhs_event1)

    waldoNetworkSerializer.deserialize_peered_object_into_variable(
        lhs._host_uuid,serializabled,lhs_event2,lhs.map)
    

    if not lhs_event1.hold_can_commit():
        print '\nError: should be able to commit lhs\'s write.\n'
        return False
    lhs_event1.complete_commit()

    if not rhs_event1.hold_can_commit():
        print '\nError: should be able to commit rhs\'s delete.\n'
        return False
    rhs_event1.complete_commit()

    if not rhs_event2.hold_can_commit():
        print '\nError: rhs_evt1 and rhs_evt2 should be able to commit in parallel.\n'
        return False
    rhs_event2.complete_commit()

    if not lhs_event2.hold_can_commit():
        print '\nError: should be able to commit the rhs change on lhs2.\n'
        return False
    lhs_event2.complete_commit()
    
    
    # check to ensure that both sides saw the changes from above
    lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()
    
    if lhs.map.get_val(lhs_event).get_val_on_key(lhs_event,1).get_val(lhs_event).get_val_on_key(lhs_event,2) != 66:
        print '\nError: lhs_event should have seen updated value of 66.\n'
        return False
    if lhs.map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_len(lhs_event) != 2:
        print '\nError: lhs_event should know that it contains a list of length 2.\n'
        return False    

    if rhs.map.get_val(rhs_event).get_val_on_key(rhs_event,1).get_val(rhs_event).get_val_on_key(rhs_event,2) != 66:
        print '\nError: rhs_event should have seen updated value of 66.\n'
        return False
    
    if rhs.map.get_val(rhs_event).get_val_on_key(rhs_event,2).get_val(rhs_event).get_len(rhs_event) != 2:
        print '\nError: rhs_event should know that it contains a list of length 2.\n'
        return False    

    
    
    return True
    
        

if __name__ == '__main__':
    run_test()


