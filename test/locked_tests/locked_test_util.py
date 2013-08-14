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
from waldo.lib.util import generate_uuid, partner_endpoint_msg_call_func_name
from waldo.lib import Waldo
from waldo.lib.waldoExecutingEvent import _ExecutingEventContext
from waldo.lib.waldoLockedVariables import LockedNumberVariable, LockedTextVariable
from waldo.lib.waldoLockedVariables import LockedTrueFalseVariable
from waldo.lib.waldoConnectionObj import _WaldoSameHostConnectionObject


class DummyConnectionObj(_WaldoSameHostConnectionObject):
    pass


class DummyEndpoint(_Endpoint):
    def __init__(self,conn_obj=None,host_uuid = None):
        
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


    def create_older_and_younger_root_events(self):
        older_event = self._act_event_map.create_root_event()
        younger_event = self._act_event_map.create_root_event()

        # If older, have larger uuid.  
        if older_event.uuid < younger_event.uuid:
            tmp = older_event
            older_event = younger_event
            younger_event = tmp

        return older_event,younger_event


def create_context(endpoint):
    seq_local_store = _VariableStore(endpoint._host_uuid)
    return _ExecutingEventContext(
        endpoint._global_var_store,
        seq_local_store)


class DummyPartnerEndpoint(DummyEndpoint):
    def __init__(self,conn_obj):
        super(DummyPartnerEndpoint,self).__init__(conn_obj)
