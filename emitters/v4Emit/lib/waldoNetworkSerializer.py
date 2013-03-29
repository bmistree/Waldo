import wVariables
import waldoInternalList
import waldoInternalMap
from waldoReferenceBase import _ReferenceVersion as RefVers
import util


# This dict maps Waldo object variable types to their constructors.
# The purpose of this dict is to allow deserialization of Waldo peered
# variables passed across the network.  When we serialize a variable,
# we put it into a named tuple, SerializationHelperNamedTuple-s (@see
# util._generate_serailization_named_tuple).  One of the named tuple's
# fields has a type so that we know what to deserialize its containing
# data as.  This type is an index into this dict to get the
# appropriate constructor out for the object we're using.
ReferenceTypeConstructorDict = {
    # value variables
    wVariables.WaldoNumVariable.var_type(): wVariables.WaldoNumVariable,
    wVariables.WaldoTextVariable.var_type(): wVariables.WaldoTextVariable,
    wVariables.WaldoTrueFalseVariable.var_type(): wVariables.WaldoTrueFalseVariable,
    
    # container types
    wVariables.WaldoMapVariable.var_type(): wVariables.WaldoMapVariable,
    wVariables.WaldoListVariable.var_type(): wVariables.WaldoListVariable,
    waldoInternalList.InternalList.var_type(): waldoInternalList.InternalList,
    waldoInternalMap.InternalMap.var_type(): waldoInternalMap.InternalMap,
    wVariables.WaldoUserStructVariable.var_type(): wVariables.WaldoUserStructVariable,
    }

def requires_name_arg_in_constructor(var_type):
    '''
    The InternalList and InternalMap constructors do not take a name
    argument.  The other constructors in ReferenceTypeConstructorDict
    do.
    '''
    if var_type in [waldoInternalList.InternalList.var_type(),
                    waldoInternalMap.InternalMap.var_type()]:
        return False
    return True
    
def get_constructed_obj(
    var_type,var_name,host_uuid,peered,init_data,invalidation_listener):
    '''
    @returns {WaldoReferenceObject} --- Either a wVariable or an
    InternalList or InternalMap.
    '''
    #### DEBUG
    if var_type not in ReferenceTypeConstructorDict:
        util.logger_assert(
            'Unknown variable type to deserialize')
    #### END DEBUG

    if var_type == wVariables.WaldoUserStructVariable.var_type():
        # we are constructing a user struct: in this case, init_data
        # will be an internal map.  can just deserialize the map into

        #### DEBUG
        if not isinstance(init_data,waldoInternalMap.InternalMap):
            util.logger_assert(
                'Must initialize user struct data with internal map')
        #### END DEBUG

        # FIXME: it is unclear if we just created an internal map for
        # no reason here.  maybe just serialize and deserialize
        # internal values of structs as dicts.
            
        # FIXME: it is gross that reaching into the internal map this
        # way.
        init_data._lock()
        if invalidation_listener.uuid not in init_data._dirty_map:
            new_init_data = init_data.val
        else:
            new_init_data = init_data._dirty_map[invalidation_listener.uuid].val
        init_data._unlock()
        init_data = new_init_data
        
    var_constructor = ReferenceTypeConstructorDict[var_type]
    
    if requires_name_arg_in_constructor(var_type):
        return var_constructor(var_name,host_uuid,peered,init_data)
    
    return var_constructor(host_uuid,peered,init_data)    


def create_new_variable_wrapper_from_serialized(
    host_uuid,serial_obj_named_tuple):
    '''
    @param {collections.namedtuple} serial_obj_named_tuple --- @see
    util._generate_serialization_named_tuple.  Should have elements
    var_name, var_type,var_data, version_obj_data.    

    When we are deserializing sequence local objects from messages
    sent from partner endpoint, we may not already have a
    waldoVariable to deserialize the variable into using
    deserialize_peered_object_into_variable.  In this case, we should
    first create a new _WaldoVariable to serialize into.

    This function takes a serial_obj_named_tuple, and returns a new
    variable with corresponding type to its var_type
    '''
    var_name = serial_obj_named_tuple.var_name
    var_type = serial_obj_named_tuple.var_type
    #### DEBUG: Testing whether got a valid type
    if var_type not in ReferenceTypeConstructorDict:
        util.logger_assert(
            'Error when in waldoNetworkSerializer.create_new_variable_' +
            'wrapper_from_serialized.  ' +
            'Unknown Waldo type requested for deserialization.')
    #### END DEBUG

    var_constructor = ReferenceTypeConstructorDict[var_type]
    if var_type == wVariables.WaldoUserStructVariable.var_type():
        # user structs require dict initializers.  for the time being,
        # it's okay to just write in an empt dict because we know we
        # will overwrite it anyways.
        return var_constructor(var_name,host_uuid,True,{})
        
    return var_constructor(var_name,host_uuid,True)


