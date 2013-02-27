import util
import pickle
import waldoNetworkSerializer

'''
_VariableStore keeps track of peered data, sequence local data (which
also has its peered bit marked in its WaldoReferenceBase), and a
single endpoint's global data.  Events can query the variable store
for these variables and also to determine what peered data have been
modified by an event (so that we know what to serialize to other sides
when completing a sequence block call).

An endpoint holds a single _VariableStore, global_store, which holds
endpoint global and peered data.  This gets created once on each
endpoint when the connection is first established.  It should neither
shrink nor grow.  Each executing event also has a copy of another
_VariableStore that keeps track of sequence local stae.

Three challenges:

  1) Problem: When requesting sequence blocks calls on our partner, we need to
     identify which peered and sequence local data have changed
     locally.  That way, we can send only modified data to the other
     side.

     Solution: @see _VariableStore.generate_deltas below.  Just run
     through all stored data and return all data that this
     invalidation listener has modified since beginning.

  2) We need to use consistent names for these modified data between
     both endpoints so that we can associate the variables on each
     side with each other.

     Solution: Each peered wVariable has a unique name????  The
     _name_to_var_map in each _VariableStore is indexed by these
     names.
     
     
  3) Through the course of a message sequence, we need to keep a list
     of sequence-local data available.

     Solution: We have a single execution event per message that we
     receive.  Each has its own separate context,
     _ExecutionEventContext, that holds on to a copy of a separate
     variable store for sequence local data.
'''

class _VariableStore(object):
    '''
    Each executing event has two, separate stores:

       * global_store --- Keeps track of endpoint globals as well as
         peered data.  Note: cannot change global_store.  Values there
         will only be written once.

       * sequence_local_store --- Keeps track of sequence local data.

    (Local data and function arguments are not put in any store.)

    Can query the variable store with the unique name of a variable to
    get the variable back for use.
    '''
    
    def __init__(self,host_uuid):

        self.host_uuid = host_uuid
        # string to _WaldoVariable
        self._name_to_var_map = {}

    def add_var(self,unique_name,waldo_variable):
        '''
        @param {String} unique_name ---

        @param {_WaldoVariable} waldo_variable 
        '''
        #### DEBUG
        if self.get_var_if_exists(unique_name) != None:
            util.logger_assert(
                'Already had an entry for variable trying to ' +
                'insert into store.')
        #### END DEBUG
            
        self._name_to_var_map[unique_name] = waldo_variable

        
    def get_var_if_exists(self,unique_name):
        '''
        @param {String} unique_name --- 
        
        @returns {_WaldoVariable or None} --- None if variable does
        not exist, _WaldoVariable otherwise.
        '''
        return self._name_to_var_map.get(unique_name,None)


    def _debug_print_all_vars(self):
        '''
        Runs through internal map and prints all keys to stdout
        '''
        print '\nPrinting all in variable store'
        for key in self._name_to_var_map.keys():
            print key
        print '\n'            
        
    def generate_deltas(self,invalidation_listener):
        '''
        Create a map with an entry for each piece of peered data that
        was modified.  The entry should contain a
        _SerializationHelperNamedTuple that contains the delta
        representation of the object on the other side of the
        connection.

        @returns{string} --- After this, pickle map into string and
        return it.
        
        This string should be deserializable and appliable from
        incorporate_deltas.
        '''
        changed_map = {}
        
        for key in self._name_to_var_map.keys():
            waldo_variable = self._name_to_var_map[key]

            if waldo_variable.modified(invalidation_listener):
                changed_map[key] = waldo_variable.serializable_var_tuple_for_network(
                    key,invalidation_listener)

        return changed_map
    

    def incorporate_deltas(self,invalidation_listener,delta_map):
        '''
        @param {_InvalidationListener} invalidation_listener ---

        @param {map} delta_map --- Produced from generate_deltas on
        partner endpoint.  Take this map, and incorporate the changes
        to each variable.  Indices are strings (unique names of Waldo
        variables).  Values are collections.namedtuples which are
        gennerated from util._generate_serialization_named_tuple for
        each waldo variable.
        '''
        # if it is sequence local data, it could be that we have no
        # entries in our name_to_var_map and must write in the changes
        # from the other side.
        for key in delta_map.keys():
            if key not in self._name_to_var_map:
                # need to create a new variable of the same type.
                # then, need to apply that variable's changes.
                new_var = waldoNetworkSerializer.create_new_variable_wrapper_from_serialized(
                    self.host_uuid,delta_map[key])
                self._name_to_var_map[key] = new_var
                
            waldoNetworkSerializer.deserialize_peered_object_into_variable(
                self.host_uuid,delta_map[key],invalidation_listener,
                self._name_to_var_map[key])

