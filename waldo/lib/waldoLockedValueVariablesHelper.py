from waldo.lib.waldoLockedObj import WaldoLockedObj
from waldo.lib.waldoLockedSingleThreadedObj import SingleThreadedObj
from waldo.lib.waldoLockedMultiThreadedObj import MultiThreadedObj
import waldo.lib.util as util
import numbers
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
from waldo.lib.waldoDataWrapper import ValueTypeDataWrapper


def value_variable_serializable_var_tuple_for_network(
    value_variable,parent_delta,var_name,active_event, force):
    '''
    @see waldoLockedObj.serializable_var_tuple_for_network
    '''
    var_data = value_variable.get_val(active_event)
    has_been_written_since_last_msg = value_variable.get_and_reset_has_been_written_since_last_msg(active_event)

    if (not force) and (not has_been_written_since_last_msg):
        # nothing to do because this value has not been
        # written.  NOTE: for list/dict types, must actually
        # go through to ensure no subelements were written.
        return False
    
    # check if this is a python value type.  if it is, append it
    # to delta.
    if not value_variable_py_val_serialize(
        value_variable,parent_delta,var_data,var_name):
        util.logger_assert('Should only use python values when serializing')
        
    return True


def value_variable_py_val_serialize(value_variable,parent,var_data,var_name):
    '''
    @param {} parent --- Either a ContainerAction a VarStoreDeltas.

    FIXME: unclear if actually need var_name for all elements
    py_serialize-ing, or just py variables that are in the
    top-level.

    @returns {bool} --- True if var_data was a python value type
    and we put it into parent.  False otherwise.

    If is python value type, then adds a delta message to
    parent.  Otherwise, does nothing.
    '''
    is_value_type = False
    delta = None
    if isinstance(var_data, numbers.Number):
        # can only add a pure number to var store a holder or to
        # an added key
        if parent.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            delta = parent.num_deltas.add()
        elif parent.parent_type == VarStoreDeltas.CONTAINER_ADDED:
            parent.added_what_num = var_data
        elif parent.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
            parent.what_written_num = var_data
        #### DEBUG
        else:
            util.logger_assert('Unexpected parent type in py_serialize')
        #### END DEBUG

        is_value_type = True

    elif util.is_string(var_data):
        if parent.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            delta = parent.text_deltas.add()
        elif parent.parent_type == VarStoreDeltas.CONTAINER_ADDED:
            parent.added_what_text = var_data
        elif parent.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
            parent.what_written_text = var_data

        #### DEBUG
        else:
            util.logger_assert('Unexpected parent type in py_serialize')
        #### END DEBUG                

        is_value_type = True

    elif isinstance(var_data,bool):
        if parent.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            delta = parent.true_false_deltas.add()
        elif parent.parent_type == VarStoreDeltas.CONTAINER_ADDED:
            parent.added_what_tf = var_data
        elif parent.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
            parent.what_written_tf = var_data                
        #### DEBUG
        else:
            util.logger_assert('Unexpected parent type in py_serialize')
        #### END DEBUG                

        is_value_type = True

    if delta != None:
        # all value types have same format
        delta.var_name = var_name
        delta.var_data = var_data

    return is_value_type



class LockedValueVariable(MultiThreadedObj):
    DEFAULT_VALUE = None
    
    def __init__(self,host_uuid,peered,init_val=None):
        if init_val is None:
            init_val = self.DEFAULT_VALUE
            
        super(LockedValueVariable,self).__init__(
            ValueTypeDataWrapper,host_uuid,peered,init_val)


    def return_internal_val_from_container(self):
        return True
        
    def write_if_different(self,active_event,data):
        to_write_on = self.acquire_write_lock(active_event)
        to_write_on.write(data,True)
        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoLockedObj.serializable_var_tuple_for_network
        '''
        return value_variable_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)


class SingleThreadedLockedValueVariable(SingleThreadedObj):
    DEFAULT_VALUE = None
    
    def __init__(self,host_uuid,peered,init_val=None):
        if init_val is None:
            init_val = self.DEFAULT_VALUE
        
        super(SingleThreadedLockedValueVariable,self).__init__(
            ValueTypeDataWrapper,host_uuid,peered,init_val)

    def write_if_different(self,active_event,data):
        self.val.write(data,True)

    def return_internal_val_from_container(self):
        return True
        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoLockedObj.serializable_var_tuple_for_network
        '''
        return value_variable_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)
        
