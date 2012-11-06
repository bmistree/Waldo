#!/usr/bin/env python

import numbers;

class _Shared(object):
    def __init__ (self,initialVal,resourceManager):
        # Will get written with a valid value when registering it with
        # resourceManager.
        self.id = None;

        self.val = _deepCopy(initialVal);
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
        # FIXME: should be able to handle copying lists and maps as
        # well as value types
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



class _WaldoListMapObj(object):
    '''
    Moderately bad form to just copy and paste this definition from
    uniform header: requires synchronization between compiler and
    external libraries.  But it's better than having to do a bunch of
    import path setup to get both to point to same code.
    
    Waldo lists and maps support special operations that are like
    regular maps and lists, but allow us to instrument external lists
    and maps to do special things.  For instance, if we have an
    external list/map that represents the file system, for each get
    performed on it, we could actually read the file from the file
    system.  That way, do not have to hold full file system in memory,
    but just fetch resources whenever they are required.
    '''

    def _map_list_serializable_obj(self):
        '''
        Must be able to serialize maps and lists to send across the
        network to the opposite side.  This function call returns an
        object that can be string-ified by a call to json.dumps.

        If values in list/map are lists or maps themselves, need to
        get serializable objects for these too.
        '''

        # pure virtual function in parent class.  must define in each
        # of map and list itself.
        assert(False)

    
    def _map_list_bool_in(self,val_to_check):
        return val_to_check in self.val

    def _map_list_iter(self):
        return iter(self.val)

    def _map_list_index_insert(self,index_to_insert,val_to_insert):
        self.val[index_to_insert] = val_to_insert

    def _map_list_len(self):
        return len(self.val)
        
    def _map_list_index_get(self,index_to_get):
        '''
        @param{anything} index_to_get --- Index to use to get a field
        from the map.
        '''
        return self.val[index_to_get]

    def _map_list_copy_return(self):
        '''
        When returning data from out of Waldo to application code,
        perform a deep copy of Waldo list/map so that have isolation
        between Waldo and non-Waldo code.
        '''

        # FIXME: should actually check more concretely the type of the
        # object.
        def _fixme_is_waldo_map(to_check):
            to_check_type = type(to_check)
            return '_WaldoMap' in str(to_check_type)
        def _fixme_is_waldo_list(to_check):
            to_check_type = type(to_check)
            return '_WaldoList' in str(to_check_type)
        
        def _copied_dict(to_copy):
            '''
            Produces a copy of to_copy, where all the WaldoLists
            and maps are replaced by python lists and dicts.
            '''
            new_dict = {}
            for key in to_copy.keys():
                to_add = to_copy[key]

                # if isinstance(to_add,_WaldoMap):
                if _fixme_is_waldo_map(to_add):
                    to_add = _copied_dict(to_add._map_list_serializable_obj())
                # elif isinstance(to_add,_WaldoList):                    
                elif _fixme_is_waldo_list(to_add):
                    to_add = _copied_list(to_add._map_list_serializable_obj())

                elif isinstance(to_add,dict):
                    to_add = _copied_dict(to_add)
                elif isinstance(to_add,list):
                    to_add = _copied_list(to_add)

                new_dict[key] = to_add
            return new_dict

        
        
        def _copied_list(to_copy):
            '''
            Produces a copy of to_copy, where all the WaldoLists
            and maps are replaced by python lists and dicts.
            '''        
            new_array = []
            for item in to_copy:
                to_add = item
                if _fixme_is_waldo_map(to_add):                
                # if isinstance(to_add,_WaldoMap):
                    to_add = _copied_dict(to_add._map_list_serializable_obj())
                # elif isinstance(to_add,_WaldoList):
                elif _fixme_is_waldo_list(to_add):                    
                    to_add = _copied_list(to_add._map_list_serializable_obj())

                elif isinstance(to_add,dict):
                    to_add = _copied_dict(to_add)
                elif isinstance(to_add,list):
                    to_add = _copied_list(to_add)

                new_array.append(to_add)

            return new_array

        
        # FIXME: Actually need to perform deep copy of data out.
        if isinstance(self.val,list):
            return _copied_list(self.val)
        return _copied_dict(self.val)

            
            
class SharedList(_Shared,_WaldoListMapObj):
    def __init__(self,initial_val,resourceManager):
        _Shared.__init__(self,initial_val,resourceManager);

    def _list_append(self,to_append):
        self.val.append(to_append)

    # eventually
    def _list_del(self,index_to_del):
        del self.val[index_to_del]
        
    
class SharedMap(_Shared,_WaldoListMapObj):

    # eventually
    def _map_keys(self):
        return self.val.keys()

        
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


import os

class SharedFs(SharedMap):
    def __init__(self,folder_name,resource_manager):
        self.folder_name = folder_name
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            
        SharedMap.__init__(self,{},resource_manager)
        self._write_committed()

    def _backout(self):
        if self.hasChanged:
            self.val = {}
            self.hasChanged = False;

    def _set(self,toSetTo):
        self.val = toSetTo;
        self.hasChanged = True;
            
    def _write_committed(self):
        # self.val contains all changes made to file.
        for key in self.val.keys():
            filer = open(os.path.join(self.folder_name,key),'w')
            filer.write(self.val[key])
            filer.flush()
            filer.close()

        self.val = {}
        self.hasChanged = False
        
        
    def _commit(self):
        '''
        Generic commit, plus actually write commit to file system.
        '''
        print '\n\nGot into commit\n\n'
        self._write_committed()


    def _map_list_serializable_obj(self):
        assert(False)

    
    def _map_list_bool_in(self,val_to_check):
        # check fs to see if file exists
        return os.path.exists(
            os.path.join(self.folder_name,val_to_check))

    def _get_list_of_filenames(self):
        list_of_filenames = []
        for root_dir,dirs,filenames in os.walk(self.folder_name):
            for filename in filenames:
                if (filename == '.') or (filename == '..'):
                    continue
                
                list_of_filenames.append(
                    os.path.join(root_dir,filename))

        return list_of_filenames
        
    def _map_list_iter(self):
        dict_filenames = {}
        for filename in self._get_list_of_filenames():
            dict_filenames[filename] = True
        for filename in self.val:
            dict_filenames[filename] = True
        
        return dict_filenames.keys()

    def _map_list_index_insert(self,index_to_insert,val_to_insert):
        # print '\n\ngot an index to insert'
        # print index_to_insert
        # print val_to_insert
        # print '\n\n'
        self.val[index_to_insert] = val_to_insert

    def _map_list_len(self):
        dict_of_filenames = {}
        for filename in self.get_list_of_filenames():
            dict_of_filenames[filename] = True
        for filename in self.val:
            dict_of_filenames[filename] = True
        
        return len(dict_of_filenames)
        
    def _map_list_index_get(self,index_to_get):
        if index_to_get in self.val:
            return self.val[index_to_get]

        filer = open(
            os.path.join(self.folder_name,index_to_get))
        to_return = filer.read()
        filer.close()
        self.val[index_to_get] = to_return
        return to_return

    def _map_list_copy_return(self):
        list_filenames = self._get_list_of_filenames()
        
        to_return = {}
        for filename in list_filenames:
            filer = open(
                os.path.join(self.folder_name,filename))
            to_return[filename] = filer.read()
            filer.close()
        
        return to_return

    
