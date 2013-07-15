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
CLIENT2_PORT = 6983

print "Connecting"

client = Waldo.stcp_connect(
        Client, CLIENT2_HOST, CLIENT2_PORT, cert="certificate.pem", key="key.pem", ca_certs="pleasework.pem", cert_reqs=ssl.CERT_OPTIONAL)
print "Connected"

while True:
    print "Connected"
    pass