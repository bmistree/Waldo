from waldo.lib.waldoLockedValueVariablesHelper import LockedValueVariable

def is_external(val):
    return isinstance(val,WaldoExternalVariable)

class WaldoExternalVariable(object):
    pass


class WaldoExternalValueVariable(LockedValueVariable,WaldoExternalVariable):
    def de_waldoify(self,active_event):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        wrapped_val = self.acquire_read_lock(active_event)
        return wrapped_val.val.de_waldoify(active_event)
    
