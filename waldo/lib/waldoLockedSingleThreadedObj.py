import waldo.lib.util as util
from waldo.lib.waldoLockedObj import WaldoLockedObj

class SingleThreadedObj(WaldoLockedObj):
    def __init__(self,data_wrapper_constructor,host_uuid,peered,init_val):
        '''
        @param {DataWrapper object} --- Used to store dirty values.
        For value types, can just use ValueTypeDataWrapper.  For
        reference types, should use ReferenceTypeDataWrpper.
        '''
        self.data_wrapper_constructor = data_wrapper_constructor
        self.uuid = util.generate_uuid()
        
        self.host_uuid = host_uuid
        self.peered = peered

        # still using data wrappers because data wrappers keep track
        # whether this variable was written since last message.
        self.val = self.data_wrapper_constructor(init_val,self.peered)


    def get_val(self,active_event):
        return self.val.val

    def set_val(self,active_event,new_val):
        '''
        Called as an active event runs code.
        '''
        self.val.write(new_val)


    def get_and_reset_has_been_written_since_last_msg(self,active_event):
        '''
        @returns {bool} --- True if the object has been written to
        since we sent the last message.  False otherwise.  (Including
        if event has been preempted.)
        '''
        # check if active event even has ability to write to variable
        has_been_written = self.val.get_and_reset_has_been_written_since_last_msg()
        
        return has_been_written

    def de_waldoify(self,active_event):
        return self.val.de_waldoify(active_event)
        
    def complete_commit(self,active_event):
        '''
        Nothing to do when completing commit: no other transaction
        will ever read this value, so have no work to do.
        '''
        return

    def is_peered(self):
        return self.peered
        
    def backout(self,active_event):
        '''
        Do not actually need to remove changes to this variable: no
        other transaction will ever see the changes we made + this
        transaction will just create a new single threaded variable.
        '''
        return

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoLockedObj.WaldoLockedObj
        '''
        util.logger_assert(
            'Serializable var tuple for network is pure virtual ' +
            'in SingleThreadedObj.')
                
    
