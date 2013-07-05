from waldoReferenceValue import _ReferenceValue
from waldoInternalList import InternalList, SingleThreadInternalList
from waldoInternalMap import InternalMap, SingleThreadInternalMap
from abc import abstractmethod
import util
import waldoReferenceBase
import numbers
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
from waldoObj import WaldoObj

from singleThreadReferenceValue import _SingleThreadReferenceValue

class _WaldoSingleThreadVariable(_SingleThreadReferenceValue):
    '''
    On single thread variables, do not need locks.
    '''
    def __init__(self,name,host_uuid,peered,init_val):
        self.name = name
        _SingleThreadReferenceValue.__init__(self,host_uuid,peered,init_val)

    @abstractmethod
    def is_value_type(self):
        util.logger_assert(
            'Cannot call pure virtual method is_value_type ' +
            'on _WaldoSingleThreadVariable.')

    @staticmethod
    def var_type():
        util.logger_assert(
            'Cannot call pure virtual method var_type ' +
            'on _WaldoSingleThreadVariable.')        


        
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


#### POINTERS TO ENDPOITNS #####
def is_non_ext_endpoint_var (to_check):
    return (isinstance(to_check,WaldoSingleThreadEndpointVariable) or
            isinstance(to_check,WaldoEndpointVariable))
        
class WaldoSingleThreadEndpointVariable(_WaldoSingleThreadVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        _WaldoSingleThreadVariable.__init__(self,name,host_uuid,peered,init_val)

    @staticmethod
    def var_type():
        return 'SingleThreadWaldoEndpointVariable'

    def is_value_type(self):
        return False
    
    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoEndpointVariable(self.name,self.host_uuid,peered,self.val)
        else:
            return WaldoSingleThreadEndpointVariable(self.name,self.host_uuid,peered,self.val)
        
    def de_waldoify(self,invalid_listener):
        return self.get_val(invalid_listener)

    
class WaldoEndpointVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoEndpointVariable'

    def is_value_type(self):
        return False
    
    def copy(self,invalid_listener,peered,multi_threaded):
        return WaldoEndpointVariable(
            self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)



### VALUE TYPES
def is_non_ext_num_var (to_check):
    return (isinstance(to_check,WaldoSingleThreadNumVariable) or
            isinstance(to_check,WaldoNumVariable))
            
class WaldoSingleThreadNumVariable(_WaldoSingleThreadVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = 0
        
        _WaldoSingleThreadVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoSingleThreadNumVariable'

    def is_value_type(self):
        return True
    
    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoNumVariable(self.name,self.host_uuid,peered,self.val)
        else:
            return WaldoSingleThreadNumVariable(self.name,self.host_uuid,peered,self.val)

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)

        
class WaldoNumVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = 0
        
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoNumVariable'

    def is_value_type(self):
        return True

    
    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoNumVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))
        else:
            return WaldoSingleThreadNumVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)


def is_non_ext_text_var (to_check):
    return (isinstance(to_check,WaldoSingleThreadTextVariable) or
            isinstance(to_check,WaldoTextVariable))

            
class WaldoSingleThreadTextVariable(_WaldoSingleThreadVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = ''
        
        _WaldoSingleThreadVariable.__init__(self,name,host_uuid,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoSingleThreadTextVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoTextVariable(self.name,self.host_uuid,peered,self.val)
        else:
            return WaldoSingleThreadTextVariable(self.name,self.host_uuid,peered,self.val)

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)

    
    
class WaldoTextVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = ''
        
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)

    @staticmethod
    def var_type():
        return 'WaldoTextVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoTextVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))
        else:
            return WaldoSingleThreadTextVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)


def is_non_ext_true_false_var (to_check):
    return (isinstance(to_check,WaldoSingleThreadTrueFalseVariable) or
            isinstance(to_check,WaldoTrueFalseVariable))

            
class WaldoSingleThreadTrueFalseVariable(_WaldoSingleThreadVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = False
        _WaldoSingleThreadVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoSingleThreadTrueFalseVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoTrueFalseVariable(self.name,self.host_uuid,peered,self.val)
        else:
            return WaldoSingleThreadTrueFalseVariable(self.name,self.host_uuid,peered,self.val)

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)

    
    
