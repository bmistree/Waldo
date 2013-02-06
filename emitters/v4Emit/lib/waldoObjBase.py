import threading
import util
import pickle

        
class _WaldoObj(object):
    '''
    All Waldo objects (numbers, texts, etc.) are subtypes of this
    basic object.
    '''
    
    # gets populated in initialize method of wObjects.py
    WALDO_TYPE_NAMES = {}

    # FIXME: maybe create a separate commit lock instead of
    # re-purposing the no one else can use the commit lock until....

    
    def __init__(self,_type,init_val):
        self.uuid = util.generate_uuid()
        self.type = _type
        self.version_num = 0

        self.val = init_val
        
        # keys are integers.  values are dirty values of each object.
        self._dirty_map = {}
        self._mutex = threading.Lock()

    def _lock(self):
        self._mutex.acquire()
    def _unlock(self):
        self._mutex.release()

    def _deep_copy(self):
        '''
        Deep copy val and return it
        '''
        # FIXME: using this approach, one object cannot hold a
        # reference to another object, eg., structs with maps, etc.
        return pickle.loads(pickle.dumps(self.val))
        
        
    def get_val(self,invalid_listener):
        '''
        Requests a copy of the internal 
        '''
        self._lock()
        
        if invalid_listener.uuid not in self._dirty_map:
            # FIXME: may only want to make a copy of val on write
            to_add = _DirtyMapElement(
                self.version_num,
                self._deep_copy(),
                invalid_listener)
            self._dirty_map[invalid_listener.uuid] = to_add
            invalid_listener.add_touch(self)
            
        dirty_val = self._dirty_map[invalid_listener.uuid].val
        self._unlock()
        
        return dirty_val


    def write_val(self,invalid_listener,new_val):
        '''
        Writes to a copy of internal val, dirtying it
        '''
        self._lock()
        if invalid_listener.uuid not in self._dirty_map:
            to_add = _DirtyMapElement(
                self.version_num,
                new_val,
                invalid_listener,
                True # because we know that we've written to the value
                )
            self._dirty_map[invalid_listener.uuid] = to_add
            invalid_listener.add_touch(self)
            
        self._dirty_map[invalid_listener.uuid].set_has_been_written_to(new_val)
        self._unlock()
        

    def check_commit_hold_lock(self,invalid_listener):
        '''
        @returns{bool} --- Returns True if the commit associated with
        invalid_listener can go through (ie, no one else has committed
        to this waldo object since we read/wrote our dirty values.
        False otherwise.

        Note: takes lock on object, but does not release it.  Lock
        gets unreleased either within commit or release.
        '''
        self._lock()

        #### DEBUG
        if invalid_listener.uuid not in self._dirty_map:
            util.logger_assert('Aborted in check_commit_hold_lock.  ' +
                               'Have no listener in dirty map with ' +
                               'appropriate id.')
        #### END DEBUG

        dirty_vnum = self._dirty_map[invalid_listener.uuid].version_num
        return dirty_vnum == self.version_num


    
    def backout(self,invalid_listener,release_lock_after):
        '''
        @param {_InvalidListener} invalid_listener ---

        @param {bool} release_lock_after --- If true, then it means
        that the invalid_listener that called in was holding a commit
        lock on the object.  We should release that commit lock
        afterwards.
        '''
        if not release_lock_after:
            self._lock()
        
        #### DEBUG
        if invalid_listener.uuid not in self._dirty_map:
            util.logger_assert('Aborted in backout.  ' +
                               'Have no listener in dirty map with ' +
                               'appropriate id.')
        #### END DEBUG
            
        del self._dirty_map[invalid_listener.uuid]

        self._unlock()
            
    
    def complete_commit(self,invalid_listener):
        '''
        @param {_InvalidListener} invalid_listener --- The event that
        is committing the change.
        
        Assumes already inside of lock.  (Was presumably acquired in
        check_commit_hold_lock.

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
        #### DEBUG
        if invalid_listener.uuid not in self._dirty_map:
            util.logger_assert('Aborted in commit.  ' +
                               'Have no listener in dirty map with ' +
                               'appropriate id.')
        #### END DEBUG


        dirty_map_elem  = self._dirty_map[invalid_listener.uuid]
        del self._dirty_map[invalid_listener.uuid]

        if dirty_map_elem.has_been_written_to:
            self.version_num += 1
            self.val = dirty_map_elem.val
            self._notify_all_dirty_invalid()

        self._unlock()

        
    def is_valid_type(self):
        return self.type in _WaldoObj.WALDO_TYPE_NAMES
        

    def _notify_all_dirty_invalid(self):
        '''
        Assumes already inside of lock
        '''
        to_notify_list = list(self._dirty_map.values())
        if len(to_notify_list) != 0:
            dirty_notify_thread = _DirtyNotifyThread(self,to_notify_list)
            dirty_notify_thread.start()
        
        
    
    def serialized(self):
        #### DEBUG
        if not self.is_valid_type(self.type):
            util.logger_assert('Invalid type name of object.')
        #### END DEBUG

            
        return pickle.dumps(self)


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
    
    def __init__(self,version_num,val,invalidation_listener,has_written=False):
        '''
        @param {int} version_num --- The version of the Waldo object
        that the dirty map element

        @param {Anything} val --- The dirty val that the invalidation
        listener is using.

        @param {_InvalidationListener} invalidation_listener --- 
        '''
        self.version_num = version_num
        self.val = val
        self.invalidation_listener = invalidation_listener

        # if true, means that the invalidation listener, at some
        # point, wrote to this value instead of just read it.
        self.has_been_written_to = has_written

    def set_has_been_written_to(self,new_val):
        self.has_been_written_to = True
        self.val = new_val
        

