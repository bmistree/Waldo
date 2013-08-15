class DataWrapper(object):
    def __init__(self,val):
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

class ReferenceTypeDataWrapper(DataWrapper):
    def __init__(self,val):
        self.has_been_written_since_last_msg = False
        
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
        
