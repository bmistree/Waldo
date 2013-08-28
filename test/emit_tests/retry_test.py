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
This test forces a retry on one of the events.  Ensuring that all resulting
retry logic works correctly.
'''

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
            self.result = self.endpoint.write_long_long()
            
def delay(endpoint):
    time.sleep(.5)
    
def run_test():
    endpt = Waldo.no_partner_create(SingleHost,delay)
    
    long_write_long_thread = EndpointThread(endpt,True)
    write_long_long_thread = EndpointThread(endpt,False)

    long_write_long_thread.start()
    time.sleep(.05)
    write_long_long_thread.start()

    long_write_long_thread.join()
    write_long_long_thread.join()
    
    if long_write_long_thread.result != 1:
        return False
    
    if write_long_long_thread.result != 2:
        return False

    return True


if __name__ == '__main__':
    if run_test():
        print '\nSuccess\n'
    else:
        print '\nFail\n'
