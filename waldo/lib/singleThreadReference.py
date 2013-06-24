import threading, numbers
import util
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas

from waldoObj import WaldoObj


class _SingleThreadReferenceBase(WaldoObj):
    '''
    Only one thread of control can access this variable.  Example:
    local variables or sequence peered variables.  Antonyms: peered
    data and endpoint global data.
    '''
    
    def __init__(self,host_uuid,peered,init_val,version_obj):
        '''
        @param {bool} peered --- True if this variable is a piece of
        sequence local data.  False if it's just a regular-old local
        variable.
        '''
        self.host_uuid = host_uuid
        self.uuid = util.generate_uuid()
        self.val = init_val
        self.version_obj = version_obj        
        self.peered = peered

    def is_peered(self):
        return self.peered
    
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        The runtime automatically synchronizes data between both
        endpoints.  When one side has updated a peered variable, the
        other side needs to attempt to apply those changes before
        doing further work.  This method grabs the val and version
        object of the dirty element associated with invalid_listener.
        Using these data, plus var_name, it constructs a named tuple
        for serialization.  (@see
        util._generate_serialization_named_tuple)

        Note: if the val of this object is another Reference object,
        then we recursively keep generating named tuples and embed
        them in the one we return.

        Note: we only serialize peered data.  No other data gets sent
        over the network; therefore, it should not be serialized.

        @param {*Delta or VarStoreDeltas} parent_delta --- Append any
        message that we create here to this message.
        
        @param {String} var_name --- Both sides of the connection need
        to agree on a common name for the variable being serialized.
        This is to ensure that when the data are received by the other
        side we know which variable to put them into.  This value is
        only really necessary for the outermost wrapping of the named
        type tuple, but we pass it through anyways.

        @param {bool} force --- True if regardless of whether modified
        or not we should serialize.  False otherwise.  (We migth want
        to force for instance the first time we send sequence data.)
        
        @returns {bool} --- True if some subelement was modified,
        False otherwise.
        '''
        # a val can either point to a waldo reference, a python value,
        # or a list/map of waldo references or a list/map of python
        # values.
        var_data = self.val

        if (not force) and (not self.version_obj.has_been_written_since_last_message):
            if (isinstance(var_data,numbers.Number) or
                util.is_string(var_data) or isinstance(var_data,bool)):
                # nothing to do because this value has not been
                # written.  NOTE: for list/dict types, must actually
                # go through to ensure no subelements were written.
                return False

        sub_element_modified = False
        if self.py_val_serialize(parent_delta,var_data,var_name):
            sub_element_modified = True
        
        elif isinstance(var_data,list):
            list_delta = parent_delta.internal_list_delta
            list_delta.parent_type = VarStoreDeltas.INTERNAL_LIST_CONTAINER

            if force:
                # perform each operation as a write...
                self.version_obj.add_all_data_to_delta_list(
                    list_delta,var_data,invalid_listener)
                sub_element_modified = True
            else:
                # if all subelements have not been modified, then we
                # do not need to keep track of these changes.
                # wVariable.waldoMap, wVariable.waldoList, or
                # wVariable.WaldoUserStruct will get rid of it later.
                sub_element_modified = self.version_obj.add_to_delta_list(
                    list_delta,var_data,invalid_listener)

        elif isinstance(var_data,dict):
            map_delta = parent_delta.internal_map_delta
            map_delta.parent_type = VarStoreDeltas.INTERNAL_MAP_CONTAINER

            if force:
                # perform each operation as a write...
                self.version_obj.add_all_data_to_delta_list(
                    map_delta,var_data,invalid_listener)
                sub_element_modified = True
            else:
                # if all subelements have not been modified, then we
                # do not need to keep track of these changes.
                # wVariable.waldoMap, wVariable.waldoList, or
                # wVariable.WaldoUserStruct will get rid of it later.
                sub_element_modified = self.version_obj.add_to_delta_list(
                    map_delta,var_data,invalid_listener)

                
        else:
            # creating deltas for cases where internal data are waldo
            # references.... should have been overridden in
            # wVariables.py
            util.logger_assert('Serializing unknown type.')

        self.version_obj.has_been_written_since_last_message = False
        return sub_element_modified
        
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

    def get_val(self,invalid_listener):
        return self.val

    def write_if_different(self,invalid_listener,new_val):
        '''
        Will always write.  Only reason method is
        named_write_if_different is to keep it consistent with
        interface for peered variables.
        '''
        self.val = new_val
        
    def write_val(self,invalid_listener,new_val,copy_if_peered=True):
        '''
        Writes to a copy of internal val, dirtying it
        '''
        self.val = new_val
