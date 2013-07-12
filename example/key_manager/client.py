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
MANAGER_PORT = 6974

def get_key():
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA,2048)
    keytext = crypto.dump_privatekey(crypto.FILETYPE_PEM,key)

    return keytext

def generate_request(C, ST, L, O, OU, CN, key):
    f = open('temp.pem', 'w+')
    f.write(key)
    f.close()
    #DELETE KEYFILE
    key = crypto.load_privatekey(crypto.FILETYPE_PEM,open('temp.pem').read())
    req = OpenSSL.crypto.X509Req()
    req.get_subject().C = C
    req.get_subject().ST = ST
    req.get_subject().L = L
    req.get_subject().O = O
    req.get_subject().OU = OU
    req.get_subject().CN = CN
    req.set_pubkey(key)
    req.sign(key, "sha256")
    req = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    return req


client = Waldo.stcp_connect(
        Client, MANAGER_HOST, MANAGER_PORT, cert="certificate.pem", key="key.pem")

uuid = Waldo.uuid()
print "get certificates"
key = get_key()
req = generate_request("US", "AS", "DSds", "SDSD", "DSDS", "Waldo", key)
print "got req"
cert = client.req_to_cert(req)

print(cert)