class WaldoTrueFalseVariable(_WaldoVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        if init_val == None:
            init_val = False
        _WaldoVariable.__init__(self,name,host_uuid,peered,init_val)
        
    @staticmethod
    def var_type():
        return 'WaldoTrueFalseVariable'

    def is_value_type(self):
        return True

    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoTrueFalseVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))
        else:
            return WaldoSingleThreadTrueFalseVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))

    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        return self.get_val(invalid_listener)


def recursive_map_list(val,name,host_uuid,peered,multi_threaded):
    '''
    Challenge is that both list and map types can take in
    arbitrarily-nested dicts and lists.  Eg.,
    {'a': [ [1,2,3]] , 'b': [[1],[3]]}

    In this case, we need to turn each level into a
    WaldoMap/WaldoList.  To do so, we recursively take in initializer
    val (@param val above) and check if it's a dict or a list.  If it
    is, then, check all the elements of the dict/list and create
    variables out of them.

    Returns a WaldoMapVariable or a WaldoListVariable, *NOT* an
    InternalMap or InternalList.
    '''

    # FIXME: here's probably a lot of overhead to this approach.  If
    # you look at the actual WaldoList and WaldoMap initializers, what
    # ends up happening is that we take the last WaldoMapVariable and
    # just grab the Internal representation of it.
    if isinstance(val,dict):
        copy = {}
        for key in val:
            dict_entry = val[key]
            copy[key] = recursive_map_list(dict_entry,name,host_uuid,peered,multi_threaded)
        
        if multi_threaded:
            copy = InternalMap(host_uuid,peered,copy)
            return WaldoMapVariable(name,host_uuid,peered,copy)

        copy = SingleThreadInternalMap(host_uuid,peered,copy)
        return WaldoSingleThreadMapVariable(name,host_uuid,peered,copy)
            
            
    elif isinstance(val,list):
        copy = []
        for element in val:
            copy.append( recursive_map_list(element,name,host_uuid,peered,multi_threaded))

        if multi_threaded:
            copy = InternalList(host_uuid,peered,copy)            
            return WaldoListVariable(name,host_uuid,peered,copy)
            
        copy = SingleThreadInternalList(host_uuid,peered,copy)
        return WaldoSingleThreadListVariable(name,host_uuid,peered,copy)
            

    # neither a Python map or list type, and therefore can be used as
    # itself.
    return val



### CONTAINER TYPES
## External types
class _WaldoExternalVariable(_WaldoVariable):
    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,WaldoObj):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val

    def is_value_type(self):
        return False


class _WaldoSingleThreadExternalVariable(_WaldoSingleThreadVariable):
    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,WaldoObj):
            return internal_val.de_waldoify(invalid_listener)
        return internal_val

    def is_value_type(self):
        return False

def is_non_ext_map_var (to_check):
    return (isinstance(to_check,WaldoMapVariable) or
            isinstance(to_check,WaldoSingleThreadMapVariable))

    
