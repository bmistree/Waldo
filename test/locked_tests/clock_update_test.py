#!/usr/bin/env python

import os
import sys
import time

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib import Waldo
from waldo.lib.waldoEndpoint import _Endpoint
from waldo.lib import util
from waldo.lib.waldoVariableStore import _VariableStore
from waldo.lib.waldoAllEndpoints import AllEndpoints
from waldo.lib.waldoClock import Clock
from waldo.lib.waldoConnectionObj import _WaldoSameHostConnectionObject


'''
Creates two partner endpoints.  Each uses a different clock.  Practice
skipping clock ahead on one causes clock time to skip ahead on other.
'''

# start clock a with a timestamp advancement of this much.  Check that
# this automatically causes B to update.
INITIAL_A_DELTA = 500

class ClockDummyEndpoint(_Endpoint):
    def __init__(self,conn_obj,clock,all_endpoints):
        host_uuid = util.generate_uuid()
        glob_var_store = _VariableStore(host_uuid)

        copied_waldo_classes = dict(Waldo._waldo_classes)
        copied_waldo_classes['Clock'] = clock
        copied_waldo_classes['AllEndpoints'] = all_endpoints

        _Endpoint.__init__(
            self,copied_waldo_classes,
            host_uuid,conn_obj,glob_var_store)


def run_test():

    all_endpoints_a = AllEndpoints()
    all_endpoints_b = AllEndpoints()
    
    # start a's clock 500s in the future    
    clock_a = Clock(all_endpoints_a,INITIAL_A_DELTA)
    clock_b = Clock(all_endpoints_b)
    
    # create connection object
    conn_obj = _WaldoSameHostConnectionObject()

    ### setup actual endpoints
    endpoint_a = ClockDummyEndpoint(conn_obj,clock_a,all_endpoints_a)
    endpoint_b = ClockDummyEndpoint(conn_obj,clock_b,all_endpoints_b)

    # wait for each endpoint to exchange ready messages
    time.sleep(.3)

    # check that clock_b's delta has been advanced
    if clock_b.delta == 0:
        print '\nOn ready, did not advance time delta\n'
        return False

    # inject a fake clock advancement onto clock b
    tstamp = clock_b.get_timestamp()
    new_tstamp = float(tstamp) + 20
    clock_b.got_partner_timestamp(
         '{:10.6f}'.format(new_tstamp))

    # wait for each endpoint to message each other the clock
    # advancement
    time.sleep(.3)

    # check that clock a's timestamp was advanced as well
    if clock_a.delta <= INITIAL_A_DELTA:
        print '\nDid not advance A\'s timestamp\n'
        return False
    
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
