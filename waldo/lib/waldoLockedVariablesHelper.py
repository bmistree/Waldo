from waldo.lib.waldoLockedObj import WaldoLockedObj
from waldo.lib.waldoLockedSingleThreadMultiThread import MultiThreadedObj
from waldo.lib.waldoLockedSingleThreadMultiThread import SingleThreadedObj
import waldo.lib.util as util
import numbers
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
from waldo.lib.waldoDataWrapper import ValueTypeDataWrapper
from waldo.lib.waldoLockedContainer import container_incorporate_deltas


def container_serializable_var_tuple_for_network(
    container_obj,parent_delta,var_name,active_event,force):
    '''
    @see waldoReferenceBase.serializable_var_tuple_for_network
    '''
    # reset has been written to
    has_been_written_since_last_msg = (
        container_obj.get_and_reset_has_been_written_since_last_msg(active_event))

    is_var_store = False
    if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
        is_var_store = True
        map_delta = parent_delta.map_deltas.add()
    elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_WRITTEN:            
        map_delta = parent_delta.what_written_map
    elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_ADDED:
        map_delta = parent_delta.added_what_map
    elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
        map_delta = parent_delta.map_delta
    else:
        util.logger_assert(
            'Unexpected parent container type when serializing map')

    map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER            
    map_delta.var_name = var_name

    map_delta.has_been_written = has_been_written_since_last_msg

    internal_has_been_written = internal_container_variable_serialize_var_tuple_for_network(
        container_obj,map_delta,var_name,active_event,
        # must force the write when we have written a new value over list
        force or has_been_written_since_last_msg)


    # FIXME: check to ensure that second part of condition will
    # still hide elements that do not change
    if (not internal_has_been_written) and is_var_store and (not has_been_written_since_last_message):
        # remove the newly added map delta because there were no
        # changes that it encoded
        del parent_delta.map_deltas[-1]

    return internal_has_been_written or written_since_last_message or force



def internal_container_variable_serialize_var_tuple_for_network(
    locked_container,parent_delta,var_name,active_event, force):
    '''
    @param {Map,List, or Struct Variable} locked_container
    '''
    var_data = locked_container.val.val

    # FIXME: If going to have publicly peered data, need to use
    # locked_container.dirty_val instead of locked_container.val when
    # incorporating changes???  .get_dirty_wrapped_val returns
    # wrapped val that can use for serializing data.
    dirty_wrapped_val = locked_container.get_dirty_wrapped_val(active_event)

    
    sub_element_modified = False
    if isinstance(var_data,list):
        list_delta = parent_delta.internal_list_delta
        list_delta.parent_type = VarStoreDeltas.INTERNAL_LIST_CONTAINER

        if force:
            dirty_wrapped_val.add_all_data_to_delta_list(
                list_delta,var_data,active_event,False)
            sub_element_modified = True
        else:
            # if all subelements have not been modified, then we
            # do not need to keep track of these changes.
            # wVariable.waldoMap, wVariable.waldoList, or
            # wVariable.WaldoUserStruct will get rid of it later.
            sub_element_modified = dirty_wrapped_val.add_to_delta_list(
                list_delta,var_data,active_event,False)


    elif isinstance(var_data,dict):
        map_delta = parent_delta.internal_map_delta
        map_delta.parent_type = VarStoreDeltas.INTERNAL_MAP_CONTAINER

        if force:
            # perform each operation as a write...
            dirty_wrapped_val.add_all_data_to_delta_list(
                map_delta,var_data,active_event,True)
            sub_element_modified = True
        else:
            # if all subelements have not been modified, then we
            # do not need to keep track of these changes.
            # wVariable.waldoMap, wVariable.waldoList, or
            # wVariable.WaldoUserStruct will get rid of it later.
            sub_element_modified = dirty_wrapped_val.add_to_delta_list(
                map_delta,var_data,active_event,True)

    else:
        # creating deltas for cases where internal data are waldo
        # references.... should have been overridden in
        # wVariables.py
        util.logger_assert('Serializing unknown type.')

    return sub_element_modified



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
        
        util.logger_assert(
            'Error when serializing variable for network.  ' +
            'Expected python value type')

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
        return value_variable_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)

    
