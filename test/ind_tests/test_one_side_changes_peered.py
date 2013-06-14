#!/usr/bin/env python

import os, sys, Queue, time, threading, test_util
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import wVariables, util, wVariables, waldoEndpoint
from waldo.lib import waldoVariableStore, util, waldoActiveEvent
from waldo.lib import waldoExecutingEvent, waldoCallResults


'''
When one side writes to a peered variable, check to ensure the commit
to that variable updates other side.
'''

class DummyEndpoint(test_util.DummyEndpoint):
        
    def write_numero(self):
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))
        
        var = context.global_store.get_var_if_exists(
            self.peered_number_var_name)
        var_value = var.get_val(active_event)
        var.write_val(active_event,var_value + 1)
        var_value = var.get_val(active_event)
        active_event.request_commit()
        queue_elem = active_event.event_complete_queue.get()
        return var_value

    
def run_test():
    # setup
    conn_obj = test_util.DummyConnectionObj()
    end1 = DummyEndpoint(conn_obj)
    end2 = DummyEndpoint(conn_obj)

    # only performing operations on end1.  ensure after that end2 gets
    # updated though.
    val = end1.write_numero()
    if val != 101:
        err_msg = '\nErr: should have read 101 from write '
        err_msg += 'of peered on end1.\n'
        print err_msg
        return False
    
    val = end2.write_numero()
    if val != 102:
        err_msg = '\nErr: should have read 102 from write '
        err_msg += 'of peered on end2.\n'
        print err_msg
        return False
    
    return True
    
if __name__ == '__main__':
    run_test()


