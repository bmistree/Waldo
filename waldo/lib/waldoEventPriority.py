import os
import struct

'''
Priority structure:
  abcd

  a --- Single character: 0 if boosted.  1 if standard event
  b --- 16 characters.  Lower numbers have precedence.
  c --- 8 characters.  Random data used to break ties between events
        that were begun at the exact same time.
'''



def gte_priority(prioritya,priorityb):
    '''
    Returns true if prioritya is greater than or equal to priorityb.  That is,
    returns True if prioritya should be able to preempt priorityb.
    '''
    return prioritya <= priorityb

def generate_boosted_priority(timestamp_last_boosted_completed):
    return '0' + timestamp_last_boosted_completed + os.urandom(8)

def generate_timed_priority(current_timestamp):
    return '1' + current_timestamp + os.urandom(8)

def is_boosted_priority(priority):
    return (priority[0] == '0')
