#!/usr/bin/env python

import os, sys, time, test_util
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from lib import wVariables, util


class SingleSide(test_util.DummyEndpoint):
    def __init__(self):
        test_util.DummyEndpoint.__init__(
            self,test_util.SingleEndpointConnectionObj())

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

    rhs_event = rhs.new_event()

    internal_list1,evt = create_waldo_list(lhs,[1,2,3])
    internal_list2,evt = create_waldo_list(lhs,[4,5,6],evt)
    internal_list3,evt = create_waldo_list(lhs,[7,8,9],evt)

    lhs_map = lhs._global_var_store.get_var_if_exists(
        lhs.peered_map_var_name)
    rhs_map = rhs._global_var_store.get_var_if_exists(
        rhs.peered_map_var_name)
    
    lhs_map.get_val(evt).add_key(evt,1,internal_list1)
    lhs_map.get_val(evt).add_key(evt,2,internal_list2)
    lhs_map.get_val(evt).add_key(evt,1,internal_list3)
    # should produce:
    #  { 1: [7,8,9], 2: [4,5,6] }


    var_store_delta_msg = lhs._global_var_store.generate_deltas(evt,True)
    rhs._global_var_store.incorporate_deltas(rhs_event,var_store_delta_msg)
    
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

    if lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,1).get_val(lhs_event).get_val_on_key(lhs_event,0) != 7:
        print '\nErr: did not get change from previous commit.\n'
        return False
    if lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_val_on_key(lhs_event,0) != 4:
        print '\nErr: did not get change from previous commit 2.\n'
        return False

    lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,1).get_val(lhs_event).write_val_on_key(lhs_event,0,20)

    var_store_delta_msg = lhs._global_var_store.generate_deltas(lhs_event,False)
    rhs._global_var_store.incorporate_deltas(rhs_event2,var_store_delta_msg)

    rhs_map.get_val(rhs_event1).del_key_called(rhs_event1,1)

    if not rhs_event1.hold_can_commit():
        print '\nError: should be able to commit delete'
        return False
    rhs_event1.complete_commit()

    if rhs_event2.hold_can_commit():
        err_msg = '\nError: should not be able to commit rhs\'s '
        err_msg += 'read+single write update after committed delete\n'
        print err_msg
        return False
    rhs_event2.backout_commit()
    lhs_event.hold_can_commit()
    lhs_event.backout_commit()

    # should produce:
    #  { 2: [4,5,6] }


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
    
    lhs_map.get_val(lhs_event1).get_val_on_key(lhs_event1,2).get_val(lhs_event1).write_val_on_key(lhs_event1,1,16)
    rhs_map.get_val(rhs_event1).get_val_on_key(rhs_event1,2).get_val(rhs_event1).del_key_called(rhs_event1,2)

    var_store_delta_msg = lhs._global_var_store.generate_deltas(lhs_event1,False)
    rhs._global_var_store.incorporate_deltas(rhs_event2,var_store_delta_msg)

    
    var_store_delta_msg = rhs._global_var_store.generate_deltas(rhs_event1,False)
    lhs._global_var_store.incorporate_deltas(lhs_event2,var_store_delta_msg)
    
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

    
    # should produce:
    #  { 2: [4,16] }


    # check to ensure that both sides saw the changes from above
    lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()
    
    if lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_val_on_key(lhs_event,1) != 16:
        print '\nError: lhs_event should have seen updated value of 16.\n'
        return False
    
    if lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_len(lhs_event) != 2:
        print '\nError: lhs_event should know that it contains a list of length 2.\n'
        return False    

    if rhs_map.get_val(rhs_event).get_val_on_key(rhs_event,2).get_val(rhs_event).get_val_on_key(rhs_event,1) != 16:
        print '\nError: rhs_event should have seen updated value of 16.\n'
        return False

    if rhs_map.get_val(rhs_event).get_val_on_key(rhs_event,2).get_val(rhs_event).get_len(rhs_event) != 2:
        print '\nError: rhs_event should know that it contains a list of length 2.\n'
        return False    

    # should produce:
    #  { 2: [4,16] }
    
    # another check that can do operations in parallel.  lhs_event
    # will read all values in the map (and ensure that they were set
    # correctly from above).  It also sets one value.  "concurrently"
    # rhs_event1 will delete a value from its map.  similarly,
    # rhs_event2 will try to apply the change made from lhs_event.
    # Should be able to commit {lhs_event, rhs_event2} and then
    # {rhs_event1}.

    lhs_event = lhs.new_event()
    rhs_event1 = rhs.new_event()
    rhs_event2 = rhs.new_event()

    
    if lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_val_on_key(lhs_event,0) != 4:
        print '\nErr: did not get change from previous commit.\n'
        return False
    
    if lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).get_val_on_key(lhs_event,1) != 16:
        print '\nErr: did not get change from previous commit 2.\n'
        return False

    lhs_map.get_val(lhs_event).get_val_on_key(lhs_event,2).get_val(lhs_event).write_val_on_key(lhs_event,1,20)


    var_store_delta_msg = lhs._global_var_store.generate_deltas(lhs_event,False)
    rhs._global_var_store.incorporate_deltas(rhs_event2,var_store_delta_msg)
    

    int_l,evtl = create_waldo_list(rhs,[1,2,3])
    if not evtl.hold_can_commit():
        print '\nError: should be able to append to list'
        return False
    evtl.complete_commit()

    rhs_map.get_val(rhs_event1).add_key(rhs_event1,1,int_l)

    if not rhs_event1.hold_can_commit():
        print '\nError: should be able to commit add'
        return False
    rhs_event1.complete_commit()
    
    if not rhs_event2.hold_can_commit():
        err_msg = '\nError: should not be able to commit rhs\'s '
        err_msg += 'read+single write update in parallel with add\n'
        print err_msg
        return False
    rhs_event2.complete_commit()

    if not lhs_event.hold_can_commit():
        err_msg = '\nError: should not be able to commit lhs\'s '
        err_msg += 'read+single write update in parallel with add\n'
        print err_msg
        return False
    lhs_event.complete_commit()

    return True
    
        

if __name__ == '__main__':
    run_test()


