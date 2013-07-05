import util
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
import wVariables

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


    # Pass constructors for waldo variables through to help with
    # serialization and deserialization.
    class VarConstructors(object):
        def __init__(self):
            self.list_constructor = wVariables.WaldoListVariable
            self.map_constructor = wVariables.WaldoMapVariable
            self.struct_constructor = wVariables.WaldoUserStructVariable

            self.single_thread_list_constructor = wVariables.WaldoSingleThreadListVariable
            self.single_thread_map_constructor = wVariables.WaldoSingleThreadMapVariable
            self.single_thread_struct_constructor = wVariables.WaldoSingleThreadUserStructVariable
            
            
    var_constructors = VarConstructors()

    
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
        print ('\nPrinting all in variable store')
        for key in self._name_to_var_map.keys():
            print (key)
        print ('\n')


    def generate_deltas(self,invalidation_listener,force,all_deltas=None):
        '''
        Create a map with an entry for each piece of peered data that
        was modified.  The entry should contain a
        _SerializationHelperNamedTuple that contains the delta
        representation of the object on the other side of the
        connection.

        @param {bool} force --- True if regardless of whether changed
        or not, we serialize and send its value.

        An example of when this would be used

        Sequence some_seq(Text a)
        {
            Side1.send_msg
            {
            }
            Side2.recv_msg
            {
               print (a);
            }
        }

        The first block does not actually modify a.  Therefore, it
        wouldn't be included in the message sent to Side2.recv_msg
        unless we force serialization of deltas for all sequence local
        data on the first message we send.
        
        @returns {VarStoreDeltas} @see varStoreDeltas.proto
        
        Should be deserializable and appliable from
        incorporate_deltas.
        '''
        if all_deltas == None:
            all_deltas = VarStoreDeltas()

        all_deltas.parent_type = VarStoreDeltas.VAR_STORE_DELTA

        for key in self._name_to_var_map.keys():
            waldo_variable = self._name_to_var_map[key]

            if waldo_variable.is_peered():
                waldo_variable.serializable_var_tuple_for_network(
                    all_deltas,key,invalidation_listener,force)

        return all_deltas

    def incorporate_deltas(self,invalidation_listener,var_store_deltas):
        '''
        @param {_InvalidationListener} invalidation_listener ---

        @param {varStoreDeltas.VarStoreDeltas message}
        
        @param {map} delta_map --- Produced from generate_deltas on
        partner endpoint.  Take this map, and incorporate the changes
        to each variable.  Indices are strings (unique names of Waldo
        variables).  Values are collections.namedtuples which are
        gennerated from util._generate_serialization_named_tuple for
        each waldo variable.
        '''
        
        # incorporate all numbers
        for num_delta in var_store_deltas.num_deltas:
            if num_delta.var_name not in self._name_to_var_map:
                # means that the variable was not in the variable
                # store already.  This could happen for instance if we
                # are creating a sequence local variable for the first
                # time.
                self._name_to_var_map[num_delta.var_name] = wVariables.WaldoNumVariable(
                    num_delta.var_name,self.host_uuid,True,num_delta.var_data)

            else:
                self._name_to_var_map[num_delta.var_name].write_if_different(
                    invalidation_listener,num_delta.var_data)

        # incorporate all texts
        for text_delta in var_store_deltas.text_deltas:
            if text_delta.var_name not in self._name_to_var_map:
                self._name_to_var_map[text_delta.var_name] = wVariables.WaldoTextVariable(
                    text_delta.var_name,self.host_uuid,True,text_delta.var_data)
            else:
                self._name_to_var_map[text_delta.var_name].write_if_different(
                    invalidation_listener,text_delta.var_data)

                
        # incorporate all true false-s
        for true_false_delta in var_store_deltas.true_false_deltas:
            if true_false_delta.var_name not in self._name_to_var_map:
                self._name_to_var_map[true_false_delta.var_name] = wVariables.WaldoTrueFalseVariable(
                    true_false_delta.var_name,self.host_uuid,True,true_false_delta.var_data)
            else:
                self._name_to_var_map[true_false_delta.var_name].write_if_different(
                    invalidation_listener,true_false_delta.var_data)

        # incorporate all maps
        for map_delta in var_store_deltas.map_deltas:
            if map_delta.var_name not in self._name_to_var_map:
                # need to create a new map and put all values in
                self._name_to_var_map[map_delta.var_name] = wVariables.WaldoMapVariable(
                    map_delta.var_name,self.host_uuid,True)
            self._name_to_var_map[map_delta.var_name].incorporate_deltas(
                map_delta,self.var_constructors,invalidation_listener)

        # incorporate all lists
        for list_delta in var_store_deltas.list_deltas:
            if list_delta.var_name not in self._name_to_var_map:
                # need to create a new map and put all values in
                self._name_to_var_map[list_delta.var_name] = wVariables.WaldoListVariable(
                    list_delta.var_name,self.host_uuid,True)
            self._name_to_var_map[list_delta.var_name].incorporate_deltas(
                list_delta,self.var_constructors,invalidation_listener)


        # incorporate all structs
        for struct_delta in var_store_deltas.struct_deltas:
            if struct_delta.var_name not in self._name_to_var_map:
                # need to create a new map and put all values in
                self._name_to_var_map[struct_delta.var_name] = wVariables.WaldoUserStructVariable(
                    struct_delta.var_name,self.host_uuid,True,{})
            self._name_to_var_map[struct_delta.var_name].incorporate_deltas(
                struct_delta,self.var_constructors,invalidation_listener)

            
