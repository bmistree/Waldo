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
class WaldoMapVariable(_WaldoVariable):
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


    
class WaldoListVariable(_WaldoVariable):
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
