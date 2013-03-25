from waldoReferenceValue import _ReferenceValue
from waldoInternalList import InternalList
from waldoInternalMap import InternalMap
from abc import abstractmethod
import util
import waldoReferenceBase
import numbers

class _WaldoVariable(_ReferenceValue):
    def __init__(self,name,host_uuid,peered,init_val):
        self.name = name
        _ReferenceValue.__init__(self,host_uuid,peered,init_val)

    @abstractmethod
    def is_value_type(self):
        util.logger_assert(
            'Cannot call pure virtual method is_value_type ' +
            'on _WaldoVariable.')

    @staticmethod
    def var_type():
        util.logger_assert(
            'Cannot call pure virtual method var_type ' +
            'on _WaldoVariable.')        
        


def de_waldoify_for_return(val):
    # FIXME: actually write
    return val



### Pointer to endpoint
class WaldoEndpointVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoEndpointVariable'

    def is_value_type(self):
        return False
    
    def copy(self,invalid_listener,peered):
        return WaldoEndpointVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)

    


### VALUE TYPES
class WaldoNumVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=0):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoNumVariable'

    def is_value_type(self):
        return True

    
    def copy(self,invalid_listener,peered):
        return WaldoNumVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)
    
    
class WaldoTextVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=''):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoTextVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        return WaldoTextVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)


    
class WaldoTrueFalseVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=False):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoTrueFalseVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        return WaldoTrueFalseVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)


def recursive_map_list(val,name,host_uuid,peered):
    '''
    Challenge is that both list and map types can take in
    arbitrarily-nested dicts and lists.  Eg.,
    {'a': [ [1,2,3]] , 'b': [[1],[3]]}

    In this case, we need to turn each level into a
    WaldoMap/WaldoList.  To do so, we recursively take in initializer
    val (@param val above) and check if it's a dict or a list.  If it
    is, then, check all the elements of the dict/list and create
    variables out of them.
    '''

    # FIXME: here's probably a lot of overhead to this approach.  If
    # you look at the actual WaldoList and WaldoMap initializers, what
    # ends up happening is that we take the last WaldoMapVariable and
    # just grab the Internal representation of it.
    if isinstance(val,dict):
        copy = {}
        for key in val:
            dict_entry = val[key]
            copy[key] = recursive_map_list(dict_entry,name,host_uuid,peered)

        copy = InternalMap(host_uuid,peered,copy)
        return WaldoMapVariable(name,host_uuid,peered,copy)
            
    elif isinstance(val,list):
        copy = []
        for element in val:
            copy.append( recursive_map_list(element,name,host_uuid,peered))

        copy = InternalList(host_uuid,peered,copy)            
        return WaldoListVariable(name,host_uuid,peered,copy)

    # neither a Python map or list type, and therefore can be used as
    # itself.
    return val


### CONTAINER TYPES
## External types
class _WaldoExternalVariable(_WaldoVariable):
    pass


class WaldoMapVariable(_WaldoExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        # see comments in recursive_map_list
        if init_val == None:
            init_val = recursive_map_list({},name,host_uuid,peered)
            init_val = init_val.get_val(None)
        elif isinstance(init_val, InternalMap):
            pass
        else:
            init_val = recursive_map_list(init_val,name,host_uuid,peered)
            init_val = init_val.get_val(None)
                
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)

        
    @staticmethod
    def var_type():
        return 'WaldoMapVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoMapVariable(
            self.name,self.host_uuid,peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,waldoReferenceBase._ReferenceBase):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val


    def write_val(self,invalid_listener,new_val):
        '''
        When writing a value to a peered container, we need to be
        careful that the new value also becomes peered.  Otherwise, we
        could have a peered variable holding a reference to a
        non-peered InternalMap or InternalList.
        '''
        if self.peered:
            if isinstance(new_val,waldoReferenceBase._ReferenceBase):
                new_val = new_val.copy(invalid_listener,True)
        super(WaldoMapVariable,self).write_val(invalid_listener,new_val)


    
