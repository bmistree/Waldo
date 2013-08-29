from waldo.lib.waldoEventParent import RootEventParent
from waldo.lib.waldoLockedActiveEvent import LockedActiveEvent
import waldo.lib.util as util
from waldo.lib.waldoEventPriority import generate_boosted_priority, generate_timed_priority


class BoostedManager(object):
    '''
    Each endpoint has a single outstanding boosted event.  This
    manager keeps track of all 
    '''

    def __init__(self,act_event_map,clock):
        '''
        @param {Clock} clock --- Host's global clock.  
        '''
        self.clock = clock
        self.last_boosted_complete = self.clock.get_timestamp()

        self.act_event_map = act_event_map
        
        # Each element is a root event.  the closer to zero index an
        # event is in this list, the older it is.  The oldest event in
        # this list should be made a boosted event.
        self.event_list = []


    def create_root_event(self):
        evt_uuid = util.generate_uuid()
        if len(self.event_list) == 0:
            evt_priority = generate_boosted_priority(self.last_boosted_complete)
        else:
            evt_priority = generate_timed_priority(self.clock.get_timestamp())

        rep = RootEventParent(self.act_event_map.local_endpoint,evt_uuid,evt_priority)
        root_event = LockedActiveEvent(rep,self.act_event_map)
        self.event_list.append(root_event)
        return root_event
        

    def complete_root_event(self,completed_event_uuid,retry):
        '''
        @param {UUID} completed_event_uuid

        @param {bool} retry --- If the event that we are removing is
        being removed because backout was called, we want to generate
        a new event with a successor UUID (the same high-level bits
        that control priority/precedence, but different low-level
        version bits)
        
        Whenever any root event completes, this method gets called.
        If this event had been a boosted event, then we boost the next
        waiting event.  Otherwise, we remove it from the list of
        waiting uuids.

        @returns {None/Event} --- If retry is True, we return a new
        event with successor uuid.  Otherwise, return None.
        '''
        counter = 0
        remove_counter = None
        for event in self.event_list:
            if event.uuid == completed_event_uuid:
                remove_counter = counter
                completed_event = event
                break
            counter += 1

        #### DEBUG
        if remove_counter is None:
            util.logger_assert(
                'Completing a root event that does not exist')
        #### END DEBUG

        replacement_event = None
        if retry:
            # in certain cases, we do not actually promote each
            # event's priority to boosted.  For instance, if the event
            # is already in process of committing.  However, if that
            # commit goes awry and we backout, we want the replacement
            # event generated to use a boosted event priority, rather
            # than its original priority.
            if counter == 0:
                # new event should be boosted.  
                if not is_boosted_priority(completed_event.get_priority()):
                    # if it wasn't already boosted, that means that we
                    # tried to promote it while it was in the midst of
                    # its commit and we ignored the promotion.
                    # Therefore, we want to apply the promotion on
                    # retry.
                    replacement_priority = generate_boosted_priority(self.last_boosted_complete)
                else:
                    # it was already boosted, just reuse it
                    replacement_priority = completed_event.get_priority()
            else:
                # it was not boosted, just increment the version number
                replacement_priority = completed_event.get_priority()

            rep = RootEventParent(
                self.act_event_map.local_endpoint,util.generate_uuid(),
                replacement_priority)
            replacement_event = LockedActiveEvent(rep,self.act_event_map)
            self.event_list[counter] = replacement_event
        else:
            # we are not retrying this event: remove the event from
            # the list and if there are any other outstanding events,
            # check if they should be promoted to boosted status.
            self.event_list.pop(counter)
            if counter == 0:
                self.last_boosted_complete = self.clock.get_timestamp()
                self.promote_first_to_boosted()

        return replacement_event
            
    def promote_first_to_boosted(self):
        '''
        If there is an event in event_list, then turn that event into
        a boosted event.  If there is not, then there are no events to
        promte and we should do nothing.
        '''
        if len(self.event_list) == 0:
            return

        boosted_priority = generate_boosted_priority(self.last_boosted_complete)
        self.event_list[0].promote_boosted(boosted_priority)
