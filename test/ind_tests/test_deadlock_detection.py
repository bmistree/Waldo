#!/usr/bin/env python


import os, sys, random,time
import Queue, threading, test_util
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import  wVariables, waldoEndpoint, waldoVariableStore
from waldo.lib import util, waldoCallResults, waldoActiveEvent, waldoExecutingEvent

'''

+------------+             +------------+
|            |             |            |
|  +-----+   |             |            |
|  |  r1 |   |             |            |
|  +-----+   |             |            |
|     |      |             |            |
|  +-----+   |             |  +-----+   |
|  |  a  +---+-------------+--+  b  |   |
|  +-----+   |             |  +-----+   |
|     |      |             |     |      |
|  +-----+   |             |  +-----+   |
|  |  c  +---+-------------+--+  r2 |   |
|  +-----+   |             |  +-----+   |
|            |             |            |
|            |             |            |
|            |             |            |
|   host 1   |             |   host 2   |
+------------+             +------------+


r1 ("root 1") begins an event which makes an endpoint call on a, which
then makes a partner call to b.

r2 ("root 2") begins an event which makes an endpoint call on b and
then r2 makes a partner call on c, which then makes an endpoint call
on a.

If we then start a thread that attempts to commit both events,
simultaneously we may get deadlock.  (r1 will lock a and then try to
acquire lock on b, but r2 may already have locked b and be tryiing to
lock a.)  

Data on a:
  alpha --- Endpoint global Number

Data on b:
  beta --- Endpoint global Number

Data on c:
  The endpoint for a --- (note: this isn't contained in a waldo var yet.)
  
No data on r1, or r2.


Methods on a:
  update_alpha (increments alpha)
  update_alpha_and_send_message (increments alpha + sends msg to b)

Methods on b:
  update_beta (increments beta)
  update_beta_when_receive_message (icrements beta when rcv msg)
  
Methods on c:
  receive_message_for_a (endpoint calls update_alpha on a)
  
Methods on r1:
  evt_r1 (endpoint calls update_alpha_and_send_message on a)

Methods on r2:
  evt_r2 (endpoint calls update_beta on b and then
          sends msg to receve_message_for_a on c)
  
'''


class EndpointA(test_util.DummyEndpoint):
    def __init__(self,*args):
        test_util.DummyEndpoint.__init__(self,*args)

        # adding data for a
        self.alpha_name = 'alpha'
        self._global_var_store.add_var(
            self.alpha_name,
            wVariables.WaldoNumVariable(
                self.alpha_name,self._host_uuid,
                False,1))

        setattr(
            self,
            util.endpoint_call_func_name('update_alpha'),
            self.update_alpha)
        setattr(
            self,
            util.endpoint_call_func_name('update_alpha_and_send_message'),
            self.update_alpha_and_send_message)

        
    def update_alpha(self,active_event,context):

        endpoint_var = self._global_var_store.get_var_if_exists(self.alpha_name)
        endpoint_var.write_val(
            active_event,endpoint_var.get_val(active_event) + 1)
        
    def update_alpha_and_send_message(self,active_event,context):
        self.update_alpha(active_event,context)

        threadsafe_queue = Queue.Queue()
        active_event.issue_partner_sequence_block_call(
            context,'update_beta_when_receive_message',threadsafe_queue,True)

        msg_call_res = threadsafe_queue.get()
        # not checking for backout...won't happen

        context.set_to_reply_with(msg_call_res.reply_with_msg_field)
        # apply changes to sequence variables.  (There shouldn't
        # be any, but it's worth getting in practice.)  Note: that
        # the system has already applied deltas for global data.
        context.sequence_local_store.incorporate_deltas(
            active_event,msg_call_res.sequence_local_var_store_deltas)

        
        
