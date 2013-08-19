from waldo.lib.waldoLockedObj import WaldoLockedObj
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
import numbers
import waldo.lib.util as util

class DataWrapper(object):
    def __init__(self,val,peered):
        self.val = val
        self.has_been_written_since_last_msg = False
    def write(self,val,updating_from_partner=False):
        '''
        @param {bool} updating_from_partner --- We do not want to mark
        an object as having been written if we are just updating its
        value from partner.
        '''
        self.val = val
        if not updating_from_partner:
            self.has_been_written_since_last_msg = True
            
    def get_and_reset_has_been_written_since_last_msg(self):
        to_return = self.has_been_written_since_last_msg
        self.has_been_written_since_last_msg = False
        return to_return


class ValueTypeDataWrapper(DataWrapper):
    pass


DELETE_FLAG = 0
ADD_FLAG = 1
WRITE_FLAG = 2
def delete_key_tuple(key):
    return (DELETE_FLAG,key)
def is_delete_key_tuple(tup):
    return tup[0] == DELETE_FLAG

def add_key_tuple(key):
    return (ADD_FLAG,key)
def is_add_key_tuple(tup):
    return tup[0] == ADD_FLAG

def write_key_tuple(key):
    return (WRITE_FLAG,key)
def is_write_key_tuple(tup):
    return tup[0] == WRITE_FLAG


