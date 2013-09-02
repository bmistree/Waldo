#!/usr/bin/env python

from starvation_merge_v4 import SideA,SideB
import threading
from Queue import Queue
import time
import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


'''
Starting many "one-type-events" on SideA and then starting many
"one-type-events" on SideB.  These should execute following boosted
fairness, one SideA event will complete, then one SideB event, etc.

Immediately after starting these events, we also start a series of
two-type-events.  Again, we start all of the two-type-events on SideA
first and then start all of the two-type-events on SideB.  These will
not obey boosted priorities.  And all of SideA's events should finish
before SideB's.
'''

# Whenever an event completes, it puts its result into result_queue.
# If it's an event from SideA that finished, it puts SIDE_A_RESULT in;
# if it's an event from SideB, then puts SIDE_B_RESULT in queue.
result_queue_one = Queue()
result_queue_two = Queue()
SIDE_A_RESULT_ONE = 1
SIDE_B_RESULT_ONE = -1

SIDE_A_RESULT_TWO = 2
SIDE_B_RESULT_TWO = -2

NUM_EVENTS_TO_START_PER_ENDPOINT = 50


class EndpointThread(threading.Thread):
    def __init__(self,endpt,result_to_use,result_queue):
        self.endpt = endpt
        self.result_to_use = result_to_use
        self.result_queue = result_queue
        super(EndpointThread,self).__init__()
    def run(self):

        if self.result_to_use in (SIDE_A_RESULT_ONE,SIDE_B_RESULT_ONE):
            result = self.endpt.seq_one(self.result_to_use)
        else:
            result = self.endpt.seq_two(self.result_to_use)
                
        self.result_queue.put(result)
        

def start_endpt(endpt,result_to_use,queue_to_use):
    '''
    Creates NUM_EVENTS_TO_START_PER_ENDPOINT threads, each of which request the
    endpoint to perform seq method on endpoint and put result into global
    result_queue.
    '''
    endpt_threads_list = []
    for i in range(0, NUM_EVENTS_TO_START_PER_ENDPOINT):
        endpt_threads_list.append(EndpointThread(endpt,result_to_use,queue_to_use))

    map (lambda x: x.start(), endpt_threads_list)
    
    # wait to ensure that all of the separate threads have dumped their events
    # on to endpt
    delay(None)
    return endpt_threads_list


def run_test():
    # connect endpoints to each other
    side_a, side_b=(
        Waldo.same_host_create(SideA,delay).same_host_create(SideB,delay))

    # start events on each endpoint
    global result_queue_one, result_queue_two
    all_as_one = start_endpt(side_a,SIDE_A_RESULT_ONE,result_queue_one)
    all_bs_one = start_endpt(side_b,SIDE_B_RESULT_ONE,result_queue_one)

    all_as_two = start_endpt(side_a,SIDE_A_RESULT_TWO,result_queue_two)
    all_bs_two = start_endpt(side_b,SIDE_B_RESULT_TWO,result_queue_two)

    all_events = all_as_one + all_bs_one + all_as_two + all_bs_two
    
    # wait until all events have finished
    map ( lambda x: x.join(), all_events)


    return check_result_queue()

def delay(endpt):
    time.sleep(.1)


def check_result_queue():
    global result_queue_one, result_queue_two
    running_sum = 0
    unfair = False
    result_list= []
    while True:
        try:
            result = result_queue_one.get_nowait()
            running_sum += result
            result_list.append(result)
            
            if abs(running_sum) >= 2:
                unfair = True
            
        except:
            break

    if unfair:
        print '\nUnfair\n'
        print result_list
        print '\n'
        return False


    while True:
        try:
            result = result_queue_two.get_nowait()
            print result
        except:
            break

    print '\n\n'
    return True

    

if __name__ == '__main__':
    if run_test():
        print '\nSucceded\n'
    else:
        print '\nFailed\n'


