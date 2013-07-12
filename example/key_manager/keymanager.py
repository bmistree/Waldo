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
MANAGER_PORT = 6974

ca_cert=None
ca_key=None

def generate_ca_certificate():
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

    ca = OpenSSL.crypto.X509()
    ca.set_version(3)
    ca.set_serial_number(1)
    ca.get_subject().CN = "certficate manager"
    ca.gmtime_adj_notBefore(0)
    ca.gmtime_adj_notAfter(24 * 60 * 60)
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
    ca.sign(key, "sha256")

    global ca_cert
    ca_cert=ca
    print(type(ca_cert))
    global ca_key
    ca_key=key

def sign_cert(Endpoint, C, ST, L, O, OU, CN, key):
    cert = crypto.X509()
    cert.get_subject().C = C
    cert.get_subject().ST = ST
    cert.get_subject().L = L
    cert.get_subject().O = O
    cert.get_subject().OU = OU
    cert.get_subject().CN = CN
    cert.set_serial_number()
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(24 * 60 * 60)
    global ca_cert
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(ca_key, "sha256")
    return cert

def generate_request(Endpoint, C, ST, L, O, OU, CN, key):
    f = open('temp.pem', 'w+')
    f.write(key)
    f.close()
    key = crypto.load
    req = OpenSSL.crypto.X509Req()
    req.get_subject().C = C
    req.get_subject().ST = ST
    req.get_subject().L = L
    req.get_subject().O = O
    req.get_subject().OU = OU
    req.get_subject().CN = CN
    req.set_pubkey(key)
    req.sign(key, "sha256")

    return req

def generate_cert_from_request(Endpoint, req):
    f = open('temp.pem', 'w+')
    f.write(req)
    f.close()
    global ca_cert
    global ca_key
    print(type(ca_cert))
    req = crypto.load_certificate_request(crypto.FILETYPE_PEM,open('temp.pem').read())
    cert = crypto.X509()
    cert.set_subject(req.get_subject())
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(24 * 60 * 60)
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(ca_key, "sha256")

    cert = crypto.dump_certificate(crypto.FILETYPE_PEM,cert)
    return cert

def verify_cert(Endpoint,cert):

    c=OpenSSL.crypto

    cacert=ca_cert
     
    # Get the signing algorithm
    algo=cert.get_signature_algorithm()
     
    # Get the ASN1 format of the certificate
    cert_asn1=c.dump_certificate(c.FILETYPE_ASN1, cert)
     
    # Decode the certificate
    der=asn1.DerSequence()
    der.decode(cert_asn1)
     
    # The certificate has three parts:
    # - certificate
    # - signature algorithm
    # - signature
    # http://usefulfor.com/nothing/2009/06/10/x509-certificate-basics/
    der_cert=der[0]
    der_algo=der[1]
    der_sig=der[2]
     
    # The signature is a BIT STRING (Type 3)
    # Decode that as well
    der_sig_in=asn1.DerObject()
    der_sig_in.decode(der_sig)
     
    # Get the payload
    sig0=der_sig_in.payload
     
    # Do the following to see a validation error for tests
    # der_cert=der_cert[:20]+'1'+der_cert[21:]
     
    # First byte is the number of unused bits. This should be 0
    # http://msdn.microsoft.com/en-us/library/windows/desktop/bb540792(v=vs.85).aspx
    if sig0[0]!='\x00':
        raise Exception('Number of unused bits is strange')
     
    # Now get the signature itself
    sig=sig0[1:]
     
    # And verify the certificate
    try:
        c.verify(cacert, sig, der_cert, algo)
        print "Certificate looks good"
    except OpenSSL.crypto.Error, e:
        print "Sorry. Nope."

def get_key(Endpoint):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA,2048)
    keytext = crypto.dump_privatekey(crypto.FILETYPE_PEM,key)

    return keytext

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

generate_ca_certificate()
key_manager = Waldo.stcp_accept(
        Manager, MANAGER_HOST, MANAGER_PORT, generate_cert_from_request, cert="certificate.pem", key="key.pem")

while True:
    pass

