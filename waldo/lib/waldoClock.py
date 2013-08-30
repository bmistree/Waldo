import time

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
