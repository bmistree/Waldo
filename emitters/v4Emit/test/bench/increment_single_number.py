#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('..','..','lib'))

import wVariables

import wVariables
import commitManager
import invalidationListener
import time

class BasicTestInvalidationListener(invalidationListener._InvalidationListener):
    def notify_invalidated(self,wld_obj):
        pass

NUM_ITERATIONS = 100000
    
def run_test():
    commit_manager = commitManager._CommitManager()
    number = wVariables.WaldoNumVariable(22)

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
