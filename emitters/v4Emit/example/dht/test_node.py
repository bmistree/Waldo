#!/usr/bin/env python
import conf
import util_funcs

import os,sys
sys.path.append(
    os.path.join('..','..','lib'))
import Waldo

from node_v4 import Node


def run_test():

    uuid = util_funcs.hashed_uuid(None,'some id')
    dht_node = Waldo.no_partner_create(
        Node,uuid,util_funcs.distance,util_funcs.hashed_uuid,
        util_funcs.between, util_funcs.debug_print)

    data_to_add = [
        ('key','data'),
        ('a','ata'),
        ('m','wow')]

    # add the data
    for key,data in data_to_add:
        dht_node.add_data(key,data)

    # test that the added data is still there
    for key,data in data_to_add:
        value, num_hops, exists = dht_node.get_data(key)
        if not exists:
            print '\nErr: data should have existed in dht'
            return False
        if value != data:
            print '\nErr: got incorrect value back for key'
            return False
        
    # test that data not added is not there
    not_added_data_keys = ['woie','dow','mwoe']
    for key in not_added_data_keys:
        value,num_hops,exists = dht_node.get_data(key)
        if exists:
            print '\nErr: should not have received any data from false key'
            return False

    return True

if __name__ == '__main__':
    run_test()
