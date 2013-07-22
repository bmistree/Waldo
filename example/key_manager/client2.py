#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
import OpenSSL
from OpenSSL import crypto
import ssl

from emitted import Client,Manager

CLIENT2_HOST = '127.0.0.1'
CLIENT2_PORT = 6972

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6971

Waldo.add_ca_to_list("pleasework.pem", MANAGER_HOST, 6981)

key = Waldo.get_key()
cert = Waldo.get_certificate("Client2", '127.0.0.1', 6981, key)
print cert

key_manager = Waldo.stcp_accept(
        Manager, CLIENT2_HOST, CLIENT2_PORT, cert=cert, key=key, ca_certs="pleasework.pem", cert_reqs=ssl.CERT_REQUIRED)

while True:
    pass
