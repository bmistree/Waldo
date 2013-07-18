#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(base_dir)
import Waldo
import OpenSSL
from OpenSSL import crypto
from emitted import Manager, Client

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6974
def set_hostname(name):
    '''
    Args:
        name (String) - set hostname of CA to this
    Pass in the name of hostname of the CA
    '''
    global MANAGER_HOST
    MANAGER_HOST = name

def set_port(port):
    '''
    Args:
        port (int) - set port of CA to this
    Pass in the port number of the CA
    '''
    global MANAGER_PORT
    MANAGER_PORT = port

def get_key():
    '''
    Generates a random key and returns a key object
    '''
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA,2048)
    return key

def make_temp():
    '''
    Makes a temporary directory if it doesn't exist already
    '''
    filename = "./tmp/"
    temp = os.path.dirname(filename)
    try:
        os.stat(temp)
    except:
        os.path.mkdir(temp)


def generate_request(CN, key):
    '''
    Args:
        CN (String) - identity to be put on the certificate
        key (crypto.PKey) - key going to be associated with a certificate
    Generates a certificate request that will paired with a key
    '''
    req = OpenSSL.crypto.X509Req()
    req.get_subject().CN = CN
    req.set_pubkey(key)
    req.sign(key, "sha1")
    req = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    return req

def get_cacert(host, port):
    '''
    Args:
        host (String) - hostname of the CA
        port (int) - port of the CA
    Returns the CA certificate in text format
    '''
    print "Connect"
    client = Waldo.stcp_connect(
        Client, host, port)
    print "Add CA"
    ca_cert = client.get_cacert()
    print "Stop"
    client.stop()
    print "return"
    return ca_cert

def get_certificate(CN, host, port, key=None):
    '''
    Args:
        CN (String) - name on the certificate
        host (String) - hostname of the CA
        port (int) - port of the CA
        key (crypto.PKey) - key to associate with the certificate
    Call this to get the a certificate from the CA. If no key is specified. It will
    generate one then and return that.
    '''
    client = Waldo.stcp_connect(
        Client, host, port)

    uuid = Waldo.uuid()
    noKey = False
    if key is None:
        noKey = True
        key = get_key()
    req = generate_request(CN, key)
    cert = client.req_to_cert(req)
    make_temp()
    f = open('tmp/temp.pem', 'w+')
    f.write(cert)
    f.close()

    cert = crypto.load_certificate(crypto.FILETYPE_PEM,open('tmp/temp.pem').read())
    #client.stop()
    if noKey is None:
        return cert, key
    else:
        return cert