import time
import util

class Clock(object):
    def get_timestamp(self):
        '''
        @returns {str} --- Fixed width string time since epoch as
        float in seconds.  First ten digits are seconds.  Then the six
        decimal digits represent microseconds.
        '''
        # FIXME: system dependent time call.  On many systems, this
        # will only return seconds since epoch, not microseconds.  @see
        # http://docs.python.org/3/library/time.html#time.time
        return '{:10.6f}'.format(time.time())

    def got_partner_timestamp(self,partner_clock_timestamp):
        util.logger_warn(
            'Must fill in got_partner_timestamp in Clock')
