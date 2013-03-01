import os
import sys

sys.path.append(
    os.path.join('..','..','lib'))

import util
import threading
import Queue
import waldoEndpoint
import waldoVariableStore
import wVariables
import commitManager

class DummyConnectionObj(threading.Thread):
    def __init__(self):
        self.queue = Queue.Queue()
        self.endpoint1 = None
        self.endpoint2 = None

        threading.Thread.__init__(self)
        self.daemon = True
        
    def register_endpoint (self, endpoint):
        if self.endpoint1 == None:
            self.endpoint1 = endpoint
        else:
            self.endpoint2 = endpoint
            self.endpoint1._set_partner_uuid(
                self.endpoint2._uuid)
            self.endpoint2._set_partner_uuid(
                self.endpoint1._uuid)

    def write(self,msg,endpoint):
        self.queue.put((msg,endpoint))


    def run(self):

        while True:
            msg,msg_sender_endpt = self.queue.get()
            msg_recvr_endpt = self.endpoint1
            if msg_sender_endpt == self.endpoint1:
                msg_recvr_endpt = self.endpoint2

            msg_recvr_endpt._receive_msg_from_partner(msg)



class DummyEndpoint(waldoEndpoint._Endpoint):
    def __init__(self,conn_obj,host_uuid = None):
        
        # all dummy endpoints will have the same _VariableStore
        # Peered Number numero = 100;
        # Peered Text some_str = 'test';
        # Peered List (elements: Text) text_list;
        if host_uuid == None:
            host_uuid = util.generate_uuid()
            
        glob_var_store = waldoVariableStore._VariableStore(host_uuid)
        
        self.peered_number_var_name = 'numero'
        glob_var_store.add_var(
            self.peered_number_var_name,
            wVariables.WaldoNumVariable(
                self.peered_number_var_name,host_uuid,
                True,100))

        self.peered_str_var_name = 'some_str'
        glob_var_store.add_var(
            self.peered_str_var_name,
            wVariables.WaldoTextVariable(
                self.peered_str_var_name,host_uuid,
                True,'test'))
        
        self.peered_list_var_name = 'text_list'
        glob_var_store.add_var(
            self.peered_list_var_name,
            wVariables.WaldoTextVariable(
                self.peered_list_var_name,host_uuid,True))

        waldoEndpoint._Endpoint.__init__(
            self,host_uuid,commitManager._CommitManager(),
            conn_obj,glob_var_store)


    def add_number_var_to_var_store(self,waldo_num_var):
        '''
        To test that endpoint calls work ask both sides 
        '''
        self._global_var_store.add_var(
            waldo_num_var.name,
            waldo_num_var)
        
            
# class DummyHost(object):
#     def __init__(self):
#         self.host_uuid = util.generate_uuid()
    
#     def generate_dummy_endpoint(self):
        
