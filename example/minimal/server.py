#!/usr/bin/env python

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))
import lib.Waldo as Waldo

from emitted import Server
import config

def connected_callback(server_endpoint):
    print "Got connection from client:", server_endpoint

def run():
    Waldo.initialize()

    # Listen for connections, creating a new Waldo endpoint when they
    # are accepted. Does not return.
    Waldo.accept(
        # Initialization args for Waldo onCreate would go here as
        # positional args if there were any.
        host_name = config.HOST,
        port = config.PORT,
        # The Waldo endpoint to create when get a connection
        constructor = Server,
        # callback for newly connected object
        connected_callback = connected_callback)


if __name__ == '__main__':
    run()