def deserialize_peered_object_into_variable(
    host_uuid,serial_obj_named_tuple,invalidation_listener,waldo_reference):
    '''
    @param {uuid} host_uuid --- The uuid of the host currently on.
    
    @param {collections.namedtuple} serial_obj_named_tuple --- @see
    util._generate_serialization_named_tuple.  Should have elements
    var_name, var_type,var_data, version_obj_data.    

    @param {_InvalidationListener} invalidation_listener --- The event
    that we are serializing to.

    @param {_ReferenceValue} waldo_reference --- We write the value
    and version found in serial_obj_named_tuple into the
    dirtymapelement corresponding to invalidation_listener in
    waldo_reference.  (Put another way, we try to append any changes
    that have happened to waldo_reference on the other endpoint to
    waldo_reference on this endpoint.)

    @returns {Nothing} --- Changes will be propagated through
    arguments.
    '''

    # FIXME: probably do not need "var_name"
    var_name = serial_obj_named_tuple.var_name

    serial_vobj = serial_obj_named_tuple.version_obj_data
    version_obj = RefVers.deserialize_version_obj_from_network_data(
        serial_vobj)

    var_type = serial_obj_named_tuple.var_type
    #### DEBUG: Testing whether got a valid type
    if var_type not in ReferenceTypeConstructorDict:
        util.logger_assert(
            'Error when in waldoNetworkSerializer.deserialize_peered_object' +
            '.  Unknown Waldo type requested for deserialization.')
    #### END DEBUG


    # var_data can either be a python value (string,bool,number) or a
    # python list/map or a SerializationHelperNamedTuple.  If it is a
    # list or map, it either has elements that are python values or it
    # has elements that are SerializationHelperNamedTuple-s.
    #
    # CASE 1: We have python values
    #   Put var_data directly into the dirty_map_element associated
    #   with invalidation_listener in waldo_reference.  Similarly copy
    #   over the version object.  (We cannot do this for
    #   SerializationHelperNamedTuples because these represent
    #   pointers to additional InternalMaps/Lists/Structs.  If we just
    #   copied over the values of these, then they would refer to
    #   different objects on the endpoint than they initially did.
    #   And we wouldn't be able to detect conflicts.)
    #
    # CASE 2: We have lists/maps of python values
    #   Do same as in Case 1.
    #
    # CASE 3: We have a single SerializationHelperNamedTuple
    #   This means that we are currently deserializing a
    #   WaldoVariable.  (One of the classes defined in wVariables.py.)
    #   There can be two cases for what happens.
    #   a: The WaldoVariable has not been written to.
    #      We want the changes to point to the same variable that we
    #      have been using.  Get the associated Waldo reference that
    #      waldo_reference points to and write the contents of the
    #      SerializationHelperNamedTuple into its dirty map element's
    #      val and version object.  This ensures that the changes that
    #      we are making will be made to the same waldo object on one
    #      endpoint as they were being made to the waldo object on the
    #      other endpoint.
    #   b: The WaldoVariable has been written to.
    #      What this means is that, at some point in this event, we
    #      re-defined the Waldo object that the peered variable was
    #      pointing to.  (Ie, we assigned the peered variable to
    #      another map/list/user struct.)  In this case, we should
    #      just do what we did in Case 1/Case 2.  We do NOT want our
    #      new changes to point to the same old reference.  We want
    #      them to point to a new reference.  
    #
    # CASE 4: We have a map/list of SerializationHelperNamedTuple-s
    #
    #  Here's why we need to keep track of whether each element was
    #  written to or read from.  Assume that we have a map of maps:
    #    Map(from: Text, to: Map(from: Text, to: Text)) m
    #
    #  It is important to distinguish:
    #     m['a'] = { 'other_a': 'other_a'}
    #  from
    #     m['a']['other_a'] = 'other_a' (assuming m['a'] is already defined)
    #  because if we have another operation
    #     m['a']['b'] = 'b'
    #  for the first case, there's a conflict, for the second they
    #  can execute in parallel
        
    # To determine whether written to or read from, use version_obj,
    # which will have type
    # waldoReferenceContainerBase._ReferenceContainerVersion.  For
    # each key within it that was written, added, or deleted, treat
    # the index similarly to 3b above.  For others, treat as 3a above.
        

    var_data = serial_obj_named_tuple.var_data
    if not isinstance(var_data,util._SerializationHelperNamedTuple):
        case1_or_case2 = True
        
        if isinstance(var_data,list):
            if ((len(var_data) != 0) and # it's fine to treat empty
                                         # lists as a list of python
                                         # values (instead of an empty
                                         # list of
                                         # SerHelperNamedTuple-s.
                                         # This is because we aren't
                                         # over-writing any pointed to
                                         # references by copying over
                                         # it.
                (isinstance(var_data[0],util._SerializationHelperNamedTuple))):
                case1_or_case2 = False
                
        if isinstance(var_data,dict):
            if ((len(var_data) != 0) and # see len comment in if
                                         # statement above.
                (isinstance(
                        var_data.itervalues().next(),
                        util._SerializationHelperNamedTuple))):
                case1_or_case2 = False

        if case1_or_case2:
            # CASE 1/2 above ... overwrite val and version object of
            # the variable's associated dirty map element.
                
            waldo_reference.update_version_and_val(
                invalidation_listener,version_obj,var_data)
            return

    else:
        # CASE 3 above: we have a single SerializationHelperNamedTuple
        # means that we must have a _ReferenceValue
        
        if not version_obj.has_been_written_to:
            # case 3a above
            nested_reference = waldo_reference.get_val(
                invalidation_listener)

            deserialize_peered_object_into_variable(
                host_uuid,var_data,invalidation_listener,nested_reference)
        else:
            # case 3b above
            
            # FIXME: It is correct to just create a new object here.
            # However, we do not necessarily need to create a new
            # object if we had written to the data object much earlier
            # in the event and have since updated both sides.  Could
            # incur a performance penalty doing this.

            new_obj = new_obj_from_serialized(
                host_uuid,var_data,invalidation_listener)

            
            waldo_reference.update_version_and_val(
                invalidation_listener,version_obj,new_obj)
            
        return

    # CASE 4 above: list/map of SerializationHelperNamedTuple-s
    
    # make it able to handle maps or lists.
    all_keys = range(0,len(var_data))
    if isinstance(var_data, dict):
        all_keys = list(var_data.keys())

    for key in all_keys:
        if ((key in version_obj.written_values_keys) or
            (key in version_obj.added_keys) or
            (key in version_obj.deleted_keys)):
            # handle same as 3b above

            # waldo_reference is an InternalMap/InternalDict and we
            # must notify it that this object has been
            # deleted/written/added
            new_obj = new_obj_from_serialized(
                host_uuid,var_data[key],invalidation_listener)
            waldo_reference.update_val_of_key_during_deserialize(
                invalidation_listener,key,new_obj)
        elif key in version_obj.read_values_keys:
            # only add others if have been read.  do not willy-nilly
            # add references.
            
            # handle same as 3a above...except getting val for target
            # key
            nested_reference = waldo_reference.get_val_on_key(
                invalidation_listener,key)
            # recurse
            deserialize_peered_object_into_variable(
                host_uuid,var_data[key],invalidation_listener,
                nested_reference)

    # remove any elements that may have been deleted by the other side
    if isinstance(var_data,dict):
        # it's a map.  look for keys that are not in all keys
        local_keys = waldo_reference.get_keys(invalidation_listener)
        for key in local_keys:
            if key not in all_keys:
                waldo_reference.del_key_called(invalidation_listener,key)
    if isinstance(var_data,list):
        if len(local_keys) > len(all_keys):
            # FIXME: if do something more intelligent about sliding
            # elements in the list down when they are not modified,
            # then may have to do something more intelligent than just
            # deleting off the end.
            num_times_to_delete = len(all_keys) - len(local_keys)
            for i in range(0,num_times_to_delete):
                # keep deleting the spot just beyond how long the list
                # should be.
                waldo_reference.del_key_called(
                    invalidation_listener,len(all_keys))
            
    # either way, reset the version obj of overall internal list/map
    waldo_reference.update_version_obj_during_deserialize(
        invalidation_listener,version_obj)
    
    

