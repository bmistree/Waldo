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
    
    
    
    
def add_dht_nodes():
    for node_host_port_pair in conf.NODE_HOST_PORT_PAIRS:
        add_single_dht_node(node_host_port_pair)

    
def run():
    coordinator_master = start_coordinator()
    add_dht_nodes()
    time.sleep(5)

    

if __name__ == '__main__':
    run()
