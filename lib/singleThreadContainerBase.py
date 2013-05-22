import singleThreadReference
import util
from abc import abstractmethod

from lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas

class _SingleThreadReferenceContainer(
    singleThreadReference._SingleThreadReferenceBase):
    '''
    All Waldo objects inherit from _WaldoObj.  However, non-value
    Waldo objects (maps, lists, user structs), should all inherit from
    _WaldoContainer.  This is because a WaldoContainer holds pointers
    to additional _WaldoObjs, and therefore needs to dirty those as
    well and update those simultaneously when updating _WaldoContainer.
    '''
    def __init__(
        self,host_uuid,peered,init_val,version_obj):

        singleThreadReference._SingleThreadReferenceBase.__init__(
            self,host_uuid,peered,init_val,version_obj)

        
    def get_val(self,invalid_listener):
        util.logger_assert(
            'In WaldoValueContainer, get_val disallowed.')

    def write_val(self,invalid_listener,new_val):
        util.logger_assert(
            'In WaldoValueContainer, write_val disallowed.')

    def add_key(self,invalid_listener,key_added,new_val):
        self.version_obj.add_key(key)

        # if we are peered, then we want to assign into ourselves a
        # copy of the object, not the object itslef.  This will only
        # be a problem for container types.  Non-container types
        # already have the semantics that they will be copied on read.
        
        if self.peered:
            # means that we must copy the value in if it's a reference

            if (isinstance(new_val,_ReferenceContainer) or
                isinstance(new_val,_SingleThreadReferenceContainer)):
                new_val = new_val.copy(invalid_listener,True,False)
                
            elif (isinstance(new_val,waldoReferenceBase._ReferenceBase) or
                  isinstance(new_val,waldoReferenceBase._SingleThreadReferenceBase)):
                if new_val.is_value_type():
                    new_val = new_val.get_val(invalid_listener)
                else:
                    new_val = new_val.copy(invalid_listener,True,False)

            self.val[key] = new_val
            
            
    def incorporate_deltas(self,delta_to_incorporate,constructors,active_event):
        '''
        @param {SingleInternalListDelta or SingleInternalMapDelta}
        delta_to_incorporate
        '''
        if delta_to_incorporate.parent_type == VarStoreDeltas.INTERNAL_LIST_CONTAINER:
            to_iter_over = delta_to_incorporate.list_actions
        else:
            to_iter_over = delta_to_incorporate.map_actions

        for action in to_iter_over:
            if action.container_action == VarStoreDeltas.ContainerAction.WRITE_VALUE:
                
                container_written_action = action.write_key
                # added because when serializing and deserializing data with
                # protobufs, not using integer indices, using double indices.
                # This causes a problem on the range commadn below.
                index_to_write_to = self.get_write_key_incorporate_deltas(
                    container_written_action)

                if container_written_action.HasField('what_written_text'):
                    new_val = container_written_action.what_written_text
                elif container_written_action.HasField('what_written_num'):
                    new_val = container_written_action.what_written_num
                elif container_written_action.HasField('what_written_tf'):
                    new_val = container_written_action.what_written_tf
                    
                elif container_written_action.HasField('what_written_map'):
                    new_val = constructors.single_thread_map_constructor(
                        '',self.host_uuid,True)
                    single_map_delta = container_written_action.what_written_map
                    single_map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER                    
                    new_val.incorporate_deltas(single_map_delta,constructors,active_event)
                    
                elif container_written_action.HasField('what_written_list'):
                    new_val = constructors.single_thread_list_constructor('',self.host_uuid,True)
                    single_list_delta = container_written_action.what_written_list
                    single_list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER                    
                    new_val.incorporate_deltas(single_list_delta,constructors,active_event)

                elif container_written_action.HasField('what_written_struct'):
                    new_val = constructors.single_thread_struct_constructor('',self.host_uuid,True,{})
                    single_struct_delta = container_written_action.what_written_struct
                    single_struct_delta.parent_type = VarStoreDeltas.STRUCT_CONTAINER
                    new_val.incorporate_deltas(single_struct_delta,constructors,active_event)
                    
                # actually put new value in list
                self.write_val_on_key(active_event,index_to_write_to,new_val,False)
                

            elif action.container_action == VarStoreDeltas.ContainerAction.ADD_KEY:
                container_added_action = action.added_key

                index_to_add_to = self.get_add_key_incorporate_deltas(container_added_action)

                if container_added_action.HasField('added_what_text'):
                    new_val = container_added_action.added_what_text
                elif container_added_action.HasField('added_what_num'):
                    new_val = container_added_action.added_what_num
                elif container_added_action.HasField('added_what_tf'):
                    new_val = container_added_action.added_what_tf
                    
                elif container_added_action.HasField('added_what_map'):
                    new_val = constructors.single_thread_map_constructor('',self.host_uuid,True)
                    single_map_delta = container_added_action.added_what_map
                    single_map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER
                    new_val.incorporate_deltas(single_map_delta,constructors,active_event)

                elif container_added_action.HasField('added_what_list'):
                    new_val = constructors.single_thread_list_constructor('',self.host_uuid,True)
                    single_list_delta = container_added_action.added_what_list
                    single_list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER
                    new_val.incorporate_deltas(single_list_delta,constructors,active_event)

                elif container_added_action.HasField('added_what_struct'):
                    new_val = constructors.single_thread_struct_constructor('',self.host_uuid,True,{})
                    single_struct_delta = container_added_action.added_what_struct
                    single_struct_delta.parent_type = VarStoreDeltas.STRUCT_CONTAINER
                    new_val.incorporate_deltas(single_struct_delta,constructors,active_event)

                self.handle_added_key_incorporate_deltas(
                    active_event,index_to_add_to,new_val)


            elif action.container_action == VarStoreDeltas.ContainerAction.DELETE_KEY:
                container_deleted_action = action.deleted_key
                index_to_del_from = self.get_delete_key_incorporate_deltas(
                    container_deleted_action)
                self.del_key_called(active_event,index_to_del_from)

                
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

            self.get_val_on_key(active_event,index).incorporate_deltas(
                to_incorporate,constructors,active_event)

        # do not want to send the same information back to the other side.            
        self.version_obj.clear_partner_change_log()


    def del_key_called(self,invalid_listener,key_deleted):
        self.version_obj.del_key(key_deleted)
        del self.val[key_deleted]

        
    @abstractmethod
    def copy_if_peered(self):
        '''
        Peered data only get copied in and out via value instead of by
        reference.  This is to ensure that one endpoint cannot
        directly operate on another endpoint's references.  This
        method returns a copy of self if self is not peered.
        Otherwise, it returns a deep copy of itself.

        We only need a copy_if_peered method for ReferenceContainers
        because non-ReferenceContainers will automatically return
        copied values (Numbers, Texts, TrueFalses) when we get their
        values.
        '''
        pass

    def get_len(self,invalid_listener):
        return len(self.val)

    def get_keys(self,invalid_listener):
        return self.val.keys()

    def contains_key_called(self,invalid_listener,contains_key):
        return contains_key in self.val
        
    def get_val_on_key(self,invalid_listener,key):
        return self.val[key]


    def write_val_on_key(self,invalid_listener,key,new_val,copy_if_peered=True):
        self.version_obj.write_val_on_key(key)

        if self.peered and copy_if_peered:
            # copy the data that's being written in: peereds do not
            # hold references.  If they did, could be trying to
            # synchronize references across multiple hosts.  Eg., if
            # have a peered map of lists, then when insert a list,
            # want to insert copy of list.  If did not, then might be
            # able to share the reference to the inner list between
            # many machines.
            if isinstance(new_val,waldoReferenceBase._ReferenceBase):
                new_val = new_val.copy(invalid_listener,True,False)

        self.val[key] = new_val

