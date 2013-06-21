#!/usr/bin/env python
import sys,os,Queue, time, threading,test_util
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import wVariables, waldoEndpoint, waldoVariableStore
from waldo.lib import util, waldoActiveEvent, waldoExecutingEvent, waldoCallResults

'''
Have two endpoints on the same host.  Testing:

  * When I change external data on one, the change is reflected on the
    other.

  * I cannot have two writes to external data simultaneously.  System
    will automatically backout changes for endpoint calls.
'''

# stores each new value of local var as go.  Should be ordered from
# 100 to 0 if decremented correctly in order.
array_of_values = []
            
        
class DummyEndpoint(test_util.DummyEndpoint): 
    def __init__(self,conn_obj,host_uuid=None):
        test_util.DummyEndpoint.__init__(self,conn_obj,host_uuid)

        # when dispatching to partner, we request the function name as
        # it would appear in the Waldo source file.  However, the
        # compiler mangles it into another name.  The call below
        # ensures that that the mangled name exists.
        setattr(
            self,
            util.endpoint_call_func_name('endpoint_func'),
            self.endpoint_func)

    def new_event_and_read(self,var_name):
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))

        var = context.global_store.get_var_if_exists(var_name)
        var_value = var.get_val(active_event)
        return active_event, var_value

    def new_event_and_write(self,var_name,var_val):
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))

        var = context.global_store.get_var_if_exists(var_name)
        var.write_val(active_event,var_val)
        return active_event

    
    
    def endpoint_func(self,active_event,context,other_endpoint):
        '''
        The first time that this function is called, it has neither an
        active_event, nor a context.  We need to explicitly pass in
        None for them.
        '''
        if active_event == None:
            # create active event
            active_event = self._act_event_map.create_root_event()

            # create context
            context = waldoExecutingEvent._ExecutingEventContext(
                self._global_var_store,
                # not using sequence local store
                waldoVariableStore._VariableStore(self._host_uuid))

            
        # Execute endpoint call back and forth.  Keep doing so until
        # numero is negative.
        endpoint_var = context.global_store.get_var_if_exists(
            self.endpoint_number_var_name)        
        
        if endpoint_var.get_val(active_event) > 0: # keep sending messages until less than 0.
            endpoint_var.write_val(active_event,endpoint_var.get_val(active_event) - 1)

            # store each value as go through in array so that can
            # check at the end that did in fact get sequential
            # decrement of values.
            global array_of_values
            array_of_values.append(endpoint_var.get_val(active_event))
            
            threadsafe_queue = Queue.Queue()
            
            active_event.issue_endpoint_object_call(
                other_endpoint,'endpoint_func',
                threadsafe_queue,self)
            
            endpoint_call_res = threadsafe_queue.get()

            
        # so that root can commit
        return active_event
    
                 
def run_test():
    # setup
    conn_obj1 = test_util.SingleEndpointConnectionObj()
    conn_obj2 = test_util.SingleEndpointConnectionObj()
            
    # connected to different, anonymous endpoints
    end1 = DummyEndpoint(conn_obj1) 
    end2 = DummyEndpoint(conn_obj2,end1._host_uuid)

    endpoint_var_num_name = 'external'
    end1.endpoint_number_var_name = endpoint_var_num_name
    end2.endpoint_number_var_name = endpoint_var_num_name
            
    external_num = wVariables.WaldoNumVariable (
        endpoint_var_num_name,end1._host_uuid,False,100)

    end1.add_number_var_to_var_store(external_num)
    end2.add_number_var_to_var_store(external_num)

    # actually run test
    root_act_event_to_commit = end1.endpoint_func(
        None,None,end2)

    
    # check to ensure that sequence local data were correctly
    # decremented
    if array_of_values != range(99,-1,-1):
        err_msg = '\nErr: incorrectly decremented ext '
        err_msg += 'data through endpoint calls.\n'
        print err_msg
        return False

    # now, attempt to commit change
    root_act_event_to_commit.request_commit()
    
    # block until event may have finished
    queue_elem = root_act_event_to_commit.event_complete_queue.get()
    
    
    # check that changes on both sides' peered "numero" variable have
    # been written on a new event.
    evt1,final_value_on_end1 = end1.new_event_and_read(endpoint_var_num_name)
    evt2,final_value_on_end2 = end2.new_event_and_read(endpoint_var_num_name)

    if final_value_on_end1 != 0:
        print '\nError: endpoint 1 has incorrect val for ext data.\n'
        return False
    
    if final_value_on_end1 != final_value_on_end2:
        print '\nError: ext data val on each endpoint disagrees.\n'
        return False

    evt1.request_commit()
    evt2.request_commit()
    queue_elem = evt1.event_complete_queue.get()
    queue_elem = evt2.event_complete_queue.get()
    

    # Reset the endpoint variable to some value
    new_val = 100
    evt = end1.new_event_and_write(endpoint_var_num_name,new_val)
    evt.request_commit()
    queue_elem = evt.event_complete_queue.get()
    
    # read from the endpoint variable on one side, then start the
    # endpoint calls, then commit the read.  Ensure that write does
    # not commit and must reschedule.
    new_val +=1 
    evt1 = end1.new_event_and_write(endpoint_var_num_name,new_val)

    root_act_event_to_commit = end1.endpoint_func(
        None,None,end2)

    evt1.request_commit()
    queue_elem = evt1.event_complete_queue.get()

    root_act_event_to_commit.request_commit()
    queue_elem = root_act_event_to_commit.event_complete_queue.get()
    if not isinstance(
        queue_elem,waldoCallResults._RescheduleRootCallResult):
        err_msg = '\nError: should have been unable to commit '
        err_msg += 'writes after read was committed.\n'
        print err_msg
        return False

    # do not retry event, but ensure that final values on both ends
    # are correct.
    evt1,final_value_on_end1 = end1.new_event_and_read(endpoint_var_num_name)
    evt2,final_value_on_end2 = end2.new_event_and_read(endpoint_var_num_name)

    if final_value_on_end1 != new_val:
        print '\nError: end 1 incorrect final ext data.\n'
        return False
    
    if final_value_on_end1 != final_value_on_end2:
        print '\nError: end 2 incorrect final ext data.\n'
        return False

    evt1.request_commit()
    evt2.request_commit()
    queue_elem = evt1.event_complete_queue.get()
    queue_elem = evt2.event_complete_queue.get()

    
    return True

if __name__ == '__main__':
    run_test()
