CMD_START_COORDINATOR = 'start_coord'
CMD_START_NODE = 'start_node'
SETUP_BIN = 'dht_lib.py'

class HostPortPair(object):
    def __init__(self,host,port):
        self.host = host
        self.port = port

def decode_node_start_args(args):
    '''
    @param {Array} args --- The arguments after the cmd
    
    @returns {HostPortPair}
    '''
    return HostPortPair(args[0],int(args[1]))
    
    
def encode_node_start_args(host_port_pair):
    return [host_port_pair.host,str(host_port_pair.port)]


def dht_assert(assert_msg):
    print 'DHT ASSERT: ' + assert_msg
    assert(False)
