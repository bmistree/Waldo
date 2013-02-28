#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('..','..','lib'))

import wVariables
import commitManager
import invalidationListener
import time
import util

'''
This test runs through and just determines how fast we can create
NUM_ITERATIONS events, each of which increments a variable.  (This is
in contrast to increment_single_number_single_event.py, which checks
how fast we can create a single event and increment a number
NUM_ITERATIONS times inside of it.)
'''


class BasicTestInvalidationListener(invalidationListener._InvalidationListener):
    def notify_invalidated(self,wld_obj):
        pass

NUM_ITERATIONS = 100000


def run_test():
    host_uuid = util.generate_uuid()
    commit_manager = commitManager._CommitManager()
    number = wVariables.WaldoNumVariable('some num',host_uuid,22)

    start = time.time()
    for i in range(0,NUM_ITERATIONS):
        evt1 = BasicTestInvalidationListener(commit_manager)    
        val = number.get_val(evt1)
        number.write_val(evt1,val+1)
        evt1.hold_can_commit()
        evt1.complete_commit()

    elapsed = time.time() - start
    print '\n\n'
    print elapsed
    print '\n\n'        
    

if __name__ == '__main__':
    run_test()
