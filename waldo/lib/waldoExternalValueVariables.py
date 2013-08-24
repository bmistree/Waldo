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

    def return_internal_val_from_container(self):
        return False
    
    def copy(self,active_event,peered,multi_threaded):
        if multi_threaded:
            return self.MULTI_THREADED_CONSTRUCTOR(
                self.host_uuid,peered,self.get_val(active_event).get_val(active_event))
        else:
            return self.SINGLE_THREADED_CONSTRUCTOR(
                self.host_uuid,peered,self.get_val(active_event).get_val(active_event))
