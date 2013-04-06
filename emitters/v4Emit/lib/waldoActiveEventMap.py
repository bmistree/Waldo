from waldoActiveEvent import PartnerActiveEvent
from waldoActiveEvent import EndpointCalledActiveEvent
from waldoActiveEvent import RootActiveEvent
import threading
import logging
import util

class _ActiveEventMap(object):
    '''
    Keeps track of all activeevent-s on an endpoint
    '''
    
    def __init__(self,local_endpoint):
        
        self.map = {}
        self._mutex = threading.Lock()
        self.local_endpoint = local_endpoint

        self.logging_info = {
            'mod': 'ActiveEventMap',
            'endpoint_string': self.local_endpoint._endpoint_uuid_str
            }

        
    def create_root_event(self):
        '''
        Generates a new active event for events that were begun on
        this endpoint and returns it.
        '''
        if __debug__:
            log_msg = 'Creating root event'
            util.get_logger().info(log_msg, extra=self.logging_info)

        new_event = RootActiveEvent(self.local_endpoint)
        self._lock()
        self._insert_event_into_map(new_event)
        self._unlock()
        return new_event

    def remove_event(self,event_uuid):
        if __debug__:
            log_msg = 'Remove event ' + str(event_uuid)
            util.get_logger().info(log_msg, extra=self.logging_info)
        self._lock()
        del self.map[event_uuid]
        self._unlock()

    def remove_event_if_exists(self,event_uuid):
        if __debug__:
            log_msg = 'Remove event if exists ' + str(event_uuid)
            util.get_logger().info(log_msg, extra=self.logging_info)
        self._lock()
        if event_uuid in self.map:
            del self.map[event_uuid]
        self._unlock()
        
    
    def get_or_create_partner_event(self,uuid):
        '''
        Get or create an event because partner endpoint requested it.

        @returns {_ActiveEvent}
        '''
        if __debug__:
            log_msg = 'Get or create partner event'
            util.get_logger().debug(log_msg, extra=self.logging_info)

        self._lock()
        if uuid not in self.map:
            new_event = PartnerActiveEvent(
                uuid,self.local_endpoint)
            self._insert_event_into_map(new_event)
        event = self.map[uuid]
        self._unlock()
        return event

    def get_or_create_endpoint_called_event(self,endpoint,uuid,result_queue):
        '''
        @param {Endpoint object} endpoint --- The endpoint that made
        the endpoint call onto us.
        
        Create an event because received an endpoint call
        '''
        if __debug__:
            log_msg = 'Get or create endpoint called event'
            util.get_logger().debug(log_msg, extra=self.logging_info)
        
        self._lock()
        if uuid not in self.map:
            event = EndpointCalledActiveEvent(
                uuid,self.local_endpoint,
                endpoint,result_queue)

            self._insert_event_into_map(event)
        event = self.map[uuid]
        self._unlock()
        return event

    def get_and_remove_event(self,uuid):
        '''
        @returns {_ActEvent object or None} --- _ActEvent if it
        existed in map, None otherwise.  (Also, if it existed, remove
        it.)
        '''
        if __debug__:
            log_msg = 'Get and remove event'
            util.get_logger().debug(log_msg, extra=self.logging_info)
            
        act_event = None
        self._lock()
        if uuid in self.map:
            act_event = self.map[uuid]
            del self.map[uuid]

        self._unlock()
        return act_event

    
    def get_event(self,uuid):
        '''
        @returns {None,_ActiveEvent} --- None if event with name uuid
        is not in map.  Otherwise, reutrns the _ActiveEvent in the
        map.
        '''
        if __debug__:
            log_msg = 'Get event'
            util.get_logger().debug(log_msg, extra=self.logging_info)
            
        self._lock()
        to_return = self.map.get(uuid,None)
        self._unlock()
        return to_return        
    
    def _insert_event_into_map(self,event):
        '''
        MUST BE CALLED FROM WITHIN LOCK
        
        @param {_ActiveEvent} event
        '''
        #### DEBUG
        if event.uuid in self.map:
            util.logger_assert(
                'Error with ActiveEventMap.  Should not insert an event ' +
                'that already exists.')
        #### END DEBUG
        self.map[event.uuid] = event

        if __debug__:
            log_msg = 'Inserted ' + event.str_uuid + ' into map.'
            util.get_logger().debug(log_msg, extra=self.logging_info)

    def _lock(self):
        if __debug__:
            util.lock_log('Acquire in active event map ')
        self._mutex.acquire()
        if __debug__:
            util.lock_log('Has acquired in active event map ')
        
    def _unlock(self):
        self._mutex.release()
