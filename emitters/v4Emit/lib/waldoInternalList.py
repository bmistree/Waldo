import waldoReferenceContainerBase
import util

class InternalList(waldoReferenceContainerBase._ReferenceContainer):

    def __init__(self,init_val):
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,init_val,_InternalListVersion(),
            _InternalListDirtyMapElement)
    
    def add_key(self,invalid_listener,key,new_val):
        util.logger_assert(
            'Cannot call add_key on a list')

    def get_keys(self,invalid_listener):
        util.logger_assert(
            'Cannot call get_keys on a list')
        
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
        dirty_elem.append_val(new_val)
        self._unlock()
    

class _InternalListDirtyMapElement(
    waldoReferenceContainerBase._ReferenceContainerDirtyMapElement):    

    def add_key(self,key,new_val):
        util.logger_assert(
            'Cannot call add_key on a list')

    def del_key(self,key):
        self.version_obj.del_key_list(key,len(self.val))
        del self.val[key]
        
    def append_val(self,new_val):
        # adding key at end.
        self.version_obj.add_key(len(self.val))
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

        for shifted_write_index in range(del_index,length_of_list_before_del):
            self.deleted_keys[shifted_write_index] = self.commit_num
        
        
