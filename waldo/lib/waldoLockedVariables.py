from waldoLockedObj import WaldoLockedObj
from waldoDataWrapper import ValueTypeDataWrapper
from waldoDataWrapper import ReferenceTypeDataWrapper
from waldoLockedContainer import WaldoLockedContainer

class LockedValueVariable(WaldoLockedObj):
    def __init__(self,host_uuid,peered,init_val):
        super(LockedValueVariable,self).__init__(
            ValueTypeDataWrapper,host_uuid,peered,init_val)

class LockedNumberVariable(LockedValueVariable):
    pass

class LockedTextVariable(LockedValueVariable):    
    pass

class LockedTrueFalseVariable(LockedValueVariable):
    pass


class WaldoLockedMap(WaldoLockedContainer):
    def __init__(self,host_uuid,peered,init_val):
        super(WaldoLockedMap,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)
    
    def add_key(self,active_event,key_added,new_val):
        '''
        Map specific
        '''
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val[key_added] = new_val

class WaldoLockedList(WaldoLockedContainer):

    def __init__(self,host_uuid,peered,init_val):
        super(WaldoLockedMap,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)
    
    def insert_val(self,active_event,where_to_insert,new_val):
        '''
        List specific
        '''
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val.insert(where_to_insert, new_val)
        
    def append_val(self,active_event,new_val):
        '''
        List specific
        '''
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val.append(new_val)
