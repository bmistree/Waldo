import waldoReferenceContainerBase
import waldoReferenceBase
import waldoExecutingEvent

from waldoReferenceContainerBase import delete_key_tuple, is_delete_key_tuple
from waldoReferenceContainerBase import add_key_tuple, is_add_key_tuple
from waldoReferenceContainerBase import write_key_tuple, is_write_key_tuple

import numbers
import util
from lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas

class InternalMap(waldoReferenceContainerBase._ReferenceContainer):
    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,host_uuid,peered,init_val,_InternalMapVersion(),
            _InternalMapDirtyMapElement)

    def copy_if_peered(self,invalid_listener):
        '''
        @see waldoReferenceContainerBase._ReferenceContainer
        '''
        if not self.peered:
            return self

        return self.copy(invalid_listener,False)

    
    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        keys = self.get_keys(invalid_listener)
        to_return = {}

        for key in keys:
            key = waldoExecutingEvent.de_waldoify(key,invalid_listener)
            val = waldoExecutingEvent.de_waldoify(
                self.get_val_on_key(invalid_listener,key),invalid_listener)

            to_return[key] = val
            
        return to_return

    
    @staticmethod
    def var_type():
        return 'internal map'
    
    def copy(self,invalid_listener,peered):
        '''
        Returns a deep copy of the object.
        '''
        # will be used as initial_val when constructing copied
        # InternalMap that we return.
        new_internal_val = {}
        
        self._lock()
        val_to_copy = self.val
        self_to_copy = True
        if invalid_listener.uuid in self._dirty_map:
            self_to_copy = False
            val_to_copy = self._dirty_map[invalid_listener.uuid].val
            
        # if copying from internal: stay within the lock so that
        # nothing else can write to internal while we are.
        if not self_to_copy:
            self._unlock()

        for key in val_to_copy:
            to_copy = val_to_copy[key]

            if isinstance(
                to_copy,waldoReferenceContainerBase._ReferenceContainer):
                to_copy = to_copy.copy(invalid_listener,peered)
            elif isinstance(
                to_copy,waldoReferenceBase._ReferenceBase):

                if to_copy.is_value_type():
                    to_copy = to_copy.get_val(invalid_listener)
                else:
                    to_copy = to_copy.copy(invalid_listener,peered)
                
            new_internal_val[key] = to_copy
            
        if self_to_copy:
            self._unlock()

        return InternalMap(self.host_uuid,peered,new_internal_val)


    def copy_internal_val(self,invalid_listener,peered):
        '''
        Used by WaldoUserStruct when copying it.

        @returns {dict} --- Just want to return a copy of the internal
        dict of this InternalMap.
        '''

        # FIXME: very ugly.
        new_internal_map = self.copy(invalid_listener,peered)
        new_internal_map._lock()
        new_internal_map._add_invalid_listener(invalid_listener)
        internal_dict =  new_internal_map._dirty_map[invalid_listener.uuid].val
        new_internal_map._unlock()
        return internal_dict


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
        self.write_val_on_key(active_event,index_to_add_to,new_val,False)

    
class _InternalMapDirtyMapElement(
    waldoReferenceContainerBase._ReferenceContainerDirtyMapElement):
    pass

