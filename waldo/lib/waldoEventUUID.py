import os
import struct

'''
UUID structure:
  abcd

  a --- Single character: 0 if boosted.  1 if standard event
  b --- 16 characters.  Lower numbers have precedence.
  c --- 8 characters.  Random data used to break ties between events
        that were begun at the exact same time.
  d --- 4 characters.  Version.  Starts at 0, goes to 2^32 -1
        
'''
VERSION_NUM_CHARACTERS = 4


def in_place_sort_uuid_list(list_to_sort):
    '''
    @param {list} --- Each element is an event uuid.
    
    Sorts the list in place.  Lower indices will contain higher
    priority uuids.

    @returns sorted list
    '''
    list_to_sort.sort(key=gte_uuid_sort_key,reverse=True)
    return list_to_sort

    
def gte_uuid(uuida,uuidb):
    '''
    Returns true if uuida is greater than or equal to uuidb.  That is,
    returns True if uuida should be able to preempt uuidb.
    '''
    return gte_uuid_sort_key(uuida) >= gte_uuid_sort_key(uuidb)

def gte_uuid_sort_key(uuid):
    '''
    Returns an object that can be compared using >, >=, <, <= in
    python.
    '''
    return uuid[0:-VERSION_NUM_CHARACTERS]


def update_version_uuid(prev_uuid):
    non_version_prefix = prev_uuid[0:-VERSION_NUM_CHARACTERS]
    vnum = get_version_number(prev_uuid)
    return non_version_prefix + struct.pack('I',vnum+1)
    
STARTING_VERSION_NUMBER = struct.pack('I',0)
def generate_boosted_uuid(timestamp_last_boosted_completed):
    return '0' + timestamp_last_boosted_completed + os.urandom(8) + STARTING_VERSION_NUMBER

def generate_timed_uuid(current_timestamp):
    starting_version_number = 0
    return '1' + current_timestamp + os.urandom(8) + STARTING_VERSION_NUMBER

def get_version_number(uuid):
    packed_v_num = uuid[-VERSION_NUM_CHARACTERS]
    return struct.unpack('I',v_num)[0]

