#!/usr/bin/env python

from emitted import Chatter
from room import PORT_NO, HOST_NAME

import os
import sys
import time

proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
import lib.Waldo as Waldo

def print_chat_log(chat_log):
    print '\n'    
    print chat_log
    print '\n'

    
def run(chatter_name):

    Waldo.initialize()

    # actually produce the endpoint object by connecting to the host
    # and port that are running the room.
    chatter = Waldo.connect(
        # initialization args for chatter
        chatter_name,
        print_chat_log,
        # who to connect to args
        connection_type = Waldo.CONNECTION_TYPE_TCP,
        host_name = HOST_NAME,
        port = PORT_NO,
        # the Waldo endpoint to create when connecting
        constructor = Chatter)
                  

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

