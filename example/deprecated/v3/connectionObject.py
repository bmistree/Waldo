#!/usr/bin/python

import threading;
import time;

#in seconds
SIM_HOW_LONG_TO_DELAY = .5;

class ConnectionObject():
    '''
    Abstract class for the connection between two Waldo endpoints.
    '''
    
    def writeMsg(self,dictToWrite,endpointObj):
        '''
        @param {dictionary} dictToWrite -- The actual message want to
        send from one endpoint to the other

        @param {_Endpoint object} endpointObj --- Only used to
        identify who the writer is and who the receiver is.
        '''
        errMsg = '\nBehram error: making pure virtual call to writeMsg ';
        errMsg += 'of ConnectionObject.\n';
        print(errMsg);
        assert(False);

    def addEndpoint(self,endpoint):
        '''
        @param {Endpoint} -- One of the endpoints.
        '''
        errMsg = '\nBehram error: making pure virtual call to addEndpoint ';
        errMsg += 'of ConnectionObject.\n';
        print(errMsg);
        assert(False);

    def ready (self):
        '''
        @returns {Bool} True if ready to send and receive data, false
        otherwise.
        '''
        errMsg = '\nBehram error: making pure virtual call to ready ';
        errMsg += 'of ConnectionObject.\n';
        print(errMsg);
        assert(False);


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
        

class LocalEndpointsConnection(ConnectionObject):
    '''
    Will be used between Endpoints on the same machine for testing.
    '''
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
        waitAndDeliver = SimulatedDelay(SIM_HOW_LONG_TO_DELAY,self,dictToWrite,senderEndpoint);
        # waitAndDeliver.start(SIM_HOW_LONG_TO_DELAY,self,dictToWrite,msgSenderName);
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

