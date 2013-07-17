#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
import OpenSSL
from OpenSSL import crypto

from emitted import Client,Manager

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6971

client = Waldo.stcp_connect(
        Client, MANAGER_HOST, MANAGER_PORT)

print "Get Key"
key = Waldo.get_key()
print "Get get_certificate"
cert = Waldo.get_certificate("Gavin", '127.0.0.1', 6981, key)

print "Test"
print crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
print crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

