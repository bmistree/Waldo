import random

class DataItem(object):
    def __init__(self,key,val):
        self.key = key
        self.val = val

def get_data(num_items):
    data = []
    for i in range(0,num_items):
        key = str(random.random())
        val = str(random.random())
        data.append(DataItem(key,val))
    return data

