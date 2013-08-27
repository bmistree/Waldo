import os
from waldo.lib.waldoEventParent import RootEventParent
from waldo.lib.waldoLockedActiveEvent import LockedActiveEvent
import waldo.lib.util as util

def generate_boosted_uuid(timestamp_last_boosted_completed):
    return '0' + timestamp_last_boosted_completed + os.urandom(8)

def generate_timed_uuid(current_timestamp):
    return '1' + current_timestamp + os.urandom(8)


class BoostedManager(object):
    '''
    Each endpoint has a single outstanding boosted event.  This
    manager keeps track of all 
    '''

    def __init__(self,clock):
        '''
        @param {Clock} clock --- Host's global clock.  
        '''
        self.clock = clock
        self.last_boosted_complete = self.clock.get_timestamp()
        
        # Each element is a root event.  the closer to zero index an
        # event is in this list, the older it is.  The oldest event in
        # this list should be made a boosted event.
        self.event_list = []


    def create_root_event(self,local_endpoint,act_event_map):
        if len(self.event_list) == 0:
            evt_uuid = generate_boosted_uuid(self.last_boosted_complete)
        else:
            evt_uuid = generate_timed_uuid(self.clock.get_timestamp())
            
        rep = RootEventParent(act_event_map.local_endpoint,evt_uuid)
        root_event = LockedActiveEvent(rep,act_event_map)
        self.event_list.append(root_event)
        return root_event
        

    def complete_root_event(self,completed_event_uuid):
        '''
        @param {UUID} completed_event_uuid
        
        Whenever any root event completes, this method gets called.
        If this event had been a boosted event, then we boost the next
        waiting event.  Otherwise, we remove it from the list of
        waiting uuids.
        '''
        counter = 0
        remove_counter = None
        for event in self.event_list:
            if event.uuid == completed_event_uuid:
                remove_counter = counter
                break
            counter += 1

        #### DEBUG
        if remove_counter is None:
            util.logger_assert(
                'Completing a root event that does not exist')
        #### END DEBUG

        self.event_list.pop(counter)

        if counter == 0:
            self.last_boosted_complete = self.clock.get_timestamp()
            self.promote_first_to_boosted()

        return None
            
    def promote_first_to_boosted(self):
        '''
        If there is an event in event_list, then turn that event into
        a boosted event.  If there is not, then there are no events to
        promte and we should do nothing.
        '''
        if len(self.event_list) == 0:
            return

        boosted_uuid = generate_boosted_uuid(self.last_boosted_complete)
        self.event_list[0].promote_boosted(boosted_uuid)
