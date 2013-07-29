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
Creates two endpoints.  Each with a single number variable.  Sets the
number variable on each endpoint to a known value.

Then, start an event which reads both values and commits.  
'''

DATA_INIT_VAL = 12

def initialize_data(endpoint):
    '''
    @returns {bool} --- True if setting worked; False otherwise.
    '''
    num_var = endpoint._global_var_store.get_var_if_exists(
        endpoint.end_global_number_var_name)

    write_event = endpoint.create_root_event()
    num_var.set_val(write_event,DATA_INIT_VAL)
    write_event.begin_first_phase_commit()

    return check_data_val(endpoint, DATA_INIT_VAL)

def check_data_val(endpoint,expected_val):
    '''
    @returns {bool} --- True if the number held by the endpoint equals
    expected val.  False otherwise.
    '''
    num_var = endpoint._global_var_store.get_var_if_exists(
        endpoint.end_global_number_var_name)
    
    read_event = endpoint.create_root_event()
    gotten = num_var.get_val(read_event)
    read_event.begin_first_phase_commit()
    return (gotten == expected_val)


def run_test():
    endpoint_a = DummyEndpoint()
    endpoint_b = DummyEndpoint()

    if not initialize_data(endpoint_a):
        print '\nError Setting initial value A\n'
        return False
    if not initialize_data(endpoint_b):
        print '\nError Setting initial value B\n'
        return False
    
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
