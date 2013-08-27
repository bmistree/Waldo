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


def update_version_uuid(prev_uuid):
    non_version_prefix = prev_uuid[0:-4]
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
