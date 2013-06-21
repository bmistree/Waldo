import waldoReferenceBase


class _ReferenceValue(waldoReferenceBase._ReferenceBase):
    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceBase._ReferenceBase.__init__(
            self,host_uuid,peered,init_val,_ReferenceValueVersion(),
            _ReferenceValueDirtyMapElement)
    

class _ReferenceValueDirtyMapElement(waldoReferenceBase._DirtyMapElement):
    '''
    For now: a precise duplicate of _DirtyMapElement.  Unclear if
    should always be this way.
    '''
    pass


class _ReferenceValueVersion(waldoReferenceBase._ReferenceVersion):
    '''
    The version type used for Waldo's value types: Numbers,
    TrueFalses, Texts.
    '''
    def __init__(self,init_version_num=0):
        self.version_num = init_version_num
        self.has_been_written_to = False

        # For container types (maps, lists, structs), we need to keep
        # track of whether the internal value that each of these are
        # pointing to has been overwritten with a new internal
        # map/list/struct altogether or whether it hasn't.  This way,
        # the other side knows whether the internal deltas it receives
        # are for a brand new internal container or should be applied
        # to the old, existing one.  Any time calling write_val on
        # this _ReferenceBase, set to True.  Any time call
        # serialize..., set to False.
        self.has_been_written_since_last_message = False

        
    def copy(self):
        return _ReferenceValueVersion(self.version_num)
        
    def set_has_been_written_to(self):
        self.has_been_written_to = True
        self.has_been_written_since_last_message = True
                
        
    def update(self,dirty_vtype_version_obj):
        if dirty_vtype_version_obj.has_been_written_to:
            self.version_num += 1
        
    def conflicts(self,dirty_vtype_version_obj):
        '''
        Will conflict if have different version numbers.
        '''
        return (dirty_vtype_version_obj.version_num !=
                self.version_num)

    def modified(self,invalidation_listener):
        return self.has_been_written_to
    
    def update_obj_val_and_version(self,w_obj,val):
        '''
        @param {_WaldoObject} w_obj --- We know that w_obj must be one
        of the value type objects at this point.  That means that if
        we have written to our value, we increment w_obj's version
        number and overwrite its value.  Otherwise, do nothing

        @param {val}
        '''

        if not self.has_been_written_to:
            return

        w_obj.version_obj.update(self)
        w_obj.val = val
        
