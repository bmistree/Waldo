
class HostPortPair(object):
    def __init__(self,host,port):
        self.host = host
        self.port = port

# MAX_NUMBER_FINGER_TABLE_ENTRIES = 5
MAX_NUMBER_FINGER_TABLE_ENTRIES = 10        
COORDINATOR_HOST_PORT_PAIR = HostPortPair('127.0.0.1',5555)

NODE_HOST_PORT_PAIRS = [
    HostPortPair('127.0.0.1',15556),
    HostPortPair('127.0.0.1',15557),
    HostPortPair('127.0.0.1',15558),
    HostPortPair('127.0.0.1',15559),


    HostPortPair('127.0.0.1',15560),
    HostPortPair('127.0.0.1',15561),
    HostPortPair('127.0.0.1',15562),
    HostPortPair('127.0.0.1',15563),
    HostPortPair('127.0.0.1',15564),
    HostPortPair('127.0.0.1',15565),
    HostPortPair('127.0.0.1',15566),
    HostPortPair('127.0.0.1',15567),
    
    
    ]
    

NUMBER_DATA_ITEMS = 500
