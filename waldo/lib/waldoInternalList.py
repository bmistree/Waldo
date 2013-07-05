import waldoReferenceContainerBase
import util
import waldoReferenceBase
import singleThreadReference
from waldoReferenceContainerBase import is_reference_container

import waldoExecutingEvent
from waldoReferenceContainerBase import delete_key_tuple, is_delete_key_tuple
from waldoReferenceContainerBase import add_key_tuple, is_add_key_tuple
from waldoReferenceContainerBase import write_key_tuple, is_write_key_tuple
import numbers
from waldoObj import WaldoObj

from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas


def _list_get_write_key_incorporate_deltas(container_written_action):
    return int(container_written_action.write_key_num)

def _list_get_add_key_incorporate_deltas(container_added_action):
    return int(container_added_action.added_key_num)    

def _list_get_delete_key_incorporate_deltas(container_deleted_action):
    return int(container_deleted_action.deleted_key_num)

def _list_handle_added_key_incorporate_deltas(
    list_obj,active_event,index_to_add_to,new_val):
    list_obj.insert_into(active_event,index_to_add_to,new_val,False)

def _list_de_waldoify(list_obj,invalid_listener):
    '''
    @see _ReferenceBase.de_waldoify
    '''
    internal_len = list_obj.get_len(invalid_listener)
    to_return = []
    for index in range(0, internal_len):
        val = list_obj.get_val_on_key(invalid_listener,index)
        de_waldoed_val = waldoExecutingEvent.de_waldoify(
            val, invalid_listener)

        to_return.append(de_waldoed_val)

    return to_return
    
    
