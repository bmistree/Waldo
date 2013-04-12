#!/usr/bin/env python

from atomic_int_v4 import AtomicInt
import threading,os,sys

# set path to import Waldo lib
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)

# contains Waldo utilities
import lib.Waldo


'''
Starts 100 threads to increment a shared atomic variable.
'''

def run_example():

    # create an AtomicInt "endpoint" with no partner
    atomic_int = lib.Waldo.no_partner_create(AtomicInt, 0)
    
    all_threads = []
    for i in range(0,100):
        t = threading.Thread(target=increment_atomic,args=(atomic_int,))
        t.start()
        all_threads.append(t)

    # wait on all threads to finish
    map(lambda t: t.join(), all_threads)

    final_value = atomic_int.get_int()
    print '\nFinal atomic int value: %s\n' % str(final_value)
    

def increment_atomic(atomic_int):
    '''
    Increments atomic integer passed in.
    '''
    atomic_int.add_to_int(1)


    
if __name__ == '__main__':
    run_example()
