import waldo.lib.util as util
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas


def create_map_delta(parent_delta):
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
    return map_delta,is_var_store


def create_list_delta(parent_delta):
    is_var_store = False
    if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
        is_var_store = True
        list_delta = parent_delta.list_deltas.add()
    elif parent_delta.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
        list_delta = parent_delta.what_written_list
    elif parent_delta.parent_type == VarStoreDeltas.CONTAINER_ADDED:
        list_delta = parent_delta.added_what_list
    elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
        list_delta = parent_delta.list_delta
    else:
        util.logger_assert('Unexpected parent container type when serializing list')

    list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER        

    return list_delta,is_var_store
    

def container_serializable_var_tuple_for_network(
    container_obj,parent_delta,var_name,active_event,force,for_map):
    '''
    @see waldoReferenceBase.serializable_var_tuple_for_network
    '''
    # reset has been written to
    has_been_written_since_last_msg = (
        container_obj.get_and_reset_has_been_written_since_last_msg(active_event))

    if for_map:
        container_delta,is_var_store = create_map_delta(parent_delta)
    else:
        container_delta,is_var_store = create_list_delta(parent_delta)

    container_delta.var_name = var_name
    container_delta.has_been_written = has_been_written_since_last_msg

    internal_has_been_written = internal_container_variable_serialize_var_tuple_for_network(
        container_obj,container_delta,var_name,active_event,
        # must force the write when we have written a new value over list
        force or has_been_written_since_last_msg)


    # FIXME: check to ensure that second part of condition will
    # still hide elements that do not change
    if (not internal_has_been_written) and is_var_store and (not has_been_written_since_last_message):
        # remove the newly added map delta because there were no
        # changes that it encoded
        if for_map:
            del parent_delta.map_deltas[-1]
        else:
            del parent_delta.list_deltas[-1]

        
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


