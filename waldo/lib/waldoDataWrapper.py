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
        
        if isinstance(val,ReferenceTypeDataWrapper):
            val = val.val
            
        if isinstance(val,dict):
            self.val = {}
            for key in val:
                self.val[key] = val[key]
        else:
            self.val = []
            for list_val in val:
                self.val.append(list_val)

    def set_val_on_key(self,active_event,key,to_write,incorporating_deltas=False):
        '''
        @param {bool} incorporating_deltas --- True if we are setting
        a value as part of incorporating deltas that were made by
        partner to peered data.  In this case, we do not want to log
        the changes: we do not want our partner to replay the same
        changes they already have.
        '''
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(set_val_tuple(key))

        return self.val[key].set_val(active_event,to_write)

    def del_key (self,active_event,key_to_delete,incorporating_deltas=False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(delete_key_tuple(key_to_delete))
            
        del wrapped_val.val[key_to_delete]

    def add_key(self,active_event,key_added,new_val,incorporating_deltas=False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(add_key_tuple(key_added))

        self.val[key_added] = new_val

    def insert(self,active_event,where_to_insert,new_val,incorporating_deltas = False):
        util.logger_assert(
            'Insertion still unsupported')

    def append(self,active_event,new_val,incorporating_deltas=False):
        if self.peered and (not incorporating_deltas):
            self.partner_change_log.append(add_key_tuple(len(self.val)))

        self.val.append(new_val)

    
