import util
from abc import abstractmethod

class _InvalidationListener(object):
    '''
    An atomic event must be a subtype of _InvalidationListener.  When
    we touch a Waldo object, we note that the listener depends on a
    particular version number of the object.

    If make a commit with a later version number, we send an
    invalidation message to all listeners.
    '''

    def __init__(self,commit_manager,uuid=None):
        '''
        @param {_CommitManager} commit_manager --- When we either want
        to commit or backout the changes that the invalidation
        listener makes to its objs_touched, do so through _CommitManager

        @param {uuid} uuid --- If uuid is None, generates a new uuid.
        Otherwise, uses old one.
        '''        
        self.objs_touched = {}

        if uuid == None:
            uuid = util.generate_uuid()
        self.uuid = uuid
        
        self.commit_manager = commit_manager

        
    def peered_modified(self):
        '''
        @returns{bool} --- True if one of the objects that we touched
        was peered and we modified it.
        '''
        for obj_uuid in self.objs_touched.keys():
            obj = self.objs_touched[obj_uuid]
            if obj.is_peered() and obj.modified(self):
                return True
        
        return False
        
        
    @abstractmethod
    def notify_invalidated(self,wld_obj):
        '''
        @param {_WaldoObject} wld_obj --- The Waldo object, which
        changed since we read it.
        
        IMPORTANT: Note that we are not guaraneed that we are still
        out of date with wld_obj by the time we receive this message.
        We may have attempted to commit our changes, been rejected
        (because of an out of date version number) and restarted the
        event.
        '''
        pass

    def notify_removed_subscriber(
        self,removed_subscriber_uuid,resource_uuid):
        '''
        @see notify_additional_subscriber, except for removals instead of
        additions.
        '''
        pass
    
    def notify_additional_subscriber(
        self,additional_subscriber_uuid,resource_uuid):
        '''
        When we are asked to perform the first phase of a commit, we
        subscribe for events simultaneously trying to commit to the
        same resources. This is to detect and avoid deadlocks: if two
        events are both listening for subscribers on different hosts
        for the same piece of data, then there's a chance for
        deadlock, and we must back one of the events out.  (In this
        case, we backout the event that has the lower uuid.)

        To determine if there is the potential for deadlock, each time
        we try to acquire a lock for the first phase of a variable's
        commit, subscribe for others doing the same, and forward these
        subscribers ids and the resource id back to the root.  The
        root can detect and backout commits as described in the
        previous paragraph.
        '''
        # InvalidationListeners that also want to prevent deadlocks
        # during commit (eg., _ActiveEvents) must override this
        # method.
        pass
        
    def notify_existing_subscribers(
        self,list_of_existing_subscriber_uuids,resource_uuid):
        '''
        @see notify_additional_subscriber
        
        @param {array} list_of_existing_subscriber_uuids --- Each
        element is a uuid of an invalidation listener that is trying
        to hold a commit lock on the Waldo reference with uuid
        resource_uuid.
        '''
        # InvalidationListeners that also want to prevent deadlocks
        # during commit (eg., _ActiveEvents) must override this
        # method.
        pass

    def add_touch(self,what_touched):
        '''
        @param {_WaldoObj} what_touched --- The object that was
        touched by this python object.  Any time we read or write to
        an object, we register it as having been "touched" by this
        InvalidationListener.
        '''
        self.objs_touched[what_touched.uuid] = what_touched


    ### Each of the next three functions for now are thin wrappers
    ### around commit_manager functions.
    def hold_can_commit(self):
        '''
        @see _CommitManager.hold_can_commit
        '''
        return self.commit_manager.hold_can_commit(self)
        
    def complete_commit(self):
        '''
        @see _CommitManager.complete_commit
        '''        
        self.commit_manager.complete_commit(self)

    def backout_commit(self,currently_holding_object_locks):
        '''
        @param {bool} currently_holding_object_locks --- True if we
        have previously called hold_can_commit (ie, we're holding
        locks on variables), False otherwise.
        
        @see _CommitManager.backout_commit
        '''        
        self.commit_manager.backout_commit(
            self,currently_holding_object_locks)
        
