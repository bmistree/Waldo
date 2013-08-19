import waldo.lib.util as util
from waldo.lib.waldoLockedContainerHelpers import container_incorporate_deltas
from waldo.lib.waldoLockedSingleThreadedObj import SingleThreadedObj
from waldo.lib.waldoLockedMultiThreadedObj import MultiThreadedObj
import pickle

class WaldoLockedContainer(MultiThreadedObj):
        
    def get_val(self,active_event):
        util.logger_assert('Cannot call get val on a container object')
    def set_val(self,active_event,new_val):
        util.logger_assert('Cannot call set val on a container object')        
        
    def get_val_on_key(self,active_event,key):
        wrapped_val = self.acquire_read_lock(active_event)
        return wrapped_val.val[key].get_val(active_event)
        
    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        util.logger_warn('Not handling copy_if_peered: should not copy in this case')
        wrapped_val =  self.acquire_read_lock(active_event)
        return wrapped_val.set_val_on_key(active_event,key,to_write)

    def del_key_called(self,active_event,key_to_delete):
        wrapped_val = self.acquire_write_lock(active_event)
        wrapped_val.del_key(active_event,key_to_delete)

    def get_len(self,active_event):
        wrapped_val = self.acquire_read_lock(active_event)
        return len(wrapped_val.val)
            
    def get_keys(self,active_event):
        wrapped_val = self.acquire_read_lock(active_event)
        return list(wrapped_val.val.keys())

    def contains_key_called(self,active_event,contains_key):
        wrapped_val = self.acquire_read_lock(active_event)
        return contains_key in wrapped_val.val

    def contains_val_called(self,active_event,contains_val):
        wrapped_val = self.acquire_read_lock(active_event)
        return contains_val in wrapped_val.val
    
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):

        util.logger_assert(
            'Still must define serializable_var_tuple_for_network on ' +
            'locked container objects.')

    def de_waldoify(self,active_event):
        wrapped_val = self.acquire_read_lock(active_event)
        return pickle.loads(pickle.dumps(wrapped_val.val))

        
    def incorporate_deltas(self,delta_to_incorporate,constructors,active_event):
        '''
        @param {SingleListDelta or SingleMapDelta} delta_to_incorporate
        
        @param {SingleInternalListDelta or SingleInternalMapDelta}
        delta_to_incorporate

        When a peered or sequence peered container (ie, map, list, or
        struct) is modified by one endpoint, those changes must be
        reflected on the other endpoint.  This method takes the
        changes that one endpoint has made on a container, represented
        by delta_to_incorporate, and applies them (if we can).
        '''
        container_incorporate_deltas(
            self,delta_to_incorporate,constructors,active_event)
        

        
class SingleThreadedLockedContainerVariable(SingleThreadedObj):

    def get_val(self,active_event):
        util.logger_assert('Cannot call get val on a container object')
    def set_val(self,active_event,new_val):
        util.logger_assert('Cannot call set val on a container object')        
        
    def get_val_on_key(self,active_event,key):
        return self.val.val[key].get_val(active_event)

    def set_val_on_key(self,active_event,key,to_write,copy_if_peered=False):
        util.logger_warn('Not handling copy_if_peered: should not copy in this case')
        return self.val.set_val_on_key(active_event,key,to_write)

    def del_key_called(self,active_event,key_to_delete):
        self.val.del_key(active_event,key_to_delete)

    def get_len(self,active_event):
        return len(self.val.val)
            
    def get_keys(self,active_event):
        return list(self.val.val.keys())

    def contains_key_called(self,active_event,contains_key):
        return contains_key in self.val.val

    def contains_val_called(self,active_event,contains_val):
        return contains_val in self.val.val
    
    def get_dirty_wrapped_val(self,active_event):
        '''
        @see waldoLockedObj.waldoLockedObj
        '''
        return self.val

    def de_waldoify(self,active_event):
        return pickle.loads(pickle.dumps(self.val.val))
    
    def incorporate_deltas(self,delta_to_incorporate,constructors,active_event):
        '''
        @param {SingleListDelta or SingleMapDelta} delta_to_incorporate
        
        @param {SingleInternalListDelta or SingleInternalMapDelta}
        delta_to_incorporate

        When a peered or sequence peered container (ie, map, list, or
        struct) is modified by one endpoint, those changes must be
        reflected on the other endpoint.  This method takes the
        changes that one endpoint has made on a container, represented
        by delta_to_incorporate, and applies them (if we can).
        '''
        container_incorporate_deltas(
            self,delta_to_incorporate,constructors,active_event)
