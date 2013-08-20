import waldo.lib.util as util
from waldo.lib.waldoLockedContainerHelpers import container_serializable_var_tuple_for_network

class ListBaseClass(object):
    def get_write_key_incorporate_deltas(self,container_written_action):
        return int(container_written_action.write_key_num)

    def get_add_key_incorporate_deltas(self,container_added_action):
        return int(container_added_action.added_key_num)
    
    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        return int(container_deleted_action.deleted_key_num)
        
    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        self.add_key(active_event,index_to_add_to,new_val,False)


    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        container_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force,False)

    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        self.insert_val(active_event,index_to_add_to,new_val,False)

