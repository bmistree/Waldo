import pickle

class DataWrapper(object):
    def __init__(self,val):
        self.val = val
    def write(self,val):
        self.val = val


class ValueTypeDataWrapper(DataWrapper):
    pass

class ReferenceTypeDataWrapper(DataWrapper):
    def __init__(self,val):
        # FIXME: does not work for nested waldo values...eg., a map of
        # maps
        val = pickle.loads(pickle.dumps(val))

    def write(self,val):
        self.val = val
