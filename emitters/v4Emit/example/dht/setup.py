#!/usr/bin/env python
import conf, util_funcs, data, dht_util

import os,sys, time
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
    dht_node = Waldo.no_partner_create(
        Node,uuid,util_funcs.distance,util_funcs.hashed_uuid)
    
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


def load_data(dht_node_list):
    '''
    @param {List} dht_node_list --- Each element is a dht node

    @returns {List} --- Each element is a a data.DataItem, which is a thin
    wrapper for data key and value.
    '''
    data_items = data.get_data(conf.NUMBER_DATA_ITEMS)
    if len(dht_node_list) == 0:
        dht_util.dht_assert(
            'No dht nodes passed in when loading data')
    dht_load_node = dht_node_list[0]

    for counter in range(0, len(data_items)):
        if (counter % 5) == 0:
            print '\nLoading data ' + str(counter) + ' of ' + str(len(data_items))
        
        data_item = data_items[counter]
        dht_load_node.add_data(data_item.key,data_item.val)

    return data_items
        
def query_loaded_data(dht_node_list,loaded_data_list):

    total_num_hops = 0
    for counter in range(0,len(loaded_data_list)):

        if (counter % 5) == 0:
            print ('About to query for index ' +
                   str(counter) + ' of ' +
                   str(len(loaded_data_list)))
        
        data_item_to_query_for = loaded_data_list[counter]
        node_to_query = dht_node_list[counter % len(dht_node_list)  ]
        
        gotten_value, num_hops_to_get, found = node_to_query.get_data(
            data_item_to_query_for.key)

        if not found:
            import pdb
            pdb.set_trace()
            dht_util.dht_assert(
                'Could not find value expecting when querying dht')
        if gotten_value != data_item_to_query_for.val:
            dht_util.dht_assert(
                'Queried value disagrees with expected value when querying the dht')

        total_num_hops += num_hops_to_get

    print '\n\n'
    print 'Average number of hops: ' + str(total_num_hops/counter)
    print '\n\n'

    
def add_dht_nodes():
    dht_node_list = []
    for node_host_port_pair in conf.NODE_HOST_PORT_PAIRS:
        dht_node_list.append(add_single_dht_node(node_host_port_pair))
    return dht_node_list
    
def run():
    coordinator_master = start_coordinator()
    dht_node_list = add_dht_nodes()
    print '\nAbout to load data'
    loaded_data_list = load_data(dht_node_list)
    print '\nAbout to query data'    
    query_loaded_data(dht_node_list,loaded_data_list)


    

    
    

if __name__ == '__main__':
    run()
