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
from waldo.lib import util

'''
Creates two endpoints.  Each with a single number variable.  Sets the
number variable on each endpoint to a known value.

Then, start an event which reads both values and commits.  
'''

class DummyEndpointWithCalls(DummyEndpoint): 
    def __init__(self):
        DummyEndpoint.__init__(self)

        # when dispatching to partner, we request the function name as
        # it would appear in the Waldo source file.  However, the
        # compiler mangles it into another name.  The call below
        # ensures that that the mangled name exists.
        setattr(
            self,
            util.endpoint_call_func_name('endpoint_func'),
            self.endpoint_func)

    def endpoint_func(self,active_event,context):
        '''
        The first time that this function is called, it has neither an
        active_event, nor a context.  We need to explicitly pass in
        None for them.
        '''
        # Execute endpoint call back and forth.  Keep doing so until
        # numero is negative.
        endpoint_var = context.global_store.get_var_if_exists(
            self.endpoint_number_var_name)        

        val = endpoint_var.get_val(active_event)
        return val


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

    ### setup and initialization
    endpoint_a = DummyEndpointWithCalls()
    endpoint_b = DummyEndpointWithCalls()

    if not initialize_data(endpoint_a):
        print '\nError Setting initial value A\n'
        return False
    if not initialize_data(endpoint_b):
        print '\nError Setting initial value B\n'
        return False

    ### endpoint call

    num_var_a = endpoint_a._global_var_store.get_var_if_exists(
        endpoint_a.end_global_number_var_name)
    num_var_b = endpoint_b._global_var_store.get_var_if_exists(
        endpoint_b.end_global_number_var_name)
    
    # # create event for endpoint call
    # read_endpoint_event = endpoint_a.create_root_event()
    # # perform read on endpoint_a
    # num_var_a.get_val(read_endpoint_event)


    
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
