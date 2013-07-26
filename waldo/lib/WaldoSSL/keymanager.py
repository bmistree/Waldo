#!/usr/bin/env python

import os,sys, Queue, time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..')
sys.path.append(base_dir)
import Waldo
import OpenSSL
from OpenSSL import crypto
from Crypto.Util import asn1


from emitted import Manager, Client

MANAGER_HOST = '127.0.0.1'
MANAGER_PORT = 6974

ca_cert=None
ca_key=None

certfilep = ""
keyfilep = ""

key_manager = None
certificate_exp_start = 0
certificate_exp_end = 30*24*60*60
module = None
a_func = None

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

def generate_ca_certificate(certfilepath, keyfilepath, start_time, end_time):
    '''
    Generate a CA certificate and key for the CA.
    Args:
        certfilepath (String) - where the CA certificate will be stored
        keyfilepath (String) - where the keyfile will be stored
    
    This function generates a key and matching certificate and 
    writes it to the files specified.
    '''
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

    ca = OpenSSL.crypto.X509()
    ca.set_version(3)
    ca.set_serial_number(1)
    ca.get_subject().CN = "Certficate manager"
    if start_time is None:
        start_time = 0
    ca.gmtime_adj_notBefore(start_time)
    if end_time is None:
        end_time = 365 * 24 * 60 * 60
    else:
        end_time += start_time
    ca.gmtime_adj_notAfter(end_time)
    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(key)
    ca.add_extensions([
      OpenSSL.crypto.X509Extension("basicConstraints", True,
                                   "CA:TRUE, pathlen:0"),
      OpenSSL.crypto.X509Extension("keyUsage", True,
                                   "keyCertSign, cRLSign"),
      OpenSSL.crypto.X509Extension("subjectKeyIdentifier", False, "hash",
                                   subject=ca),
      ])
    ca.sign(key, "sha1")

    global ca_cert
    ca_cert=ca
    global ca_key
    ca_key=key
    f = open(certfilepath, "w")
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert))
    f.close()
    f = open(keyfilepath, "w")
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key))
    f.close()

def load_ca_certificate(certfilepath, keyfilepath):
    '''
    Args:
        certfilepath (String) - where the certfile is stored
        keyfilepath (String) - where the keyfile is stored

    This function just loads a stored certificate and key and puts them in global variables
    '''
    global ca_cert
    ca_cert=crypto.load_certificate(crypto.FILETYPE_PEM,open(certfilepath).read())
    global ca_key
    ca_key=crypto.load_privatekey(crypto.FILETYPE_PEM,open(keyfilepath).read())

def dump_cert(Endpoint):
    '''
    This function returns the CA certificate in text form
    '''
  
    global ca_cert
    return crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert)

def start_ca(generate=False, certfile="cacertificate.pem", keyfile="cakey.pem", host=None, port=None, ca_start_time=None, ca_end_time=None, cert_start=None, cert_end=None, authentication_function=None):
    '''
    Args:
        generate (boolean) - Tells it where to generate a certificate or not
        certfile (String) - where the CA certificate is or will be stored
        keyfile (String) - where the keyfile is or will be stored
        host (String) - hostname of the CA
        port (int) - port of the CA

    Call this function to start a CA. You can specify it to generate a certificate or use a preloaded one

    '''
    if cert_start is None:
        cert_start = 0
    if cert_end is None:
        cert_end = cert_start + (30*24*60*60)
    else:
        cert_end += cert_start


    if generate is True:
        generate_ca_certificate(certfile, keyfile, start_time, end_time)
    else:
        load_ca_certificate(certfile, keyfile)
    if host is not None:
        set_hostname(host)
    if port is not None:
        set_port(port)
    global key_manager
    global MANAGER_HOST
    global MANAGER_PORT

    if authentication_function is None:
        authentication_function = lambda text: True
    key_manager = Waldo.stcp_accept(
        Manager, MANAGER_HOST, MANAGER_PORT, generate_cert_from_request, dump_cert, cert_start, cert_end, authentication_function)


def turn_off_ca():
    '''
    Call this to have the CA stop running
    '''
    global key_manager
    key_manager.stop()


def make_temp():
    '''
    Makes a temporary directory if it doesn't exist already
    '''
    filename = "./tmp/"
    temp = os.path.dirname(filename)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

def generate_cert_from_request(Endpoint, req, start, end, auth_func):
    '''
    Args:
        Endpoint - this is to be used in conjunction with a Waldo file
        req (crypto.X509Request) - this is a certificate request object that will be be turned into a certificate
    Pass in a request and it will be turned into a certificate
    '''

    global ca_cert
    global ca_key
 
    if auth_func(req.get_subject().commonName()) == False:
        return None
    req = crypto.load_certificate_request(crypto.FILETYPE_PEM,req)
    cert = crypto.X509()
    cert.set_subject(req.get_subject())
    cert.set_serial_number(1000)

    cert.gmtime_adj_notBefore(start)
    cert.gmtime_adj_notAfter(end)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(ca_key, "sha1")

    cert = crypto.dump_certificate(crypto.FILETYPE_PEM,cert)
    return cert


