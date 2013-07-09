#!/usr/bin/env python

from retry_cb_v4 import SingleHost

import threading,os,sys,time,Queue

# set path to import Waldo lib
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
# contains Waldo utilities
from waldo.lib import Waldo

NUM_ITERATIONS = 1000

got_retry = False
got_aborted_retry = False

class LongThread(threading.Thread):
    def __init__ (self,endpt):
        self.endpt = endpt
        threading.Thread.__init__(self)
    def run(self):
        for i in range(0,NUM_ITERATIONS):
            try:
                self.endpt.long_event(retry_cb=long_retry_cb)
            except:
                global got_aborted_retry
                got_aborted_retry = True
                break


def long_retry_cb(endpt):
    global got_retry
    got_retry = True
    return False
            
class ShortThread(threading.Thread):
    def __init__ (self,endpt):
        self.endpt = endpt
        threading.Thread.__init__(self)
    def run(self):
        for i in range(0,NUM_ITERATIONS):
            self.endpt.short_event()

            
def delay(endpt):
    time.sleep(.0001)
    return
    
def run_test():
    endpt = Waldo.no_partner_create(SingleHost,delay)
    
    lt = LongThread(endpt)
    st = ShortThread(endpt)

    start = time.time()
    lt.start()
    st.start()
    lt.join()
    st.join()

    global got_retry, got_aborted_retry
    if not got_retry:
        return False
    if not got_aborted_retry:
        return False

    return True

        
    
if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
