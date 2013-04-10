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

        
    def create_root_event(self):
        '''
        Generates a new active event for events that were begun on
        this endpoint and returns it.
        '''
        new_event = RootActiveEvent(self.local_endpoint)
        self._lock()
        self.map[new_event.uuid] = new_event
        self._unlock()
        return new_event

    def remove_event(self,event_uuid):
        self._lock()
        del self.map[event_uuid]
        self._unlock()

    def remove_event_if_exists(self,event_uuid):
        self._lock()
        try:
            del self.map[event_uuid]
        except:
            pass
        
        self._unlock()
        
    
    def get_or_create_partner_event(self,uuid):
        '''
        Get or create an event because partner endpoint requested it.

        @returns {_ActiveEvent}
        '''
        self._lock()
        event = self.map.setdefault(
            uuid,
            PartnerActiveEvent(uuid,self.local_endpoint))
        self._unlock()
        return event

    def get_or_create_endpoint_called_event(self,endpoint,uuid,result_queue):
        '''
        @param {Endpoint object} endpoint --- The endpoint that made
        the endpoint call onto us.
        
        Create an event because received an endpoint call
        '''
        self._lock()
        event = self.map.setdefault(
            uuid,
            EndpointCalledActiveEvent(
                uuid,self.local_endpoint,
                endpoint,result_queue))
        self._unlock()
        return event

    def get_and_remove_event(self,uuid):
        '''
        @returns {_ActEvent object or None} --- _ActEvent if it
        existed in map, None otherwise.  (Also, if it existed, remove
        it.)
        '''
        act_event = None
        self._lock()
        try:
            act_event = self.map[uuid]
            del self.map[uuid]
        except:
            pass
            
        self._unlock()
        return act_event

    
    def get_event(self,uuid):
        '''
        @returns {None,_ActiveEvent} --- None if event with name uuid
        is not in map.  Otherwise, reutrns the _ActiveEvent in the
        map.
        '''
        self._lock()
        to_return = self.map.get(uuid,None)
        self._unlock()
        return to_return        

    def _lock(self):
        self._mutex.acquire()

    def _unlock(self):
        self._mutex.release()
