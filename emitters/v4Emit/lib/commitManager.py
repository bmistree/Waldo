import threading

class _CommitManager(object):
    '''
    Challenge is to avoid deadlock when acquiring the locks of all
    objects that we have touched.  To do so, all requests for locks on
    Waldo objects go through a single manager.
    '''
    def __init__(self):
        self._mutex = threading.Lock()

    def _lock(self):
        self._mutex.acquire()
    def _unlock(self):
        self._mutex.release()

    def hold_can_commit(self,invalid_listener):
        '''
        @returns{bool} --- True if can commit to all of the objects
        invalid listener touched

        @param{_InvalidListener} invalid_listener --- Runs through all
        state that the invalid listener touched.  Take locks the
        commit manager (this way, the commit manager can ensure that
        you don't get deadlock between two sides that are trying to
        acquire the locks for two sets of objects simultaneously).
        Then take locks on all the individual objects that we want to
        commit to.
        '''

        # FIXME: this implementation has a lot of undesirable
        # properties.  Most notably, if two invalid listeners try to
        # commit to the same object simultaneously, then one holds the
        # lock on that object.  When the other tries to acquire a lock
        # on the same object, it waits for the first event's lock to
        # be released.  However, while it is waiting, it holds the
        # commit manager's lock and no other invalid_listener can use
        # the commit manager.

        
        self._lock()
        can_commit = True
        for touched_obj in invalid_listener.objs_touched.values():
            # touched_obj is a subtype of _WaldoObject
            
            # when make call to check_commit_hold_lock, means that we
            # are actually holding the lock on committing to this
            # object.  nothing else can commit to the object in the
            # meantime.
            can_commit = (touched_obj.check_commit_hold_lock(invalid_listener) and
                          can_commit)
        self._unlock()

        return can_commit

    def complete_commit(self, invalid_listener):
        '''
        Should only be called if hold_can_commit returned True.  Runs
        through all touched objects and completes their commits.
        '''
        for touched_obj in invalid_listener.objs_touched.values():
            touched_obj.complete_commit(invalid_listener)
        
    
    def backout_commit(self,invalid_listener,currently_holding_object_locks):
        '''
        @param {_InvalidListener} invalid_listener --- The
        invalid_listener whose changes to a Waldo object we want to
        back out.

        @param {bool} currently_holding_object_locks --- True if
        invalid_listener is currently holding the locks on all the
        waldo objects that it has touched.
        '''
        
        for touched_obj in invalid_listener.objs_touched.values():
            touched_obj.backout(
                invalid_listener,currently_holding_object_locks)
