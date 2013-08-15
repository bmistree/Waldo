from waldoLockedObj import WaldoLockedObj
from waldoDataWrapper import ValueTypeDataWrapper
from waldoDataWrapper import ReferenceTypeDataWrapper
from waldoLockedContainer import WaldoLockedContainer
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
import util
import numbers

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
    

class LockedValueVariable(WaldoLockedObj):
    def __init__(self,host_uuid,peered,init_val):
        super(LockedValueVariable,self).__init__(
            ValueTypeDataWrapper,host_uuid,peered,init_val)

    def write_if_different(self,active_event,data):
        to_write_on = self.acquire_write_lock(active_event)
        to_write_on.write(data,True)
        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoLockedObj.serializable_var_tuple_for_network
        '''
        var_data = self.get_val(active_event)
        has_been_written_since_last_msg = self.get_and_reset_has_been_written_since_last_msg(active_event)

        if (not force) and (not has_been_written_since_last_msg):
            # nothing to do because this value has not been
            # written.  NOTE: for list/dict types, must actually
            # go through to ensure no subelements were written.
            return False
        
        # check if this is a python value type.  if it is, append it
        # to delta.
        if not self.py_val_serialize(parent_delta,var_data,var_name):
            util.logger_assert(
                'Error when serializing variable for network.  ' +
                'Expected python value type')

        return True


    def py_val_serialize(self,parent,var_data,var_name):
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

        
        

class LockedNumberVariable(LockedValueVariable):
    pass

class LockedTextVariable(LockedValueVariable):    
    pass

class LockedTrueFalseVariable(LockedValueVariable):
    pass


class LockedMapVariable(WaldoLockedContainer):
    def __init__(self,host_uuid,peered,init_val):
        super(LockedMapVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)

    def add_key(self,active_event,key_added,new_val):
        '''
        Map specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val[key_added] = new_val

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
        wrapped_val.val.insert(where_to_insert, new_val)
        
    def append_val(self,active_event,new_val):
        '''
        List specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val.append(new_val)
