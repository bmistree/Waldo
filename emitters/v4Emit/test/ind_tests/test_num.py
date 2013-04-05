#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('../../lib/'))

import wVariables
import time
import util
import test_util
host_uuid = util.generate_uuid()


        
INITIAL_NUMBER = 31
def setup():
    dummy_endpoint = test_util.DummyEndpoint(
        test_util.SingleEndpointConnectionObj(),host_uuid)
    
    evt1 = dummy_endpoint._act_event_map.create_root_event()
    evt2 = dummy_endpoint._act_event_map.create_root_event()
    evt3 = dummy_endpoint._act_event_map.create_root_event()

    number = wVariables.WaldoNumVariable('some_name',host_uuid,False,INITIAL_NUMBER)
    return evt1,evt2,evt3,number
    
def run_test():
    evt1,evt2,evt3,number = setup()

    if number.get_val(evt1) != INITIAL_NUMBER:
        err_msg = '\nerror on basic get: expected '
        err_msg += str(INITIAL_NUMBER)
        print (err_msg)
        return False

    number.write_val(evt1,2)
    if number.get_val(evt1) != 2:
        err_msg = '\nerr on second basic get\n'
        print (err_msg)
        return False
    

    # evt2 shouldn't know anything about evt1's changes to number.
    if number.get_val(evt2) != INITIAL_NUMBER:
        err_msg = '\nerr basic gets should be isolated\n'
        print (err_msg)
        return False


    if not evt1.hold_can_commit():
        print ('\nError: should be able to commit a single committer.\n')
        return False

    evt1.complete_commit()

    # wait some small amount of time to ensure that the invalidation
    # notification was passed forward.
    time.sleep(.1)

    if not evt2.is_invalidated:
        err_msg = '\nerr: should have been notified of invalidation'
        print (err_msg)
        return False

    
    if evt2.hold_can_commit():
        print ('\nError: should have been unable to commit second event.\n')
        return False
    evt2.backout_commit()

    
    # check that final value is what evt1 committed
    if number.get_val(evt3) != 2:
        print ('\nerr: should have seen changes evt1 made.\n')
        return False

    return True


        

if __name__ == '__main__':
    run_test()


