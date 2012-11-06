#!/usr/bin/env python

from emitted import Chatter
from room import PORT_NO, HOST_NAME

import os
import sys
import time

proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
from emitters.v3Emit.lib import TCPConnectionObject
from emitters.v3Emit.lib import ReservationManager

def print_chat_log(chat_log):
    print '\n'    
    print chat_log
    print '\n'

    
def run(chatter_name):
    # no external objects for reservation manager to control, but
    # still used.
    reservation_manager = ReservationManager()

    # try to bind to HOST_NAME:PORT_NO when creating chatter
    tcp_conn_obj = TCPConnectionObject(HOST_NAME,PORT_NO,None)
    chatter = Chatter(tcp_conn_obj,reservation_manager,
                      chatter_name,print_chat_log)

    # ugly sleep for now.  more likely that in the future, will block
    # until connection is established.
    time.sleep(1)

    while True:
        # event loop to grab user input        
        print '\nType in a message.\n'
        user_input = raw_input ('-->')
        chatter.write_msg(user_input)
        

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage_msg = '\nUsage error: ./chatter.py <username>\n'
        print usage_msg
    else:
        run(sys.argv[1]);

