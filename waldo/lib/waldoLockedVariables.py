from waldo.lib.waldoLockedObj import WaldoLockedObj
import numbers
import waldo.lib.util as util
from waldo.lib.waldoLockedValueVariablesHelper import SingleThreadedLockedValueVariable
from waldo.lib.waldoLockedValueVariablesHelper import LockedValueVariable
from waldo.lib.waldoExternalValueVariables import WaldoExternalValueVariable

from waldo.lib.waldoLockedInternalContainers import SingleThreadedLockedInternalListVariable
from waldo.lib.waldoLockedInternalContainers import SingleThreadedLockedInternalMapVariable
from waldo.lib.waldoLockedInternalContainers import SingleThreadedLockedInternalStructVariable
from waldo.lib.waldoLockedInternalContainers import LockedInternalListVariable, LockedInternalMapVariable
from waldo.lib.waldoLockedInternalContainers import LockedInternalStructVariable
from waldo.lib.waldoLockedContainerReference import MultiThreadedContainerReference, SingleThreadedContainerReference
from waldo.lib.waldoEndpointBase import EndpointBase


#### HELPER FUNCTIONS ####

def ensure_locked_obj(new_val,host_uuid,single_threaded):
    '''
    @param {Anything} new_val --- If new_val is a non-Waldo object,
    convert it to a Waldo object.  Otherwise, return it unchanged.

    This method is used to ensure that each individual entry in a
    map/list is also protected.

    @param {bool} single_threaded --- True if the variable should be
    single threaded.
    
    '''

    util.logger_warn(
        'Need to include function object check in ensure locked obj')
    
    if isinstance(new_val, WaldoLockedObj):
        return new_val

    if single_threaded:
        if isinstance(new_val, bool):
            return SingleThreadedLockedTrueFalseVariable(host_uuid,False,new_val)
        elif isinstance(new_val, numbers.Number):
            return SingleThreadedLockedNumberVariable(host_uuid,False,new_val)
        elif util.is_string(new_val):
            return SingleThreadedLockedTextVariable(host_uuid,False,new_val)
        elif isinstance(new_val,list):
            return SingleThreadedLockedListVariable(host_uuid,False,new_val)
        elif isinstance(new_val,dict):
            return SingleThreadedLockedMapVariable(host_uuid,False,new_val)
        elif isinstance(new_val,EndpointBase):
            return SingleThreadedLockedEndpointVariable(host_uuid,False,new_val)
        else:
            util.logger_assert('Unknown object type.')

    else:
        if isinstance(new_val, bool):
            return LockedTrueFalseVariable(host_uuid,False,new_val)
        elif isinstance(new_val, numbers.Number):
            return LockedNumberVariable(host_uuid,False,new_val)
        elif util.is_string(new_val):
            return LockedTextVariable(host_uuid,False,new_val)
        elif isinstance(new_val,list):
            return LockedListVariable(host_uuid,False,new_val)
        elif isinstance(new_val,dict):
            return LockedMapVariable(host_uuid,False,new_val)
        elif isinstance(new_val,EndpointBase):
            return LockedEndpointVariable(host_uuid,False,new_val)
        else:
            util.logger_assert('Unknown object type.')


def is_non_ext_func_var(to_check):
    return (isinstance(to_check, LockedFunctionVariable) or
            isinstance(to_check, SingleThreadedLockedFunctionVariable))
            
def is_non_ext_text_var (to_check):
    return (isinstance(to_check,LockedTextVariable) or
            isinstance(to_check,SingleThreadedLockedTextVariable))


def is_non_ext_map_var (to_check):
    return (isinstance(to_check,LockedMapVariable) or
            isinstance(to_check,SingleThreadedLockedMapVariable))

def is_non_ext_list_var (to_check):
    return (isinstance(to_check,LockedListVariable) or
            isinstance(to_check,SingleThreadedLockedListVariable))

def is_non_ext_num_var (to_check):
    return (isinstance(to_check,LockedNumberVariable) or
            isinstance(to_check,SingleThreadedLockedNumberVariable))

def is_non_ext_true_false_var (to_check):
    return (isinstance(to_check,LockedTrueFalseVariable) or
            isinstance(to_check,SingleThreadedLockedTrueFalseVariable))


##### Multi-threaded value variables #####
class LockedNumberVariable(LockedValueVariable):
    DEFAULT_VALUE = 0

class LockedTextVariable(LockedValueVariable):
    DEFAULT_VALUE = ''

class LockedTrueFalseVariable(LockedValueVariable):
    DEFAULT_VALUE = False

