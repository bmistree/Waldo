
class HostPortPair(object):
    def __init__(self,host,port):
        self.host = host
        self.port = port

MAX_NUMBER_FINGER_TABLE_ENTRIES = 5
COORDINATOR_HOST_PORT_PAIR = HostPortPair('127.0.0.1',5555)

NODE_HOST_PORT_PAIRS = [
    HostPortPair('127.0.0.1',15556),
    HostPortPair('127.0.0.1',15557),
    HostPortPair('127.0.0.1',15558),
    HostPortPair('127.0.0.1',15559),
    ]
    