class InternalList(waldoReferenceContainerBase._ReferenceContainer):

    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,host_uuid,peered,init_val,_InternalListVersion(),
            _InternalListDirtyMapElement)

    def add_key(self,invalid_listener,key,new_val):
        util.logger_assert('Cannot call add_key on a list')

    def get_keys(self,invalid_listener):
        util.logger_assert('Cannot call get_keys on a list')

    @staticmethod
    def var_type():
        return 'internal list'

    def get_val_on_key(self,invalid_listener,key):
        key = int(key)
        return super(InternalList, self).get_val_on_key(invalid_listener,key)

    def de_waldoify(self,invalid_listener):
        return _list_de_waldoify(self,invalid_listener)


    def contains_val_called(self,invalid_listener,val):
        '''
        Run through internal list, check if any element in the list is
        equal to val.  (Note == will only work with value types.)
        '''
        found = False

        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        self._unlock()

        # essentially, just iterate through each element of list
        # looking for a matching val.
        for i in range(0,dirty_elem.get_len()):
            if dirty_elem.get_val_on_key(i) == val:
                found=True
                break


        return found
    
    def insert_into(self,invalid_listener, index, val,copy_if_peered=True):
        # this will get overwritten later.  for now, just append some
        # val

        # FIXME: This looks horribly inefficient
        self.append_val(invalid_listener,val)

        len_list = self.get_len(invalid_listener)
        for i in range(len_list-1,index,-1):
            self.write_val_on_key(
                invalid_listener,
                i,self.get_val_on_key(invalid_listener,i-1))

        self.write_val_on_key(invalid_listener,index,val)

    def get_write_key_incorporate_deltas(self,container_written_action):
        return _list_get_write_key_incorporate_deltas(container_written_action)

    def get_add_key_incorporate_deltas(self,container_added_action):
        return _list_get_add_key_incorporate_deltas(container_added_action)

    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        return _list_get_delete_key_incorporate_deltas(container_deleted_action)
    
    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        
        return _list_handle_added_key_incorporate_deltas(
            self,active_event,index_to_add_to,new_val)
    

    def contains_key(self,invalid_listener, key):
        util.logger_assert(
            'Cannot call contains_key on list')


    def append_val(self,invalid_listener,new_val):
        '''
        When we append, we insert at the end of the list.
        Changes contains, len, keys.
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        dirty_elem.append_val(new_val,invalid_listener,self.peered)
        if self.peered:
            invalid_listener.add_peered_modified()
        self._unlock()

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
        new_internal_val = []

        # a peered internal map may point to values or it may point to
        # _ReferenceContainers.  (It may not point to non
        # _ReferenceContainer _WaldoObjects because we disallow
        # externals as value types for maps and lists.)
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

        for to_copy in val_to_copy:
            # if it's not a _ReferenceContainer, then it must just
            # have a value type.  (See comment after
            # new_internal_val.)
            if is_reference_container(to_copy):
                to_copy = to_copy.copy(invalid_listener,peered,multi_threaded)

            elif isinstance(to_copy, WaldoObj):

                if to_copy.is_value_type():
                    to_copy = to_copy.get_val(invalid_listener)
                else:
                    to_copy = to_copy.copy(invalid_listener,peered,multi_threaded)

            new_internal_val.append(to_copy)

        if self_to_copy:
            self._unlock()

        if multi_threaded:
            return InternalList(
                self.host_uuid,peered,new_internal_val)
        else:
            return SingleThreadInternalList(
                self.host_uuid,peered,new_internal_val)            



class _InternalListDirtyMapElement(
    waldoReferenceContainerBase._ReferenceContainerDirtyMapElement):

    def add_key(self,key,new_val,invalid_listener):
        util.logger_assert(
            'Cannot call add_key on a list')

    def del_key(self,key):
        self.version_obj.del_key_list(key,len(self.val))
        if not self.written_at_least_once:
            self.written_at_least_once = True
            self.val = self.waldo_reference._non_waldo_copy()

        del self.val[key]
        
    def append_val(self,new_val,invalid_listener,peered):
        # adding key at end.
        self.version_obj.add_key(len(self.val))

        # if we are peered, then we want to assign into ourselves a
        # copy of the object, not the object itself.  This will only
        # be a problem for container types.  Non-container types
        # already have the semantics that they will be copied on read.
        # (And we throw an error if a peered variable has a container
        # with externals inside of it.)
        if peered:
            if is_reference_container(new_val):
                new_val = new_val.copy(invalid_listener,True,True)

            elif isinstance(new_val, WaldoObj):
                if new_val.is_value_type():
                    new_val = new_val.get_val(invalid_listener)
                else:
                    new_val = new_val.copy(invalid_listener,True,True)

        if not self.written_at_least_once:
            self.written_at_least_once = True
            self.val = self.waldo_reference._non_waldo_copy()

        self.val.append(new_val)


class _InternalListVersion(
    waldoReferenceContainerBase._ReferenceContainerVersion):

    def del_key(self,to_del):
        util.logger_assert(
            'Cannot call del_key on list.  Use del_key_list instead.')

    def copy(self):
        '''
        @see _ReferenceContainerVersion.copy
        '''
        copy = _InternalListVersion()
        copy.commit_num = self.commit_num
        return copy

    def del_key_list(self,del_index,length_of_list_before_del):
        '''
        When we delete an element:
          * add a delete on del_index

          * make a write from all elements from del_index until
            length_of_list_before_del - 1.  This is because when you
            delete a value from the middle of a list all the other
            values shift downwards.
        '''

        self.deleted_keys[del_index] = self.commit_num

        # FIXME: should only append to change log if peered.
        self.partner_change_log.append(delete_key_tuple(del_index))

        for shifted_write_index in range(del_index,length_of_list_before_del):
            self.deleted_keys[shifted_write_index] = self.commit_num


    def add_all_data_to_delta_list(
        self,delta_to_add_to,current_internal_val,action_event):
        '''
        Run through entire list.  Create an add action for each element.
        '''

        for key in range(0,len(current_internal_val)):
            list_action = delta_to_add_to.list_actions.add()

            list_action.container_action = VarStoreDeltas.ContainerAction.ADD_KEY

            add_action = list_action.added_key
            add_action.parent_type = VarStoreDeltas.CONTAINER_ADDED
            add_action.added_key_num = key

            # now actually add the value to the map
            list_val = current_internal_val[key]

            if isinstance(list_val,numbers.Number):
                add_action.added_what_num = list_val
            elif util.is_string(list_val):
                add_action.added_what_text = list_val
            elif isinstance(list_val,bool):
                add_action.added_what_tf = list_val

            elif isinstance(list_val,WaldoObj):

                list_val.serializable_var_tuple_for_network(
                    add_action,'',action_event,True)


    def add_to_delta_list(self,delta_to_add_to,current_internal_val,action_event):
        '''
        @param {varStoreDeltas.SingleListDelta} delta_to_add_to ---

        @param {list} current_internal_val --- The internal val of the action event.

        @param {_InvalidationListener} action_event

        @returns {bool} --- Returns true if have any changes to add false otherwise.
        '''
        modified_indices = {}

        changes_made = False

        # FIXME: only need to keep track of change log for peered
        # variables.  May be expensive to otherwise.
        for partner_change in self.partner_change_log:
            changes_made = True

            # FIXME: no need to transmit overwrites.  but am doing
            # that currently.
            list_action = delta_to_add_to.list_actions.add()

            if is_delete_key_tuple(partner_change):
                list_action.container_action = VarStoreDeltas.ContainerAction.DELETE_KEY
                delete_action = list_action.deleted_key
                key = partner_change[1]
                modified_indices[key] = True
                delete_action.deleted_key_num = key


            elif is_add_key_tuple(partner_change):
                key = partner_change[1]
                modified_indices[key] = True

                if key < len(current_internal_val):
                    # note, key may not be in internal val, for
                    # instance if we had deleted it after adding.
                    # in this case, can ignore the add here.

                    list_action.container_action = VarStoreDeltas.ContainerAction.ADD_KEY
                    add_action = list_action.added_key
                    add_action.parent_type = VarStoreDeltas.CONTAINER_ADDED
                    add_action.added_key_num = key

                    # now actually add the value to the map
                    list_val = current_internal_val[key]

                    if isinstance(list_val,numbers.Number):
                        add_action.added_what_num = list_val
                    elif util.is_string(list_val):
                        add_action.added_what_text = list_val
                    elif isinstance(list_val,bool):
                        add_action.added_what_tf = list_val

                    elif isinstance(list_val,WaldoObj):
                        
                        list_val.serializable_var_tuple_for_network(
                            add_action,'',action_event,
                            # true here because if anything is written
                            # or added, then we must force the entire
                            # copy of it.
                            True)

                    #### DEBUG
                    else:
                        util.logger_assert('Unknown list value type when serializing')
                    #### END DEBUG

            elif is_write_key_tuple(partner_change):
                key = partner_change[1]
                modified_indices[key] = True

                if key < len(current_internal_val):
                    list_action.container_action = VarStoreDeltas.ContainerAction.WRITE_VALUE
                    write_action = list_action.write_key

                    write_action.parent_type = VarStoreDeltas.CONTAINER_WRITTEN
                    write_action.write_key_num = key

                    list_val = current_internal_val[key]
                    if isinstance(list_val,numbers.Number):
                        write_action.what_written_num = list_val
                    elif util.is_string(list_val):
                        write_action.what_written_text = list_val
                    elif isinstance(list_val,bool):
                        write_action.what_written_tf = list_val
                    elif isinstance(list_val,WaldoObj):
                        list_val.serializable_var_tuple_for_network(
                            write_action,'',action_event,
                            # true here because if anything is written
                            # or added, then we must force the entire
                            # copy of it.
                            True)

                    #### DEBUG
                    else:
                        util.logger_assert('Unknown list type')
                    #### END DEBUG


            #### DEBUG
            else:
                util.logger_assert('Unknown container operation')
            #### END DEBUG

        for index in range(0,len(current_internal_val)):
            list_val = current_internal_val[index]

            if not isinstance(list_val,WaldoObj):
                break

            if index not in modified_indices:
                # create action
                sub_element_action = delta_to_add_to.sub_element_update_actions.add()
                sub_element_action.parent_type = VarStoreDeltas.SUB_ELEMENT_ACTION

                sub_element_action.key_num = index

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

class SingleThreadInternalList(
    waldoReferenceContainerBase._SingleThreadReferenceContainer):

    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceContainerBase._SingleThreadReferenceContainer.__init__(
            self,host_uuid,peered,init_val,_InternalListVersion())

    def add_key(self,invalid_listener,key,new_val):
        util.logger_assert('Cannot call add_key on a list')

    def get_keys(self,invalid_listener):
        util.logger_assert('Cannot call get_keys on a list')
        
    @staticmethod
    def var_type():
        return 'single thread internal list'

    def de_waldoify(self,invalid_listener):
        return _list_de_waldoify(self,invalid_listener)

    def promote_multithreaded(self,peered):
        '''
        @see promote_multithreaded in waldoReferenceContainerBase.py
        '''
        if self.multithreaded is None:
            promoted_list = []
            for ind_val in self.val:
                if isinstance(
                    ind_val,
                    waldoReferenceContainerBase._SingleThreadReferenceContainer):
                    
                    ind_val = ind_val.promote_multithreaded(peered)
                    
                promoted_list.append(ind_val)          

            self.multithreaded = InternalList(
                self.host_uuid,peered,promoted_list)

        return self.multithreaded
    
    def contains_val_called(self,invalid_listener,val):
        '''
        Run through internal list, check if any element in the list is
        equal to val.  (Note == will only work with value types.)
        '''
        found = False

        # essentially, just iterate through each element of list
        # looking for a matching val.
        for i in range(0,self.get_len(invalid_listener)):
            if self.get_val_on_key(invalid_listener,i) == val:
                found=True
                break

        return found

    def get_write_key_incorporate_deltas(self,container_written_action):
        return _list_get_write_key_incorporate_deltas(container_written_action)

    def get_add_key_incorporate_deltas(self,container_added_action):
        return _list_get_add_key_incorporate_deltas(container_added_action)

    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        return _list_get_delete_key_incorporate_deltas(container_deleted_action)
    
    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        return _list_handle_added_key_incorporate_deltas(
            self,active_event,index_to_add_to,new_val)

    def insert_into(self,invalid_listener, index, val,copy_if_peered=True):
        # this will get overwritten later.  for now, just append some
        # val

        # FIXME: This looks horribly inefficient
        self.append_val(invalid_listener,val)

        len_list = self.get_len(invalid_listener)
        for i in range(len_list-1,index,-1):
            self.write_val_on_key(
                invalid_listener,
                i,self.get_val_on_key(invalid_listener,i-1))
            
        self.write_val_on_key(invalid_listener,index,val)

        
    def contains_key(self,invalid_listener, key):
        util.logger_assert(
            'Cannot call contains_key on list')
        
    def append_val(self,invalid_listener,new_val):
        '''
        When we append, we insert at the end of the list.
        Changes contains, len, keys.
        '''
        # adding key at end.
        self.version_obj.add_key(len(self.val))

        # if we are peered, then we want to assign into ourselves a
        # copy of the object, not the object itself.  This will only
        # be a problem for container types.  Non-container types
        # already have the semantics that they will be copied on read.
        # (And we throw an error if a peered variable has a container
        # with externals inside of it.)
        if self.peered:

            if is_reference_container(new_val):
                new_val = new_val.copy(invalid_listener,True,True)

            elif isinstance(new_val,WaldoObj):
                
                if new_val.is_value_type():
                    new_val = new_val.get_val(invalid_listener)
                else:
                    new_val = new_val.copy(invalid_listener,True,True)
                    
        self.val.append(new_val)


    def copy(self,invalid_listener,peered,multi_threaded):
        # will be used as initial_val when constructing copied
        # InternalMap that we return.
        new_internal_val = []
        
        # a peered internal map may point to values or it may point to
        # _ReferenceContainers.  (It may not point to non
        # _ReferenceContainer _WaldoObjects because we disallow
        # externals as value types for maps and lists.)
        val_to_copy = self.val
            

        for to_copy in val_to_copy:
            # if it's not a _ReferenceContainer, then it must just
            # have a value type.  (See comment after
            # new_internal_val.)
            if is_reference_container(to_copy):

                to_copy = to_copy.copy(
                    invalid_listener,peered,multi_threaded)

            elif isinstance(to_copy,WaldoObj):

                if to_copy.is_value_type():
                    to_copy = to_copy.get_val(invalid_listener)
                else:
                    to_copy = to_copy.copy(
                        invalid_listener,peered,multi_threaded)
                
            new_internal_val.append(to_copy)


        if multi_threaded:
            return InternalList(
                self.host_uuid,peered,new_internal_val)
        else:
            return SingleThreadInternalList(
                self.host_uuid,peered,new_internal_val)


    def get_val_on_key(self,invalid_listener,key):
        key = int(key)
        return super(SingleThreadInternalList, self).get_val_on_key(invalid_listener,key)
        
    def del_key_called(self,invalid_listener,key_deleted):
        self.version_obj.del_key_list(key_deleted,len(self.val))
        del self.val[key_deleted]
