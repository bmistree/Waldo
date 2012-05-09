#!/usr/bin/python

# from pingPong import Ping;
# from pingPong import Pong;

from pingPong import Ping;
from pingPong import Pong;
import time;
from connectionObject import LocalEndpointsConnection;





if __name__ == '__main__':
    conn = LocalEndpointsConnection();
    ping = Ping(conn);
    pong = Pong(conn);

    ping.initiateSend();
    ping.initiateSend();
    ping.initiateSend();
    ping.initiateSend();
                
    

