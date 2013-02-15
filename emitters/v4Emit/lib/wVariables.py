from waldoReferenceValue import _ReferenceValue
from waldoInternalList import InternalList
from waldoInternalMap import InternalMap

### VALUE TYPES
class WaldoNumVariable(_ReferenceValue):
    def __init__(self,peered=False,init_val=0):
        _ReferenceValue.__init__(self,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoNumVariable'

    def is_value_type(self):
        return True

    
    def copy(self,invalid_listener,peered):
        return WaldoNumVariable(
            peered,self.get_val(invalid_listener))
                                
    
    
class WaldoTextVariable(_ReferenceValue):
    def __init__(self,peered=False,init_val=''):
        _ReferenceValue.__init__(self,peered,init_val)        

    @staticmethod
    def var_type():
        return 'WaldoTextVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        return WaldoTextVariable(
            peered,self.get_val(invalid_listener))

    
        
class WaldoTrueFalseVariable(_ReferenceValue):
    def __init__(self,peered=False,init_val=False):
        _ReferenceValue.__init__(self,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoTrueFalseVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        return WaldoTrueFalseVariable(
            peered,self.get_val(invalid_listener))

    

### CONTAINER TYPES        
class WaldoMapVariable(_ReferenceValue):
    def __init__(self,peered=False,init_val=None):
        if init_val == None:
            init_val = InternalMap(peered,{})

        _ReferenceValue.__init__(self,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoMapVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoMapVariable(
            peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))

    
        
class WaldoListVariable(_ReferenceValue):
    def __init__(self,peered=False,init_val=None):
        if init_val == None:
            init_val = InternalList(peered,[])

        _ReferenceValue.__init__(self,peered,init_val)
    
    @staticmethod
    def var_type():
        return 'WaldoListVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoListVariable(
            peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))

