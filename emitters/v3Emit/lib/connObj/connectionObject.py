#!/usr/bin/python


class ConnectionObject(object):
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

