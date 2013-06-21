import threading

class _DeadlockDetector(object):
    '''
    When going through first phase of commit, there's a possibility of
    deadlock.  This can occur if two events are committing and to the
    same variables on at least two hosts.  If the Event 1 acquires a
    lock on var a on Host A first while the Event 2 tries to acquire a
    lock on var b on Host B, everything is fine.  But, if then, Event
    1 tries to acquire a lock on var b and Event 2 tries to acquire a
    lock on var a, can get into a case of deadlock.

    More concretely, we have the potential for deadlock iff we are
    subscribing to resources that another event is also subscribed to
    on more than one host.

    FIXME: eventually will want to combine read lock requests in first
    phase of commit.  In that case, deadlock detection may be more
    sophisticated, having to rely on what type of subscription the
    subscriber is maintaining.
    '''
    
    def __init__(self,root_active_event):
        '''
        @param {waldoActiveEvent._RootActiveEvent} root_active_event
        '''
        self.root_active_event = root_active_event
        self.mutex = threading.Lock()

        #  index: event uuid
        #  val: {
        #          index: host_uuid
        #          val: {
        #                   index: resource_uuid
        #                   val: True (actual val isn't important)
        #               }
        #       }
        self.other_event_hosts = {}
        
        
    # FIXME: may not need locks in this class if will always be used
    # within locks of RootActiveEvent.  (Currently the removed
    # subscription is not.)
        
    def _lock(self):
        self.mutex.acquire()

    def _unlock(self):
        self.mutex.release()
        

    def _potential_deadlock(self,subscriber_uuid):
        '''
        ASSUMES ALREADY INSIDE OF LOCK
        
        @returns {bool} --- True if there is a potential for deadlock,
        False otherwise.
        '''
        if self._count_num_hosts(subscriber_uuid) > 1:
            return True
        return False

    def _count_num_hosts(self,other_event_uuid):
        '''
        ASSUMES ALREADY INSIDE OF LOCK
        
        @returns {int} --- The number of hosts that event with uuid
        other_event_uuid is subscribed to the same resources as we
        are.
        '''
        return len(self.other_event_hosts[other_event_uuid])
        
    def add_subscriber(self,subscriber_uuid,resource_host_uuid,resource_uuid):
        '''
        @param {uuid} subscriber_uuid, resource_host_uuid, resource_uuid

        @returns {bool} --- @see _potential_deadlock
        '''
        self._lock()
        
        if subscriber_uuid not in self.other_event_hosts:
            self.other_event_hosts[subscriber_uuid] = {}
        if resource_host_uuid not in self.other_event_hosts[subscriber_uuid]:
            self.other_event_hosts[subscriber_uuid][resource_host_uuid] = {}

        self.other_event_hosts[subscriber_uuid][resource_host_uuid][resource_uuid] = True

        potential_deadlock = self._potential_deadlock(subscriber_uuid)
        self._unlock()

        return potential_deadlock

        
    def remove_subscriber(self,subscriber_uuid,resource_host_uuid,resource_uuid):
        '''
        Removes subscription of subscriber_uuid 
        '''
        self._lock()
        if subscriber_uuid in self.other_event_hosts:
            host_map = self.other_event_hosts[subscriber_uuid]

            if resource_host_uuid in host_map:
                resource_map = host_map[resource_host_uuid]

                if resource_uuid in resource_map:
                    del resource_map[resource_uuid]

                if len(resource_map) == 0:
                    del host_map[resource_host_uuid]

            if len(host_map) == 0:
                del self.other_event_hosts[subscriber_uuid]
                
        self._unlock()
