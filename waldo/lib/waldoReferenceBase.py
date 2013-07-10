import threading, numbers
import util
from abc import abstractmethod
import waldoNotificationMap
from waldo.lib.proto_compiled.varStoreDeltas_pb2 import VarStoreDeltas
from  waldoObj import WaldoObj


class _ReferenceBase(WaldoObj):
    '''
    Whenever we have a reference, ie a variable, map, list, struct, it
    derives from this.
    '''
    # FIXME: maybe use a separate commit lock instead of
    # re-purposing the no one else can use the commit lock until....

    
    def __init__(
        self,host_uuid,peered,init_val,version_obj,
        dirty_element_constructor):

        self.host_uuid = host_uuid
        self.uuid = util.generate_uuid()
        self.version_obj = version_obj
        self.peered = peered
        
        self.val = init_val
        self.dirty_element_constructor = dirty_element_constructor

        self.notification_map = waldoNotificationMap._NotificationMap(
            self.uuid,self.host_uuid)
        
        # keys are uuids.  values are dirty values of each object.
        self._dirty_map = {}
        self._mutex = threading.Lock()

        
    def _lock(self,blocking=True):
        to_return = self._mutex.acquire(blocking)
        return to_return
    
    def _unlock(self):
        self._mutex.release()

    def is_peered(self):
        return self.peered

    def modified(self,invalidation_listener):
        '''
        Have we changed this variable?
        
        @returns {bool} --- True if have modified the variable.  False
        otherwise.
        '''
        self._lock()
        dirty_elem = self._dirty_map.get(invalidation_listener.uuid,None)
        self._unlock()

        modified = False
        if dirty_elem != None:
            modified = dirty_elem.modified(invalidation_listener)
            
        return modified
        
    @staticmethod
    def var_type():
        '''
        @returns {String} --- Each subtype of _ReferenceBase has a
        unique name.
        '''
        util.logger_assert(
            'var_type is pure virtual in _ReferenceBase.')

    @abstractmethod
    def copy(self,invalid_listener,peered):
        '''
        Returns a deep copy of this object.  Useful when assigning
        to/from a peered variable.  Eg., if have a peered map of
        lists, any list that we assign into the map should be copied
        as peered first.  This way, avoid problem of sharing references.
        '''
        util.logger_assert(
            'copy is pure virtual in _ReferenceBase.')

    @abstractmethod
    def de_waldoify(self,invalid_listener):
        '''
        Returns a Python-ized version of this object accessed by the
        current invalid listener.  Eg., if it was a Waldo number that
        wrapped 2, then it just returns 2.  Lists, maps and strings
        are more complex.
        '''
        util.logger_assert(
            'de_waldoify is pure virtual in _ReferenceBase.')

        
    @abstractmethod
    def is_value_type(self):
        '''
        @returns {bool} --- True if the reference base points at a
        value type (Text, Bool, Number).  False otherwise.
        '''
        util.logger_assert(
            'is_value_type is pure virtual in _ReferenceBase.')

    def serializable_var_tuple_for_network(
        self,parent_delta,var_name,invalid_listener,force):
        '''
        The runtime automatically synchronizes data between both
        endpoints.  When one side has updated a peered variable, the
        other side needs to attempt to apply those changes before
        doing further work.  This method grabs the val and version
        object of the dirty element associated with invalid_listener.
        Using these data, plus var_name, it constructs a named tuple
        for serialization.  (@see
        util._generate_serialization_named_tuple)

        Note: if the val of this object is another Reference object,
        then we recursively keep generating named tuples and embed
        them in the one we return.

        Note: we only serialize peered data.  No other data gets sent
        over the network; therefore, it should not be serialized.

        @param {*Delta or VarStoreDeltas} parent_delta --- Append any
        message that we create here to this message.
        
        @param {String} var_name --- Both sides of the connection need
        to agree on a common name for the variable being serialized.
        This is to ensure that when the data are received by the other
        side we know which variable to put them into.  This value is
        only really necessary for the outermost wrapping of the named
        type tuple, but we pass it through anyways.

        @param {bool} force --- True if regardless of whether modified
        or not we should serialize.  False otherwise.  (We migth want
        to force for instance the first time we send sequence data.)
        
        @returns {bool} --- True if some subelement was modified,
        False otherwise.
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        self._unlock()
        version_obj = dirty_element.version_obj

        # a val can either point to a waldo reference, a python value,
        # or a list/map of waldo references or a list/map of python
        # values.
        var_data = dirty_element.val

        
        if (not force) and (not version_obj.has_been_written_since_last_message):
            if (isinstance(var_data,numbers.Number) or
                util.is_string(var_data) or isinstance(var_data,bool)):
                # nothing to do because this value has not been
                # written.  NOTE: for list/dict types, must actually
                # go through to ensure no subelements were written.
                return False

        sub_element_modified = False
        if self.py_val_serialize(parent_delta,var_data,var_name):
            sub_element_modified = True
        
        elif isinstance(var_data,list):
            list_delta = parent_delta.internal_list_delta
            list_delta.parent_type = VarStoreDeltas.INTERNAL_LIST_CONTAINER

            if force:
                # perform each operation as a write...
                version_obj.add_all_data_to_delta_list(
                    list_delta,var_data,invalid_listener)
                sub_element_modified = True
            else:
                # if all subelements have not been modified, then we
                # do not need to keep track of these changes.
                # wVariable.waldoMap, wVariable.waldoList, or
                # wVariable.WaldoUserStruct will get rid of it later.
                sub_element_modified = version_obj.add_to_delta_list(
                    list_delta,var_data,invalid_listener)


        elif isinstance(var_data,dict):
            map_delta = parent_delta.internal_map_delta
            map_delta.parent_type = VarStoreDeltas.INTERNAL_MAP_CONTAINER

            if force:
                # perform each operation as a write...
                version_obj.add_all_data_to_delta_list(
                    map_delta,var_data,invalid_listener)
                sub_element_modified = True
            else:
                # if all subelements have not been modified, then we
                # do not need to keep track of these changes.
                # wVariable.waldoMap, wVariable.waldoList, or
                # wVariable.WaldoUserStruct will get rid of it later.
                sub_element_modified = version_obj.add_to_delta_list(
                    map_delta,var_data,invalid_listener)

                
        else:
            # creating deltas for cases where internal data are waldo
            # references.... should have been overridden in
            # wVariables.py
            util.logger_assert('Serializing unknown type.')

        version_obj.has_been_written_since_last_message = False
        return sub_element_modified
        
    def py_val_serialize(self,parent,var_data,var_name):
        '''
        @param {} parent --- Either a ContainerAction a VarStoreDeltas.

        FIXME: unclear if actually need var_name for all elements
        py_serialize-ing, or just py variables that are in the
        top-level.

        @returns {bool} --- True if var_data was a python value type
        and we put it into parent.  False otherwise.
        
        If is python value type, then adds a delta message to
        parent.  Otherwise, does nothing.
        '''
        is_value_type = False
        delta = None
        if isinstance(var_data, numbers.Number):
            # can only add a pure number to var store a holder or to
            # an added key
            if parent.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
                delta = parent.num_deltas.add()
            elif parent.parent_type == VarStoreDeltas.CONTAINER_ADDED:
                parent.added_what_num = var_data
            elif parent.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
                parent.what_written_num = var_data
            #### DEBUG
            else:
                util.logger_assert('Unexpected parent type in py_serialize')
            #### END DEBUG
                
            is_value_type = True
            
        elif util.is_string(var_data):
            if parent.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
                delta = parent.text_deltas.add()
            elif parent.parent_type == VarStoreDeltas.CONTAINER_ADDED:
                parent.added_what_text = var_data
            elif parent.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
                parent.what_written_text = var_data
                
            #### DEBUG
            else:
                util.logger_assert('Unexpected parent type in py_serialize')
            #### END DEBUG                
                
            is_value_type = True
            
        elif isinstance(var_data,bool):
            if parent.parent_type == VarStoreDeltas.VAR_STORE_DELTA:
                delta = parent.true_false_deltas.add()
            elif parent.parent_type == VarStoreDeltas.CONTAINER_ADDED:
                parent.added_what_tf = var_data
            elif parent.parent_type == VarStoreDeltas.CONTAINER_WRITTEN:
                parent.what_written_tf = var_data                
            #### DEBUG
            else:
                util.logger_assert('Unexpected parent type in py_serialize')
            #### END DEBUG                

                
            is_value_type = True

        if delta != None:
            # all value types have same format
            delta.var_name = var_name
            delta.var_data = var_data
            
        return is_value_type

        
    def _non_waldo_copy(self):
        '''
        When we are establishing dirty map elements, we make a copy of
        our committed value so that changes do not polute the
        committed val.  (For instance, if val is a python list, we do
        not want an invalidation listener's deletion of elements to be
        visible until the invalidation listener has been committed.)

        However, if val holds an object derived from _ReferenceBase,
        then we just want to return that object itself (because we
        know that it can handle delaying exposing side effects until
        commit).

        self.val can only contain value types or lists of
        values/_ReferenceBases or dicts of values/_ReferenceBases.  
        '''
        copied_val = self.val
        
        if isinstance(self.val,dict):
            copied_val = {}
            for key in self.val.keys():
                copied_val[key] = self.val[key]
        elif isinstance(self.val,list):
            copied_val = []
            for element in self.val:
                copied_val.append(element)

        return copied_val


    def update_version_and_val(
        self,invalid_listener,version_obj,val):
        '''
        @param {_ReferenceVersion} version_obj 
        @param {Anything} val
        
        If we are a peered variable, then when the other side makes a
        change, we want to update the dirty version of our object and
        resume from there.  To do this, just overwrite the dirty
        element's version_obj + val.
        '''

        # FIXME: eventually, want to transmit deltas instead of the
        # full val and version_obj.
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        dirty_element.set_version_obj_and_val(version_obj,val)
        
        self._unlock()

        
    def _add_invalid_listener(self,invalid_listener):
        '''
        ASSUMES ALREADY WITHIN LOCK
        '''
        if invalid_listener.uuid not in self._dirty_map:
            
            # FIXME: may only want to make a copy of val on write
            to_add = self.dirty_element_constructor(
                self.version_obj.copy(),
                self.val,
                invalid_listener,self)

            self._dirty_map[invalid_listener.uuid] = to_add
            invalid_listener.add_touch(self)

            
    def get_val(self,invalid_listener):
        '''
        Requests a copy of the internal

        If invalid_listener is None, then that means that we actually
        want the last committed val directly.  (Shouldn't be used
        frequently, mostly just for initialization, when otherwise do
        not have an active value.)
        '''
        if invalid_listener == None:
            self._lock()
            internal_val = self.val
            self._unlock()
            return internal_val
        
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_val = self._dirty_map[invalid_listener.uuid].val
        self._unlock()
        return dirty_val

    def write_if_different(self,invalid_listener,new_val):
        self._lock()
        self._add_invalid_listener(invalid_listener)
        dirty_element = self._dirty_map[invalid_listener.uuid]
        if dirty_element.val != new_val:
            self._dirty_map[invalid_listener.uuid].set_has_been_written_to(new_val)
            if self.peered:
                invalid_listener.add_peered_modified()
        self._unlock()

    def write_val(self,invalid_listener,new_val,copy_if_peered=True):
        '''
        Writes to a copy of internal val, dirtying it
        '''
        self._lock()
        self._add_invalid_listener(invalid_listener)
        self._dirty_map[invalid_listener.uuid].set_has_been_written_to(new_val)
        if self.peered:
            invalid_listener.add_peered_modified()

        self._unlock()


    def check_commit_hold_lock(self,invalid_listener,blocking=True):
        '''
        @returns{bool or None} --- Returns True if the commit
        associated with invalid_listener can go through (ie, no one
        else has committed to this waldo object since we read/wrote
        our dirty values.  False if acquired lock and got a read/write
        conflict.  None if could not acquire lock.

        Note: if takes lock on object, but does not release it.  Lock
        gets unreleased either within commit or release.
        '''
        self.notification_map.add_invalidation_listener(invalid_listener)

        acquired_lock = self._lock(blocking)
        
        if not acquired_lock:
            # FIXME: may be able to do an opportunistic conflicts
            # check here.
            return None

        return not self.version_obj.conflicts(
            self._dirty_map[invalid_listener.uuid].version_obj)


    
    def backout(self,invalid_listener):
        '''
        @param {_InvalidListener} invalid_listener ---
        '''
        self.notification_map.remove_invalidation_listener(invalid_listener)
        del self._dirty_map[invalid_listener.uuid]
        self._unlock()

    
    def complete_commit(self,invalid_listener):
        '''
        @param {_InvalidListener} invalid_listener --- The event that
        is committing the change.
        
        Assumes already inside of lock.  (Was presumably acquired in
        check_commit_hold_lock.)

        Called when committing an invalid_listener's event.  

        If the invalid listener has only read the value (ie, the dirty
        map element associated with invalid_listener's uuid has a
        has_been_written_to of false), then make no change.

        If the invalid listener has modified val, then change val and
        increment the version number of the variable.  Additionally,
        run through all invalidation elements notifying them that
        their version numbers may be out of sync.

        In either case, remove the dirty map element associated with
        invalid_listener and release the lock.
        '''
        self.notification_map.remove_invalidation_listener(invalid_listener)
        dirty_map_elem  = self._dirty_map[invalid_listener.uuid]
        del self._dirty_map[invalid_listener.uuid]

        # will update version obj as well
        dirty_map_elem.update_obj_val_and_version(self)

        # determine who we need to send invalidation messages to
        to_invalidate_list = []
        for potentially_invalidate in list(self._dirty_map.values()):
            if potentially_invalidate.version_obj.conflicts(
                self.version_obj):
                to_invalidate_list.append(potentially_invalidate)


        # FIXME: May eventually want to send what the conflict was so
        # can determine how much the invalidation listener actually
        # needs to backout.
        if len(to_invalidate_list) != 0:
            dirty_notify_thread = _DirtyNotifyThread(
                self,to_invalidate_list)
            dirty_notify_thread.start()

        self._unlock()


class _DirtyNotifyThread(threading.Thread):
    '''
    When we commit a change to a Waldo object, notify all
    invalidation_listeners (essentially, events) of the change so that
    they can restart themselves accordingly.
    '''
    
    def __init__(self,wld_obj,to_notify_list):
        '''
        @param {_WaldoObj} wld_obj --- Who is notifying you that you
        are out of date.
        
        @param {List<DirtyMapElements>} to_notify_list --- Notify
        each of these invalid iterators that they are operating on an
        out-of-date value of the Waldo object, wld_obj.
        '''
        self.wld_obj = wld_obj
        self.to_notify_list = to_notify_list
        threading.Thread.__init__(self)
        self.daemon = True
        
    def run(self):
        for dirty_map_elem in self.to_notify_list:
            inv_listener = dirty_map_elem.invalidation_listener
            inv_listener.notify_invalidated(self.wld_obj)


            
class _DirtyMapElement(object):
    '''
    Each _WaldoObj holds a dirty map.  Its elements are of type
    _DirtyMapElement.  
    '''
    
    def __init__(self,version_obj,val,invalidation_listener,waldo_reference):
        '''
        @param {_WaldoObjVersion} version_obj --- The version of the
        Waldo object that the dirty map element

        @param {Anything} val --- The dirty val that the invalidation
        listener is using.

        @param {_InvalidationListener} invalidation_listener ---

        @param {Any subtype of _ReferenceBase} waldo_reference
        '''
        self.version_obj = version_obj
        self.val = val
        self.invalidation_listener = invalidation_listener

        self.waldo_reference = waldo_reference
        
        
    def set_version_obj_and_val(self,version_obj,val):
        '''
        @see update_version_and_val in _ReferenceBase.
        '''
        self.version_obj = version_obj
        self.val = val

    def set_has_been_written_to(self,new_val):
        self.version_obj.set_has_been_written_to()
        self.val = new_val

    def update_obj_val_and_version(self,w_obj):
        '''
        @param {_WaldoObject} w_obj --- Take our version object and
        determine if we need to update w_obj's val and version.  This
        already assumes that DirtyMapElement has already had no commit
        conflict and is in the process of committing.  Similarly, we
        are already inside of w_obj's internal lock.
        '''
        self.version_obj.update_obj_val_and_version(w_obj,self.val)

    def modified(self,invalidation_listener):
        '''
        @returns {bool} true if has been modified; false otherwise
        '''
        # in the case of lists of lists, maps of lists, maps of maps,
        # etc., it is not enough to check that the current version
        # object has not been modified.  This is because a version
        # object only keeps track of one level of the tree of
        # lists/maps.  If data below this level have been modified,
        # then must check with lower levels.  Eg, a = Map(from:
        # number; to: Map(from: number; to:number)); a = {1: {2:
        # 3}}. <commit> a[1][2] = 4.  After the commit, a's version
        # object shows no modification.  That is why we must check a's
        # submaps for modification.
        
        if self.version_obj.modified(invalidation_listener):
            return True

        # check if sub-object was modified
        if isinstance(self.val,WaldoObj):
            if self.val.modified(invalidation_listener):
                return True

        elif ((isinstance(self.val,list) or isinstance(self.val,dict)) and
              (len(self.val) != 0)):

            keys = range(0,len(self.val))
            if isinstance(self.val,dict):
                keys = list(self.val.keys())

            # iterate through all subobjects in list/map to see if
            # they were modified.
            for key in keys:
                item = self.val[key]

                if isinstance(self.val,WaldoObj):
                    if item.modified(invalidation_listener):
                        return True
                else:
                    # means that subobjects are not waldo references.
                    # if we aren't modified, they aren't.
                    return False
                
        return False


class _ReferenceVersion(object):
    '''
    To keep track of whether an object is dirty, each WaldoObj holds a
    _WaldoOjbVersion object.  Using its methods, can automatically
    determine if an update from a dirtyElement will apply cleanly, or
    need to be backed out.
    '''
    
    @abstractmethod
    def copy(self):
        '''
        Whenever we create a dirty element, we create a new
        WaldoObjVersion.  This is used to check whether there might be
        any conflicts when trying to commit an event, using the
        conflicts method.
        '''
        pass

    @abstractmethod
    def update(self,dirty_version_obj):
        '''
        @param{_WaldoObjVersion} dirty_version_obj --- Commit the
        version held by dirty_version_obj to self.  (Assumes already
        has called conflicts to determine that there was no conflict
        from applying the new version.)
        '''
        pass

    @abstractmethod
    def conflicts(self,dirty_version_obj):
        '''
        @param{_WaldoObjVersion} dirty_version_obj
        
        @returns {bool} --- True if the there would be a read-write
        conflict from attempting to commit the event with
        dirty_version_obj on top of this version obj.
        '''
        pass

    @abstractmethod
    def update_obj_val_and_version(self,w_obj,val):
        '''
        @param {_WaldoObject} w_obj --- Take our version object and
        determine if we need to update w_obj's val and version.  This
        already assumes that DirtyMapElement has already had no commit
        conflict and is in the process of committing.  Similarly, we
        are already inside of w_obj's internal lock.

        @param {Anything} val --- What the dirtyelementobject thinks
        the current value of the object should be.
        '''
        pass

    @abstractmethod
    def modified(self,invalidation_listener):
        '''
        Returns True if the object has been modified, False otherwise.
        '''
        util.logger_assert(
            'modified is pure virtual in _ReferenceVersion class.')
        
