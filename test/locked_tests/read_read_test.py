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
Creates two readers.  Both should be able to commit.
'''


def run_test():
    
    endpoint = DummyEndpoint()
    initial_value = 'init_val'
    num_var = LockedTextVariable(Waldo._host_uuid,False,initial_value)

    ### Check that each can read initial value
    read_event_1 = endpoint.create_root_event()
    read_event_2 = endpoint.create_root_event()
    for i in range(0,10):
        if ((num_var.get_val(read_event_1) != initial_value) or
            (num_var.get_val(read_event_2) != initial_value)):
            print '\nIncorrect value on read\n'
            return False

    # try to commit both events
    read_event_1.begin_first_phase_commit()
    read_event_2.begin_first_phase_commit()

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
