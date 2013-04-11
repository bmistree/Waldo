#!/usr/bin/env python

import os, sys, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from lib import wVariables, util, Waldo

sys.path.append(
    os.path.join('..','ind_tests'))
import test_util

'''
This test runs through and just determines how fast we can create
NUM_ITERATIONS events, each of which increments a variable.  (This is
in contrast to increment_single_number_single_event.py, which checks
how fast we can create a single event and increment a number
NUM_ITERATIONS times inside of it.)
'''


NUM_ITERATIONS = 100000


def run_test():
    host_uuid = util.generate_uuid()
    dummy_endpoint = test_util.DummyEndpoint(
        test_util.SingleEndpointConnectionObj(),host_uuid)
    number = wVariables.WaldoNumVariable('some num',host_uuid,22)

    start = time.time()
    for i in range(0,NUM_ITERATIONS):
        evt1 = dummy_endpoint._act_event_map.create_root_event()        
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
