import waldoReferenceBase
import util
from abc import abstractmethod
import itertools, numbers

from lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas

class _ReferenceContainer(waldoReferenceBase._ReferenceBase):
    '''
    All Waldo objects inherit from _WaldoObj.  However, non-value
    Waldo objects (maps, lists, user structs), should all inherit from
    _WaldoContainer.  This is because a WaldoContainer holds pointers
    to additional _WaldoObjs, and therefore needs to dirty those as
    well and update those simultaneously when updating _WaldoContainer.
    '''
    def __init__(
        self,host_uuid,peered,init_val,version_obj,
        dirty_element_constructor):
        
        waldoReferenceBase._ReferenceBase.__init__(
            self,host_uuid,peered,init_val,version_obj,
            dirty_element_constructor)

    def get_val(self,invalid_listener):
        util.logger_assert(
            'In WaldoValueContainer, get_val disallowed.')

    def write_val(self,invalid_listener,new_val):
        util.logger_assert(
            'In WaldoValueContainer, write_val disallowed.')

    def add_key(self,invalid_listener,key_added,new_val):
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        dirty_elem.add_key(key_added,new_val,invalid_listener,self.peered)
        if self.peered:
            invalid_listener.add_peered_modified()
        self._unlock()


    def incorporate_deltas(self,delta_to_incorporate,active_event):
        util.logger_assert(
            'Error: incorporate_deltas in waldoReferenceContainerBase ' +
            'is pure virtual')


    def del_key_called(self,invalid_listener,key_deleted):
        self._lock()
        self._add_invalid_listener(invalid_listener)
        
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        dirty_elem.del_key(key_deleted)
        if self.peered:
            invalid_listener.add_peered_modified()
        self._unlock()

    @abstractmethod
    def copy_if_peered(self):
        '''
        Peered data only get copied in and out via value instead of by
        reference.  This is to ensure that one endpoint cannot
        directly operate on another endpoint's references.  This
        method returns a copy of self if self is not peered.
        Otherwise, it returns a deep copy of itself.

        We only need a copy_if_peered method for ReferenceContainers
        because non-ReferenceContainers will automatically return
        copied values (Numbers, Texts, TrueFalses) when we get their
        values.
        '''
        pass

    def update_val_of_key_during_deserialize(
        self,invalid_listener,key,val):
        '''
        @param {Text,Number,TrueFalse} key --- The index of the
        internal map or list (if list, then key is just a number)

        @param {Anything} val --- Can be a python value or pointers to
        additional Waldo variables.

        Called when deserializing nested maps/lists.  See case 4 in
        the comments for the method
        waldoNetworkSerializer.deserialize_peered_object_into_variables.
        '''
        #### DEBUG
        # note only should be serializing and deserializing peered data
        if not self.peered:
            util.logger_assert(
                'Should not be updating value and version for a ' +
                'non-peered data item.')
        #### END DEBUG
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        dirty_element.val[key] = val
        self._unlock()

    def update_version_obj_during_deserialize(
        self,invalid_listener,new_version_obj):
        '''
        @see update_val_of_key_during_deserialize
        '''
        #### DEBUG        
        # note only should be serializing and deserializing peered data
        if not self.peered:
            util.logger_assert(
                'Should not be updating value and version for a ' +
                'non-peered data item.')
        #### END DEBUG
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        dirty_element.version_obj = new_version_obj
        self._unlock()


    def get_len(self,invalid_listener):
        self._lock()
        self._add_invalid_listener(invalid_listener)
        
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        cur_len = dirty_elem.get_len()
        self._unlock()
        return cur_len

    def get_keys(self,invalid_listener):
        '''
        When requests a list of all keys
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        keys = dirty_elem.get_keys()
        self._unlock()
        return keys


    def contains_key_called(self,invalid_listener,contains_key):
        self._lock()
        self._add_invalid_listener(invalid_listener)

        dirty_elem = self._dirty_map[invalid_listener.uuid]
        contains_val = dirty_elem.contains_key(contains_key)
        self._unlock()
        return contains_val

    def get_val_on_key(self,invalid_listener,key):
        self._lock()
        self._add_invalid_listener(invalid_listener)
        
        dirty_elem = self._dirty_map[invalid_listener.uuid]
        dirty_val = dirty_elem.get_val_on_key(key)
        self._unlock()
        return dirty_val
        
    
    def write_val_on_key(self,invalid_listener,key,new_val,copy_if_peered=True):
        self._lock()
        self._add_invalid_listener(invalid_listener)
        
        dirty_elem = self._dirty_map[invalid_listener.uuid]

        if self.peered and copy_if_peered:
            # copy the data that's being written in: peereds do not
            # hold references.  If they did, could be trying to
            # synchronize references across multiple hosts.  Eg., if
            # have a peered map of lists, then when insert a list,
            # want to insert copy of list.  If did not, then might be
            # able to share the reference to the inner list between
            # many machines.
            if isinstance(new_val,waldoReferenceBase._ReferenceBase):
                new_val = new_val.copy(invalid_listener,True)
            
        dirty_elem.write_val_on_key(key,new_val)
        if self.peered:
            invalid_listener.add_peered_modified()        
        self._unlock()

    
    def _add_invalid_listener(self,invalid_listener):
        '''
        ASSUMES ALREADY WITHIN LOCK
        '''
        if invalid_listener.uuid not in self._dirty_map:
            
            # FIXME: may only want to make a copy of val on write
            to_add = self.dirty_element_constructor(
                self.version_obj.copy(),
                # self.val,
                # this copy has a huge performance affect!
                self._non_waldo_copy(),
                invalid_listener)

            self._dirty_map[invalid_listener.uuid] = to_add
            invalid_listener.add_touch(self)
        

class _ReferenceContainerDirtyMapElement(waldoReferenceBase._DirtyMapElement):

    def __init__(self,*args):
        '''
        For args, @see waldoObjBase._DirtyMapElement.
        '''
        waldoReferenceBase._DirtyMapElement.__init__(self,*args)

        
    def get_val_on_key(self,key):
        self.version_obj.get_val_on_key(key)
        return self.val[key]
    
    def is_value_type(self):
        return False

    # when go to non-value containers, then will probably need to add
    # touches when write value on key.
    def write_val_on_key(self,key,new_val):
        self.version_obj.write_val_on_key(key)
        self.val[key] = new_val
        self.has_been_written_since_last_message = True

        
    def add_key(self,key,new_val,invalid_listener,peered):
        self.version_obj.add_key(key)
        # if we are peered, then we want to assign into ourselves a
        # copy of the object, not the object itself.  This will only
        # be a problem for container types.  Non-container types
        # already have the semantics that they will be copied on read.
        # (And we throw an error if a peered variable has a container
        # with externals inside of it.)
        self.has_been_written_since_last_message = True
        
        if peered:
            if isinstance(
                new_val,_ReferenceContainer):
                new_val = new_val.copy(invalid_listener,True)

            elif isinstance(
                new_val,waldoReferenceBase._ReferenceBase):

                if new_val.is_value_type():
                    new_val = new_val.get_val(invalid_listener)
                else:
                    new_val = new_val.copy(invalid_listener,True)

                
                # # need to check again in case it's a
                # # WaldoVariableList/Map that we are adding.
                # if isinstance(
                #     new_val,waldoReferenceContainerBase._ReferenceContainer):
                #     new_val = new_val.copy(invalid_listener,peered)

        self.val[key] = new_val



    def clear_partner_change_log(self):
        self.version_obj.clear_partner_change_log()
        
    def del_key(self,key):
        self.has_been_written_since_last_message = True
        self.version_obj.del_key(key)        
        del self.val[key]

    def get_len(self):
        self.version_obj.get_len()
        return len(self.val)

    def get_keys(self):
        '''
        When requests a list of all keys
        '''
        self.version_obj.get_keys()
        return self.val.keys()

    def contains_key(self,key):
        self.version_obj.contains_key(key)        
        return key in self.val 
        
    def set_has_been_written_to(self,new_val):
        util.logger_assert('In _DirtyMapContainerElement, should never get ' +
                           'a call to set_has_been_written_to.')


class _ReferenceContainerVersion(waldoReferenceBase._ReferenceVersion):

    def __init__(self):
        '''
        Keeping track of separate version numbers for each operation.
        We need to know the last version number each 
        '''

        self.commit_num = 0

        # none if have not called len.  otherwise an integer from the
        # commit num that len was last called.
        self.len_called = None
        self.keys_called = None

        # maps from string to int.  each int corresponds to the
        # version number at which the key was added.        
        self.contains_keys = {}
        self.read_values_keys = {}
        self.written_values_keys = {}
        self.added_keys ={}
        self.deleted_keys = {}

        # keeps track of what has not yet been sent over the network
        # to partner.  Each element should be a 2-tuple.  The first
        # element of the 2-tuple should be the relevant operation
        # type: WRITE, ADD, DELETE.  The second element should be the
        # key identifier.  See helper functions at bottom of file for
        # tuples.
        self.partner_change_log = []
        
    def clear_partner_change_log(self):
        self.partner_change_log = []
        
    def modified(self,invalidation_listener):
        '''
        @returns {bool} true if has been modified; false otherwise
        '''
        if ((len(self.written_values_keys) != 0) or
            (len(self.added_keys) != 0) or (len(self.deleted_keys) != 0)):
            return True
        
        return False

        
    def update_obj_val_and_version(self,w_obj,val):
        '''
        @param {_WaldoObject} w_obj --- We know that w_obj must be one
        of the value type objects at this point.  That means that if
        we have written to our value, we increment w_obj's version
        number and overwrite its value.  Otherwise, do nothing

        @param {val}
        '''
        fields_to_update = w_obj.version_obj.update(self)
        # FIXME: probably do not want to overwrite the entire val each
        # time.  could just apply deltas instead.
        if isinstance(val,dict):
            for field_to_update in fields_to_update.keys():
                if field_to_update not in val:
                    # to handle deletions for maps
                    if field_to_update in w_obj.val:
                        # if just performed a contains call on a
                        # missing entry, then we might have
                        # field_to_update not be in w_obj.val.  In
                        # that case, we cannot delete it.
                        del w_obj.val[field_to_update]
                else:
                    w_obj.val[field_to_update] = val[field_to_update]

                    
        elif isinstance(val,list):
            if len(w_obj.val) > len(val):
                del w_obj.val[len(val):]

            for field_to_update in fields_to_update.keys():

                if field_to_update >= len(val):
                    # skip this because it means we deleted something
                    # off of val that no longer exists.  it's okay to
                    # ignore deleting it here because of the above
                    # if/elif checks that ensure both lists are the
                    # same size.
                    continue

                if field_to_update >= len(w_obj.val):
                    num_elements_to_append = field_to_update + 1 - len(w_obj.val)
                    # note: using this approach, may have val fields
                    # that are None.  This will only happen for
                    # sequence peered data that are not accessed, so
                    # this is fine.
                    to_append = [None]*num_elements_to_append
                    w_obj.val += to_append
                
                w_obj.val[field_to_update] = val[field_to_update]


    def copy(self):
        '''
        When copy, do not need to copy key maps themselves.  We only
        need this information once: when trying to determine
        conflicts.  We always run the method conflicts against the
        "official" version object, the one that keeps track of the
        current state of the committed value.  The official object has
        access to all the keys and maps and therefore we do not need
        to put them into our copies.  However, we do need to copy over
        their vnums so that we know what they're making modifications
        on top of.
        '''
        copy = _ReferenceContainerVersion()
        copy.commit_num = self.commit_num
        return copy
        

    def conflicts(self,dirty_cv_ver_obj):
        '''
        Called on official object
        
        conflict iff
          1) len called and either added or deleted keys
          2) contains key called and added key called contain on
          3) contains key called and deleted key called contain on
          4) read key called and wrote to same key read from
          5) read key called and deleted key read from
          6) read key called and added key read from
        Note: when inserting a key into the middle of a list, will
        add a single key, and mark all keys between insertion and
        that key as having been written to (inclusive)
          7) written key called and added key written to
          8) written key called and deleted key written to
          9) written key called and read a key in the meantime
          10) keys called and added or deleted any keys

          11) add called and either called keys or len
          12) add called and called contains on the same key
          13) add called on same key as read or wrote
          
          14) delete called and either called keys or len
          15) delete called and called contains on the same key
          16) delete called on same key as read or wrote

        @returns{bool} --- True if there was a conflict from
        attempting to apply dirty_cv_ver_obj on top of this.  False
        otherwise.
        '''
        # testing 1 from comments above
        if dirty_cv_ver_obj.len_called != None:
            for size_chng_time in itertools.chain(self.added_keys.values(),
                                                  self.deleted_keys.values()):
                # we copied the original into dirty_cv_ver_obj then we
                # called len on that.  Before we committed it though,
                # we committed some other change that included adding
                # and/or deleting keys.                
                if size_chng_time >= dirty_cv_ver_obj.len_called:
                    return True


                
        # testing 2 + 3 from comments above
        for contains_key in dirty_cv_ver_obj.contains_keys.keys():
            contains_time = dirty_cv_ver_obj.contains_keys[contains_key]

            # testing 2: was a key with the same name added in a
            # concurrent event that committed first and therefore
            # would cause a conflict with our contains?
            if ((contains_key in self.added_keys) and
                self.added_keys[contains_key] >= contains_time):
                return True
            
            # testing 3: was a key with the same name removed in a
            # concurrent event that committed first and therefore
            # would cause a conflict with our contains?            
            if ((contains_key in self.deleted_keys) and
                self.deleted_keys[contains_key] >= contains_time):
                return True

        # testing 4 + 5 + 6 from comments above
        for read_key in dirty_cv_ver_obj.read_values_keys.keys():
            read_time = dirty_cv_ver_obj.read_values_keys[read_key]

            # testing 4
            if ((read_key in self.written_values_keys) and
                (self.written_values_keys[read_key] >= read_time)):
                return True

            # testing 5
            if ((read_key in self.deleted_keys) and
                (self.deleted_keys[read_key] >= read_time)):
                return True

            # testing 6
            if ((read_key in self.added_keys) and
                (self.added_keys[read_key] >= read_time)):
                return True

        
        # testing 7 + 8 + 9 from comments above
        for written_key in dirty_cv_ver_obj.written_values_keys.keys():
            write_time = dirty_cv_ver_obj.written_values_keys[written_key]
            
            # testing 7
            if ((written_key in self.added_keys) and
                (self.added_keys[written_key] >= write_time)):
                return True
            
            # testing 8
            if ((written_key in self.deleted_keys) and
                (self.deleted_keys[written_key] >= write_time)):
                return True
            
            # testing 9
            if ((written_key in self.read_values_keys) and
                (self.read_values_keys[written_key] >= write_time)):
                return True

            
        # testing 10 from comments above
        if dirty_cv_ver_obj.keys_called != None:
            for size_chng_time in itertools.chain(self.added_keys.values(),
                                                  self.deleted_keys.values()):
                # we copied the original into dirty_cv_ver_obj then we
                # called len on that.  Before we committed it though,
                # we committed some other change that included adding
                # and/or deleting keys.                
                if size_chng_time >= dirty_cv_ver_obj.keys_called:
                    return True

        # testing 11 + 12 + 13 from comments above
        for add_key in dirty_cv_ver_obj.added_keys.keys():
            add_time = dirty_cv_ver_obj.added_keys[add_key]

            # testing 11 len
            if ((self.len_called != None) and
                (self.len_called >= add_time)):
                return True
            
            # testing 11 keys
            if ((self.keys_called != None) and
                (self.keys_called >= add_time)):
                return True

            # testing 12
            if ((add_key in self.contains_keys) and
                (self.contains_keys[add_key] >= add_time)):
                return True

            # testing 13 read
            if ((add_key in self.read_values_keys) and
                (self.read_values_keys[add_key] >= add_time)):
                return True
            
            # testing 13 write
            if ((add_key in self.written_values_keys) and
                (self.written_values_keys[add_key] >= add_time)):
                return True            
            
        # testing 14+15+16 from comments above
        for del_key in dirty_cv_ver_obj.deleted_keys.keys():
            del_time = dirty_cv_ver_obj.deleted_keys[del_key]

            # testing 11 len
            if ((self.len_called != None) and
                (self.len_called >= del_time)):
                return True
            
            # testing 11 keys
            if ((self.keys_called != None) and
                (self.keys_called >= del_time)):
                return True

            # testing 12
            if ((del_key in self.contains_keys) and
                (self.contains_keys[del_key] >= del_time)):
                return True

            # testing 13 read
            if ((del_key in self.read_values_keys) and
                (self.read_values_keys[del_key] >= del_time)):
                return True
            
            # testing 13 write
            if ((del_key in self.written_values_keys) and
                (self.written_values_keys[del_key] >= del_time)):
                return True            
                
        return False
                        
    @staticmethod                    
    def _test_and_overwrite(original_map,dirty_map,require_update_map):
        '''
        @param{map} original_map, dirty_map --- Each is structured
        with the same keys and integer values.  They represent the
        official and committing _ContainerValueTypeVersion object's
        contains_keys, read_values_keys, written_values_keys,
        added_keys, and deleted_keys maps, respectively.

        We want to update the values in the official map
        (original_map) with those that we are committing.
        '''

        # FIXME: Essentially want require_update_map to be a set
        # instead of a map.
        
        for key in dirty_map.keys():
            new_commit_time = dirty_map[key]
            if ((key in original_map) and
                (original_map[key]  > new_commit_time)):
                new_commit_time = original_map[key]
            else:
                require_update_map[key] = True
                
            original_map[key] = new_commit_time

            
    def update(self,dirty_version_obj):
        '''
        Called on official version object.  Already guaranteed that
        there are no conflicts.

        @returns {map} --- Indices are keys that need to be copied on
        update.  Values don't matter.
        '''
        
        updated_fields = {}
        _ReferenceContainerVersion._test_and_overwrite(
            self.contains_keys,dirty_version_obj.contains_keys,
            updated_fields)

        # Should not need to copy values that we only read from:
        # should already have copies of those.
        # _ReferenceContainerVersion._test_and_overwrite(
        # self.read_values_keys,dirty_version_obj.read_values_keys,
        # updated_fields)
        _ReferenceContainerVersion._test_and_overwrite(
            self.written_values_keys,dirty_version_obj.written_values_keys,
            updated_fields)
        _ReferenceContainerVersion._test_and_overwrite(
            self.added_keys,dirty_version_obj.added_keys,
            updated_fields)
        _ReferenceContainerVersion._test_and_overwrite(
            self.deleted_keys,dirty_version_obj.deleted_keys,
            updated_fields)

        if len(updated_fields) != 0:
            # if all we did were reads, then can use same commit
            # number.  this is because the object has not actually
            # changed due to performing this commit.
            self.commit_num += 1

        # FIXME: check through the logic on keys + len.  I'm not
        # entirely satisfied that they are correct.
            
        # if dirty_version_obj.len_called != None:
        #     if ((self.len_called == None) or
        #         (dirty_version_obj.len_called > self.len_called)):
        #         self.len_called = dirty_version_obj.len_called

        # if dirty_version_obj.keys_called != None:
        #     if ((self.keys_called == None) or
        #         (dirty_version_obj.keys_called > self.keys_called)):
        #         self.keys_called = dirty_version_obj.keys_called
        
        return updated_fields

    # FIXME: will infinitely grow key monitoring maps using this
    # approach.  probably want some way to reclaim those that are
    # unused by other active events.

    def get_val_on_key(self,key):
        self.read_values_keys[key] = self.commit_num    

    # when go to non-value containers, then will probably need to add
    # touches when write value on key.
    def write_val_on_key(self,key):
        self.written_values_keys[key] = self.commit_num

        # FIXME: should only append to change log if peered.
        self.partner_change_log.append(write_key_tuple(key))

        
    def add_key(self,key_added):
        self.added_keys[key_added] = self.commit_num

        # FIXME: should only append to change log if peered.
        self.partner_change_log.append(add_key_tuple(key_added))

    def add_to_delta_list(self,delta_to_add_to,current_internal_val,action_event):
        '''
        @param delta_to_add_to --- Either
        varStoreDeltas.SingleMapDelta or
        varStoreDeltas.SingleListDelta

        We log all operations on this variable 
        '''
        util.logger_assert(
            'Pure virutal add_to_delta_list in waldoReferenceContainerBase')

    def add_all_data_to_delta_list(
        self,delta_to_add_to,current_internal_val,action_event):
        util.logger_assert(
            'Pure virutal add_all_data_to_delta_list in waldoReferenceContainerBase')
        
    def del_key(self,key_deleted):
        self.deleted_keys[key_deleted] = self.commit_num

        # FIXME: should only append to change log if peered.
        self.partner_change_log.append(delete_key_tuple(key_deleted))

        
    def get_len(self):
        self.len_called = self.commit_num

    def get_keys(self):
        '''
        When requests a list of all keys
        '''
        self.keys_called = self.commit_num

    def contains_key(self,contains_key):
        self.contains_keys[contains_key] = self.commit_num
        
    def set_has_been_written_to(self,new_val):
        util.logger_assert('In _DirtyMapContainerElement, should never get ' +
                           'a call to set_has_been_written_to.')


    @staticmethod
    def deserialize_version_obj_from_network_data(
        version_network_data):

        rcv = _ReferenceContainerVersion()
        rcv.commit_num = version_network_data[1]
        rcv.len_called = version_network_data[2]

        rcv.keys_called = version_network_data[3]
        rcv.contains_keys  = version_network_data[4]
        rcv.read_values_keys  = version_network_data[5]
        rcv.written_values_keys  = version_network_data[6]
        rcv.added_keys  = version_network_data[7]
        rcv.deleted_keys  = version_network_data[8]
        
        return rcv

        

    def serializable_for_network_data(self):
        return (
            self.REFERENCE_CONTAINER_VERSION,
            self.commit_num,
            self.len_called,
            self.keys_called,

            self.contains_keys,
            self.read_values_keys,
            self.written_values_keys,
            self.added_keys,
            self.deleted_keys)


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
