#!/usr/bin/env python

from connectionObject import ConnectionObject
import threading;
import time;


class SimulatedDelay(threading.Thread):
    def __init__(self,timeInSeconds,connection,toWrite,senderEndpoint):
        '''
        @param {Float} timeInSeconds -- Amount of time to sleep before
        delivering message.

        @param {LocalEndpointsConnection} connection
        
        @param {dict} toWrite @see writeMsg function of abstract
        ConnectionObject class.
        
        @param {_Endpoint object} senderEndpoint @see writeMsg
        function of abstract ConnectionObject class.
        '''        
        self.timeInSeconds = timeInSeconds;
        self.connection = connection;
        self.toWrite = toWrite;
        self.senderEndpoint = senderEndpoint;
	threading.Thread.__init__(self)

    def run(self):
        time.sleep(self.timeInSeconds);
        self.connection._actuallyWriteMsg(self.toWrite,self.senderEndpoint);
        

class LocalConnectionObject(ConnectionObject):
    '''
    Will be used between Endpoints on the same machine for testing.
    '''
    
    # in seconds
    # SIM_HOW_LONG_TO_DELAY = .5;
    SIM_HOW_LONG_TO_DELAY = .005;
    
    def __init__(self):
        print('\nBehram error: probably should have some locks around somewhere\n');
        self.endpoint1 = None;
        self.endpoint2 = None;

        
    def addEndpoint(self,endpoint):
        if (self.endpoint1 == None):
            self.endpoint1 = endpoint;
            return;

        if (self.endpoint2 == None):
            self.endpoint2 = endpoint;
            return;

        errMsg = '\nBehram error: trying to add a third endpoint to a ';
        errMsg += 'connnection in LocalEndpointsConnection.\n';
        print(errMsg);
        assert(False);

    def ready (self):
        return ((self.endpoint1 != None) and (self.endpoint2 != None));
            
    def writeMsg(self,dictToWrite,senderEndpoint):
        if (not self.ready()):
            errMsg = '\nBehram error: trying to write a message when not ';
            errMsg += 'ready in LocalEndpointsConnection.\n';
            print(errMsg);
            assert(False);

        #queues the message to be sent after a SIM_HOW_LONG_TO_DELAY (s) delay.
        waitAndDeliver = SimulatedDelay(
            self.SIM_HOW_LONG_TO_DELAY,self,dictToWrite,senderEndpoint);

        waitAndDeliver.start();
        
    def _actuallyWriteMsg(self,dictToWrite,senderEndpoint):
        '''
        Gets called after a timer expires from SimulatedDelay class.
        @see writeMsg class for argument descriptions and types.
        '''
        if senderEndpoint == self.endpoint1:
            self.endpoint2._msgReceive(dictToWrite);
        elif senderEndpoint == self.endpoint2:
            self.endpoint1._msgReceive(dictToWrite);
        else:
            errMsg = '\nBehram error in _actuallyWriteMsg of ';
            errMsg += 'LocalEndpointsConnection.  Have unknown ';
            errMsg += 'sender.\n';
            print(errMsg);
            assert(False);

