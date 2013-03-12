from waldoReferenceValue import _ReferenceValue
from waldoInternalList import InternalList
from waldoInternalMap import InternalMap
from abc import abstractmethod
import util
import waldoReferenceBase
import numbers

class _WaldoVariable(_ReferenceValue):
    def __init__(self,name,host_uuid,peered,init_val):
        self.name = name
        _ReferenceValue.__init__(self,host_uuid,peered,init_val)

    @abstractmethod
    def is_value_type(self):
        util.logger_assert(
            'Cannot call pure virtual method is_value_type ' +
            'on _WaldoVariable.')

    @staticmethod
    def var_type():
        util.logger_assert(
            'Cannot call pure virtual method var_type ' +
            'on _WaldoVariable.')        
        


def de_waldoify_for_return(val):
    # FIXME: actually write
    return val

        

### VALUE TYPES
class WaldoNumVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=0):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoNumVariable'

    def is_value_type(self):
        return True

    
    def copy(self,invalid_listener,peered):
        return WaldoNumVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)
    
    
    
class WaldoTextVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=''):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoTextVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        return WaldoTextVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))


    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)

    
        
class WaldoTrueFalseVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=False):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoTrueFalseVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        return WaldoTrueFalseVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)

    
    

### CONTAINER TYPES        
class WaldoMapVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = InternalMap(host_uuid,peered,{})
        else:
            if isinstance(init_val,dict):
                init_val = InternalMap(host_uuid,peered,init_val)
                
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)

        
    @staticmethod
    def var_type():
        return 'WaldoMapVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoMapVariable(
            self.name,self.host_uuid,peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,waldoReferenceBase._ReferenceBase):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val

    
class WaldoListVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = InternalList(host_uuid,peered,[])
        else:
            if isinstance(init_val,list):
                init_val = InternalList(host_uuid,peered,init_val)
            
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
    
    @staticmethod
    def var_type():
        return 'WaldoListVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoListVariable(
            self.name,self.host_uuid,peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,waldoReferenceBase._ReferenceBase):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val

