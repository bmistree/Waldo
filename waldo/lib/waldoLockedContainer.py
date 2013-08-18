from waldo.lib.waldoLockedObj import WaldoLockedObj
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
import waldo.lib.util as util

def container_incorporate_deltas(
    container_obj,delta_to_incorporate,constructors,active_event):
    '''
    @param {WaldoLockedContainer or SingleThreadedLockedContainer}
    
    @param {SingleListDelta or SingleMapDelta} delta_to_incorporate

    @param {SingleInternalListDelta or SingleInternalMapDelta}
    delta_to_incorporate

    When a peered or sequence peered container (ie, map, list, or
    struct) is modified by one endpoint, those changes must be
    reflected on the other endpoint.  This method takes the
    changes that one endpoint has made on a container, represented
    by delta_to_incorporate, and applies them (if we can).    
    '''
    if delta_to_incorporate.parent_type == VarStoreDeltas.LIST_CONTAINER:
        delta_to_incorporate = delta_to_incorporate.internal_list_delta
        to_iter_over = delta_to_incorporate.list_actions
    else:
        delta_to_incorporate = delta_to_incorporate.internal_map_delta
        to_iter_over = delta_to_incorporate.map_actions

    for action in to_iter_over:
        if action.container_action == VarStoreDeltas.ContainerAction.WRITE_VALUE:

            container_written_action = action.write_key
            # added because when serializing and deserializing data with
            # protobufs, not using integer indices, using double indices.
            # This causes a problem on the range commadn below.
            index_to_write_to = container_obj.get_write_key_incorporate_deltas(
                container_written_action)

            if container_written_action.HasField('what_written_text'):
                new_val = container_written_action.what_written_text
            elif container_written_action.HasField('what_written_num'):
                new_val = container_written_action.what_written_num
            elif container_written_action.HasField('what_written_tf'):
                new_val = container_written_action.what_written_tf

            elif container_written_action.HasField('what_written_map'):
                new_val = constructors.single_thread_map_constructor(
                    container_obj.host_uuid,True,{})
                single_map_delta = container_written_action.what_written_map
                single_map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER
                new_val.incorporate_deltas(single_map_delta,constructors,active_event)

            elif container_written_action.HasField('what_written_list'):
                new_val = constructors.single_thread_list_constructor(container_obj.host_uuid,True,[])
                single_list_delta = container_written_action.what_written_list
                single_list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER                    
                new_val.incorporate_deltas(single_list_delta,constructors,active_event)

            elif container_written_action.HasField('what_written_struct'):
                new_val = constructors.single_thread_struct_constructor(container_obj.host_uuid,True,{})
                single_struct_delta = container_written_action.what_written_struct
                single_struct_delta.parent_type = VarStoreDeltas.STRUCT_CONTAINER
                new_val.incorporate_deltas(single_struct_delta,constructors,active_event)

            # actually put new value in list
            container_obj.set_val_on_key(active_event,index_to_write_to,new_val,False)


        elif action.container_action == VarStoreDeltas.ContainerAction.ADD_KEY:
            container_added_action = action.added_key

            index_to_add_to = container_obj.get_add_key_incorporate_deltas(container_added_action)

            if container_added_action.HasField('added_what_text'):
                new_val = container_added_action.added_what_text
            elif container_added_action.HasField('added_what_num'):
                new_val = container_added_action.added_what_num
            elif container_added_action.HasField('added_what_tf'):
                new_val = container_added_action.added_what_tf

            elif container_added_action.HasField('added_what_map'):
                new_val = constructors.single_thread_map_constructor(container_obj.host_uuid,True,{})
                single_map_delta = container_added_action.added_what_map
                single_map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER
                new_val.incorporate_deltas(single_map_delta,constructors,active_event)

            elif container_added_action.HasField('added_what_list'):
                new_val = constructors.single_thread_list_constructor(container_obj.host_uuid,True,[])
                single_list_delta = container_added_action.added_what_list
                single_list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER
                new_val.incorporate_deltas(single_list_delta,constructors,active_event)

            elif container_added_action.HasField('added_what_struct'):
                new_val = constructors.single_thread_struct_constructor(container_obj.host_uuid,True,{})
                single_struct_delta = container_added_action.added_what_struct
                single_struct_delta.parent_type = VarStoreDeltas.STRUCT_CONTAINER
                new_val.incorporate_deltas(single_struct_delta,constructors,active_event)

            container_obj.handle_added_key_incorporate_deltas(
                active_event,index_to_add_to,new_val)


        elif action.container_action == VarStoreDeltas.ContainerAction.DELETE_KEY:
            container_deleted_action = action.deleted_key
            index_to_del_from = container_obj.get_delete_key_incorporate_deltas(
                container_deleted_action)
            container_obj.del_key_called(active_event,index_to_del_from)


    for sub_element_action in delta_to_incorporate.sub_element_update_actions:
        index = sub_element_action.key_num

        if sub_element_action.HasField('map_delta'):
            to_incorporate = sub_element_action.map_delta
        elif sub_element_action.HasField('list_delta'):
            to_incorporate = sub_element_action.list_delta
        #### DEBUG
        else:
            util.logger_assert('Unkwnown action type in subelements')
        #### END DEBUG

        container_obj.get_val_on_key(active_event,index).incorporate_deltas(
            to_incorporate,constructors,active_event)

    # do not want to send the same information back to the other side.
    container_obj.get_and_reset_has_been_written_since_last_msg(active_event)



class WaldoLockedContainer(WaldoLockedObj):
        
    def get_val(self,active_event):
        util.logger_assert('Cannot call get val on a container object')
    def set_val(self,active_event,new_val):
        util.logger_assert('Cannot call set val on a container object')        
        
    def get_val_on_key(self,active_event,key):
        wrapped_val = self.acquire_read_lock(active_event)
        return wrapped_val.val[key].get_val(active_event)
        
    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        util.logger_warn('Not handling copy_if_peered: should not copy in this case')
        wrapped_val =  self.acquire_read_lock(active_event)
        return wrapped_val.set_val_on_key(active_event,key,to_write)

    def del_key_called(self,active_event,key_to_delete):
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.del_key(active_event,key_to_delete)

    def get_len(self,active_event):
        wrapped_val = self.acquire_read_lock(active_event)
        return len(wrapped_val.val)
            
    def get_keys(self,active_event):
        wrapped_val = self.acquire_read_lock(active_event)
        return list(wrapped_val.val.keys())

    def contains_key_called(self,active_event,contains_key):
        wrapped_val = self.acquire_read_lock(active_event)
        return contains_key in wrapped_val.val

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):

        util.logger_assert(
            'Still must define serializable_var_tuple_for_network on ' +
            'locked container objects.')

        
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
        

        
