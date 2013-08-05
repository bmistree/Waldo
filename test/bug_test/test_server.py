from test_waldo_emitted import UserTestHelper
from optparse import OptionParser
import sys, os, time
sys.path.append(os.path.join("../../"))
import OpenSSL
from waldo.lib import Waldo
HOSTNAME = '127.0.0.1'
PORT = 6922
KEY_MANAGER_HOST = '127.0.0.1'
KEY_MANAGER_PORT = 6974


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-g", "--generate", action ="store_true", dest = "generate", default = False)
    (option, args) = parser.parse_args()
    Waldo.start_ca(option.generate, host = KEY_MANAGER_HOST, port = KEY_MANAGER_PORT, cert_end = 60*60*24*365)
    if option.generate:
        Waldo.add_ca_to_list("ca_list.pem", KEY_MANAGER_HOST, KEY_MANAGER_PORT)
    Waldo.stcp_accept(UserTestHelper, HOSTNAME, PORT, Waldo.get_ca_endpoint(KEY_MANAGER_HOST, KEY_MANAGER_PORT))
    while raw_input() != "close": 
        pass
