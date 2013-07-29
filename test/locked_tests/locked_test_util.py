import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib.waldoLockedActiveEvent import LockedActiveEvent
from waldo.lib.waldoEventParent import RootEventParent
from waldo.lib.waldoVariableStore import _VariableStore
from waldo.lib.waldoEndpoint import _Endpoint
from waldo.lib.util import generate_uuid
from waldo.lib.waldoConnectionObj import _WaldoSingleSideConnectionObject
from waldo.lib.util import generate_uuid
from waldo.lib import Waldo

from waldo.lib.waldoLockedVariables import LockedNumberVariable, LockedTextVariable
from waldo.lib.waldoLockedVariables import LockedTrueFalseVariable

class _DummyActiveEventMap(object):
    def __init__(self):
        self.map = {}

    def add_event(self,evt):
        self.map[evt.uuid] = evt
    def remove_event(self,evt_uuid):
        del self.map[evt_uuid]
        

class DummyEndpoint(_Endpoint):
    def __init__(self,conn_obj=None,host_uuid = None):
        self.evt_map = _DummyActiveEventMap()
        
        if conn_obj is None:
            conn_obj = _WaldoSingleSideConnectionObject()

        if host_uuid == None:
            host_uuid = generate_uuid()
            
        glob_var_store = _VariableStore(host_uuid)
        
        self.end_global_number_var_name = 'numero'
        glob_var_store.add_var(
            self.end_global_number_var_name,
            LockedNumberVariable(host_uuid,False,100))

        _Endpoint.__init__(
            self,Waldo._waldo_classes,
            host_uuid,conn_obj,glob_var_store)

    def create_root_event(self):
        rep = RootEventParent(self,generate_uuid())
        self.evt_map.add_event(rep)
        return LockedActiveEvent(rep,self.evt_map)

