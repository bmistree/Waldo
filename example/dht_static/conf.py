import dht_util

# MAX_NUMBER_FINGER_TABLE_ENTRIES = 5
# MAX_NUMBER_FINGER_TABLE_ENTRIES = 10
MAX_NUMBER_FINGER_TABLE_ENTRIES = 2
COORDINATOR_HOST_PORT_PAIR = dht_util.HostPortPair('127.0.0.1',15555)


NODE_HOST_PORT_PAIRS = [
    dht_util.HostPortPair('127.0.0.1',15556),
    dht_util.HostPortPair('127.0.0.1',15557),
    # dht_util.HostPortPair('127.0.0.1',15558),
    # dht_util.HostPortPair('127.0.0.1',15559),
    # dht_util.HostPortPair('127.0.0.1',15560)
    ]
    

NUMBER_DATA_ITEMS = 5000
