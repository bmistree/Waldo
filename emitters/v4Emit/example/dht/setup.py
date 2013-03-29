#!/usr/bin/env python
import conf
import util_funcs
import time

import os,sys
sys.path.append(
    os.path.join('..','..','lib'))
import Waldo

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

    requester = Waldo.tcp_connect(
        Requester,
        conf.COORDINATOR_HOST_PORT_PAIR.host,
        conf.COORDINATOR_HOST_PORT_PAIR.port,
        # the host and port that our new dht node will listen on for
        # connections to other dht nodes.
        node_host_port_pair.host,
        node_host_port_pair.port)

    uuid, finger_table, next, prev = requester.register()
    dht_node = Waldo.no_partner_create(Node,uuid,util_funcs.distance)
    
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

        
def add_dht_nodes():
    dht_node_list = []
    for node_host_port_pair in conf.NODE_HOST_PORT_PAIRS:
        dht_node_list.append(add_single_dht_node(node_host_port_pair))
    return dht_node_list
    
def run():
    coordinator_master = start_coordinator()
    dht_node_list = add_dht_nodes()

    import pdb
    pdb.set_trace()
    
    time.sleep(5)

    

    
    

if __name__ == '__main__':
    run()
