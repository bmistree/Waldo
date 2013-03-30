#!/usr/bin/env python
import conf
import util_funcs

import os,sys
sys.path.append(
    os.path.join('..','..','lib'))
import Waldo

from node_v4 import Node
from node_connection_v4 import NodeSideA, NodeSideB
import random

HOSTA = '127.0.0.1'
HOSTB = HOSTA
PORTA = 5902
PORTB = PORTA + 2

'''
Tests to ensure that can connect atomically two nodes to each other via
connection_nodes.  (Previously, had a bug where would infinitely hang when
trying to connect.)
'''

def create_single_node(listen_on_host, listen_on_port, should_accept=False):
    uuid = util_funcs.hashed_uuid(None,str(random.random()))
    dht_node = Waldo.no_partner_create(
        Node,uuid,util_funcs.distance,util_funcs.hashed_uuid)

    if should_accept:
        def on_connected(endpoint):
            pass
            # print '\nGot into on connected\n'

        # listen for connections to dht node
        Waldo.tcp_accept(
            NodeSideA,
            listen_on_host, listen_on_port,
            dht_node,
            listen_on_host, listen_on_port,
            connected_callback = on_connected)

    return dht_node


def run_test():

    dhta = create_single_node(HOSTA,PORTA)
    dhtb = create_single_node(HOSTB,PORTB,True)

    # now try to connect the nodes to each other. a connects to b.
    connection = Waldo.tcp_connect(
        NodeSideB,HOSTB,PORTB,dhta, HOSTA, PORTA)

    connection.add_connection_to_node()
    
    return True

if __name__ == '__main__':
    run_test()
