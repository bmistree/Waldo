#!/usr/bin/env python

import time
# import buuid
import uuid

NUM_ITERATIONS = 100000
    
def run_test():
    start = time.time()
    for i in range(0,NUM_ITERATIONS):
        # u = buuid.uuid4()
        u = uuid.uuid4()

    elapsed = time.time() - start
    print '\n\n'
    print elapsed
    print '\n\n'        
    

if __name__ == '__main__':
    run_test()
