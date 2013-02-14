import waldoReferenceContainerBase
import waldoReferenceBase


class InternalMap(waldoReferenceContainerBase._ReferenceContainer):
    def __init__(self,peered,init_val):
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,peered,init_val,_InternalMapVersion(),
            _InternalMapDirtyMapElement)

    def copy_if_peered(self,invalid_listener):
        '''
        @see waldoReferenceContainerBase._ReferenceContainer
        '''
        if not self.peered:
            return self

        return self.copy(invalid_listener,False)

    def copy(self,invalid_listener,peered):
        # will be used as initial_val when constructing copied
        # InternalMap that we return.
        new_internal_val = {}
        
        self._lock()
        val_to_copy = self.val
        self_to_copy = True
        if invalid_listener.uuid in self._dirty_map:
            self_to_copy = False
            val_to_copy = self.dirty_map[invalid_listener.uuid].val
            
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
                to_copy = to_copy.get_val(invalid_listener)
                
            new_internal_val[key] = to_copy
            
        if self_to_copy:
            self._unlock()

        return InternalMap(False,new_internal_val)
        
            
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


