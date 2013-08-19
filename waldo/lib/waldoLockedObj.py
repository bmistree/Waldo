import threading
import waldo.lib.util as util

    
class WaldoLockedObj(object):
    '''
    Base class from which all other waldo objects inherit.
    '''
    
    def get_val(self,active_event):
        util.logger_assert('get_val is pure virtual in WaldoLockedObj')

    def set_val(self,active_event,new_val):
        util.logger_assert('set_val is pure virtual in WaldoLockedObj')

    def get_and_reset_has_been_written_since_last_msg(self,active_event):
        '''
        @returns {bool} --- True if the object has been written to
        since we sent the last message.  False otherwise.  (Including
        if event has been preempted.)
        '''
        util.logger_assert(
            'get_and_reset_has_been_written_since_last_msg is ' +
            'pure virtual in WaldoLockedObj')    
        
    def complete_commit(self,active_event):
        util.logger_assert(
            'complete_commit is pure virtual in WaldoLockedObj')    
        
    def is_peered(self):
        util.logger_assert(
            'is_peered is pure virtual in WaldoLockedObj')            
        
    def backout(self,active_event):
        util.logger_assert(
            'backout is pure virtual in WaldoLockedObj')            

    def de_waldoify(self,active_event):
        util.logger_assert(
            'de_waldoify is pure virutal in WaldoLockedObj')

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoLockedObj.WaldoLockedObj
        '''
        util.logger_assert(
            'Serializable var tuple for network is pure virtual ' +
            'in WaldoLockedObj.')

