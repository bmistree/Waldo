#!/usr/bin/env python

import os
import sys
import time

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib import Waldo
from waldo.lib.waldoLockedVariables import LockedNumberVariable, LockedTextVariable
from waldo.lib.waldoLockedVariables import LockedTrueFalseVariable
from locked_test_util import DummyEndpoint

'''
Creates a reader and a writer.  Begin the event with a younger uuid.
Read from the variable.  Then execute the event with an older uuid as
a writer.  The older uuid should preempt the younger uuid.  Test that
it does.
'''


def run_test():
    
    endpoint = DummyEndpoint()
    initial_value = 0
    num_var = LockedNumberVariable(Waldo._host_uuid,False,initial_value)

    ### Check that each can read initial value
    older_event = endpoint._act_event_map.create_root_event()
    younger_event = endpoint._act_event_map.create_root_event()

    if num_var.get_val(younger_event) != initial_value:
        return False

    # now preempt with older event
    preempting_set_val = 4
    num_var.set_val(older_event, preempting_set_val)
    older_event.begin_first_phase_commit()
    # try to perform operations with younger event

    try:
        if num_var.get_val(younger_event) != preempting_set_val:
            return False
    except:
        # expected to get a backout exception
        pass

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
