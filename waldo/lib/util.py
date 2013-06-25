import uuid, os

SIZE_THREAD_POOL = 2

# Queue was changed to queue in Python 3.  
try:
    import Queue as Queue
except:
    import queue as Queue

PARTNER_ENDPOINT_SENTINEL = -1

# if we cannot acquire a lock for the first phase of a variable's
# commit, then do not block on it.  Go to sleep for this amount of
# time and then try to re-acquire the lock (if we haven't already been
# told to back out).
TIME_TO_SLEEP_BEFORE_ATTEMPT_TO_ACQUIRE_VAR_FIRST_PHASE_LOCK = .2

def is_string(obj):
    '''
    Python3 deprecates basestring
    '''
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


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

def internal_oncreate_func_call_name(func_name):
    return '_onCreate'


# def generate_py_uuid():
#     return uuid.uuid4()

import random, os
def generate_uuid():
    return os.urandom(16)



def logger_assert(assert_msg):
    assert_msg = 'Compiler error: ' + assert_msg
    print (assert_msg)
    assert(False)

def logger_warn(warn_msg):
    warn_msg = 'Compiler warn: ' + warn_msg
    print (warn_msg)


class BackoutException(Exception):
    pass
class StoppedException(Exception):
    pass