class WaldoMapVariable(_WaldoExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        # see comments in recursive_map_list
        if init_val == None:
            init_val = recursive_map_list({},name,host_uuid,peered,True)
            init_val = init_val.get_val(None)
        elif isinstance(init_val, InternalMap):
            pass
        elif isinstance(init_val, SingleThreadInternalMap):
            init_val = recursive_map_list(init_val.val,name,host_uuid,peered,True)
        else:
            init_val = recursive_map_list(init_val,name,host_uuid,peered,True)
            init_val = init_val.get_val(None)

        _WaldoExternalVariable.__init__(self,name,host_uuid,peered,init_val)


    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        self._unlock()

        version_obj = dirty_element.version_obj

        is_var_store = False
        if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            is_var_store = True
            map_delta = parent_delta.map_deltas.add()
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_WRITTEN:            
            map_delta = parent_delta.what_written_map
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_ADDED:
            map_delta = parent_delta.added_what_map
        elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
            map_delta = parent_delta.map_delta
        else:
            util.logger_assert('Unexpected parent container type when serializing map')
            
        map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER            
        map_delta.var_name = var_name
        map_delta.has_been_written = version_obj.has_been_written_since_last_message

        # reset has been written to
        written_since_last_message = version_obj.has_been_written_since_last_message
        version_obj.has_been_written_since_last_message = False
        
        var_data = dirty_element.val
        internal_has_been_written = var_data.serializable_var_tuple_for_network(
            map_delta,'',invalid_listener,
            # must force the write when we have written a new value over list
            force or written_since_last_message)

        
        # FIXME: check to ensure that second part of condition will
        # still hide elements that do not change
        if (not internal_has_been_written) and is_var_store and (not written_since_last_message):
            # remove the newly added map delta because there were no
            # changes that it encoded
            del parent_delta.map_deltas[-1]

        return internal_has_been_written or written_since_last_message or force
        
    def incorporate_deltas(self,map_delta,constructors,active_event):
        '''
        @param {SingleMapDelta} map_delta --- @see varStoreDeltas.proto
        '''
        if map_delta.has_been_written:
            # create a new internal
            internal_map = recursive_map_list({},self.name,self.host_uuid,True,True).get_val(None)
            internal_map.incorporate_deltas(
                map_delta.internal_map_delta,constructors,active_event)

            self.write_val(active_event,internal_map,False)
        else:
            self.get_val(active_event).incorporate_deltas(
                map_delta.internal_map_delta,constructors,active_event)

    
    @staticmethod
    def var_type():
        return 'WaldoMapVariable'


    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoMapVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered,multi_threaded))
        else:
            return WaldoSingleThreadMapVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered,multi_threaded))

    def write_val(
        self,invalid_listener,new_val,copy_if_peered=True,multi_threaded=True):
        '''
        When writing a value to a peered container, we need to be
        careful that the new value also becomes peered.  Otherwise, we
        could have a peered variable holding a reference to a
        non-peered InternalMap or InternalList.
        '''
        if self.peered and copy_if_peered:
            if isinstance(new_val,WaldoObj):
                new_val = new_val.copy(invalid_listener,True,multi_threaded)
        super(WaldoMapVariable,self).write_val(invalid_listener,new_val)


def is_non_ext_list_var (to_check):
    return (isinstance(to_check,WaldoListVariable) or
            isinstance(to_check,WaldoSingleThreadListVariable))
            
    
