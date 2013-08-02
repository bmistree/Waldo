from waldoLockedObj import WaldoLockedObj
from waldoDataWrapper import ValueTypeDataWrapper
from waldoDataWrapper import ReferenceTypeDataWrapper


class LockedValueVariable(WaldoLockedObj):
    def __init__(self,host_uuid,peered,init_val):
        super(LockedValueVariable,self).__init__(
            ValueTypeDataWrapper,host_uuid,peered,init_val)

class LockedNumberVariable(LockedValueVariable):
    pass

class LockedTextVariable(LockedValueVariable):    
    pass

class LockedTrueFalseVariable(LockedValueVariable):
    pass
