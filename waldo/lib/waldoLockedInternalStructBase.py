from waldoLockedInternalMapBase import InternalMapBaseClass
from waldo.lib.waldoLockedContainerHelpers import container_serializable_var_tuple_for_network
from waldo.lib.waldoLockedContainerHelpers import FOR_STRUCT_CONTAINER_SERIALIZABLE

class InternalStructBaseClass(InternalMapBaseClass):
    '''
    Should look identical to internal map base class
    '''
    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        container_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force,FOR_STRUCT_CONTAINER_SERIALIZABLE)
        
    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        self.add_key(active_event,index_to_add_to,new_val,FOR_STRUCT_CONTAINER_SERIALIZABLE)
