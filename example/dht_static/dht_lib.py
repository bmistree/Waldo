#!/usr/bin/env python
import conf, util_funcs, data, dht_util

import os,sys, time
sys.path.append(
    os.path.join('..','..'))
import waldo.lib.Waldo as Waldo
import waldo.lib.util as util


from coordinator_master_v4 import CoordinatorMaster
from coordinator_connection_v4 import Coordinator, Requester
from node_v4 import Node
from node_connection_v4 import NodeSideA, NodeSideB


def start_coordinator():
    math_endpoint = Waldo.math_endpoint_lib()
    
    coordinator_master = Waldo.no_partner_create(
        CoordinatorMaster, util_funcs.between,
        util_funcs.rand_uuid,math_endpoint,
        conf.MAX_NUMBER_FINGER_TABLE_ENTRIES)

    # begin listening for connections to coordinator master
    Waldo.tcp_accept(
        Coordinator, conf.COORDINATOR_HOST_PORT_PAIR.host,
        conf.COORDINATOR_HOST_PORT_PAIR.port, coordinator_master)
    
    return coordinator_master


def add_single_dht_node(node_host_port_pair):

    # first: connect to discovery service
    requester = Waldo.tcp_connect(
        Requester,
        conf.COORDINATOR_HOST_PORT_PAIR.host,
        conf.COORDINATOR_HOST_PORT_PAIR.port,
        # the host and port that our new dht node will listen on for
        # connections to other dht nodes.
        node_host_port_pair.host,
        node_host_port_pair.port)

    # request request addresses of other nodes to contact from
    # discovery service, plus register self with discovery service.
    uuid, finger_table, next, prev = requester.register()
    dht_node = Waldo.no_partner_create(
        Node,uuid,util_funcs.distance,util_funcs.hashed_uuid,
        util_funcs.between, util_funcs.debug_print)
    
    # listen for connections to my node
    def on_connected(sidea_endpoint):
        sidea_endpoint.add_connection_to_node()

    Waldo.tcp_accept(
        NodeSideA, node_host_port_pair.host,
        node_host_port_pair.port, dht_node,
        node_host_port_pair.host,
        node_host_port_pair.port,
        connected_callback = on_connected)
    
    # connect to other nodes in my finger table
    for uuid in finger_table.keys():
        # table_entry has form:
        #   host: <text>
        #   port: <number>
        #   valid: <bool>
        #   uuid: <text>
        table_entry = finger_table[uuid]
        host_to_connect_to = table_entry['host']
        port_to_connect_to = table_entry['port']
        
        connection_to_finger_table_node = Waldo.tcp_connect(
            NodeSideB, host_to_connect_to, port_to_connect_to,
            dht_node,node_host_port_pair.host, node_host_port_pair.port)
    
    return dht_node


def load_data(dht_load_node,data_to_load):
    '''
    @param {Node} dht_load_node --- Use this to load data
    
    @param {List} data_to_load --- Each element is a a data.DataItem,
    which is a thin wrapper for data key and value.
    '''
    start = time.time()
    for counter in range(0, len(data_to_load)):

        if (counter % 100) == 0:
            print (
                'Loading %s of %s ' % (str(counter),str(len(data_to_load))))
        
        data_item = data_to_load[counter]
        dht_load_node.add_data(data_item.key,data_item.val)

    elapsed = time.time() - start
    print '\nLoad time: ' + str(elapsed)
    print '\n'
    
        
def query_loaded_data(dht_node_list,loaded_data_list):
    start = time.time()
    total_num_hops = 0
    what_to_query_for = None
    what_to_query = None

    node_to_query = dht_node_list[0]
    
    for counter in range(0,len(loaded_data_list)):

        if (counter % 100)  == 0:
            print (
                'Querying %s of %s ' % (str(counter),str(len(loaded_data_list))))
        
        data_item_to_query_for = loaded_data_list[counter]

        gotten_value, num_hops_to_get, found = node_to_query.get_data(
            data_item_to_query_for.key)

        if not found:
            util.get_logger().critical(
                ('Could not find value for key %s.' % data_item_to_query_for),
                extra={'mod': 'DHT Query', 'endpoint_string': 'None'})
            print '\nERROR: check logs for critical\n'
            
        if gotten_value != data_item_to_query_for.val:
            util.get_logger().critical(
                ('Incorrect value for key %s.' % data_item_to_query_for),
                extra={'mod': 'DHT Query', 'endpoint_string': 'None'})
            print '\nERROR: check logs for critical\n'
            

        total_num_hops += num_hops_to_get

    elapsed = time.time() - start
    print '\n\n'
    print 'Average number of hops: ' + str(float(total_num_hops)/float(counter))
    print 'Elapsed time: ' + str(elapsed)
    print '\n\n'

    
def add_dht_nodes():
    dht_node_list = []
    for node_host_port_pair in dht_util.NODE_HOST_PORT_PAIRS:
        dht_node_list.append(add_single_dht_node(node_host_port_pair))
        time.sleep(2)
    return dht_node_list
    
def run():
    coordinator_master = start_coordinator()
    dht_node_list = add_dht_nodes()
    print '\nAbout to load data'
    data_to_load = data.get_data(dht_util.NUMBER_DATA_ITEMS)
    load_data(dht_node_list[0],data_to_load)
    print '\nAbout to query data'    
    query_loaded_data(dht_node_list,data_to_load)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # if run without any arguments, will run all dht
        # nodes in this process.
        run()
    else:
        # Arguments:
        #   ./dht_lib.py start_coord --- Starts the discovery service
        #   ./dht_lib.py start_node <host> <port> --- Starts a
        #   separate dht node.
        cmd = sys.argv[1]
        if cmd == dht_util.CMD_START_COORDINATOR:
            start_coordinator()
        elif cmd == dht_util.CMD_START_NODE:
            host_port_pair = dht_util.decode_node_start_args(sys.argv[2:])
            add_single_dht_node(host_port_pair)

        # Waldo does not yet have semantics for shutting a connection
        # down.  Therefore, just keep the connection open for
        # arbitrary time.
        time.sleep(600)
