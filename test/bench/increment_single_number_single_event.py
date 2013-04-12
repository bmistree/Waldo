#!/usr/bin/env python

import os, sys, time

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from lib import wVariables, util


sys.path.append(
    os.path.join('..','ind_tests'))
import test_util


'''
This test runs through and just determines how fast we can create a
single event, which increments a variable NUM_ITERATIONS times.  (This
is in contrast to increment_single_number_separate_events.py, which
checks how fast we can create separate events for each time we
increment the variable.  The two together gives us a sense of how much
overhead there is in creating an event.)
'''

NUM_ITERATIONS = 100000
    
def run_test():
    host_uuid = util.generate_uuid()
    dummy_endpoint = test_util.DummyEndpoint(
        test_util.SingleEndpointConnectionObj(),host_uuid)    
    number = wVariables.WaldoNumVariable('some num',host_uuid,22)

    start = time.time()
    evt1 = dummy_endpoint._act_event_map.create_root_event()            
    for i in range(0,NUM_ITERATIONS):
        val = number.get_val(evt1)
        number.write_val(evt1,val+1)        
    evt1.hold_can_commit()
    evt1.complete_commit()

    elapsed = time.time() - start
    print '\n\n'
    print str(NUM_ITERATIONS) + ' in ' + str(elapsed) + ' seconds'    
    print '\n\n'        
    

if __name__ == '__main__':
    run_test()
