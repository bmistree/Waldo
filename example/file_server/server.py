#!/usr/bin/env python

# assumes that the Waldo file file_server.wld has been compiled to a
# python file named emitted.py
from emitted import Server


import os
import sys
proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
from emitters.v3Emit.lib import TCPConnectionObject
from emitters.v3Emit.lib import ReservationManager
from emitters.v3Emit.lib import ExternalFs

PORT_NO = 5554
HOST_NAME = '127.0.0.1'
FOLDER_NAME = 'test_folder'


def connected_callback(server_endpoint_obj):
    print '\nClient connected!\n'

def written_callback(filename,contents):
    print '\nClient has written \n'
    print contents
    print '\nto file ' + filename + '\n'
    
def run():
    # used to synchronize access to all external objects
    reservation_manager = ReservationManager()
    external_fs = ExternalFs(FOLDER_NAME,reservation_manager)        

    # listen for incoming client connections on HOST_NAME:PORT_NO.
    # when a client connects:
    #    * create a Server object (as defined in the Waldo file),
    #      passing it in the arguments reservation_manager,
    #      external_fs, and written_callback (all of which match the
    #      signature of its onCreate method.
    #    * execute the connected_callback, which takes in the newly
    #      created Waldo Server endpoint object as an argument.
    TCPConnectionObject.accept(
        HOST_NAME,PORT_NO,connected_callback,
        Server,reservation_manager,external_fs,
        written_callback)

if __name__ == '__main__':
    run();

