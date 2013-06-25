import waldoReferenceContainerBase
import waldoReferenceBase
import waldoExecutingEvent

from waldoReferenceContainerBase import delete_key_tuple, is_delete_key_tuple
from waldoReferenceContainerBase import add_key_tuple, is_add_key_tuple
from waldoReferenceContainerBase import write_key_tuple, is_write_key_tuple
from waldoReferenceContainerBase import is_reference_container

import numbers
import util

from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
from waldoObj import WaldoObj

def _map_get_write_key_incorporate_deltas(container_written_action):
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


def _map_get_add_key_incorporate_deltas(container_added_action):
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


def _map_get_delete_key_incorporate_deltas(container_deleted_action):
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

def _map_handle_added_key_incorporate_deltas(
    map_to_write_on,active_event,index_to_add_to,new_val):
    map_to_write_on.write_val_on_key(active_event,index_to_add_to,new_val,False)

def _map_copy_internal_val(map_obj,invalid_listener,peered):
    '''
    Used by WaldoUserStruct when copying it.

    @returns {dict} --- Just want to return a copy of the internal
    dict of this InternalMap.
    '''
    # FIXME: very ugly.

    # always trying to just get internal data from map.  so create
    # a variable that is single threaded. always.    
    single_thread_new_internal_map = map_obj.copy(
        invalid_listener,peered,False)
    internal_dict =  single_thread_new_internal_map.val
    return internal_dict


def _map_de_waldoify(map_obj,invalid_listener):
    '''
    @see _ReferenceBase.de_waldoify
    '''
    keys = map_obj.get_keys(invalid_listener)
    to_return = {}

    for key in keys:
        key = waldoExecutingEvent.de_waldoify(key,invalid_listener)
        val = waldoExecutingEvent.de_waldoify(
            map_obj.get_val_on_key(invalid_listener,key),invalid_listener)

        to_return[key] = val

    return to_return

class InternalMap(waldoReferenceContainerBase._ReferenceContainer):
    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,host_uuid,peered,init_val,_InternalMapVersion(),
            _InternalMapDirtyMapElement)

    def de_waldoify(self,invalid_listener):
        return _map_de_waldoify(self,invalid_listener)
    
    @staticmethod
    def var_type():
        return 'internal map'

    def copy(self,invalid_listener,peered,multi_threaded):
        '''
        @param {} invalid_listener

        @param {bool} peered --- Should the returned copy be peered or
        un-peered

        @param {bool} multi_threaded --- Do we need to use locking on
        the object.  Ie., can the object be accessed from multiple
        threads simultaneously?  (True if yes, False if no.)
        
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

            if is_reference_container(to_copy):
                to_copy = to_copy.copy(invalid_listener,peered,multi_threaded)
            elif isinstance(to_copy,WaldoObj):

                if to_copy.is_value_type():
                    to_copy = to_copy.get_val(invalid_listener)
                else:
                    to_copy = to_copy.copy(invalid_listener,peered,multi_threaded)
                
            new_internal_val[key] = to_copy
            
        if self_to_copy:
            self._unlock()

        if multi_threaded:
            return InternalMap(self.host_uuid,peered,new_internal_val)
        else:
            return SingleThreadInternalMap(
                self.host_uuid,peered,new_internal_val)

    def copy_internal_val(self,invalid_listener,peered):
        return _map_copy_internal_val(self,invalid_listener,peered)

    def get_write_key_incorporate_deltas(self,container_written_action):
        return _map_get_write_key_incorporate_deltas(container_written_action)

    def get_add_key_incorporate_deltas(self,container_added_action):
        return _map_get_add_key_incorporate_deltas(container_added_action)

    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        return _map_get_delete_key_incorporate_deltas(container_deleted_action)

    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        return _map_handle_added_key_incorporate_deltas(
            self,active_event,index_to_add_to,new_val)
    
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

            elif isinstance(map_val,WaldoObj):
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

                    elif isinstance(map_val,WaldoObj):
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

                    elif isinstance(map_val,WaldoObj):
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
            if not isinstance(map_val,WaldoObj):
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


#### SINGLE THREADED VERSION #####

class SingleThreadInternalMap(
    waldoReferenceContainerBase._SingleThreadReferenceContainer):
    
    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceContainerBase._SingleThreadReferenceContainer.__init__(
            self,host_uuid,peered,init_val,_InternalMapVersion())
        
    def de_waldoify(self,invalid_listener):
        return _map_de_waldoify(self,invalid_listener)


    def promote_multithreaded(self,peered):
        '''
        @see promote_multithreaded in waldoReferenceContainerBase.py
        '''
        if self.multithreaded is None:
            promoted_map = {}

            for ind_key in self.val:
                ind_val = self.val[ind_key]
                if isinstance(
                    ind_val,
                    waldoReferenceContainerBase._SingleThreadReferenceContainer):
                    
                    ind_val = ind_val.promote_multithreaded(peered)
                    
                promoted_map[ind_key] = ind_val

            self.multithreaded = InternalMap(
                self.host_uuid,peered,promoted_map)

        return self.multithreaded
            
    
    @staticmethod
    def var_type():
        return 'single thread internal map'
    
    def copy(self,invalid_listener,peered,multi_threaded):
        '''
        Returns a deep copy of the object.
        '''
        # will be used as initial_val when constructing copied
        # InternalMap that we return.
        new_internal_val = {}

        val_to_copy = self.val
            
        for key in val_to_copy:
            to_copy = val_to_copy[key]

            if is_reference_container(to_copy):
                to_copy = to_copy.copy(invalid_listener,peered,multi_threaded)
            elif isinstance(to_copy,WaldoObj):

                if to_copy.is_value_type():
                    to_copy = to_copy.get_val(invalid_listener)
                else:
                    to_copy = to_copy.copy(
                        invalid_listener,peered,multi_threaded)
                
            new_internal_val[key] = to_copy

        if multi_threaded:
            return InternalMap(
                self.host_uuid,peered,new_internal_val)
        else:
            return SingleThreadInternalMap(
                self.host_uuid,peered,new_internal_val)

    def copy_internal_val(self,invalid_listener,peered):
        return _map_copy_internal_val(self,invalid_listener,peered)
    
    def get_write_key_incorporate_deltas(self,container_written_action):
        return _map_get_write_key_incorporate_deltas(container_written_action)

    def get_add_key_incorporate_deltas(self,container_added_action):
        return _map_get_add_key_incorporate_deltas(container_added_action)

    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        return _map_get_delete_key_incorporate_deltas(container_deleted_action)

    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        return _map_handle_added_key_incorporate_deltas(
            self,active_event,index_to_add_to,new_val)