class ReferenceTypeDataWrapper(DataWrapper):
    def __init__(self,val,peered):
        '''
        For peered data, keep track of operations made on data so that
        can update other side with deltas instead of overwriting full.
        '''
        self.has_been_written_since_last_msg = False
        self.peered = peered

        # tracks all insertions, removals, etc. made to this reference
        # object so can send deltas across network to partners.
        # (Note: only used for peered data.)
        self.partner_change_log = []

        self.val = val
        
        # if isinstance(val,ReferenceTypeDataWrapper):
        #     val = val.val
            
        # if isinstance(val,dict):
        #     self.val = {}
        #     for key in val:
        #         self.val[key] = val[key]
        # else:
        #     self.val = []
        #     for list_val in val:
        #         self.val.append(list_val)

    def set_val_on_key(self,active_event,key,to_write,incorporating_deltas=False):
        '''
        @param {bool} incorporating_deltas --- True if we are setting
        a value as part of incorporating deltas that were made by
        partner to peered data.  In this case, we do not want to log
        the changes: we do not want our partner to replay the same
        changes they already have.
        '''
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(write_key_tuple(key))

        return self.val[key].set_val(active_event,to_write)

    def del_key (self,active_event,key_to_delete,incorporating_deltas=False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(delete_key_tuple(key_to_delete))
            
        del wrapped_val.val[key_to_delete]

    def add_key(self, active_event, key_added, new_val, incorporating_deltas=False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(add_key_tuple(key_added))

        self.val[key_added] = new_val

    def insert(self,active_event,where_to_insert,new_val,incorporating_deltas = False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(add_key_tuple(len(self.val)))

        self.val.insert(where_to_insert,new_val)


    def append(self,active_event,new_val,incorporating_deltas=False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(add_key_tuple(len(self.val)))

        self.val.append(new_val)


    def add_all_data_to_delta_list(
        self,delta_to_add_to,current_internal_val,action_event,for_map):
        '''
        Run through entire list.  Create an add action for each element.

        @param {bool} for_map --- True if performing operations for
        map.  false if performing for list.
        '''
        if for_map:
            to_iter_over = current_internal_val.keys()
        else:
            to_iter_over = range(0,len(current_internal_val))

            
        for key in to_iter_over:
            if for_map:
                action = delta_to_add_to.map_actions.add()
            else:
                action = delta_to_add_to.list_actions.add()

            action.container_action = VarStoreDeltas.ContainerAction.ADD_KEY

            add_action = action.added_key
            add_action.parent_type = VarStoreDeltas.CONTAINER_ADDED

            if isinstance(key,numbers.Number):
                add_action.added_key_num = key
            elif util.is_string(key):
                add_action.added_key_text = key
            else:
                add_action.added_key_tf = key

            
            # now actually add the value to the map
            list_val = current_internal_val[key]

            
            if isinstance(list_val,numbers.Number):
                add_action.added_what_num = list_val
            elif util.is_string(list_val):
                add_action.added_what_text = list_val
            elif isinstance(list_val,bool):
                add_action.added_what_tf = list_val
            elif isinstance(list_val,WaldoLockedObj):
                list_val.serializable_var_tuple_for_network(
                    add_action,'',action_event,True)
                
            #### DEBUG
            else:
                util.logger_assert(
                    'Unkonw type to serialize')
            #### END DEBUG
                

    def add_to_delta_list(
        self,delta_to_add_to,current_internal_val,action_event, for_map):
        '''
        @param {varStoreDeltas.SingleListDelta} delta_to_add_to ---

        @param {list} current_internal_val --- The internal val of the action event.

        @param {_InvalidationListener} action_event

        @param {bool} for_map --- True if performing operations for
        map.  false if performing for list.
        
        @returns {bool} --- Returns true if have any changes to add false otherwise.
        '''
        modified_indices = {}

        changes_made = False

        # FIXME: only need to keep track of change log for peered
        # variables.  May be expensive to otherwise.
        for partner_change in self.partner_change_log:
            changes_made = True

            # FIXME: no need to transmit overwrites.  but am doing
            # that currently.
            if for_map:
                action = delta_to_add_to.map_actions.add()                
            else:
                action = delta_to_add_to.list_actions.add()

            if is_delete_key_tuple(partner_change):
                action.container_action = VarStoreDeltas.ContainerAction.DELETE_KEY
                delete_action = action.deleted_key
                key = partner_change[1]
                modified_indices[key] = True
                if isinstance(key,numbers.Number):
                    delete_action.deleted_key_num = key
                elif util.is_string(key):
                    delete_action.deleted_key_text = key
                elif isinstance(key,bool):
                    delete_action.deleted_key_tf = key
                #### DEBUG
                else:
                    util.logger_assert('Unknown map key type when serializing')
                #### END DEBUG


            elif is_add_key_tuple(partner_change):
                key = partner_change[1]
                modified_indices[key] = True

                key_in_internal = key < len(current_internal_val)
                if for_map:
                    key_in_internal = (key in current_internal_val)

                if key_in_internal:
                    # note, key may not be in internal val, for
                    # instance if we had deleted it after adding.
                    # in this case, can ignore the add here.

                    action.container_action = VarStoreDeltas.ContainerAction.ADD_KEY
                    add_action = action.added_key
                    add_action.parent_type = VarStoreDeltas.CONTAINER_ADDED

                    if isinstance(key,numbers.Number):
                        add_action.added_key_num = key
                    elif util.is_string(key):
                        add_action.added_key_text = key
                    elif isinstance(key,bool):
                        add_action.added_key_tf = key
                    #### DEBUG
                    else:
                        util.logger_assert('Unknown map key type when serializing')
                    #### END DEBUG

                    # now actually add the value to the map
                    list_val = current_internal_val[key]

                    if isinstance(list_val,numbers.Number):
                        add_action.added_what_num = list_val
                    elif util.is_string(list_val):
                        add_action.added_what_text = list_val
                    elif isinstance(list_val,bool):
                        add_action.added_what_tf = list_val

                    elif isinstance(list_val,WaldoLockedObj):
                        list_val.serializable_var_tuple_for_network(
                            add_action,'',action_event,
                            # true here because if anything is written
                            # or added, then we must force the entire
                            # copy of it.
                            True)
                    #### DEBUG
                    else:
                        util.logger_assert(
                            'Unkonw type to serialize')
                    #### END DEBUG


            elif is_write_key_tuple(partner_change):
                key = partner_change[1]
                modified_indices[key] = True

                key_in_internal = key < len(current_internal_val)
                if for_map:
                    key_in_internal = (key in current_internal_val)

                if key_in_internal:
                    action.container_action = VarStoreDeltas.ContainerAction.WRITE_VALUE
                    write_action = action.write_key

                    write_action.parent_type = VarStoreDeltas.CONTAINER_WRITTEN

                    if isinstance(key,numbers.Number):
                        write_action.write_key_num = key
                    elif util.is_string(key):
                        write_action.write_key_text = key
                    elif isinstance(key,bool):
                        write_action.write_key_tf = key
                    #### DEBUG
                    else:
                        util.logger_assert('Unknown map key type when serializing')
                    #### END DEBUG


                    list_val = current_internal_val[key]
                    if isinstance(list_val,numbers.Number):
                        write_action.what_written_num = list_val
                    elif util.is_string(list_val):
                        write_action.what_written_text = list_val
                    elif isinstance(list_val,bool):
                        write_action.what_written_tf = list_val
                    else:
                        list_val.serializable_var_tuple_for_network(
                            write_action,'',action_event,
                            # true here because if anything is written
                            # or added, then we must force the entire
                            # copy of it.
                            True)

            #### DEBUG
            else:
                util.logger_assert('Unknown container operation')
            #### END DEBUG

        if for_map:
            to_iter_over = current_internal_val.keys()
        else:
            to_iter_over = range(0,len(current_internal_val))


        for index in to_iter_over:
            list_val = current_internal_val[index]

            if not isinstance(list_val,WaldoLockedObj):
                break

            if index not in modified_indices:
                # create action
                sub_element_action = delta_to_add_to.sub_element_update_actions.add()
                sub_element_action.parent_type = VarStoreDeltas.SUB_ELEMENT_ACTION

                if isinstance(map_key,numbers.Number):
                    sub_element_action.key_num = index
                elif util.is_string(map_key):
                    sub_element_action.key_text = index
                else:
                    sub_element_action.key_tf = index


                if map_val.serializable_var_tuple_for_network(sub_element_action,'',action_event,False):
                    changes_made = True
                else:
                    # no change made to subtree: go ahead and delete added subaction
                    del delta_to_add_to.sub_element_update_actions[-1]


        # clean out change log: do not need to re-send updates for
        # these changes to partner, so can just reset after sending
        # once.
        self.partner_change_log = []
        return changes_made


        
