import uuid
import ctypes
import os
import inspect
from collections import namedtuple


PARTNER_ENDPOINT_SENTINEL = -1


def endpoint_call_func_name(func_name):
    '''
    Takes in the name of the function that another endpoint has
    requested to be called.  Adds a prefix to distinguish the function
    as being called from an endpoint function call rather than from
    external code.
    '''
    return '_endpoint_func_call_prefix__waldo__' + func_name

def partner_endpoint_msg_call_func_name(func_name):
    '''
    @see endpoint_call_func_name, except as a result of partner
    sending a message in a message sequence.
    '''
    return '_partner_endpoint_msg_func_call_prefix__waldo__' + func_name



# FIXME: Lower overhead to using named tuple, however, when I try to,
# I get a pickling error: "pickle.PicklingError: Can't pickle <class
# 'util.SerializationHelperNamedTuple'>: it's not found as
# util.SerializationHelperNamedTuple", which I should fix.
# _SerializationHelperNamedTuple = namedtuple(
#         'SerializationHelperNamedTuple',
#         ['var_name', 'var_type','var_data','version_obj_data'])

class _SerializationHelperNamedTuple(object):
    def __init__(self,var_name,var_type,var_data,version_obj_data):
        self.var_name = var_name
        self.var_type = var_type
        self.var_data = var_data
        self.version_obj_data = version_obj_data


def _generate_serialization_named_tuple(
    var_name,var_type,var_data,version_obj_data):
    '''
    @param {String} var_name ---
    
    @param {String} var_type --- Must be an key in
    waldoNetworkSerializer.ReferenceTypeConstructorDict.

    @param {} version_obj_data --- Either the actual python value of
    the variable or another SerializationHelperNamedTuple in the case
    that the data are pointing at additional name
    SerializationHelperNamedTuples.
    '''
    tup = _SerializationHelperNamedTuple(
        var_name,var_type,var_data,version_obj_data)

    return tup



current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) 
waldo_uuid_lib_abs_path = os.path.join(
    current_dir, 'waldo_uuid',
    'waldo_foreign.so')

wuuid_lib = None
if os.path.exists(waldo_uuid_lib_abs_path):
    wuuid_lib = ctypes.CDLL(waldo_uuid_lib_abs_path)
else:
    warn_msg = '\nWaldo warning: Cannot find shared object file '
    warn_msg += 'for generating uuids.  For now, using Python\'s '
    warn_msg += 'uuid module to generate uuids.  To fix, make '
    warn_msg += 'inside of emitters/v4Emit/lib/waldo_uuid.\n'
    print warn_msg


class WaldoFFUUID(object):
    '''
    @see generate_foreign_function_uuid
    '''
    def __init__(self,high_order_bits, low_order_bits):
        self.high_order_bits = high_order_bits
        self.low_order_bits = low_order_bits

        self._hash = hash((self.high_order_bits,self.low_order_bits))
        
    def __str__(self):
        return str(self.high_order_bits) + str(self.low_order_bits)
    
    def __hash__(self):
        return self._hash

    def __eq__(self,other):

        if other == None:
            return False
        
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
    if wuuid_lib == None:
        return generate_py_uuid()
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
    
