#!/usr/bin/env python

import dht_lib, conf, dht_util, data
import subprocess, time

def run():
    to_kill = []
    
    # start coordinator
    cmd = ['python', dht_util.SETUP_BIN,dht_util.CMD_START_COORDINATOR]
    print '\nStarting discovery coordinator'
    proc = subprocess.Popen(cmd,shell=False)
    to_kill.append(proc)
    time.sleep(2)
    
    # start nodes
    for i in range(0,len(conf.NODE_HOST_PORT_PAIRS) -1 ):
        print 'Starting node %s of %s ' % (str(i + 1), str(len(conf.NODE_HOST_PORT_PAIRS)))
        host_port_pair = conf.NODE_HOST_PORT_PAIRS[i]
        encoded_node_host_port_pair = dht_util.encode_node_start_args(
            host_port_pair)
        cmd = (
            ['python',dht_util.SETUP_BIN,dht_util.CMD_START_NODE] +
            encoded_node_host_port_pair)
        proc = subprocess.Popen(cmd,shell=False)
        to_kill.append(proc)        
        time.sleep(5)

    print (
        'Starting node %s of %s ' %
        (str(len(conf.NODE_HOST_PORT_PAIRS)),str(len(conf.NODE_HOST_PORT_PAIRS))))
             
    local_node_host_port_pair = conf.NODE_HOST_PORT_PAIRS[-1]
    local_dht_node = dht_lib.add_single_dht_node(local_node_host_port_pair)
    time.sleep(5)


    data_to_load = data.get_data(conf.NUMBER_DATA_ITEMS)
    print 'Starting loading %s data items' % str(len(data_to_load))
    dht_lib.load_data(local_dht_node,data_to_load)
    print 'Waiting period'
    time.sleep(10)
    print 'Querying data (once for each loaded item)'
    dht_lib.query_loaded_data([local_dht_node],data_to_load)

    print 'Shutting down'
    for proc_to_kill in to_kill:
        proc_to_kill.kill()

    
if __name__ == '__main__':
    run()
