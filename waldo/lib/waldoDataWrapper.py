class DataWrapper(object):
    def __init__(self,val):
        self.val = val
    def write(self,val):
        self.val = val


class ValueTypeDataWrapper(DataWrapper):
    pass

class ReferenceTypeDataWrapper(DataWrapper):
    def __init__(self,val):
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
            
    def write(self,val):
        self.val = val
