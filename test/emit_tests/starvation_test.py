#!/usr/bin/env python

from starvation_test_v4 import SideA,SideB
import threading
from Queue import Queue
import time
import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


'''
Starts many events on SideA.  Following this, starts many events on
SideB.  Each started event requires a write lock on the same
variables.  This means that only one event can execute at a time.  If
we were just running wound/wait, because all of SideA's events were
begun earlier, all of them would be processed before SideB's events.
However, using boosted, we should see the events alternate from
completing a SideA event to completing a SideB event.
'''

# Whenever an event completes, it puts its result into result_queue.
# If it's an event from SideA that finished, it puts SIDE_A_RESULT in;
# if it's an event from SideB, then puts SIDE_B_RESULT in queue.
result_queue = Queue()
SIDE_A_RESULT = 1
SIDE_B_RESULT = -1
NUM_EVENTS_TO_START_PER_ENDPOINT = 50


class EndpointThread(threading.Thread):
    def __init__(self,endpt,result_to_use):
        self.endpt = endpt
        self.result_to_use = result_to_use
        super(EndpointThread,self).__init__()
    def run(self):
        result = self.endpt.seq(self.result_to_use)
        global result_queue
        result_queue.put(result)
        


def start_endpt(endpt,result_to_use):
    '''
    Creates NUM_EVENTS_TO_START_PER_ENDPOINT threads, each of which request the
    endpoint to perform seq method on endpoint and put result into global
    result_queue.
    '''
    endpt_threads_list = []
    for i in range(0, NUM_EVENTS_TO_START_PER_ENDPOINT):
        endpt_threads_list.append(EndpointThread(endpt,result_to_use))

    map (lambda x: x.start(), endpt_threads_list)
    
    # wait to ensure that all of the separate threads have dumped their events
    # on to endpt
    delay(None)
    return endpt_threads_list


def run_test():
    # connect endpoints to each other
    side_a, side_b=(
        Waldo.same_host_create(SideA,delay).same_host_create(SideB,delay))

    # print '\n\n'
    # print 'A: ' + str(side_a)
    # print 'B: ' + str(side_b)
    # print '\n\n'
    
    # start events on each endpoint
    all_as = start_endpt(side_a,SIDE_A_RESULT)
    all_bs = start_endpt(side_b,SIDE_B_RESULT)

    # wait until all events have finished
    map ( lambda x: x.join(), all_as)
    map ( lambda x: x.join(), all_bs)

    return check_result_queue()

def delay(endpt):
    time.sleep(.1)


def check_result_queue():
    global result_queue
    running_sum = 0
    unfair = False
    result_list= []
    while True:
        try:
            result = result_queue.get_nowait()
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

        
    return True

    

if __name__ == '__main__':
    if run_test():
        print '\nSucceded\n'
    else:
        print '\nFailed\n'


