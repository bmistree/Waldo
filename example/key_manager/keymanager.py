#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
import OpenSSL
from OpenSSL import crypto

from emitted import Manager, Client

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6981

def generate_cert_and_key(Endpoint, C, ST, L, O, OU, CN):
    print "generating certificates"
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA,2048)
    keytext = crypto.dump_privatekey(crypto.FILETYPE_PEM,key)

    cert = crypto.X509()
    cert.get_subject().C = C
    cert.get_subject().ST = ST
    cert.get_subject().L = L
    cert.get_subject().O = O
    cert.get_subject().OU = OU
    cert.get_subject().CN = CN

    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    print "signed certificates"

    certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    return certificate, keytext



key_manager = Waldo.stcp_accept(
        Manager, MANAGER_HOST, MANAGER_PORT, None, None, None, generate_cert_and_key)

while True:
    pass

