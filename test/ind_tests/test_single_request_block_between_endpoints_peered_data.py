#!/usr/bin/env python
import sys,os,test_util,Queue,time, threading

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import wVariables, waldoEndpoint, waldoVariableStore
from waldo.lib import util, waldoActiveEvent, waldoExecutingEvent

'''
Testing:
  * Can request block sequence actions between partner endpoints

  * Can create peered data and writes and reads to that peered data
    will be shared by both sides.

  * Can commit changes and both sides see the committed changes.
'''

# stores each new value of local var as go.  Should be ordered from
# 100 to 0 if decremented correctly in order.
array_of_values = []
            
        
class DummyEndpoint(test_util.DummyEndpoint):
    def __init__(self,conn_obj):
        test_util.DummyEndpoint.__init__(self,conn_obj)

        # when dispatching to partner, we request the function name as
        # it would appear in the Waldo source file.  However, the
        # compiler mangles it into another name.  The call below
        # ensures that that the mangled name exists.
        setattr(
            self,
            util.partner_endpoint_msg_call_func_name('sequence_block'),
            self.sequence_block)

    def new_event_and_read_numero(self):
        '''
        Create a new event that reads the value of the peered number
        'numero.'
        '''
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))
        
        peered_var = context.global_store.get_var_if_exists(
            self.peered_number_var_name)
        var_value = peered_var.get_val(active_event)
        # warning just assuming that commit goes through instead of
        # retrying the event.
        
        active_event.request_commit()
        queue_elem = active_event.event_complete_queue.get()
        return var_value
        
        
    def sequence_block(self,active_event=None,context=None):
        '''
        The first time that this function is called, it has neither an
        active_event, nor a context.  We create them.
        '''

        # keep track of whether this is the first message sent in a
        # sequence so that we know whether or not we must force
        # updating all the new sequence local data.
        _first_msg = False
        if active_event == None:
            # create active event
            active_event = self._act_event_map.create_root_event()
            
            # create context
            context = waldoExecutingEvent._ExecutingEventContext(
                self._global_var_store,
                # not using sequence local store
                waldoVariableStore._VariableStore(self._host_uuid))

            _first_msg = True
            
        # Send messages back and forth to each other to decrement
        # peered local data seq_local_num.  Keep doing so until
        # numero is negative.
        peered_var = context.global_store.get_var_if_exists(
            self.peered_number_var_name)
        if peered_var.get_val(active_event) > 0: # keep sending messages until less than 0.
            peered_var.write_val(active_event,peered_var.get_val(active_event) - 1)

            # store each value as go through in array so that can
            # check at the end that did in fact get sequential
            # decrement of values.
            global array_of_values
            array_of_values.append(peered_var.get_val(active_event))
            
            threadsafe_queue = Queue.Queue()
            active_event.issue_partner_sequence_block_call(
                context,'sequence_block',threadsafe_queue,_first_msg)

            seq_msg_call_res = threadsafe_queue.get()
            
            context.set_to_reply_with(seq_msg_call_res.reply_with_msg_field)
            
            # apply changes to sequence variables.  (There shouldn't
            # be any, but it's worth getting in practice.)  Note: that
            # the system has already applied deltas for global data.
            context.sequence_local_store.incorporate_deltas(
                active_event,seq_msg_call_res.sequence_local_var_store_deltas)

            # send more messages
            to_exec_next = seq_msg_call_res.to_exec_next_name_msg_field
            to_exec = getattr(self,to_exec_next)
            to_exec(active_event,context)

        # so that root can commit
        return active_event
            
                 
def run_test():
    # setup
    conn_obj = test_util.DummyConnectionObj()
    end1 = DummyEndpoint(conn_obj)
    end2 = DummyEndpoint(conn_obj)

    # actually run test
    root_act_event_to_commit = end1.sequence_block()

    # check to ensure that sequence local data were correctly
    # decremented
    if array_of_values != range(99,-1,-1):
        print '\nErr: incorrectly decremented sequence local data.\n'
        return False

    # now, attempt to commit change
    root_act_event_to_commit.request_commit()
    
    # block until event may have finished
    queue_elem = root_act_event_to_commit.event_complete_queue.get()
    
    
    # check that changes on both sides' peered "numero" variable have
    # been written on a new event.
    final_value_on_end1 = end1.new_event_and_read_numero()
    final_value_on_end2 = end2.new_event_and_read_numero()

    if final_value_on_end1 != 0:
        print '\nError: endpoint 1 has incorrect final value for numero.\n'
        return False
    
    if final_value_on_end1 != final_value_on_end2:
        print '\nError: final numero value on each endpoint disagrees.\n'
        return False
    
    return True

if __name__ == '__main__':
    run_test()
