import time
import waldo.lib.util as util
import threading

class Clock(object):
    def __init__(self,all_endpoints,initial_delta=0):
        self.delta = initial_delta
        self._delta_mutex = threading.Lock()
        self.all_endpoints = all_endpoints

    def _delta_lock(self):
        self._delta_mutex.acquire()
    def _delta_unlock(self):
        self._delta_mutex.release()
        
    def get_timestamp(self):
        '''
        @returns {str} --- Fixed width string time since epoch as
        float in seconds.  First ten digits are seconds.  Then the six
        decimal digits represent microseconds.
        '''
        # FIXME: system dependent time call.  On many systems, this
        # will only return seconds since epoch, not microseconds.  @see
        # http://docs.python.org/3/library/time.html#time.time
        self._delta_lock()
        timestamp = time.time() + self.delta
        self._delta_unlock()        
        return '{:10.6f}'.format(timestamp)

    def got_partner_timestamp(self,partner_clock_timestamp):
        '''
        @param {string} partner_clock_timestamp --- The string
        representation of a 16 digit float.

        If partner_clock_timestamp is from the future, we should
        forward our clock by updating delta with the amount of time
        the partner clock timestamp is from the future.

        Then, we notify all partners to check if they should update
        their clocks.

        '''
        partner_float = float(partner_clock_timestamp)
        needs_update = False
        

        # note: need to change delta atomically: therefore cannot call
        # get_timestamp separately
        self._delta_lock()
        # timestamp = float('{:10.6f}'.format(time.time() + self.delta))
        timestamp = time.time() + self.delta
        if partner_float > timestamp:
            self.delta = self.delta + partner_float - timestamp
            needs_update = True
            
        self._delta_unlock()

        if needs_update:
            self.all_endpoints.send_clock_update()
