import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import Waldo, util,waldoEndpoint,waldoVariableStore,wVariables,waldoConnectionObj
import threading
from waldo.lib.util import Queue


class DummyConnectionObj(waldoConnectionObj._WaldoSameHostConnectionObject):
    pass

class SingleEndpointConnectionObj(waldoConnectionObj._WaldoSingleSideConnectionObject):
    pass


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

        self.peered_map_var_name = 'some map'
        glob_var_store.add_var(
            self.peered_map_var_name,
            wVariables.WaldoMapVariable('some map',host_uuid,True))

        
        waldoEndpoint._Endpoint.__init__(
            self,Waldo._waldo_classes,
            host_uuid,conn_obj,glob_var_store)


    def add_number_var_to_var_store(self,waldo_num_var):
        '''
        To test that endpoint calls work ask both sides 
        '''
        self._global_var_store.add_var(
            waldo_num_var.name,
            waldo_num_var)
