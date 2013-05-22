import singleThreadReference
import waldoReferenceValue

class _SingleThreadReferenceValue(singleThreadReference._SingleThreadReferenceBase):
    def __init__(self,host_uuid,peered,init_val):
        waldoReferenceBase._ReferenceBase.__init__(
            self,host_uuid,peered,init_val,
            waldoReferenceValue._ReferenceValueVersion())
