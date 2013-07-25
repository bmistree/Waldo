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
    older_event = endpoint.create_root_event()
    younger_event = endpoint.create_root_event()

    # If older, have larger uuid.  
    if older_event.uuid < younger_event.uuid:
        tmp = older_event
        older_event = younger_event
        younger_event = tmp

    if num_var.get_val(younger_event) != initial_value:
        return False

    # now preempt with older event
    preempting_set_val = 4
    num_var.set_val(older_event, preempting_set_val)

    # try to commit both events
    older_event.begin_first_phase_commit()
    time.sleep(1)
    if num_var.get_val(younger_event) != preempting_set_val:
        return False

    younger_event.begin_first_phase_commit()
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
