import threading

class _CommitManager(object):
    '''
    Challenge is to avoid deadlock when acquiring the locks of all
    objects that we have touched.

    We can guarantee that will not get deadlock if all invalidation
    listeners try to acquire locks on the resources that they have
    modified in order of their uuids.  For example, consider two
    invalidation listeners, A and B.

    A's read/write set is {beta, alpha, gamma}
    B's read/write set is {gamma, beta, alpha}

    If, before acquiring locks, we order each's read/write set, and
    attempt to acquire locks in sorted order, we can guarantee no
    deadlock.

    A acquires in order alpha, beta, gamma
    B acquires in order alpha, beta, gamma
    '''

    def hold_can_commit(self,invalid_listener):
        '''
        @returns{bool} --- True if can commit to all of the objects
        invalid listener touched

        @param{_InvalidListener} invalid_listener --- Runs through all
        state that the invalid listener touched.  Take locks on all the
        individual objects that we want to commit to.
        '''
        can_commit = True
        sorted_touched_obj_ids = sorted(list(invalid_listener.objs_touched.keys()))
        for obj_id in sorted_touched_obj_ids:
            touched_obj = invalid_listener.objs_touched[obj_id]
            # touched_obj is a subtype of _ReferenceBase
            
            # when make call to check_commit_hold_lock, means that we
            # are actually holding the lock on committing to this
            # object.  nothing else can commit to the object in the
            # meantime.
            can_commit = (touched_obj.check_commit_hold_lock(invalid_listener) and
              can_commit)

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
