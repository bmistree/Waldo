from waldo.lib.waldoLockedObj import WaldoLockedObj
import numbers
from waldo.lib.waldoDataWrapper import ReferenceTypeDataWrapper
from waldo.lib.waldoLockedContainer import WaldoLockedContainer
import waldo.lib.util as util
from waldo.lib.waldoLockedSingleThreadMultiThread import MultiThreadedObj
from waldo.lib.waldoLockedSingleThreadMultiThread import SingleThreadedObj
from waldo.lib.waldoLockedVariablesHelper import LockedValueVariable

def ensure_locked_obj(new_val,host_uuid):
    '''
    @param {Anything} new_val --- If new_val is a non-Waldo object,
    convert it to a Waldo object.  Otherwise, return it unchanged.

    This method is used to ensure that each individual entry in a
    map/list is also protected.
    '''
    if isinstance(new_val , WaldoLockedObj):
        return new_val

    if isinstance(new_val, bool):
        return LockedTrueFalseVariable(host_uuid,False,new_val)
    elif isinstance(new_val, numbers.Number):
        return LockedNumberVariable(host_uuid,False,new_val)
    elif util.is_string(new_val):
        return LockedTextVariable(host_uuid,False,new_val)
    else:
        util.logger_assert('Unknown object type.')
    


class LockedNumberVariable(LockedValueVariable):
    pass

class LockedTextVariable(LockedValueVariable):    
    pass

class LockedTrueFalseVariable(LockedValueVariable):
    pass


class LockedMapVariable(WaldoLockedContainer):
    def __init__(self,host_uuid,peered,init_val):
        super(LockedMapVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)

    def add_key(self,active_event,key_added,new_val):
        '''
        Map specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val[key_added] = new_val

class LockedListVariable(WaldoLockedContainer):

    def __init__(self,host_uuid,peered,init_val):
        super(LockedListVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,init_val)
    
    def insert_val(self,active_event,where_to_insert,new_val):
        '''
        List specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val.insert(where_to_insert, new_val)
        
    def append_val(self,active_event,new_val):
        '''
        List specific
        '''
        new_val = ensure_locked_obj(new_val,self.host_uuid)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.val.append(new_val)
