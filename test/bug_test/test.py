from test_waldo_emitted import UserTest
import sys, os, time
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
import OpenSSL
HOSTNAME = '127.0.0.1'
PORT = 6922

if __name__ == '__main__':
    user_login = Waldo.stcp_connect(UserTest, HOSTNAME, PORT)
    user_login.register_user(Waldo.generate_request("edric", Waldo.get_key()))