class EndpointB(test_util.DummyEndpoint):
    def __init__(self,*args):
        test_util.DummyEndpoint.__init__(self,*args)

        # adding data for b
        self.beta_name = 'beta'
        self._global_var_store.add_var(
            self.beta_name,
            wVariables.WaldoNumVariable(
                self.beta_name,self._host_uuid,
                False,1))
        setattr(
            self,
            util.endpoint_call_func_name('update_beta'),
            self.update_beta)
        setattr(
            self,
            util.partner_endpoint_msg_call_func_name('update_beta_when_receive_message'),
            self.update_beta_when_receive_message)
        
    def update_beta(self,active_event,context):
        endpoint_var = self._global_var_store.get_var_if_exists(self.beta_name)
        endpoint_var.write_val(
            active_event,endpoint_var.get_val(active_event) + 1)
        
    def update_beta_when_receive_message(self,active_event,context):
        self.update_beta(active_event,context)
        
        # last message in sequence, so tell other side we're all done.
        active_event.issue_partner_sequence_block_call(
            context,None,None,False)

        
class EndpointC(test_util.DummyEndpoint):
    def __init__(self,endpoint_a,*args):
        test_util.DummyEndpoint.__init__(self,*args)

        self.endpoint_a = endpoint_a
        
        setattr(
            self,
            util.partner_endpoint_msg_call_func_name('receive_message_for_a'),
            self.receive_message_for_a)
        
    def receive_message_for_a(self,active_event,context):
        threadsafe_queue = Queue.Queue()
        active_event.issue_endpoint_object_call(
            self.endpoint_a,'update_alpha',
            threadsafe_queue)
        endpoint_call_res = threadsafe_queue.get()
        
        # last message in sequence, so tell other side we're all done.
        active_event.issue_partner_sequence_block_call(
            context,None,None,False)


        
class EndpointR1(test_util.DummyEndpoint):
    # no data on r1

    def evt_r1(self,endpoint_a):
        active_event = self._act_event_map.create_root_event()
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))

        threadsafe_queue = Queue.Queue()
        active_event.issue_endpoint_object_call(
            endpoint_a,'update_alpha_and_send_message',
            threadsafe_queue)

        endpoint_call_res = threadsafe_queue.get()
        return active_event
        

class EndpointR2(test_util.DummyEndpoint):
    # no data on r2

    def evt_r2(self,endpoint_b):
        active_event = self._act_event_map.create_root_event()
        
        # create context
        context = waldoExecutingEvent._ExecutingEventContext(
            self._global_var_store,
            # not using sequence local store
            waldoVariableStore._VariableStore(self._host_uuid))

        # first, call method on b
        threadsafe_queue = Queue.Queue()
        active_event.issue_endpoint_object_call(
            endpoint_b,'update_beta',
            threadsafe_queue)


        endpoint_call_res = threadsafe_queue.get()
        
        # call method on c, which calls method on a
        threadsafe_queue = Queue.Queue()
        active_event.issue_partner_sequence_block_call(
            context,'receive_message_for_a',threadsafe_queue,True)
        msg_call_res = threadsafe_queue.get()
        return active_event



class TryCommit(threading.Thread):
    def __init__(self,act_event):
        self.act_event = act_event
        threading.Thread.__init__(self)
        self.daemon = True
    def run(self):
        self.act_event.request_commit()
        queue_elem = self.act_event.event_complete_queue.get()


def run_test():
    # run 10 times to exercise different timings
    for i in range(0,10):
        if not basic_setup():
            return False

    return True
        
def basic_setup():
    # setup
    host1_uuid = util.generate_uuid()
    host2_uuid = util.generate_uuid()

    a_b_conn = test_util.DummyConnectionObj()
    c_r2_conn = test_util.DummyConnectionObj()

    garbage_conn = test_util.DummyConnectionObj()

    # host one endpoints
    r1 = EndpointR1(garbage_conn,host1_uuid)
    a = EndpointA(a_b_conn,host1_uuid)
    c = EndpointC(a,c_r2_conn,host1_uuid)

    # host two endpoints
    r2 = EndpointR2(c_r2_conn,host2_uuid)
    b = EndpointB(a_b_conn,host2_uuid)

    # start each event
    act_r1 = r1.evt_r1(a)
    act_r2 = r2.evt_r2(b)

    try1 = TryCommit(act_r1)
    try2 = TryCommit(act_r2)
    try2.start()
    try1.start()


    return True

if __name__ == '__main__':
    run_test()


