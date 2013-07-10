#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

from emitted import Client,Manager

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6981



client = Waldo.stcp_connect(
        Client, MANAGER_HOST, MANAGER_PORT, None, None)

print "get uuid"
uuid = Waldo.uuid()
print "get certificates"
key = client.gen_key(uuid)
print "got stuff"
print(key)

