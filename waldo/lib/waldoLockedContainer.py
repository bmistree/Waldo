from waldoLockedObj import WaldoLockedObj

class WaldoLockedContainer(WaldoLockedObj):
        
    def get_val(self,active_event):
        util.logger_assert('Cannot call get val on a container object')
    def set_val(self,active_event,new_val):
        util.logger_assert('Cannot call set val on a container object')        
        
    def get_val_on_key(self,active_event,key):
        wrapped_val = self.acquire_read_lock(active_event)
        return wrapped_val.val[key].get_val(active_event)
        
    def set_val_on_key(self,active_event,key,to_write):
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

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        
        util.logger_assert(
            'Still must define serializable_var_tuple_for_network on ' +
            'locked container objects.')
    
