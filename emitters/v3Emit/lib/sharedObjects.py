#!/usr/bin/env python

import numbers;

class _Shared(object):
    def __init__ (self,initialVal,resourceManager):
        # Will get written with a valid value when registering it with
        # resourceManager.
        self.id = None;
        
        self.val = initialVal;
        self.committedVal = _deepCopy(initialVal);
        resourceManager.registerShared(self);
        self.hasChanged = False;
        
    def _get(self):
        return self.val;
    
    def _set(self,toSetTo):
        self.val = toSetTo;
        self.hasChanged = True;
        
    def _commit(self):
        if self.hasChanged:
            self.committedVal = _deepCopy(self.val);
            self.hasChanged = False;
        
    def _backout(self):
        if self.hasChanged:
            self.val = _deepCopy(self.committedVal);
            self.hasChanged = False;
        
def _deepCopy(valToCopy):
    if isinstance(valToCopy, dict):
        returner = {};
        for key in valToCopy:
            returner[ _deepCopy(key) ] = _deepCopy(valToCopy);
    elif isinstance(valToCopy,list):
        returner = [];
        for index in range(0,len(valToCopy)):
            returner[ index ] = _deepCopy(valToCopy);
    elif (isinstance(valToCopy, numbers.Number) or
          isinstance(valToCopy, basestring) or
          isinstance(valToCopy,bool)):
        returner = valToCopy;
    else:
        assert(False);

    return returner;
        
class SharedTrueFalse(_Shared):
    def __init__(self,initialVal,resourceManager):
        if isinstance(initialVal,bool):
            _Shared.__init__(self,initialVal,resourceManager);
        else:
            errMsg = '\nError required TrueFalse type in SharedTrueFalse.\n';
            print(errMsg);
            assert(False);
            
class SharedNumber(_Shared):
    def __init__(self,initialVal,resourceManager):
        if isinstance(initialVal,numbers.Number):
            _Shared.__init__(self,initialVal,resourceManager);
        else:
            errMsg = '\nError required number type in SharedNumber.\n';
            print(errMsg);
            assert(False);

class SharedText(_Shared):
    def __init__(self,initialVal,resourceManager):
        if isinstance(initialVal,basestring):
            _Shared.__init__(self,initialVal,resourceManager);
        else:
            errMsg = '\nError required string type in SharedText.\n';
            print(errMsg);
            assert(False);


class SharedList(_Shared):
    '''
    Note: all lists are initialized empty
    '''
    def __init__(self,resourceManager):
        _Shared.__init__(self,[],resourceManager);

    def _list_get(self,index_to_get):
        return self.val[index_to_get]

    def _list_in(self,val_to_check):
        return val_to_check in self.val

    def _list_iter(self):
        return iter(self.val)

    def _list_append(self,to_append):
        self.val.append(to_append)

    # eventually
    def _list_del(self,index_to_del):
        del self.val[index_to_del]
        
    def _list_insert(self,index_to_insert,val_to_insert):
        self.val[index_to_insert] = val_to_insert

        
    
class SharedMap(_Shared):
    '''
    Note: all maps are initialized empty
    '''
    def __init__(self,resourceManager):
        _Shared.__init__(self,{},resourceManager);

    def _map_get(self,index_to_get,default=None):
        '''
        @param{anything} index_to_get --- Index to use to get a field
        from the map.
        '''
        return self.val.get(index_to_get,default)

    def _map_in(self,index_to_check):
        return index_to_check in self.val

    def _map_keys(self):
        return self.val.keys()

    def _map_iter(self):
        return iter(self.val)

    
        
class SharedFile(SharedText):

    def __init__(self,filename,file_contents,resource_manager):
        self.filename = filename
        SharedText.__init__(self,file_contents,resource_manager)
        self._write_committed()

    def _write_committed(self):
        '''
        Acutally writes committed value to file.  Could do something
        much more sensible here with only writing changed parts, etc.
        But good enough for now.
        '''
        filer = open(self.filename,'w')
        filer.write(self.committedVal)
        filer.flush()
        filer.close()
        
    def _commit(self):
        '''
        Generic commit, plus actually write commit to file system.
        '''
        SharedText._commit(self)
        self._write_committed()
        
