#!/usr/bin/env python

from emitted import Room


import os
import sys

proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
import lib.Waldo as Waldo



PORT_NO = 8787
HOST_NAME = '127.0.0.1'

# keeps track of all endpoints that have been generated so far.
all_endpoints = []

def connected_callback(room_endpoint_obj):
    global all_endpoints
    all_endpoints.append(room_endpoint_obj)
    print '\nChatter connected!\n'

    
def update_callback():
    global all_endpoints
    for endpoint in all_endpoints:
        endpoint.update_msg_log()
    
    
def run():
    
    Waldo.initialize()
    external_chat_log = Waldo.ExternalText('')


    # listen for incoming client connections on HOST_NAME:PORT_NO.
    # when a client connects:
    #    * create a Room object (as defined in the Waldo file),
    #      passing it in the arguments reservation_manager,
    #      external_fs, and written_callback (all of which match the
    #      signature of its onCreate method.
    #    * execute the connected_callback, which takes in the newly
    #      created Waldo Room endpoint object as an argument.
    Waldo.accept(
        # initialization args for room
        external_chat_log,
        update_callback,
        # who to connect to args
        connection_type = Waldo.CONNECTION_TYPE_TCP,
        host_name = HOST_NAME,
        port = PORT_NO,
        # the Waldo endpoint to create when get a connection
        constructor = Room,
        # callback for newly connected object
        connected_callback = connected_callback)
        

if __name__ == '__main__':
    run();

