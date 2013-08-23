from waldo.lib.waldoLockedContainer import WaldoLockedContainer
from waldo.lib.waldoLockedContainer import SingleThreadedLockedContainer
from waldo.lib.waldoLockedInternalListBase import InternalListBaseClass
from waldo.lib.waldoLockedInternalMapBase import InternalMapBaseClass
from waldo.lib.waldoLockedInternalStructBase import InternalStructBaseClass
from waldo.lib.waldoDataWrapper import ReferenceTypeDataWrapper


################## STRUCTS ########################

class LockedInternalStructVariable(WaldoLockedContainer,InternalStructBaseClass):
    def __init__(self,ensure_locked_obj,host_uuid,peered,init_val=None):
        self.ensure_locked_obj = ensure_locked_obj
        
        super(LockedInternalStructVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,{})
        
        if init_val is not None:
            # initialize with new data
            for key in init_val.keys():
                val = self.ensure_locked_obj(init_val[key],self.host_uuid,False)
                self.val.add_key(None,key,val,True)

    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        '''
        Struct specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,False)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.add_key(active_event,key_added,new_val,incorporating_deltas)

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        return InternalStructBaseClass.serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        to_write = self.ensure_locked_obj(to_write,self.host_uuid,False)
        return super (LockedInternalStructVariable,self).set_val_on_key(
            active_event,key,to_write,copy_if_peered)

class SingleThreadedLockedInternalStructVariable(
    SingleThreadedLockedContainer, InternalStructBaseClass):
    
    def __init__(self,ensure_locked_obj,host_uuid,peered,init_val=None):
        self.ensure_locked_obj = ensure_locked_obj        
        super(SingleThreadedLockedInternalStructVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,{})

        if init_val is not None:
            # initialize with new data
            for key in init_val.keys():
                val = self.ensure_locked_obj(init_val[key],self.host_uuid,True)
                self.val.add_key(None,key,val,True)

        
    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        '''
        Map specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,True)
        self.val.add_key(active_event,key_added,new_val,incorporating_deltas)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        to_write = self.ensure_locked_obj(to_write,self.host_uuid,True)
        return super (SingleThreadedLockedInternalStructVariable,self).set_val_on_key(
            active_event,key,to_write,copy_if_peered)
        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        return InternalStructBaseClass.serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)


    
########### MAPS #####################
    
class LockedInternalMapVariable(WaldoLockedContainer,InternalMapBaseClass):
    def __init__(self,ensure_locked_obj,host_uuid,peered,init_val=None):
        self.ensure_locked_obj = ensure_locked_obj
        
        super(LockedInternalMapVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,{})
        
        if init_val is not None:
            # initialize with new data
            for key in init_val.keys():
                val = self.ensure_locked_obj(init_val[key],self.host_uuid,False)
                self.val.add_key(None,key,val,True)


    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        '''
        Map specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,False)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.add_key(active_event,key_added,new_val,incorporating_deltas)

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        return InternalMapBaseClass.serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        to_write = self.ensure_locked_obj(to_write,self.host_uuid,False)
        return super (LockedInternalMapVariable,self).set_val_on_key(
            active_event,key,to_write,copy_if_peered)
    

class SingleThreadedLockedInternalMapVariable(
    SingleThreadedLockedContainer, InternalMapBaseClass):
    
    def __init__(self,ensure_locked_obj,host_uuid,peered,init_val=None):
        self.ensure_locked_obj = ensure_locked_obj        
        super(SingleThreadedLockedInternalMapVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,{})

        if init_val is not None:
            # initialize with new data
            for key in init_val.keys():
                val = self.ensure_locked_obj(init_val[key],self.host_uuid,True)
                self.val.add_key(None,key,val,True)

        
    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        '''
        Map specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,True)
        self.val.add_key(active_event,key_added,new_val,incorporating_deltas)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        to_write = self.ensure_locked_obj(to_write,self.host_uuid,True)
        return super (SingleThreadedLockedInternalMapVariable,self).set_val_on_key(
            active_event,key,to_write,copy_if_peered)
        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        return InternalMapBaseClass.serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)


############# LISTS ##################    

class LockedInternalListVariable(WaldoLockedContainer,InternalListBaseClass):

    def __init__(self,ensure_locked_obj,host_uuid,peered,init_val=None):
        self.ensure_locked_obj = ensure_locked_obj        
        super(LockedInternalListVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,[])

        if init_val is not None:
            # initialize with new data
            for key in range(0,len(init_val)):
                val = self.ensure_locked_obj(init_val[key],self.host_uuid,False)
                self.val.append(None,val,True)

        
    def insert_val(self,active_event,where_to_insert,new_val,incorporating_deltas=False):
        '''
        List specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,False)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.insert(active_event,where_to_insert,new_val,incorporating_deltas)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        to_write = self.ensure_locked_obj(to_write,self.host_uuid,False)
        return super (LockedInternalListVariable,self).set_val_on_key(
            active_event,key,to_write,copy_if_peered)
        
    def append_val(self,active_event,new_val):
        '''
        List specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,False)
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.append(active_event,new_val)

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        return InternalListBaseClass.serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)


class SingleThreadedLockedInternalListVariable(
    SingleThreadedLockedContainer, InternalListBaseClass):

    def __init__(self,ensure_locked_obj,host_uuid,peered,init_val=None):
        self.ensure_locked_obj = ensure_locked_obj        
        super(SingleThreadedLockedInternalListVariable,self).__init__(
            ReferenceTypeDataWrapper,host_uuid,peered,[])

        if init_val is not None:
            # initialize with new data
            for key in range(0,len(init_val)):
                val = self.ensure_locked_obj(init_val[key],self.host_uuid,True)
                self.val.append(None,val,True)


    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        to_write = self.ensure_locked_obj(to_write,self.host_uuid,True)
        return super (SingleThreadedLockedInternalListVariable,self).set_val_on_key(
            active_event,key,to_write,copy_if_peered)
        
    def insert_val(self,active_event,where_to_insert,new_val,incorporating_deltas=False):
        '''
        List specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,True)
        self.val.insert(active_event,where_to_insert,new_val,incorporating_deltas)

    def append_val(self,active_event,new_val):
        '''
        List specific
        '''
        new_val = self.ensure_locked_obj(new_val,self.host_uuid,True)
        self.val.append(active_event,new_val)

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        return InternalListBaseClass.serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)
        
