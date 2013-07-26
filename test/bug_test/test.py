from test_waldo_emitted import Test
import ssl, sys, os
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo

KEY_MANAGER_HOST = '127.0.0.1'
KEY_MANAGER_PORT = 6974


Waldo.start_ca(False, host = KEY_MANAGER_HOST, port = KEY_MANAGER_PORT, cert_end = 60*60*24*365)
CA = Waldo.get_ca_endpoint(KEY_MANAGER_HOST, KEY_MANAGER_PORT)
tester = Waldo.no_partner_create(Test, CA)
print(tester.print_cert(Waldo.generate_request("edric", Waldo.get_key())))
