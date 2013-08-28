#!/usr/bin/env python

from retry_test_v4 import SingleHost
import threading,os,sys,time

# set path to import Waldo lib
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
# contains Waldo utilities
from waldo.lib import Waldo

'''
This test checks to ensure that the retry callback mechanism works
correctly.
'''

NUM_ITERATIONS = 1000

got_retry = False
got_aborted_retry = False


class EndpointThread(threading.Thread):
    def __init__(self,endpoint,run_long_write_long):
        self.endpoint = endpoint
        self.run_long_write_long = run_long_write_long
        self.result = None
        threading.Thread.__init__(self)
    def run(self):
        if self.run_long_write_long:
            self.result = self.endpoint.long_write_long()
        else:
            try:
                self.result = self.endpoint.write_long_long(
                    retry_cb=write_long_long_retry_cb)
            except:
                global got_aborted_retry
                got_aborted_retry = True

            
def delay(endpoint):
    time.sleep(.5)

def write_long_long_retry_cb(endpt):
    global got_retry
    got_retry = True
    return False
    
def run_test():
    endpt = Waldo.no_partner_create(SingleHost,delay)
    
    long_write_long_thread = EndpointThread(endpt,True)
    write_long_long_thread = EndpointThread(endpt,False)

    long_write_long_thread.start()
    time.sleep(.05)
    write_long_long_thread.start()

    long_write_long_thread.join()
    write_long_long_thread.join()

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
