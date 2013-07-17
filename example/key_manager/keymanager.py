#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
import OpenSSL
from OpenSSL import crypto
from Crypto.Util import asn1


from emitted import Manager, Client

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6971

key_manager = Waldo.stcp_accept(
        Manager, MANAGER_HOST, MANAGER_PORT)

Waldo.start_ca(True, host='127.0.0.1', port=6981)

while True:
    pass