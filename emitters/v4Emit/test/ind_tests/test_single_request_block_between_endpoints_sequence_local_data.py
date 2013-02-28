#!/usr/bin/env python
import sys,os

sys.path.append(
    os.path.join('..','..','lib'))
import wVariables
import waldoEndpoint
import commitManager
import waldoVariableStore
import util
import Queue
import waldoActiveEvent
import waldoExecutingEvent
import threading
import test_util

'''
Testing:
  * Can request block sequence actions between partner endpoints

  * Can create sequence local data that will be shared across a series
    of calls alternating between sides.

  * Changes to sequence local data are shared between both sides

Want to ensure that I can create two endpoints that can request block
sequence actions on each side.

THIS TEST DOES NOT CHECK WHETHER COMMITS WORK.
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
        
    def sequence_block(self,active_event=None,context=None):
        '''
        The first time that this function is called, it has neither an
        active_event, nor a context.  We create them.
        '''
        seq_local_num_name = 'seq_local_num'
        
        if active_event == None:
            # create active event
            active_event = self._act_event_map.create_root_event()

            # create context
            seq_local_store = waldoVariableStore._VariableStore(self._host_uuid)
            seq_local_store.add_var(
                seq_local_num_name,
                wVariables.WaldoNumVariable(
                    seq_local_num_name,self._host_uuid,True,100))

            context = waldoExecutingEvent._ExecutingEventContext(
                self._global_var_store,seq_local_store)


        # Send messages back and forth to each other to decrement
        # sequence local data seq_local_num.  Keep doing so until
        # seq_local_num is negative.
        local_var = context.sequence_local_store.get_var_if_exists(seq_local_num_name)
        if local_var.get_val(active_event) > 0: # keep sending messages until less than 0.
            local_var.write_val(active_event,local_var.get_val(active_event) - 1)

            # store each value as go through in array so that can
            # check at the end that did in fact get sequential
            # decrement of values.
            global array_of_values
            array_of_values.append(local_var.get_val(active_event))

            
            threadsafe_queue = Queue.Queue()
            active_event.issue_partner_sequence_block_call(
                context,'sequence_block',threadsafe_queue)

            
            seq_msg_call_res = threadsafe_queue.get()

            
            context.set_to_reply_with(seq_msg_call_res.reply_with_msg_field)
            
            # apply changes to sequence local data.  (global changes,
            # which aren't applicable in this example, have already
            # been applied.)
            context.sequence_local_store.incorporate_deltas(
                active_event,seq_msg_call_res.sequence_local_var_store_deltas)


            # send more messages
            to_exec_next = seq_msg_call_res.to_exec_next_name_msg_field
            to_exec = getattr(self,to_exec_next)
            to_exec(active_event,context)
            
        else:
            # at this point, should initiate the commit of data.
            # print '\nComplete!!!\n'
            pass

            
                 
def run_test():
    # setup
    conn_obj = test_util.DummyConnectionObj()
    end1 = DummyEndpoint(conn_obj)
    end2 = DummyEndpoint(conn_obj)
    conn_obj.register_endpoint(end1)
    conn_obj.register_endpoint(end2)
    conn_obj.start()

    # actually run test
    end1.sequence_block()

    # check to ensure that sequence local data were correctly
    # decremented
    if array_of_values != range(99,-1,-1):
        print '\nErr: incorrectly decremented sequence local data.\n'
        return False

    return True

if __name__ == '__main__':
    run_test()
