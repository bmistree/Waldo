
import threading
import waldo.lib.util as util

from waldo.lib.waldoLockedActiveEvent import LockedActiveEvent
from waldo.lib.waldoEventParent import RootEventParent
from waldo.lib.waldoEventParent import PartnerEventParent
from waldo.lib.waldoEventParent import EndpointEventParent
from waldo.lib.waldoBoostedManager import BoostedManager
import traceback
from waldo.lib.waldoLockedActiveEvent import NETWORK, BACKOUT

#### DEBUG
import time, random
class Monitor(threading.Thread):
    def __init__(self,active_event_map):
        self.active_event_map = active_event_map
        super(Monitor,self).__init__()
    def run(self):
        time.sleep(5 + random.random())
        print '\nActive event map after: '
        print('\n'.join(self.active_event_map.map.keys()))
        print '\n\n'

class _ActiveEventMap(object):
    '''
    Keeps track of all activeevent-s on an endpoint
    '''
    
    def __init__(self,local_endpoint,clock):
        # m = Monitor(self)
        # m.start()
        self.map = {}
        self._mutex = threading.RLock()
        self.local_endpoint = local_endpoint
        self.in_stop_phase = False
        self.in_stop_complete_phase = False
        self.stop_callback = None
        self.waiting_on_stop = {}
        self.boosted_manager = BoostedManager(self,clock)
        

    def initiate_stop(self,skip_partner):
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
        
        # note that when we stop events, they may try to remove
        # themselves from the map.  To prevent invalidating the map as
        # we iterate over it, we first copy all the elements into a
        # list, then iterate.
        map_list = list(self.map.values())
        self.in_stop_phase = True
        self._unlock()
        for evt in map_list:
            evt.stop(skip_partner)
        
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

        root_event = self.boosted_manager.create_root_event()
        self.map[root_event.uuid] = root_event
        self._unlock()

        return root_event

    def remove_event(self,event_uuid,retry):
        '''
        @param {bool} retry --- If retry is true, when we remove the
        event, we create another root event whose uuid is either:
           1) Boosted and/or
           
           2) Has the same highlevel bits in its uuid as the removed
              event.  (The high level bits hold the time stamp that
              the event began as well as whether the event is
              boosted.)

        This way, if we are removing an event because the event is
        retrying, the event will not lose its priority in the event
        map on retry.

        @returns --- @see remove_event_if_exists' return statement
        '''
        return self.remove_event_if_exists(event_uuid, retry)

    def remove_event_if_exists(self,event_uuid,retry):
        '''
        @param {bool} retry --- @see remove_event

        @returns {2-tuple} --- (a,b)
        
           a {Event or None} --- If an event existed in the map, then
                                 we return it.  Otherwise, return None.

           b {Event or None} --- If we requested retry-ing, then
                                 return a new root event with
                                 successor uuid to event_uuid.
                                 Otherwise, return None.
        
        '''
        self._lock()
        
        to_remove = self.map.pop(event_uuid,None)
        successor_event = None
        
        if ((to_remove is not None) and
            isinstance(to_remove.event_parent, RootEventParent)):
            successor_event = self.boosted_manager.complete_root_event(event_uuid,retry)
            if successor_event is not None:
                self.map[successor_event.uuid] = successor_event
            
        fire_stop_complete_callback = False
        if (len(self.map) == 0) and (self.in_stop_complete_phase):
            fire_stop_complete_callback = True
            
        self._unlock()
        
        if fire_stop_complete_callback:
            self.stop_callback()

        return to_remove, successor_event

    
    def get_or_create_partner_event(self,uuid,priority):
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
                pep = PartnerEventParent(uuid,self.local_endpoint,priority)
                new_event = LockedActiveEvent(pep,self)
                self.map[uuid] = new_event
                
        to_return = self.map[uuid]
        self._unlock()
        return to_return


    def get_or_create_endpoint_called_event(
        self,endpoint,uuid,priority,result_queue):
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
                eep = EndpointEventParent(
                    uuid,endpoint,self.local_endpoint,result_queue,priority)
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
        evt,_ = self.remove_event_if_exists(uuid,False)
        return evt

    
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

    def _map(self,func,dict):
        '''
        Applies the supplied function to each active event in the map.

        Assumes that if modification is going to be made to the map then the
        supplied function will lock and release the mutex.

        @arg {dict} -- map of argument names to values. Unpacked when passed to
        the provided function. May be None to indicate that there are no args.
        '''
        event_list = [pair[1] for pair in self.map.items()]
        # self._lock()
        for event in event_list:
            if dict:
                func(event,**dict)
            else:
                func(event)
        # self._unlock()
        
    def _stop_event(self,event,should_skip_partner):
        '''
        Backs out the event and removes it from the
        active event map while setting stop_request=True to indicate that the
        event should not be retried.
        '''
        event.forward_backout_request_and_backout_self(
            skip_partner=should_skip_partner, stop_request=True)

        self.remove_event_if_exists(event.uuid,False)

    def backout_from_all_events(self,skip_partner=False):
        '''
        Iterates through each active event in the map and backs out from each.
        '''
        dict = {'should_skip_partner':skip_partner}
        self._map(self._stop_event,dict)

    def _indicate_network_failure(self,event):
        '''
        Indicates to the event that a network failure has occured if it has
        previously sent or received a message.
        '''
        if event.partner_contacted:
            event.set_network_failure()
            tb_list = traceback.format_stack()
            trace_str = "Traceback (most recent call last):\n"
            trace_str += "".join(tb_list)
            trace_str += "NetworkException: raised in endpoint "
            trace_str += str(event.event_parent.local_endpoint)
            trace_str += "; connection with partner failed.\n"
            event.put_exception(util.NetworkException(trace_str))

    def inform_events_of_network_failure(self):
        '''
        Iterates through each active event in the map and sends it a message
        indicating that a network failure has occured if it has previously
        sent a message.
        '''
        self._map(self._indicate_network_failure, None)

    def _lock(self):
        self._mutex.acquire()

    def _unlock(self):
        self._mutex.release()