class _InternalMapVersion(
    waldoReferenceContainerBase._ReferenceContainerVersion):

    def copy(self):
        '''
        @see _ReferenceContainerVersion.copy
        '''
        copy = _InternalMapVersion()
        copy.commit_num = self.commit_num
        return copy

    def add_all_data_to_delta_list(
        self,delta_to_add_to,current_internal_val,action_event):
        '''
        Run through entire map.  Create an add action for each element.
        '''
        for key in current_internal_val.keys():
            map_action = delta_to_add_to.map_actions.add()

            map_action.container_action = VarStoreDeltas.ContainerAction.ADD_KEY
            
            add_action = map_action.added_key
            add_action.parent_type = VarStoreDeltas.CONTAINER_ADDED

            if isinstance(key,numbers.Number):
                add_action.added_key_num = key
            elif util.is_string(key):
                add_action.added_key_text = key
            else:
                add_action.added_key_tf = key
            
            
            # now actually add the value to the map
            map_val = current_internal_val[key]

            if isinstance(map_val,numbers.Number):
                add_action.added_what_num = map_val
            elif util.is_string(map_val):
                add_action.added_what_text = map_val
            elif isinstance(map_val,bool):
                add_action.added_what_tf = map_val

            elif isinstance(
                map_val,waldoReferenceBase._ReferenceBase):

                map_val.serializable_var_tuple_for_network(
                    add_action,'',action_event,True)
    

    def add_to_delta_list(self,delta_to_add_to,current_internal_val,action_event):
        '''
        @param {varStoreDeltas.SingleMapDelta} delta_to_add_to --- 

        We log all operations on this variable 
        '''
        changes_made = False

        # for all keys that were not changed directly, must check
        # whether any potentially nested elements changed.
        keys_affected = {}

        # FIXME: only need to keep track of change log for peered
        # variables.  May be expensive to otherwise.
        for partner_change in self.partner_change_log:
            changes_made = True
            
            # FIXME: no need to transmit overwrites.  but am doing
            # that currently.
            map_action = delta_to_add_to.map_actions.add()

            if is_delete_key_tuple(partner_change):
                map_action.container_action = VarStoreDeltas.ContainerAction.DELETE_KEY
                delete_action = map_action.deleted_key
                
                key = partner_change[1]
                keys_affected[key] = True
                if isinstance(key,numbers.Number):
                    delete_action.deleted_key_num = key
                elif util.is_string(key):
                    delete_action.deleted_key_text = key
                elif isinstance(key,bool):
                    delete_action.deleted_key_tf = key
                #### DEBUG
                else:
                    util.logger_assert('Unknown map key type when serializing')
                #### END DEBUG

            elif is_add_key_tuple(partner_change):
                key = partner_change[1]
                keys_affected[key] = True                
                if key in current_internal_val:
                    # note, key may not be in internal val, for
                    # instance if we had deleted it after adding.
                    # in this case, can ignore the add here.

                    map_action.container_action = VarStoreDeltas.ContainerAction.ADD_KEY
                    add_action = map_action.added_key
                    add_action.parent_type = VarStoreDeltas.CONTAINER_ADDED

                    if isinstance(key,numbers.Number):
                        add_action.added_key_num = key
                    elif util.is_string(key):
                        add_action.added_key_text = key
                    elif isinstance(key,bool):
                        add_action.added_key_tf = key
                    #### DEBUG
                    else:
                        util.logger_assert('Unknown map key type when serializing')
                    #### END DEBUG
                        
                    # now actually add the value to the map
                    map_val = current_internal_val[key]

                    if isinstance(map_val,numbers.Number):
                        add_action.added_what_num = map_val
                    elif util.is_string(map_val):
                        add_action.added_what_text = map_val
                    elif isinstance(map_val,bool):
                        add_action.added_what_tf = map_val

                    elif isinstance(
                        map_val,waldoReferenceBase._ReferenceBase):
                        map_val.serializable_var_tuple_for_network(
                            add_action,'',action_event,
                            # true here because if anything is written
                            # or added, then we must force the entire
                            # copy of it.
                            True)
                    #### DEBUG
                    else:
                        util.logger_assert('Unknown map value type when serializing')
                    #### END DEBUG


            elif is_write_key_tuple(partner_change):
                key = partner_change[1]

                keys_affected[key] = True
                if key in current_internal_val:
                    # note, key may not be in internal val, for
                    # instance if we had deleted it after adding.
                    # in this case, can ignore the add here.
                    map_action.container_action = VarStoreDeltas.ContainerAction.WRITE_VALUE
                    write_action = map_action.write_key
                    write_action.parent_type = VarStoreDeltas.CONTAINER_WRITTEN
                    
                    if isinstance(key,numbers.Number):
                        write_action.write_key_num = key
                    elif util.is_string(key):
                        write_action.write_key_text = key
                    elif isinstance(key,bool):
                        write_action.write_key_tf = key
                    #### DEBUG
                    else:
                        util.logger_assert('Unknown map key type when serializing')
                    #### END DEBUG

                    # now actually add the value to the map
                    map_val = current_internal_val[key]

                    if isinstance(map_val,numbers.Number):
                        write_action.what_written_num = map_val
                    elif util.is_string(map_val):
                        write_action.what_written_text = map_val
                    elif isinstance(map_val,bool):
                        write_action.what_written_tf = map_val

                    elif isinstance(
                        map_val,waldoReferenceBase._ReferenceBase):
                        map_val.serializable_var_tuple_for_network(
                            write_action,'',action_event,
                            # true here because if anything is written
                            # or added, then we must force the entire
                            # copy of it.                            
                            True)

                    #### DEBUG
                    else:
                        util.logger_assert('Unknown map value type when serializing')
                    #### END DEBUG
                        

            #### DEBUG
            else:
                util.logger_assert('Unknown container operation')
            #### END DEBUG


        for map_key in current_internal_val:
            map_val = current_internal_val[map_key]
            if not isinstance(map_val,waldoReferenceBase._ReferenceBase):
                break

            if map_key not in keys_affected:
                # create action
                sub_element_action = delta_to_add_to.sub_element_update_actions.add()
                sub_element_action.parent_type = VarStoreDeltas.SUB_ELEMENT_ACTION

                if isinstance(map_key,numbers.Number):
                    sub_element_action.key_num = map_key
                elif util.is_string(map_key):
                    sub_element_action.key_text = map_key
                else:
                    sub_element_action.key_tf = map_key
                
                if map_val.serializable_var_tuple_for_network(sub_element_action,'',action_event,False):
                    changes_made = True
                else:
                    # no change made to subtree: go ahead and delete added subaction
                    del delta_to_add_to.sub_element_update_actions[-1]

        # clean out change log: do not need to re-send updates for
        # these changes to partner, so can just reset after sending
        # once.
        self.partner_change_log = []

        return changes_made