def new_obj_from_serialized(
    host_uuid,serial_obj_named_tuple,invalidation_listener):
    '''
    @param {collections.namedtuple} serial_obj_named_tuple --- @see
    util._generate_serialization_named_tuple.  Should have elements
    var_name, var_type,var_data, version_obj_data.
    
    @returns (a,b):
      a: a subtype of _ReferenceValue
      b: a version object (ie, a subtype of
         waldoReferenceBase._ReferenceVersion).
    '''

    var_name = serial_obj_named_tuple.var_name

    serial_vobj = serial_obj_named_tuple.version_obj_data
    version_obj = RefVers.deserialize_version_obj_from_network_data(
        serial_vobj)

    var_data = serial_obj_named_tuple.var_data
    var_type = serial_obj_named_tuple.var_type

    if isinstance(var_data,util._SerializationHelperNamedTuple):
        nested_obj = new_obj_from_serialized(
            host_uuid,var_data,invalidation_listener)
        new_obj = get_constructed_obj(
            var_type,var_name,host_uuid,True,nested_obj,
            invalidation_listener)
    else:
        if (isinstance(var_data,dict) and
            (len(var_data) != 0) and
            (isinstance(var_data.itervalues().next(),
                        util._SerializationHelperNamedTuple))):
            new_obj = {}
            for key in var_data.keys():
                new_obj[key] = get_constructed_obj(
                    var_type,var_name,host_uuid,True,var_data[key],
                    invalidation_listener)
                
        elif (isinstance(var_data,list) and
              (len(var_data) != 0) and
              (isinstance(var_data[0],
                          util._SerializationHelperNamedTuple))):

            new_obj = []
            for key in range(0,len(var_data)):
                new_obj.append(
                    get_constructed_obj(
                        var_type,var_name,host_uuid,True,var_data[key],
                        invalidation_listener))
        else:
            new_obj = get_constructed_obj(
                var_type,var_name,host_uuid,True,var_data,invalidation_listener)

    # do not need to copy in version object because creating a new
    # object, which means that no other events were able to perform
    # operations on new_obj anyways (because they could not see it).
    return new_obj
    
