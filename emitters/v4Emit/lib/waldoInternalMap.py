import waldoReferenceContainerBase



class InternalMap(waldoReferenceContainerBase._ReferenceContainer):
    def __init__(self,init_val):
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,init_val,_InternalMapVersion(),
            _InternalMapDirtyMapElement)
                                                                 

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


