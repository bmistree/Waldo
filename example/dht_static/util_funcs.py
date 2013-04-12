import hashlib
import random

# Python doesn't support integers large enough to handle computing
# distances between full keyspace of md5.  Therefore, just taking a
# subset of each uuid and using that when computing distances.
NUM_HASH_OCTETS = 4
MAX_HASH = int( 'F'*NUM_HASH_OCTETS, 16)
MIN_HASH = 0

def debug_print(endpoint,msg):
    print msg

def hashed_uuid(endpoint,to_hash):
    '''
    @param {String} to_hash --- Arbitrarily long string.
    
    @returns {uuid string} --- 32 character-long string, where each
    character is a hex value.  (Note: do not use full string when
    calculating distances, etc.)
    '''
    hasher = hashlib.md5()
    hasher.update(to_hash)
    uuid = hasher.hexdigest()
    return uuid
    
def rand_uuid(endpoint):
    return hashed_uuid(endpoint,str(random.random()))

def between(endpoint,x,a,b):
    '''
    @param x,a,b {uuid string} --- @see create_uuid for a description
    of its format.

    @returns {bool} --- True if distance(a,x) + distance(x,b) <=
    distance(a,b), ie, True if x lies on the shortest arc of the
    consistently-hashed uuid keyspace between a and b.
    '''
    if distance(endpoint,a,x) + distance(endpoint,x,b) <= distance(endpoint,a,b):
        return True
    
    return False
    
def distance(endpoint,str_uuid_a, str_uuid_b):
    '''
    @returns {Number} ---

    Assume keyspace is a circle. Returns the minimum number of keys to
    traverse between str_uuid_a and str_uuid_b.

    Because distances in keyspace may be too large to represent in
    Python, only using NUM_HASH_OCTETS of the key to calculate distances.
    '''
    capped_a = str_uuid_a[0:NUM_HASH_OCTETS]
    capped_b = str_uuid_b[0:NUM_HASH_OCTETS]

    int_a = int(capped_a, 16)
    int_b = int(capped_b, 16)

    higher_val = max(int_a,int_b)
    lower_val = min(int_a,int_b)

    straight_line_distance = higher_val - lower_val
    wrapped_distance =  (
        (MAX_HASH - higher_val) +
        (lower_val - MIN_HASH) + 1)

    return min(straight_line_distance, wrapped_distance)
