import waldo.lib.singleThreadReference as singleThreadReference
import waldo.lib.waldoReferenceValue as waldoReferenceValue

class _SingleThreadReferenceValue(singleThreadReference._SingleThreadReferenceBase):
    def __init__(self,host_uuid,peered,init_val):
        singleThreadReference._SingleThreadReferenceBase.__init__(
            self,host_uuid,peered,init_val,
            waldoReferenceValue._ReferenceValueVersion())