class LockedEndpointVariable(LockedValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if peered:
            util.logger_assert('Cannot have peered endpoint variable')
        super(LockedEndpointVariable,self).__init__(host_uuid,peered,init_val)


class LockedFunctionVariable(LockedValueVariable):
    def __init__(
        self,host_uuid,peered=False,init_val=None):

        if peered:
            util.logger_assert(
                'Function variables may not be peered')

        def _default_helper_func(*args,**kwargs):
            pass

        if init_val == None:
            init_val = _default_helper_func
        super(LockedFunctionVariable,self).__init__(host_uuid,peered,init_val)

        # {Array} --- Each element is an int.  When making a call to a
        # function object, the function object takes in arguments.
        # For non-externals, we de-waldoify these arguments.  However,
        # for external arguments, we do not.  If an argument is
        # supposed to be an external, then we just pass it through
        # directly
        self.ext_args_array = None

    def set_external_args_array(self,ext_args_array):
        '''
        @see comment above declartion of ext_args_array.  Used by
        _ExecutingEventContext.call_func_obj to de-waldo-ify arguments
        passed to non-Waldo function objects.

        As soon as we create a new WaldoFunctionObject, we instantly
        set its args array.
        '''
        self.ext_args_array = ext_args_array
        return self

        
##### Single threaded value variables #####
class SingleThreadedLockedNumberVariable(SingleThreadedLockedValueVariable):
    DEFAULT_VALUE = 0

class SingleThreadedLockedTextVariable(SingleThreadedLockedValueVariable):
    DEFAULT_VALUE = ''

class SingleThreadedLockedTrueFalseVariable(SingleThreadedLockedValueVariable):
    DEFAULT_VALUE = False

class SingleThreadedLockedEndpointVariable(SingleThreadedLockedValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if peered:
            util.logger_assert('Cannot have peered endpoint variable')
        super(SingleThreadedLockedEndpointVariable,self).__init__(host_uuid,peered,init_val)



class SingleThreadedLockedFunctionVariable(SingleThreadedLockedValueVariable):
    def __init__(
        self,host_uuid,peered=False,init_val=None):

        if peered:
            util.logger_assert(
                'Function variables may not be peered')

        def _default_helper_func(*args,**kwargs):
            pass

        if init_val == None:
            init_val = _default_helper_func
        super(SingleThreadedLockedFunctionVariable,self).__init__(host_uuid,peered,init_val)

        # {Array} --- Each element is an int.  When making a call to a
        # function object, the function object takes in arguments.
        # For non-externals, we de-waldoify these arguments.  However,
        # for external arguments, we do not.  If an argument is
        # supposed to be an external, then we just pass it through
        # directly
        self.ext_args_array = None

    def set_external_args_array(self,ext_args_array):
        '''
        @see comment above declartion of ext_args_array.  Used by
        _ExecutingEventContext.call_func_obj to de-waldo-ify arguments
        passed to non-Waldo function objects.

        As soon as we create a new WaldoFunctionObject, we instantly
        set its args array.
        '''
        self.ext_args_array = ext_args_array
        return self
        

##### Multi-threaded container variables ######
class LockedMapVariable(MultiThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = {}
        if isinstance(init_val,dict):
            init_val = LockedInternalMapVariable(
                ensure_locked_obj,host_uuid,peered,init_val)

        super(LockedMapVariable,self).__init__(host_uuid,peered,init_val)


        
class LockedListVariable(MultiThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = []

        if isinstance(init_val,list):
            init_val = LockedInternalListVariable(
                ensure_locked_obj,host_uuid,peered,init_val)

        super(LockedListVariable,self).__init__(host_uuid,peered,init_val)


class LockedStructVariable(MultiThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if not isinstance(init_val,dict):
            util.logger_assert(
                'User structs must always have init_vals.  ' 
                'Otherwise, not initializing struct data')
        else:
            init_val = LockedInternalStructVariable(
                ensure_locked_obj,host_uuid,peered,init_val)
            
        super(LockedStructVariable,self).__init__(host_uuid,peered,init_val)
        
        
##### Single-threaded container variables ######
class SingleThreadedLockedMapVariable(SingleThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = {}
        if isinstance(init_val,dict):
            init_val = SingleThreadedLockedInternalMapVariable(
                ensure_locked_obj,host_uuid,peered,init_val)

        super(SingleThreadedLockedMapVariable,self).__init__(host_uuid,peered,init_val)

        
class SingleThreadedLockedListVariable(SingleThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = []
        if isinstance(init_val,list):
            init_val = SingleThreadedLockedInternalListVariable(
                ensure_locked_obj,host_uuid,peered,init_val)

        super(SingleThreadedLockedListVariable,self).__init__(host_uuid,peered,init_val)

class SingleThreadedLockedStructVariable(SingleThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            util.logger_assert(
                'User structs must always have init_vals.  ' 
                'Otherwise, not initializing struct data')

        if isinstance(init_val,dict):
            init_val = SingleThreadedLockedInternalStructVariable(
                ensure_locked_obj,host_uuid,peered,init_val)

        super(SingleThreadedLockedStructVariable,self).__init__(host_uuid,peered,init_val)

        
        
        
###### External value variables #####
class WaldoExternalTextVariable(WaldoExternalValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = ''
        if util.is_string(init_val):
            init_val = LockedTextVariable(host_uuid,False,init_val)

        super(WaldoExternalTextVariable,self).__init__(host_uuid,False,init_val)

        
class WaldoExternalNumberVariable(WaldoExternalValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = 0
        if isinstance(init_val,numbers.Number):
            init_val = LockedNumberVariable(host_uuid,False,init_val)
            
        super(WaldoExternalNumberVariable,self).__init__(host_uuid,False,init_val)

class WaldoExternalTrueFalseVariable(WaldoExternalValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = False
        if isinstance(init_val,bool):
            init_val = LockedTrueFalseVariable(host_uuid,False,False)
            
        super(WaldoExternalTrueFalseVariable,self).__init__(host_uuid,False,init_val)
        