class WaldoListVariable(_WaldoExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        # see comments in recursive_map_list
        if init_val == None:
            init_val = recursive_map_list([],name,host_uuid,peered,True)
            init_val = init_val.get_val(None)
        elif isinstance(init_val, InternalList):
            pass
        elif isinstance(init_val, SingleThreadInternalList):
            init_val = recursive_map_list(init_val.val,name,host_uuid,peered,True)
        else:
            init_val = recursive_map_list(init_val,name,host_uuid,peered,True)
            init_val = init_val.get_val(None)
            
        _WaldoExternalVariable.__init__(self,name,host_uuid,peered,init_val)


    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        self._unlock()

        version_obj = dirty_element.version_obj

        is_var_store = False
        if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            is_var_store = True
            list_delta = parent_delta.list_deltas.add()
        elif parent_delta.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
            list_delta = parent_delta.what_written_list
        elif parent_delta.parent_type == VarStoreDeltas.CONTAINER_ADDED:
            list_delta = parent_delta.added_what_list
        elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
            list_delta = parent_delta.list_delta
        else:
            util.logger_assert('Unexpected parent container type when serializing list')

        list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER
        list_delta.var_name = var_name
        list_delta.has_been_written = version_obj.has_been_written_since_last_message

        # reset has been written to
        written_since_last_message = version_obj.has_been_written_since_last_message
        version_obj.has_been_written_since_last_message = False

        var_data = dirty_element.val
        internal_has_been_written = var_data.serializable_var_tuple_for_network(
            list_delta,'',invalid_listener,
            # must force the write when we have written a new value over list
            force or written_since_last_message)


        # FIXME: check to ensure that second part of condition will
        # still hide elements that do not change
        if (not internal_has_been_written) and is_var_store and (not written_since_last_message):
            # remove the newly added list delta because there were no
            # changes that it encoded
            del parent_delta.list_deltas[-1]
        
        return internal_has_been_written or written_since_last_message or force

    def incorporate_deltas(self,list_delta,constructors,active_event):
        '''
        @param {SingleListDelta} list_delta --- @see varStoreDeltas.proto
        '''
        if list_delta.has_been_written:
            # create a new internal
            internal_list = recursive_map_list([],self.name,self.host_uuid,True,True).get_val(None)
            internal_list.incorporate_deltas(
                list_delta.internal_list_delta,constructors,active_event)

            self.write_val(active_event,internal_list,False)
        else:
            self.get_val(active_event).incorporate_deltas(
                list_delta.internal_list_delta,constructors,active_event)

    @staticmethod
    def var_type():
        return 'WaldoListVariable'


    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoListVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered, True))
        else:
            return WaldoSingleThreadListVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered,False))
        
    def write_val(self,invalid_listener,new_val,copy_if_peered=True):
        '''
        @see write_val in WaldoMapVariable
        '''
        if self.peered and copy_if_peered:
            if isinstance(new_val,WaldoObj):
                new_val = new_val.copy(invalid_listener,True,True)
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
    
    @staticmethod
    def var_type():
        return 'WaldoUserStructVariable'


    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            to_return = WaldoUserStructVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy_internal_val(invalid_listener,peered))
        else:
            to_return = WaldoSingleThreadUserStructVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy_internal_val(invalid_listener,peered))
            
        return to_return

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        self._unlock()

        version_obj = dirty_element.version_obj

        is_var_store = False
        if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            is_var_store = True
            struct_delta = parent_delta.struct_deltas.add()
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_WRITTEN:            
            struct_delta = parent_delta.what_written_map
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_ADDED:
            struct_delta = parent_delta.added_what_map
        elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
            struct_delta = parent_delta.struct_delta
        else:
            util.logger_assert('Unexpected parent container type when serializing map')
            
        struct_delta.parent_type = VarStoreDeltas.STRUCT_CONTAINER
        struct_delta.var_name = var_name
        struct_delta.has_been_written = version_obj.has_been_written_since_last_message

        # reset has been written to
        written_since_last_message = version_obj.has_been_written_since_last_message
        version_obj.has_been_written_since_last_message = False

        
        var_data = dirty_element.val
        internal_has_been_written = var_data.serializable_var_tuple_for_network(
            struct_delta,'',invalid_listener,
            # must force the write when we have written a new value over list
            force or written_since_last_message)
        

        # FIXME: check to ensure that second part of condition will
        # still hide elements that do not change
        if (not internal_has_been_written) and is_var_store and (not written_since_last_message):
            # remove the newly added map delta because there were no
            # changes that it encoded
            del parent_delta.struct_deltas[-1]

        return internal_has_been_written or written_since_last_message or force

    

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

    def copy(self,invalid_listener,peered, multi_threaded):
        if multi_threaded:
            new_func_variable = WaldoFunctionVariable(
                self.name,self.host_uuid,peered,self.get_val(invalid_listener))
        else:
            new_func_variable = WaldoSingleThreadFunctionVariable(
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

    def copy(self,invalid_listener,peered,multi_threaded):
        return self.get_val(invalid_listener).copy(invalid_listener,peered,multi_threaded)
        
    def de_waldoify(self,invalid_listener):
        '''
        @see _ReferenceBase.de_waldoify
        '''
        internal_val = self.get_val(invalid_listener)

        if isinstance(internal_val,WaldoObj):
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
                 
        _WaldoExternalValueType.__init__(self,name,host_uuid,peered,init_val)
        
    def var_type():
        return 'WaldoExternalNumVariable'

    
class WaldoExtTextVariable(_WaldoExternalValueType):
    def __init__(self,name,host_uuid,peered=False,init_val=None):

        if init_val == None:
            init_val = WaldoTextVariable(name,host_uuid,False,'')
        elif isinstance(init_val,WaldoTextVariable):
            pass
        else:
            init_val = WaldoTextVariable(name,host_uuid,False,init_val)
                 
        _WaldoExternalValueType.__init__(self,name,host_uuid,peered,init_val)
        
            
    def var_type():
        return 'WaldoExternalTextVariable'

    

class WaldoExtTrueFalseVariable(_WaldoExternalValueType):
    def __init__(self,name,host_uuid,peered=False,init_val=None):

        if init_val == None:
            init_val = WaldoTextVariable(name,host_uuid,False,'')
        elif isinstance(init_val,WaldoTextVariable):
            pass
        else:
            init_val = WaldoTextVariable(name,host_uuid,False,init_val)
                 
        _WaldoExternalValueType.__init__(self,name,host_uuid,peered,init_val)
        
            
    def var_type():
        return 'WaldoExternalTrueFalseVariable'




#### SINGLE THREAD CONTAINER VARIABLES ####
class WaldoSingleThreadMapVariable(_WaldoSingleThreadExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        # see comments in recursive_map_list
        if init_val == None:
            init_val = recursive_map_list({},name,host_uuid,peered,False)
            init_val = init_val.get_val(None)
        elif isinstance(init_val, InternalMap):
            pass
        elif isinstance(init_val, SingleThreadInternalMap):
            pass
        else:
            init_val = recursive_map_list(init_val,name,host_uuid,peered,False)
            init_val = init_val.get_val(None)
                
        _WaldoSingleThreadExternalVariable.__init__(self,name,host_uuid,peered,init_val)

        
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        version_obj = self.version_obj

        is_var_store = False
        if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            is_var_store = True
            map_delta = parent_delta.map_deltas.add()
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_WRITTEN:            
            map_delta = parent_delta.what_written_map
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_ADDED:
            map_delta = parent_delta.added_what_map
        elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
            map_delta = parent_delta.map_delta
        else:
            util.logger_assert('Unexpected parent container type when serializing map')
            
        map_delta.parent_type = VarStoreDeltas.MAP_CONTAINER            
        map_delta.var_name = var_name
        map_delta.has_been_written = version_obj.has_been_written_since_last_message

        # reset has been written to
        written_since_last_message = version_obj.has_been_written_since_last_message
        version_obj.has_been_written_since_last_message = False
        
        var_data = self.val
        internal_has_been_written = var_data.serializable_var_tuple_for_network(
            map_delta,'',invalid_listener,
            # must force the write when we have written a new value over list
            force or written_since_last_message)

        
        # FIXME: check to ensure that second part of condition will
        # still hide elements that do not change
        if (not internal_has_been_written) and is_var_store and (not written_since_last_message):
            # remove the newly added map delta because there were no
            # changes that it encoded
            del parent_delta.map_deltas[-1]

        return internal_has_been_written or written_since_last_message or force
        
    def incorporate_deltas(self,map_delta,constructors,active_event):
        '''
        @param {SingleMapDelta} map_delta --- @see varStoreDeltas.proto
        '''
        if map_delta.has_been_written:
            # create a new internal
            internal_map = recursive_map_list({},self.name,self.host_uuid,True,False).get_val(None)
            internal_map.incorporate_deltas(
                map_delta.internal_map_delta,constructors,active_event)

            self.write_val(active_event,internal_map,False)
        else:
            self.get_val(active_event).incorporate_deltas(
                map_delta.internal_map_delta,constructors,active_event)

    
    @staticmethod
    def var_type():
        return 'SingleThreadWaldoMapVariable'

    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoMapVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered,multi_threaded))
        else:
            return WaldoSingleThreadMapVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered,multi_threaded))

    def write_val(self,invalid_listener,new_val,copy_if_peered=True,multi_threaded=True):
        '''
        When writing a value to a peered container, we need to be
        careful that the new value also becomes peered.  Otherwise, we
        could have a peered variable holding a reference to a
        non-peered InternalMap or InternalList.
        '''
        if self.peered and copy_if_peered:
            if isinstance(new_val,WaldoObj):
                new_val = new_val.copy(invalid_listener,True,multi_threaded)
                
        super(WaldoSingleThreadMapVariable,self).write_val(invalid_listener,new_val)


