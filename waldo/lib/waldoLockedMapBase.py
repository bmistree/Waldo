import waldo.lib.util as util
from waldo.lib.waldoLockedContainerHelpers import container_serializable_var_tuple_for_network


class MapBaseClass(object):
    def get_write_key_incorporate_deltas(self,container_written_action):
        if container_written_action.HasField('write_key_text'):
            index_to_write_to = container_written_action.write_key_text
        elif container_written_action.HasField('write_key_num'):
            index_to_write_to = container_written_action.write_key_num
        elif container_written_action.HasField('write_key_tf'):
            index_to_write_to = container_written_action.write_key_tf
        #### DEBUG
        else:
            util.logger_assert('Unknown map index')
        #### END DEBUG

        return index_to_write_to


    def get_add_key_incorporate_deltas(self,container_added_action):
        if container_added_action.HasField('added_key_text'):
            index_to_add_to = container_added_action.added_key_text
        elif container_added_action.HasField('added_key_num'):
            index_to_add_to = container_added_action.added_key_num
        elif container_added_action.HasField('added_key_tf'):
            index_to_add_to = container_added_action.added_key_tf
        #### DEBUG
        else:
            util.logger_assert('Unknown map index')
        #### END DEBUG

        return index_to_add_to

    
    def get_delete_key_incorporate_deltas(self,container_deleted_action):
        if container_deleted_action.HasField('deleted_key_text'):
            index_to_del_from = container_deleted_action.deleted_key_text
        elif container_deleted_action.HasField('deleted_key_num'):
            index_to_del_from = container_deleted_action.deleted_key_num
        elif container_deleted_action.HasField('deleted_key_tf'):
            index_to_del_from = container_deleted_action.deleted_key_tf
        #### DEBUG
        else:
            util.logger_assert('Error in delete: unknown key type.')
        #### END DEBUG

        return index_to_del_from

    def handle_added_key_incorporate_deltas(
        self,active_event,index_to_add_to,new_val):
        self.add_key(active_event,index_to_add_to,new_val,False)


    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,active_event,force):
        '''
        @see waldoReferenceBase.serializable_var_tuple_for_network
        '''
        container_serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force,True)

