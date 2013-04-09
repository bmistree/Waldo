import waldoReferenceContainerBase
import waldoReferenceBase
import waldoExecutingEvent

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
        
        self._lock('copy')
        val_to_copy = self.val
        self_to_copy = True
        if invalid_listener.uuid in self._dirty_map:
            self_to_copy = False
            val_to_copy = self._dirty_map[invalid_listener.uuid].val
            
        # if copying from internal: stay within the lock so that
        # nothing else can write to internal while we are.
        if not self_to_copy:
            self._unlock('copy')

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
            self._unlock('copy')

        return InternalMap(self.host_uuid,peered,new_internal_val)


    def copy_internal_val(self,invalid_listener,peered):
        '''
        Used by WaldoUserStruct when copying it.

        @returns {dict} --- Just want to return a copy of the internal
        dict of this InternalMap.
        '''

        # FIXME: very ugly.
        new_internal_map = self.copy(invalid_listener,peered)
        new_internal_map._lock('copy_internal_val')
        new_internal_map._add_invalid_listener(invalid_listener)
        internal_dict =  new_internal_map._dirty_map[invalid_listener.uuid].val
        new_internal_map._unlock('copy_internal_val')
        return internal_dict

    
            
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


