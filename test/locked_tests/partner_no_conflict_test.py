#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib import Waldo
from waldo.lib import util
from waldo.lib.waldoVariableStore import _VariableStore
from waldo.lib.waldoExecutingEvent import _ExecutingEventContext
from waldo.lib.waldoLockedVariables import LockedNumberVariable, LockedTextVariable
from waldo.lib.waldoLockedVariables import LockedTrueFalseVariable
from locked_test_util import DummyEndpoint,DummyConnectionObj

'''
Create two, connected endpoints.  Create a single number variable on
each and read their value to ensure that they're correct.  

Then, create an event on one that writes to local variable, and then
issues a sequence call to other endpoint so that it also writes to its
variable.

Following committing the event, re-read both variables to ensure that
they've been written properly.
'''

B_VAL = 3339

def create_context(endpoint):
    seq_local_store = _VariableStore(endpoint._host_uuid)
    return _ExecutingEventContext(
        endpoint._global_var_store,
        seq_local_store)


class PartnerEndpoint(DummyEndpoint):
    def __init__(self,conn_obj):
        super(PartnerEndpoint,self).__init__(conn_obj)

        setattr(
            self,
            util.partner_endpoint_msg_call_func_name('test_partner'),
            self.test_partner)

    def test_partner (self,active_event,context):
        num_var = context.global_store.get_var_if_exists(
            self.end_global_number_var_name)
        num_var.set_val(active_event,B_VAL)
        context.hide_sequence_completed_call(self,active_event)


def run_test():

    conn_obj = DummyConnectionObj()
    end_a = PartnerEndpoint(conn_obj)
    end_b = PartnerEndpoint(conn_obj)

    ctx_a = create_context(end_a)
    ctx_b = create_context(end_b)
    num_var_a = ctx_a.global_store.get_var_if_exists(
        end_a.end_global_number_var_name)
    num_var_b = ctx_b.global_store.get_var_if_exists(
        end_b.end_global_number_var_name)            


    # perform write locally
    a_val = 3920
    write_event = end_a._act_event_map.create_root_event()
    num_var_a.set_val(write_event,a_val)
    
    # send sequence message to the other side to perform write there.
    # block until call completes
    ctx_a.hide_partner_call(
        end_a,write_event,'test_partner',True)

    # actually try to commit write event
    write_event.begin_first_phase_commit()

    # check that both values were updated
    read_event_a = end_a._act_event_map.create_root_event()
    if num_var_a.get_val(read_event_a) != a_val:
        print '\nWrite did not go through on A\n'
        return False

    read_event_a.begin_first_phase_commit()

    read_event_b = end_b._act_event_map.create_root_event()
    if num_var_b.get_val(read_event_b) != B_VAL:
        print '\nWrite did not go through on B\n'
        return False
    read_event_b.begin_first_phase_commit()

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
