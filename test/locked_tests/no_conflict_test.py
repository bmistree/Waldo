#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib import Waldo
from waldo.lib.waldoLockedVariables import LockedNumberVariable, LockedTextVariable
from waldo.lib.waldoLockedVariables import LockedTrueFalseVariable
from locked_test_util import DummyEndpoint

'''
Tries creating a single number variable, getting its value and then
committing.

Then writes a value to it in a new event and commits.

Finally re-reads the value and checks that it's bene updated.
'''


def run_test():
    
    endpoint = DummyEndpoint()
    initial_value = -330
    num_var = LockedNumberVariable(Waldo._host_uuid,False,initial_value)

    ### Check that can read initial value
    read_event = endpoint._act_event_map.create_root_event()
    for i in range(0,10):
        if num_var.get_val(read_event) != initial_value:
            print '\nIncorrect value on read\n'
            print num_var.get_val(read_event)
            return False

    # try to commit the event
    read_event.begin_first_phase_commit()

    
    ### Check that can write a value
    write_event = endpoint._act_event_map.create_root_event()
    amount_added = 0
    for i in range(0,10):
        amount_added += i
        gotten_val = num_var.get_val(write_event)
        num_var.set_val(write_event,gotten_val + i)
        
    # commit the write
    write_event.begin_first_phase_commit()

    #### Check final value after write
    read_event = endpoint._act_event_map.create_root_event()
    if num_var.get_val(read_event) != (initial_value + amount_added):
        return False

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
