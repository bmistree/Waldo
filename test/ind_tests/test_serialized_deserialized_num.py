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


def run_test():
    lhs = SingleSide()
    rhs = SingleSide()

    lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()

    lhs_number = lhs._global_var_store.get_var_if_exists(
        lhs.peered_number_var_name)

    rhs_number = rhs._global_var_store.get_var_if_exists(
        rhs.peered_number_var_name)

    # make a change to lhs' number and try to update rhs' number.
    # ensure they can both commit the change.
    lhs_number.write_val(lhs_event,23)

    var_store_delta_msg = lhs._global_var_store.generate_deltas(lhs_event,True)

    rhs._global_var_store.incorporate_deltas(rhs_event,var_store_delta_msg)

    if not lhs_event.hold_can_commit():
        print '\nError: should be able to commit lhs.\n'
        return False
    lhs_event.complete_commit()


    if not rhs_event.hold_can_commit():
        print '\nError: should be able to commit rhs.\n'
        return False
    rhs_event.complete_commit()


    # check that both sides have the new number
    lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()
    
    if lhs_number.get_val(lhs_event) != 23:
        print '\nErr: for some reason, did not commit on lhs.\n'
        return False

    if rhs_number.get_val(rhs_event) != 23:
        print '\nErr: for some reason, did not commit on rhs.\n'
        return False


    if not lhs_event.hold_can_commit():
        print '\nError: should be able to commit lhs second time.\n'
        return False
    lhs_event.complete_commit()


    if not rhs_event.hold_can_commit():
        print '\nError: should be able to commit rhs second time.\n'
        return False
    rhs_event.complete_commit()

    
    return True
    

if __name__ == '__main__':
    run_test()


