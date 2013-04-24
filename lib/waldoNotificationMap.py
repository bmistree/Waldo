import threading
import util

class _NotificationMap(object):
    '''
    Each waldo reference contains a _NotificationMap.

    Here is how locking a reference for the first phase of its commit
    works:

       * The invalidation listener calls hold_can_commit on
         commit_manager.

       * Inside hold_can_commit, the commit_manager runs through every
         object that the invalidation listener touched, calling
         check_commit_hold_lock.  check_commit_hold_lock does two things:

             1: It adds the invalidation listener to this notification map.

             2: It takes a lock on the entire object reference and
                checks for conflicts, returning True if there are no
                conflicts, and False otherwise.

                
        Briefly focusing on #1:
        
           We are trying to prevent commit-time deadlock, which could
           happen with two events and endpoint calls.  Consider an
           example with Events A and B that need to commit on hosts
           Alpha, Beta, Gamma.  If A locks alpha on Alpha, then B
           locks beta on Beta, then A tries to lock beta on Beta, and
           then B tries to lock alpha on Alpha, we'd get deadlock.

           To do this, before the invalidation listener acquires the
           lock for a resource, it first registers into the resource's
           notification map.  The idea behind the notification map is
           that we send all those that are attempting to lock a
           resource a notification when another invalidation listener
           is trying to lock the same resource.  They forward the
           notification to the root event.  The root event can
           (conservatively) detect potential deadlocks and backout
           requests for locks.
    '''
    def __init__(self,resource_uuid,host_uuid):
        '''
        @param {uuid} resource_uuid --- The uuid of the resource that
        others are trying to subscribe to.

        @param {uuid} host_uuid --- The uuid of the host that the
        resource is held on.
        '''
        # maps from invalidation listener uuid to invalidation
        # listener.
        self.invalid_listener_map = {}
        self._mutex = threading.Lock()
        self.resource_uuid = resource_uuid
        self.host_uuid = host_uuid

    def _lock(self):
        self._mutex.acquire()
        
        
    def _unlock(self):
        self._mutex.release()


    def add_invalidation_listener(self,invalid_listener):
        to_notify = []
        self._lock()
        if invalid_listener.uuid not in self.invalid_listener_map:
            to_notify = list(self.invalid_listener_map.values())

            self.invalid_listener_map[invalid_listener.uuid] = invalid_listener
        self._unlock()

        # now notify all those listeners that someone else subscribed
        # to same variable.
        for already_subscribed in to_notify:
            already_subscribed.notify_additional_subscriber(
                invalid_listener.uuid,self.host_uuid,self.resource_uuid)

        if len(to_notify) != 0:
            uuids_already_subscribed = [ already.uuid for already in to_notify ]
            invalid_listener.notify_existing_subscribers(
                uuids_already_subscribed,self.host_uuid,self.resource_uuid)
    

    def remove_invalidation_listener(self,invalid_listener):
        to_notify = []
        self._lock()
        if invalid_listener.uuid in self.invalid_listener_map:
            del self.invalid_listener_map[invalid_listener.uuid]
            to_notify = list(self.invalid_listener_map.values())
        self._unlock()

        # now notify all those listeners that someone else
        # unsubscribed to same variable.
        for already_subscribed in to_notify:
            already_subscribed.notify_removed_subscriber(
                invalid_listener.uuid,self.host_uuid,self.resource_uuid)
            
    