class SingleThreadedLockedValueVariable(SingleThreadedObj):
    def __init__(self,host_uuid,peered,init_val):
        super(SingleThreadedLockedValueVariable,self).__init__(
            ValueTypeDataWrapper,host_uuid,peered,init_val)

    def write_if_different(self,active_event,data):
        self.val.write(data,True)
        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoLockedObj.serializable_var_tuple_for_network
        '''
        return value_variable_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)



class MapBaseClass(object):
    def get_write_key_incorporate_deltas(self,container_written_action):
        if container_written_action.HasField('write_key_text'):
            index_to_write_to = container_written_action.write_key_text
        elif container_written_action.HasField('write_key_num'):
            index_to_write_to = container_written_action.write_key_num
        elif container_written_action.HasField('write_key_tf'):
            index_to_write_to = container_written_action.write_key_tf
        #### DEBUG
        else:
            util.logger_assert('Unknown map index')
        #### END DEBUG

        return index_to_write_to

    
    def get_add_key_incorporate_deltas(self,container_added_action):
        if container_added_action.HasField('added_key_text'):
            index_to_add_to = container_added_action.added_key_text
        elif container_added_action.HasField('added_key_num'):
            index_to_add_to = container_added_action.added_key_num
        elif container_added_action.HasField('added_key_tf'):
            index_to_add_to = container_added_action.added_key_tf
        #### DEBUG
        else:
            util.logger_assert('Unknown map index')
        #### END DEBUG

        return index_to_add_to

    
    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        if container_deleted_action.HasField('deleted_key_text'):
            index_to_del_from = container_deleted_action.deleted_key_text
        elif container_deleted_action.HasField('deleted_key_num'):
            index_to_del_from = container_deleted_action.deleted_key_num
        elif container_deleted_action.HasField('deleted_key_tf'):
            index_to_del_from = container_deleted_action.deleted_key_tf
        #### DEBUG
        else:
            util.logger_assert('Error in delete: unknown key type.')
        #### END DEBUG

        return index_to_del_from

    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        self.add_key(active_event,index_to_add_to,new_val,False)


    
class SingleThreadedLockedContainerVariable(SingleThreadedObj):

    def get_val(self,active_event):
        util.logger_assert('Cannot call get val on a container object')
    def set_val(self,active_event,new_val):
        util.logger_assert('Cannot call set val on a container object')        
        
    def get_val_on_key(self,active_event,key):
        return self.val.val[key].get_val(active_event)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        util.logger_warn('Not handling copy_if_peered: should not copy in this case')
        wrapped_val =  self.acquire_read_lock(active_event)
        return self.val.set_val_on_key(active_event,key,to_write)

    def del_key_called(self,active_event,key_to_delete):
        self.val.del_key(active_event,key_to_delete)

    def get_len(self,active_event):
        return len(self.val.val)
            
    def get_keys(self,active_event):
        return list(self.val.val.keys())

    def contains_key_called(self,active_event,contains_key):
        return contains_key in self.val.val

    def get_dirty_wrapped_val(self,active_event):
        '''
        @see waldoLockedObj.waldoLockedObj
        '''
        return self.val

    def incorporate_deltas(self,delta_to_incorporate,constructors,active_event):
        '''
        @param {SingleListDelta or SingleMapDelta} delta_to_incorporate
        
        @param {SingleInternalListDelta or SingleInternalMapDelta}
        delta_to_incorporate

        When a peered or sequence peered container (ie, map, list, or
        struct) is modified by one endpoint, those changes must be
        reflected on the other endpoint.  This method takes the
        changes that one endpoint has made on a container, represented
        by delta_to_incorporate, and applies them (if we can).
        '''
        container_incorporate_deltas(
            self,delta_to_incorporate,constructors,active_event)




        
