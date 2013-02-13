import uuid
import ctypes
import os
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) 
waldo_uuid_lib_abs_path = os.path.join(
    current_dir, 'waldo_uuid',
    'waldo_foreign.so')


wuuid_lib = ctypes.CDLL(waldo_uuid_lib_abs_path)


class WaldoFFUUID(object):
    '''
    @see generate_foreign_function_uuid
    '''
    def __init__(self,high_order_bits, low_order_bits):
        self.high_order_bits = high_order_bits
        self.low_order_bits = low_order_bits

    def __str__(self):
        return str(self.high_order_bits) + str(self.low_order_bits)
    
    def __hash__(self):
        return hash((self.high_order_bits,self.low_order_bits))

    def __eq__(self,other):
        return ((self.high_order_bits == other.high_order_bits) and
                (self.low_order_bits == other.low_order_bits))

    def __gt__(self,other):
        if ((self.high_order_bits > other.high_order_bits)
            
            or
            
            ((self.high_order_bits == other.high_order_bits)
             and
             (self.low_order_bits > other.low_order_bits))):

            return True

        return False

    def __lt__(self,other):
        if ((self.high_order_bits < other.high_order_bits)
            
            or
            
            ((self.high_order_bits == other.high_order_bits)
             and
             (self.low_order_bits < other.low_order_bits))):

            return True

        return False

    def __ne__(self,other):
        return not (self == other)
    
    def __gte__(self,other):
        return (self > other) or (self == other)

    def __lte__(self,other):
        return (self < other) or (self == other)
        
    
    
def generate_uuid():
    return generate_foreign_function_uuid()

def generate_foreign_function_uuid():
    '''
    Python's UUID generation takes a long time.  Instead of using it
    (such as in generate_py_uuid), we wrote our own foreign function
    which will return a WaldoFFUUID object.  It cannot be mixed with
    regular python uuids, but its hash, comparison and equality
    operations should be the same as a python-generated uuid.
    '''
    high_bits = ctypes.c_ulonglong(0)
    low_bits = ctypes.c_ulonglong(0)

    wuuid_lib.foreign_uuid_two_unsigned_longs(
        ctypes.byref(high_bits),ctypes.byref(low_bits))
    
    return WaldoFFUUID(high_bits.value,low_bits.value)

def generate_py_uuid():
    return uuid.uuid4()


def logger_assert(assert_msg):
    print 'Compiler error: ' + assert_msg
    assert(False)
    
