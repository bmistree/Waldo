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
from locked_test_util import create_context, DummyPartnerEndpoint


'''
Create a sequence local variable, send message to other endpoint.
Other endpoint modifies the sequence local variable, and we test that
we get the modification back.
'''

B_VAL = 3339

SEQ_LOC_VAR_NAME = 'seq_loc'
class PartnerEndpoint(DummyPartnerEndpoint):
    def __init__(self,conn_obj):
        super(PartnerEndpoint,self).__init__(conn_obj)

        setattr(
            self,
            util.partner_endpoint_msg_call_func_name('test_partner_write'),
            self.test_partner_write)

    def test_partner_write (self,active_event,context):
        num_var = context.sequence_local_store.get_var_if_exists(
            SEQ_LOC_VAR_NAME)
        num_var.set_val(active_event,B_VAL)
        context.hide_sequence_completed_call(self,active_event)

        
def run_test():
    conn_obj = DummyConnectionObj()
    end_a = PartnerEndpoint(conn_obj)
    end_b = PartnerEndpoint(conn_obj)

    ctx_a = create_context(end_a)
    # load a sequence variable into ctx_a

    ctx_a.sequence_local_store.add_var(
        SEQ_LOC_VAR_NAME,
        # True means that it's peered
        LockedNumberVariable(Waldo._host_uuid,True,100))
    
    # send sequence message to the other side to perform write there.
    # block until call completes
    write_event = end_a._act_event_map.create_root_event()


    num_var = ctx_a.sequence_local_store.get_var_if_exists(
        SEQ_LOC_VAR_NAME)

    # FIXME: unclear why need this.
    num_var.get_val(write_event)
    
    ctx_a.hide_partner_call(
        end_a,write_event,'test_partner_write',True)

    # check that sequence local value was updated
    num_var = ctx_a.sequence_local_store.get_var_if_exists(
        SEQ_LOC_VAR_NAME)

    gotten_val = num_var.get_val(write_event)

    
    if num_var.get_val(write_event) != B_VAL:
        print '\nRead incorrect value from num_var.\n'
        return False

    # actually try to commit write event
    write_event.begin_first_phase_commit()
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
