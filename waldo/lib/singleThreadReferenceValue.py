import singleThreadReference
import waldoReferenceValue

class _SingleThreadReferenceValue(singleThreadReference._SingleThreadReferenceBase):
    def __init__(self,host_uuid,peered,init_val):
        singleThreadReference._SingleThreadReferenceBase.__init__(
            self,host_uuid,peered,init_val,
            waldoReferenceValue._ReferenceValueVersion())
