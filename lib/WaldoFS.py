
from wVariables import WaldoExtTextVariable, WaldoTextVariable
import util
from Waldo import _host_uuid

class _WaldoFileVariable(WaldoTextVariable):
    '''
    Used internally.  Should not be used directly by programmer
    '''
    def __init__(self,filename,name,host_uuid,peered=False,init_val=None):
        self.filename = filename
        
        if peered:
            util.logger_assert('Cannot peer a file')

        WaldoTextVariable.__init__(self,name,host_uuid,False,init_val)
        self.flush_file(self.val)
        
    def flush_file(self,to_write):
        filer = file(self.filename,'w')
        filer.write(to_write)
        filer.flush()
        filer.close()

    def complete_commit(self,invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        self.flush_file(dirty_map_elem.val)
        super(_WaldoFileVariable,self).complete_commit(invalid_listener)
        

class WaldoExtFileVariable(WaldoExtTextVariable):
    '''
    Should be used directly by user.
    '''
    
    def __init__(self,filename,init_val=None):
        '''
        @param {bool} dummy_peered --- Should always be false.  cannot
        peer a file.
        '''
        init_val = _WaldoFileVariable(filename,'',_host_uuid,False,init_val)
        WaldoExtTextVariable.__init__(
            self,'',_host_uuid,False,init_val)
