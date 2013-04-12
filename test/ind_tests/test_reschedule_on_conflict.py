#!/usr/bin/env python

import os, sys, test_util, time, threading, Queue
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from lib import wVariables, waldoEndpoint, waldoVariableStore
from lib import util, waldoActiveEvent, waldoExecutingEvent
from lib import waldoCallResults

'''
Check to ensure that when two root events conflict, the runtime
signals that the event needs to be rescheduled.
'''

class DummyEndpoint(test_util.DummyEndpoint):
    def __init__(self,conn_obj):
        test_util.DummyEndpoint.__init__(
            self,conn_obj)
        
        # Endpoint global Number numeroer = 100;
        self.end_global_var_num_name = 'numeroer'
        self._global_var_store.add_var(
            self.end_global_var_num_name,
            wVariables.WaldoNumVariable(
                self.end_global_var_num_name,
                self._host_uuid,False,100))

    def new_event_and_read_numero(self):
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))

        var = context.global_store.get_var_if_exists(
            self.end_global_var_num_name)
        var_value = var.get_val(active_event)
        return active_event, var_value

    def new_event_and_write_numero(self):
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))        

        var = context.global_store.get_var_if_exists(
            self.end_global_var_num_name)
        var_value = var.get_val(active_event)
        var.write_val(active_event,var_value + 1)
        var_value = var.get_val(active_event)
        
        return active_event, var_value
        
    
def run_test():
    # setup
    conn_obj = test_util.DummyConnectionObj()
    end1 = DummyEndpoint(conn_obj)
    end2 = DummyEndpoint(conn_obj)

    # only performing operations on end1
    read_root_event,read_var_value = end1.new_event_and_read_numero()
    write_root_event,write_var_value = end1.new_event_and_write_numero()

    if read_var_value != 100:
        err_msg = '\nErr: should have read 100 from read '
        err_msg += 'of endpoint global.\n'
        print err_msg
        return False

    if write_var_value != 101:
        err_msg = '\nErr: should have read 101 from write '
        err_msg += 'of endpoint global.\n'
        print err_msg
        return False
    

    write_root_event.request_commit()
    queue_elem = write_root_event.event_complete_queue.get()

    got_retry = False
    
    read_root_event.request_commit()
    queue_elem = read_root_event.event_complete_queue.get()
    while isinstance(queue_elem,waldoCallResults._RescheduleRootCallResult):
        read_root_event,read_var_value = end1.new_event_and_read_numero()
        read_root_event.request_commit()
        queue_elem = read_root_event.event_complete_queue.get()    
        got_retry = True
        
        if read_var_value != 101:
            err_msg = '\nErr: should have read 101 from read '
            err_msg += 'of endpoint global in loop.\n'
            print err_msg
            return False

        
    if not got_retry:
        err_msg = '\nErr: should have been unable to commit read after ' 
        err_msg += 'write without a retry.\n'
        print err_msg
        return False
    
    return True
    
if __name__ == '__main__':
    run_test()


