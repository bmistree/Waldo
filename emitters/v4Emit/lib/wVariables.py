from waldoReferenceValue import _ReferenceValue
from waldoInternalList import InternalList
from waldoInternalMap import InternalMap



### VALUE TYPES
class WaldoNumVariable(_ReferenceValue):
    def __init__(self,init_val=0):
        _ReferenceValue.__init__(self,init_val)

    
class WaldoTextVariable(_ReferenceValue):
    def __init__(self,init_val=''):
        _ReferenceValue.__init__(self,init_val)        

        
class WaldoTrueFalseVariable(_ReferenceValue):
    def __init__(self,init_val=False):
        _ReferenceValue.__init__(self,init_val)

class WaldoMapVariable(_ReferenceValue):
    def __init__(self,init_val=None):
        if init_val == None:
            init_val = InternalMap({})

        _ReferenceValue.__init__(self,init_val)


class WaldoListVariable(_ReferenceValue):
    def __init__(self,init_val=None):
        if init_val == None:
            init_val = InternalList([])

        _ReferenceValue.__init__(self,init_val)
    