class WaldoListVariable(_WaldoExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        # see comments in recursive_map_list
        if init_val == None:
            init_val = recursive_map_list([],name,host_uuid,peered)
            init_val = init_val.get_val(None)
        elif isinstance(init_val, InternalList):
            pass
        else:
            init_val = recursive_map_list(init_val,name,host_uuid,peered)
            init_val = init_val.get_val(None)
            
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
    
    @staticmethod
    def var_type():
        return 'WaldoListVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoListVariable(
            self.name,self.host_uuid,peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        # FIXME: this will not work if we want userstructs to return
        # as dicts.
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,waldoReferenceBase._ReferenceBase):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val

    def write_val(self,invalid_listener,new_val):
        '''
        @see write_val in WaldoMapVariable
        '''
        if self.peered:
            if isinstance(new_val,waldoReferenceBase._ReferenceBase):
                new_val = new_val.copy(invalid_listener,True)
        super(WaldoListVariable,self).write_val(invalid_listener,new_val)


class WaldoUserStructVariable(WaldoMapVariable):
    '''
    Under the hood, user structs in Waldo are really just maps indexed
    by text.
    '''

    def __init__(self,name,host_uuid,peered=False,init_val=None):
        '''
        @param {dict} init_val --- Required to be non-None.  Contains
        a mapping of names to WaldoVariables.  Each name corresponds
        to one of the variable fields in the struct.  
        '''
        
        if not isinstance(init_val,dict):
            util.logger_assert(
                'User structs must always have init_vals.  ' +
                'Otherwise, not initializing struct data')
    
        WaldoMapVariable.__init__(self,name,host_uuid,peered,init_val)


    def var_type():
        return 'WaldoUserStructVariable'

    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return WaldoUserStructVariable(
            self.name,self.host_uuid,peered,
            self.get_val(invalid_listener).copy(invalid_listener,peered))




class WaldoFunctionVariable(_WaldoVariable):
    def __init__(
        self,name,host_uuid,peered=False,init_val=None):

        if peered:
            util.logger_assert(
                'Function variables may not be peered')

        def _default_helper_func(*args,**kwargs):
            pass

        if init_val == None:
            init_val = _default_helper_func

        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)

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
    
        
    @staticmethod
    def var_type():
        return 'WaldoFunctionVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered):
        new_func_variable = WaldoFunctionVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))
        return new_func_variable.set_external_args_array(self.ext_args_array)

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)



class _WaldoExternalValueType(_WaldoExternalVariable):
    def is_value_type(self):
        return False

    def copy(self,invalid_listener,peered):
        return self.get_val(invalid_listener).copy(invalid_listener,peered)
        
    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,waldoReferenceBase._ReferenceBase):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val


class WaldoExtNumVariable(_WaldoExternalValueType):
    def __init__(self,name,host_uuid,peered=False,init_val=None):

        if init_val == None:
            init_val = WaldoNumVariable(name,host_uuid,False,0)
        elif isinstance(init_val,WaldoNumVariable):
            pass
        else:
            init_val = WaldoNumVariable(name,host_uuid,False,init_val)
                 
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    def var_type():
        return 'WaldoExternalNumVariable'

    
class WaldoExtTextVariable(_WaldoExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):

        if init_val == None:
            init_val = WaldoTextVariable(name,host_uuid,False,'')
        elif isinstance(init_val,WaldoTextVariable):
            pass
        else:
            init_val = WaldoTextVariable(name,host_uuid,False,init_val)
                 
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
            
    def var_type():
        return 'WaldoExternalTextVariable'

    

class WaldoExtTrueFalseVariable(_WaldoExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):

        if init_val == None:
            init_val = WaldoTextVariable(name,host_uuid,False,'')
        elif isinstance(init_val,WaldoTextVariable):
            pass
        else:
            init_val = WaldoTextVariable(name,host_uuid,False,init_val)
                 
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
            
    def var_type():
        return 'WaldoExternalTextVariable'
