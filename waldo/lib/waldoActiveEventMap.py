import threading
import util

from waldoLockedActiveEvent import LockedActiveEvent
from waldoEventParent import RootEventParent
from waldoEventParent import PartnerEventParent
from waldoEventParent import EndpointEventParent


class _ActiveEventMap(object):
    '''
    Keeps track of all activeevent-s on an endpoint
    '''
    
    def __init__(self,local_endpoint):
        self.map = {}
        self._mutex = threading.Lock()
        self.local_endpoint = local_endpoint
        self.in_stop_phase = False
        self.in_stop_complete_phase = False
        self.stop_callback = None
        self.waiting_on_stop = {}
    

    def initiate_stop(self):
        '''
        When the endpoint that this is on has said to start
        stoping, then
        '''
        self._lock()
        
        if self.in_stop_phase:
            # can happen if simultaneously attempt to stop connection
            # on both ends or if programmer calls stop twice.
            self._unlock()
            return 

        for evt in self.map.values():
            evt.stop()
        
        self.in_stop_phase = True
        self._unlock()
        
    def callback_when_stopped(self,stop_callback):
        self._lock()
        self.in_stop_complete_phase = True
        self.stop_callback = stop_callback
        len_map = len(self.map)
        self._unlock()
        
        # handles case where we called stop when we had no outstanding events.
        if len_map == 0:
            stop_callback()
        
    def create_root_event(self):
        '''
        Generates a new active event for events that were begun on
        this endpoint and returns it.
        '''
        self._lock()
        if self.in_stop_phase:
            self._unlock()
            raise util.StoppedException()

        rep = RootEventParent(self.local_endpoint,util.generate_uuid())
        root_event = LockedActiveEvent(rep,self)
        self.map[rep.get_uuid()] = root_event
        self._unlock()
        return root_event

    def remove_event(self,event_uuid):
        self.remove_event_if_exists(event_uuid)

    def remove_event_if_exists(self,event_uuid):
        self._lock()
        to_remove = self.map.pop(event_uuid,None)
        fire_stop_complete_callback = False
        if (len(self.map) == 0) and (self.in_stop_complete_phase):
            fire_stop_complete_callback = True
            
        self._unlock()
        
        if fire_stop_complete_callback:
            self.stop_callback()

        
    def get_or_create_partner_event(self,uuid):
        '''
        Get or create an event because partner endpoint requested it.
        Note: if we have to create an event and are in stop phase,
        then we throw a stopped exception.  If the event already
        exists though, we return it (this is so that we can finish any
        commits that we were waiting on).
        
        @returns {_ActiveEvent}
        '''
        
        self._lock()

        if uuid not in self.map:
            if self.in_stop_phase:
                self._unlock()
                raise util.StoppedException()
            else:
                pep = PartnerEventParent(uuid,self.local_endpoint)
                new_event = LockedActiveEvent(pep,self)
                self.map[uuid] = new_event
                
        to_return = self.map[uuid]
        self._unlock()
        return to_return

    def get_or_create_endpoint_called_event(self,endpoint,uuid,result_queue):
        '''
        @param {Endpoint object} endpoint --- The endpoint that made
        the endpoint call onto us.

        @see description above get_or_create_partner_event
        
        Create an event because received an endpoint call
        '''
        self._lock()
        if uuid not in self.map:
            if self.in_stop_phase:
                self._unlock()
                raise util.StoppedException()
            else:
                eep = EndpointEventParent(uuid,endpoint,self.local_endpoint,result_queue)
                new_event = LockedActiveEvent(eep,self)
                self.map[uuid] = new_event

        to_return = self.map[uuid]
        self._unlock()
        return to_return

    def get_and_remove_event(self,uuid):
        '''
        @returns {_ActEvent object or None} --- _ActEvent if it
        existed in map, None otherwise.  (Also, if it existed, remove
        it.)
        '''
        return self.remove_event_if_exists(uuid)

    
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
