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
from waldo.lib.waldoLockedVariables import SingleThreadedLockedListVariable
from locked_test_util import DummyEndpoint,DummyConnectionObj
from locked_test_util import create_context, DummyPartnerEndpoint


'''
Create a sequence local list, send message to other endpoint.  Other
endpoint appends data to list, and we test that we get the modification
back.
'''
VAL_A = 32
VAL_B = 39

SEQ_LOC_VAR_NAME = 'seq_loc'

failed_on_partner = False


class PartnerEndpoint(DummyPartnerEndpoint):
    def __init__(self,conn_obj):
        super(PartnerEndpoint,self).__init__(conn_obj)

        setattr(
            self,
            util.partner_endpoint_msg_call_func_name('test_partner_write'),
            self.test_partner_write)

    def test_partner_write (self,active_event,context):
        map_var = context.sequence_local_store.get_var_if_exists(
            SEQ_LOC_VAR_NAME)

        
        # check to ensure that got correct val from other side
        a_val = map_var.get_val(active_event).get_val_on_key(active_event,0)
        if a_val != VAL_A:
            global failed_on_partner
            failed_on_partner = True

        # now write change to both
        map_var.get_val(active_event).set_val_on_key(active_event,0,VAL_B)
        map_var.get_val(active_event).append_val(active_event,VAL_B)
            
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
        SingleThreadedLockedListVariable(Waldo._host_uuid,True,[]))
    
    # send sequence message to the other side to perform write there.
    # block until call completes
    write_event = end_a._act_event_map.create_root_event()

    map_var = ctx_a.sequence_local_store.get_var_if_exists(
        SEQ_LOC_VAR_NAME)

    map_var.get_val(write_event).append_val(write_event,VAL_A)
        
    ctx_a.hide_partner_call(
        end_a,write_event,'test_partner_write',True)

    # check that sequence local value was updated
    map_var = ctx_a.sequence_local_store.get_var_if_exists(
        SEQ_LOC_VAR_NAME)

    if failed_on_partner:
        print '\nPartner could not read correct data in sequence\n'
        return False
    
    if map_var.get_val(write_event).get_val_on_key(write_event,0) != VAL_B:
        print '\nDid not incorporate other side changes on key a\n'
        return False

    if map_var.get_val(write_event).get_val_on_key(write_event,1) != VAL_B:
        print '\nDid not incorporate other side changes on key b\n'
        return False    
    

    # actually try to commit write event
    write_event.begin_first_phase_commit()
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
