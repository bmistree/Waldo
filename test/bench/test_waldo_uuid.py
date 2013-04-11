#!/usr/bin/env python

import time

import sys
import os

sys.path.append(
    os.path.join('..','..','lib',))
import util

NUM_ITERATIONS = 100000
    
def run_test():
    start = time.time()
    for i in range(0,NUM_ITERATIONS):
        # u = buuid.uuid4()
        u = util.generate_uuid()

    elapsed = time.time() - start
    print '\n\n'
    print elapsed
    print '\n\n'        
    

if __name__ == '__main__':
    run_test()