class WaldoSingleThreadListVariable(_WaldoSingleThreadExternalVariable):
    def __init__(self,name,host_uuid,peered=False,init_val=None):
        # see comments in recursive_map_list
        if init_val is None:
            init_val = recursive_map_list([],name,host_uuid,peered,False)
            init_val = init_val.get_val(None)

        elif isinstance(init_val, InternalList):
            pass
        elif isinstance(init_val, SingleThreadInternalList):
            pass
        else:
            init_val = recursive_map_list(init_val,name,host_uuid,peered,False)
            init_val = init_val.get_val(None)
            
        _WaldoSingleThreadExternalVariable.__init__(self,name,host_uuid,peered,init_val)


    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        version_obj = self.version_obj

        is_var_store = False
        if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            is_var_store = True
            list_delta = parent_delta.list_deltas.add()
        elif parent_delta.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
            list_delta = parent_delta.what_written_list
        elif parent_delta.parent_type == VarStoreDeltas.CONTAINER_ADDED:
            list_delta = parent_delta.added_what_list
        elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
            list_delta = parent_delta.list_delta
        else:
            util.logger_assert('Unexpected parent container type when serializing list')

        list_delta.parent_type = VarStoreDeltas.LIST_CONTAINER
        list_delta.var_name = var_name
        list_delta.has_been_written = version_obj.has_been_written_since_last_message

        # reset has been written to
        written_since_last_message = version_obj.has_been_written_since_last_message
        version_obj.has_been_written_since_last_message = False

        var_data = self.val
        internal_has_been_written = var_data.serializable_var_tuple_for_network(
            list_delta,'',invalid_listener,
            # must force the write when we have written a new value over list
            force or written_since_last_message)


        # FIXME: check to ensure that second part of condition will
        # still hide elements that do not change
        if (not internal_has_been_written) and is_var_store and (not written_since_last_message):
            # remove the newly added list delta because there were no
            # changes that it encoded
            del parent_delta.list_deltas[-1]
        
        return internal_has_been_written or written_since_last_message or force

    def incorporate_deltas(self,list_delta,constructors,active_event):
        '''
        @param {SingleListDelta} list_delta --- @see varStoreDeltas.proto
        '''
        if list_delta.has_been_written:
            # create a new internal
            internal_list = recursive_map_list([],self.name,self.host_uuid,True,False).get_val(None)
            internal_list.incorporate_deltas(
                list_delta.internal_list_delta,constructors,active_event)

            self.write_val(active_event,internal_list,False)
        else:
            self.get_val(active_event).incorporate_deltas(
                list_delta.internal_list_delta,constructors,active_event)

    @staticmethod
    def var_type():
        return 'WaldoSingleThreadListVariable'

    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            return WaldoListVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered, True))
        else:
            return WaldoSingleThreadListVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy(invalid_listener,peered,False))

    def write_val(self,invalid_listener,new_val,copy_if_peered=True):
        '''
        @see write_val in WaldoMapVariable
        '''
        if self.peered and copy_if_peered:
            if isinstance(new_val,WaldoObj):
                new_val = new_val.copy(invalid_listener,True,False)
        super(WaldoSingleThreadListVariable,self).write_val(invalid_listener,new_val)



