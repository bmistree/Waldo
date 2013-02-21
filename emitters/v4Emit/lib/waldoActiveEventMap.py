from waldoActiveEvent import PartnerActiveEvent
from waldoActiveEvent import EndpointCalledActiveEvent
from waldoActiveEvent import RootActiveEvent
import threading

class _ActiveEventMap(object):
    '''
    Keeps track of all activeevent-s on an endpoint
    '''

    def __init__(self,commit_manager,local_endpoint):
        
        self.map = {}
        self._mutex = threading.Lock()
        self.commit_manager = commit_manager
        self.local_endpoint = local_endpoint
        
    def create_root_event(self):
        '''
        Generates a new active event for events that were begun on
        this endpoint and returns it.
        '''
        new_event = RootActiveEvent(self.commit_manager,self.local_endpoint)
        self._lock()
        self._insert_event_into_map(new_event)
        self._unlock()
        return new_event
    
    def get_or_create_partner_event(self,uuid):
        '''
        Get or create an event because partner endpoint requested it.

        @returns {_ActiveEvent}
        '''
        self._lock()
        if uuid not in self.map:
            new_event = PartnerActiveEvent(
                self.commit_manager,uuid,self.local_endpoint)
            self._insert_event_into_map(new_event)
        event = self.map[uuid]
        self._unlock()
        return event
        
    def get_or_create_endpoint_called_event(self,endpoint,uuid):
        '''
        @param {Endpoint object} endpoint --- The endpoint that made
        the endpoint call onto us.
        
        Create an event because received an endpoint call
        '''        
        self._lock()

        if uuid not in self.map:
            event = EndpointCalledActiveEvent(
                self.commit_manager,uuid,self.local_endpoint,
                endpoint,)
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
        

    
    def _lock(self):
        self._mutex.acquire()
        
    def _unlock(self):
        self._mutex.release()
