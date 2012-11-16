#!/usr/bin/env python

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))
import lib.Waldo as Waldo

from emitted import Client
import config

import time

def main():
    Waldo.initialize()

    # Initiate a connection
    client = Waldo.connect(
        # Initialization args for Waldo onCreate would go here as
        # positional args if there were any.
        host_name = config.HOST,
        port = config.PORT,
        # The Waldo endpoint to create when connecting
        constructor = Client)

    # Sleep long enough to let the client connect to the server and
    # for the server to report it.
    time.sleep(3)


if __name__ == '__main__':
    main()
