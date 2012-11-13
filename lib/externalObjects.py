#!/usr/bin/env python

import numbers;

class _External(object):
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
        
class ExternalTrueFalse(_External):
    def __init__(self,initialVal,resourceManager):
        if isinstance(initialVal,bool):
            _External.__init__(self,initialVal,resourceManager);
        else:
            errMsg = '\nError required TrueFalse type in ExternalTrueFalse.\n';
            print(errMsg);
            assert(False);
            
class ExternalNumber(_External):
    def __init__(self,initialVal,resourceManager):
        if isinstance(initialVal,numbers.Number):
            _External.__init__(self,initialVal,resourceManager);
        else:
            errMsg = '\nError required number type in ExternalNumber.\n';
            print(errMsg);
            assert(False);

class ExternalText(_External):
    def __init__(self,initialVal,resourceManager):
        if isinstance(initialVal,basestring):
            _External.__init__(self,initialVal,resourceManager);
        else:
            errMsg = '\nError required string type in ExternalText.\n';
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

    def _map_list_remove(self,index_to_del):
        del self.val[index_to_del]

    def _map_list_index_insert(self,index_to_insert,val_to_insert):
        self.val[index_to_insert] = val_to_insert
        
    def _map_list_bool_in(self,val_to_check):
        return val_to_check in self.val

    def _map_list_iter(self):
        return iter(self.val)

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

            
            
class ExternalList(_External,_WaldoListMapObj):
    def __init__(self,initial_val,resourceManager):
        _External.__init__(self,initial_val,resourceManager);

    def _list_append(self,to_append):
        self.val.append(to_append)

        
    
class ExternalMap(_External,_WaldoListMapObj):

    # eventually
    def _map_keys(self):
        return self.val.keys()

        
class ExternalFile(ExternalText):

    def __init__(self,filename,file_contents,resource_manager):
        self.filename = filename
        ExternalText.__init__(self,file_contents,resource_manager)
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
        ExternalText._commit(self)
        self._write_committed()


import os

class ExternalFs(ExternalMap):
    def __init__(self,folder_name,resource_manager):
        self.folder_name = folder_name
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        # keeps track of files that we are scheduling to remove.  when
        # committing, run through list and remove these from the fs.
        self.to_remove = {}
        
        ExternalMap.__init__(self,{},resource_manager)
        self._write_committed()

    def _backout(self):
        if self.hasChanged:
            self.val = {}
            self.hasChanged = False;

    def _map_list_remove(self,index_to_del):

        if index_to_del in self.val:
            del self.val[index_to_del]
            
        self.to_remove[index_to_del] = True
        self.hasChanged = True
        
    def _map_list_index_insert(self,index_to_insert,val_to_insert):
        if index_to_insert in self.to_remove:
            del self.to_remove[index_to_insert]
        self.val[index_to_insert] = val_to_insert
        self.hasChanged = True


    def _set(self,toSetTo):
        # if we set the map to a new value, we must delete all the
        # other values that it previously contained on the file
        # system.  get a list of all files on the file system and add
        # them to self.to_remove (for deletion on commit) if they
        # aren't in the new map that we're setting to.
        self.to_remove = {}
        list_filenames = self._get_list_of_filenames()
        for filename in list_filenams:
            if not (filename in toSetTo):
                self.to_remove[filename] = True

        self.val = toSetTo;
        self.hasChanged = True;
            
    def _write_committed(self):
        # self.val contains all changes made to file.
        for key in self.val.keys():
            filer = open(os.path.join(self.folder_name,key),'w')
            filer.write(self.val[key])
            filer.flush()
            filer.close()

        for key in self.to_remove.keys():
            filename = os.path.join(self.folder_name,key)
            
            if os.path.exists(filename):
                os.remove(filename)
            
        self.val = {}
        self.to_remove = {}        
        self.hasChanged = False

        
    def _commit(self):
        '''
        Generic commit, plus actually write commit to file system.
        '''
        self._write_committed()


    def _map_list_serializable_obj(self):
        # only call serializable obj when transferring the object from
        # one endpoint to the other.  Should never be allowed to do
        # this with an external.
        assert(False)

    
    def _map_list_bool_in(self,val_to_check):

        # already asked to remove value
        if val_to_check in self.to_remove:
            return False

        # check fs to see if file exists
        dict_filenames = self._get_dict_of_filenames_on_fs()
        if val_to_check in dict_filenames:
            return True

        # otherwise, if in buffer of actions to write, return true
        # (the file may have just been created on this sequence.
        return val_to_check in self.val

    def _get_dict_of_filenames_on_fs(self):
        dict_of_filenames = {}
        for root_dir,dirs,filenames in os.walk(self.folder_name):
            for filename in filenames:
                if (filename == '.') or (filename == '..'):
                    continue

                dict_of_filenames[filename] = True

        return dict_of_filenames
        
    def _map_list_iter(self):
        dict_filenames = self._get_dict_of_filenames_on_fs()
        for filename in self.val:
            dict_filenames[filename] = True

        for filename in self.to_remove:
            if filename in dict_filenames:
                del dict_filenames[filename]
            
        return dict_filenames.keys()

    def _map_list_len(self):
        dict_of_filenames = self._get_dict_of_filenames_on_fs()

        for filename in self.val:
            dict_of_filenames[filename] = True
            
        for filename in self.to_remove:
            if filename in dict_filenames:
                del dict_filenames[filename]

        return len(dict_of_filenames)
        
    def _map_list_index_get(self,index_to_get):
        if index_to_get in self.to_remove:
            err_msg = '"' + index_to_get + '" was removed from this map.'
            raise KeyError(err_msg)
        
        if index_to_get in self.val:
            return self.val[index_to_get]

        dict_of_filenames = self._get_dict_of_filenames_on_fs()
        if index_to_get in dict_of_filenames:
            filer = open(
                os.path.join(self.folder_name,index_to_get),'r')
            to_return = filer.read()
            filer.close()
            # cache the value in case it's needed again son
            self.val[index_to_get] = to_return
            return to_return
        
        # did not appear anywhere in map.  raise a key error
        err_msg = 'File system does not have file named "'
        err_msg += index_to_get + '" on it.'
        raise KeyError(err_msg)

    
    def _map_list_copy_return(self):
        list_filenames = self._get_list_of_filenames()
        
        to_return = {}
        for filename in list_filenames:
            filer = open(
                os.path.join(self.folder_name,filename))
            to_return[filename] = filer.read()
            filer.close()
        
        return to_return

    
