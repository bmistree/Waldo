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

CLIENT2_PORT = 6972

print "Get Key"
key = Waldo.get_key()
print "Get get_certificate"
cert = Waldo.get_certificate("Gavin", '127.0.0.1', 6981, key)

print "Test"
print crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
print crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

f = open("tmp/t.pem", "w+")
f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
f.close()

f = open("tmp/t1.pem", "w+")
f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
f.close()


secondConnect = Waldo.stcp_connect(
        Client, MANAGER_HOST, CLIENT2_PORT, cert="tmp/t.pem", key="tmp/t1.pem")

while True:
	print secondConnect.confirm()
	pass

