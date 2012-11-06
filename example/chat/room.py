#!/usr/bin/env python

from emitted import Room


import os
import sys
proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
from emitters.v3Emit.lib import TCPConnectionObject
from emitters.v3Emit.lib import ReservationManager
from emitters.v3Emit.lib import ExternalText

PORT_NO = 8787
HOST_NAME = '127.0.0.1'

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
    # used to synchronize access to all external objects
    reservation_manager = ReservationManager()
    external_chat_log = ExternalText('',reservation_manager)        

    # listen for incoming client connections on HOST_NAME:PORT_NO.
    # when a client connects:
    #    * create a Room object (as defined in the Waldo file),
    #      passing it in the arguments reservation_manager,
    #      external_fs, and written_callback (all of which match the
    #      signature of its onCreate method.
    #    * execute the connected_callback, which takes in the newly
    #      created Waldo Room endpoint object as an argument.
    TCPConnectionObject.accept(
        HOST_NAME,PORT_NO,connected_callback,
        Room,reservation_manager,external_chat_log,
        update_callback)

if __name__ == '__main__':
    run();