class WaldoSingleThreadUserStructVariable(WaldoSingleThreadMapVariable):
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
    
        WaldoSingleThreadMapVariable.__init__(self,name,host_uuid,peered,init_val)
    
    @staticmethod
    def var_type():
        return 'WaldoSingleThreadUserStructVariable'


    def copy(self,invalid_listener,peered,multi_threaded):
        if multi_threaded:
            to_return = WaldoUserStructVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy_internal_val(invalid_listener,peered))
        else:
            to_return = WaldoSingleThreadUserStructVariable(
                self.name,self.host_uuid,peered,
                self.get_val(invalid_listener).copy_internal_val(invalid_listener,peered))
            
        return to_return

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        version_obj = self.version_obj

        is_var_store = False
        if parent_delta.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
            is_var_store = True
            struct_delta = parent_delta.struct_deltas.add()
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_WRITTEN:            
            struct_delta = parent_delta.what_written_map
        elif parent_delta.parent_type  == VarStoreDeltas.CONTAINER_ADDED:
            struct_delta = parent_delta.added_what_map
        elif parent_delta.parent_type == VarStoreDeltas.SUB_ELEMENT_ACTION:
            struct_delta = parent_delta.struct_delta
        else:
            util.logger_assert('Unexpected parent container type when serializing map')
            
        struct_delta.parent_type = VarStoreDeltas.STRUCT_CONTAINER
        struct_delta.var_name = var_name
        struct_delta.has_been_written = version_obj.has_been_written_since_last_message

        # reset has been written to
        written_since_last_message = version_obj.has_been_written_since_last_message
        version_obj.has_been_written_since_last_message = False

        
        var_data = self.val
        internal_has_been_written = var_data.serializable_var_tuple_for_network(
            struct_delta,'',invalid_listener,
            # must force the write when we have written a new value over list
            force or written_since_last_message)
        

        # FIXME: check to ensure that second part of condition will
        # still hide elements that do not change
        if (not internal_has_been_written) and is_var_store and (not written_since_last_message):
            # remove the newly added map delta because there were no
            # changes that it encoded
            del parent_delta.struct_deltas[-1]

        return internal_has_been_written or written_since_last_message or force
    




