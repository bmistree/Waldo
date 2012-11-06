#!/usr/bin/env python

from tb import Ping;
from tb import Pong;
import threading;
from connectionObject import LocalEndpointsConnection;


# class DummyConnectionObject(object):

#     def addEndpoint(self,endpoint):
#         pass;
#     def writeMsg(self,msg):
#         pass;


class IncPing(threading.Thread):

    def __init__(self,pingObj):
        self.pingObj = pingObj;
        threading.Thread.__init__(self);
        

    def run(self):
        self.pingObj.incPing();
        print('Finished!');
        


def run():
    # dummy connection object for now.
    connectionObject = LocalEndpointsConnection();
    
    ping = Ping(connectionObject);
    pong = Pong(connectionObject);
    
    value = ping.incPing();

    ip1 = IncPing(ping);
    ip1.start();
    
    ip2 = IncPing(ping);
    ip2.start();

    val = ping.incOtherPing();
    print('other got: ' + str(val));
    val = ping.incOtherPing();
    print('other got: ' + str(val));

    val = ping.incOtherPing();
    print('other got: ' + str(val));

    ip1.join();
    ip2.join();


def run2():
    # dummy connection object for now.
    connectionObject = LocalEndpointsConnection();
    
    ping = Ping(connectionObject);
    pong = Pong(connectionObject);

    value = ping.msgSeq();
    print('\n\n');
    print(value);
    print('\n\n');
    
    # value = ping.incPing();

    # ip1 = IncPing(ping);
    # ip1.start();
    
    # ip2 = IncPing(ping);
    # ip2.start();

    # val = ping.incOtherPing();
    # print('other got: ' + str(val));
    # val = ping.incOtherPing();
    # print('other got: ' + str(val));

    # val = ping.incOtherPing();
    # print('other got: ' + str(val));

    # ip1.join();
    # ip2.join();

    


if __name__ == '__main__':
    # run();
    run2();
