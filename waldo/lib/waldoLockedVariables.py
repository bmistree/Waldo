from waldo.lib.waldoLockedObj import WaldoLockedObj
import numbers
import waldo.lib.util as util
from waldo.lib.waldoLockedValueVariablesHelper import SingleThreadedLockedValueVariable
from waldo.lib.waldoLockedValueVariablesHelper import LockedValueVariable
from waldo.lib.waldoExternalValueVariables import WaldoExternalValueVariable

from waldo.lib.waldoLockedInternalContainers import SingleThreadedLockedInternalListVariable
from waldo.lib.waldoLockedInternalContainers import SingleThreadedLockedInternalMapVariable
from waldo.lib.waldoLockedInternalContainers import LockedInternalListVariable, LockedInternalMapVariable
from waldo.lib.waldoLockedContainerReference import MultiThreadedContainerReference, SingleThreadedContainerReference


#### HELPER FUNCTIONS ####

def ensure_locked_obj(new_val,host_uuid):
    '''
    @param {Anything} new_val --- If new_val is a non-Waldo object,
    convert it to a Waldo object.  Otherwise, return it unchanged.

    This method is used to ensure that each individual entry in a
    map/list is also protected.
    '''
    util.logger_warn('In ensure locked obj should think about single threaded variables.')
    util.logger_warn(
        'If single threaded variable is not peered, then do not need to actually use waldo variables.')
    
    if isinstance(new_val, WaldoLockedObj):
        return new_val

    if isinstance(new_val, bool):
        return LockedTrueFalseVariable(host_uuid,False,new_val)
    elif isinstance(new_val, numbers.Number):
        return LockedNumberVariable(host_uuid,False,new_val)
    elif util.is_string(new_val):
        return LockedTextVariable(host_uuid,False,new_val)
    else:
        util.logger_assert('Unknown object type.')


def is_non_ext_text_var (to_check):
    return (isinstance(to_check,LockedTextVariable) or
            isinstance(to_check,SingleThreadedLockedTextVariable))

def is_reference_container(to_check):
    return (isinstance(to_check,WaldoLockedContainer) or
            isinstance(to_check,SingleThreadedLockedContainerVariable))

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
    pass

class LockedTextVariable(LockedValueVariable):
    pass

class LockedTrueFalseVariable(LockedValueVariable):
    pass


##### Single threaded value variables #####
class SingleThreadedLockedNumberVariable(SingleThreadedLockedValueVariable):
    pass

class SingleThreadedLockedTextVariable(SingleThreadedLockedValueVariable):
    pass

class SingleThreadedLockedTrueFalseVariable(SingleThreadedLockedValueVariable):
    pass


##### Multi-threaded container variables ######
class LockedMapVariable(MultiThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = {}
        if isinstance(init_val,dict):
            init_val = LockedInternalMapVariable(ensure_locked_obj,host_uuid,peered,init_val)

        super(LockedMapVariable,self).__init__(host_uuid,peered,init_val)


        
class LockedListVariable(MultiThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = []

        if isinstance(init_val,list):
            init_val = LockedInternalListVariable(ensure_locked_obj,host_uuid,peered,init_val)

        super(LockedListVariable,self).__init__(host_uuid,peered,init_val)


        
##### Single-threaded container variables ######
class SingleThreadedLockedMapVariable(SingleThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = {}
        if isinstance(init_val,dict):
            init_val = SingleThreadedLockedInternalMapVariable(ensure_locked_obj,host_uuid,peered,init_val)

        super(SingleThreadedLockedMapVariable,self).__init__(host_uuid,peered,init_val)

        
class SingleThreadedLockedListVariable(SingleThreadedContainerReference):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = []
        if isinstance(init_val,list):
            init_val = SingleThreadedLockedInternalListVariable(ensure_locked_obj,host_uuid,peered,init_val)

        super(SingleThreadedLockedListVariable,self).__init__(host_uuid,peered,init_val)

        
###### External value variables #####
class WaldoExternalTextVariable(WaldoExternalValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = MultiThreadedTextVariable(host_uuid,False,'')
        super(WaldoExternalMultiThreadedTextVariable,self).__init__(host_uuid,False,init_val)

        
class WaldoExternalNumberVariable(WaldoExternalValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = MultiThreadedTextVariable(host_uuid,False,0)
        super(WaldoExternalMultiThreadedTextVariable,self).__init__(host_uuid,False,init_val)

class WaldoExternalTrueFalseVariable(WaldoExternalValueVariable):
    def __init__(self,host_uuid,peered=False,init_val=None):
        if init_val is None:
            init_val = MultiThreadedTextVariable(host_uuid,False,False)
        super(WaldoExternalMultiThreadedTextVariable,self).__init__(host_uuid,False,init_val)
        

