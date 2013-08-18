from waldo.lib.waldoLockedObj import WaldoLockedObj
import numbers
from waldo.lib.waldoDataWrapper import ReferenceTypeDataWrapper
from waldo.lib.waldoLockedContainer import WaldoLockedContainer
import waldo.lib.util as util
from waldo.lib.waldoLockedVariablesHelper import SingleThreadedLockedValueVariable
from waldo.lib.waldoLockedVariablesHelper import SingleThreadedLockedContainerVariable
from waldo.lib.waldoLockedVariablesHelper import LockedValueVariable
from waldo.lib.waldoLockedVariablesHelper import MapBaseClass
from waldo.lib.waldoLockedVariablesHelper import container_serializable_var_tuple_for_network
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas

def ensure_locked_obj(new_val,host_uuid):
    '''
    @param {Anything} new_val --- If new_val is a non-Waldo object,
    convert it to a Waldo object.  Otherwise, return it unchanged.

    This method is used to ensure that each individual entry in a
    map/list is also protected.
    '''
    if isinstance(new_val , WaldoLockedObj):
        return new_val

    if isinstance(new_val, bool):
        return LockedTrueFalseVariable(host_uuid,False,new_val)
    elif isinstance(new_val, numbers.Number):
        return LockedNumberVariable(host_uuid,False,new_val)
    elif util.is_string(new_val):
        return LockedTextVariable(host_uuid,False,new_val)
    else:
        util.logger_assert('Unknown object type.')
    

##### Multi-threaded value variables #####
class LockedNumberVariable(LockedValueVariable):
    pass

class LockedTextVariable(LockedValueVariable):
    pass

class LockedTrueFalseVariable(LockedValueVariable):
    pass


##### Single threaded value variables #####
class SingleThreadedLockedNumberVariable(SingleThreadedLockedValueVariable):
    pass

class SingleThreadedLockedTextVariable(SingleThreadedLockedValueVariable):
    pass

class SingleThreadedLockedTrueFalseVariable(SingleThreadedLockedValueVariable):
    pass


class LockedMapVariable(WaldoLockedContainer,MapBaseClass):
    def __init__(self,host_uuid,peered,init_val):
        super(LockedMapVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)

    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        '''
        Map specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.add_key(active_event,key_added,new_val,incorporating_deltas)

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        container_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)


class SingleThreadedLockedMapVariable(SingleThreadedLockedContainerVariable, MapBaseClass):
    def __init__(self,host_uuid,peered,init_val):
        super(SingleThreadedLockedMapVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)

    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        '''
        Map specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        self.val.add_key(active_event,key_added,new_val,incorporating_deltas)

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        container_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)

        
    
class LockedListVariable(WaldoLockedContainer):

    def __init__(self,host_uuid,peered,init_val):
        super(LockedListVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)

    def insert_val(self,active_event,where_to_insert,new_val):
        '''
        List specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.insert(active_event,where_to_insert,new_val)


    def append_val(self,active_event,new_val):
        '''
        List specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.append(active_event,new_val)

