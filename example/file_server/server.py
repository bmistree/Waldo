#!/usr/bin/env python

# assumes that the Waldo file file_server.wld has been compiled to a
# python file named emitted.py
from emitted import Server


import os, sys
proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
import lib.Waldo as Waldo


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

    Waldo.initialize()
    external_fs = Waldo.ExternalFs(FOLDER_NAME)

    # listen for incoming client connections on HOST_NAME:PORT_NO.
    # when a client connects:
    #    * create a Server object (as defined in the Waldo file),
    #      passing it in the arguments reservation_manager,
    #      external_fs, and written_callback (all of which match the
    #      signature of its onCreate method.
    #    * execute the connected_callback, which takes in the newly
    #      created Waldo Server endpoint object as an argument.
    Waldo.accept(
        # initialization args for Server
        external_fs,
        written_callback,
        # where to listen for connections args
        connection_type = Waldo.CONNECTION_TYPE_TCP,
        host_name = HOST_NAME,
        port = PORT_NO,
        # the Waldo endpoint to create when get a connection
        constructor = Server,
        # what to do with newly connected object
        connected_callback = connected_callback)

    
if __name__ == '__main__':
    run();

