#!/usr/bin/python


#EXACT
import threading;
    
INTERMEDIATE_CONTEXT = 0;
COMMITTED_CONTEXT = 1;

# When last message fires, it sends a message back to other endpoint.
# This message is used to synchronize shared variables between two
# endpoints.  Gets passed in dispatchTo field of received messages.
STREAM_TAIL_SENTINEL = 'None';

def DEBUG(className,msg):
    toPrint = className + ':    ' + msg;
    print('\n');
    print(toPrint);
    print('\n');

'''
On wire json-ized message format.

Only data delivered to actual message receipt function should be in
data.

msg:
{

    iInitiated: <True if sender of message was initiator of message
    stream, False otherwise>,
    
    environmentData: {dictionary} a dictionary of shared variables
    indexed by name of the shared variable.
    
    data: msg arguments (dictionary);
    
    dispatchTo: {String} should be function name on opposite end of
    what to do with

};
'''



class _MessageSendQueueElement():
    '''
    EXACT -- may want to rename to prevent conflicts with
    endpoint...eg, use underscore prefix.
    
    _MessageSendQueueElements store calls that could not be processed
    because we were already in a trace, or that were reverted because
    two messages collided.
    '''

    def __init__ (self,sendFuncName, argsArray):
        '''
        @param {String} sendFuncName -- An identifier to use to
        distinguish which message send function was queued.

        @param {Array} argsArray -- All arguments that were passed
        into the function (excluding self).
        '''
        self.sendFuncName = sendFuncName;
        self.argsArray = argsArray;







class _PingContext():
    '''
    NOT EXACT
    '''
    def __init__(self,myPriority,theirPriority):
        self.pingCounter = 0;
        self.pongCounter = 0;

        self.responses = 0;

        # In cases where to sides simultaneously send, indicates which
        # side should send first (the one with the greater priority).
        self._myPriority = myPriority;
        self._theirPriority = theirPriority;

        
    def copy(self):
        returner = _PingContext(self._myPriority,self._theirPriority);
        
        #note, may need to perform deep copies of these as well.
        returner.pingCounter = self.pingCounter;
        returner.pongCounter = self.pongCounter;
        returner.responses = self.responses;

        returner._myPriority = self._myPriority;
        returner._theirPriority = self._theirPriority;
        
        return returner;

    def generateEnvironmentData(self):
        '''
        NOT EXACT
        
        Should take all the shared variables and write them to a
        dictionary.  The context of the other endpoint should be able
        to take this dictionary and re-constitute the global variables
        from it from its updateEnvironmentData function.
        '''
        returner = {};

        returner['pingCounter'] = self.pingCounter;
        returner['pongCounter'] = self.pongCounter; 

        return returner;

    def updateEnvironmentData(self,sharedVarDict):
        '''
        EXACT
        
        @param {dict} sharedVarDict -- Keys of dictionary are names of
        global variables.  Values are the actual values of the
        associated global variables.
        '''

        # run through shared variables dictionary and update all
        # shared variables held by this context to those provided in
        # sharedVarDict.  (A lot of these clumsy eval forms stem from
        # wanting to make the code emitter of the compiler as easy to
        # write as possible.)
        for s in sharedVarDict.keys():
            toExecSetSharedStr = 'self.%s = sharedVarDict["%s"];' % (s,s);
            obj = compile(toExecSetSharedStr,'','exec');
            eval(obj);


class _PongContext():
    '''
    NOT EXACT
    '''
    def __init__(self,myPriority,theirPriority):
        self.pingCounter = 0;
        self.pongCounter = 0;

        self.responses = 0;

        # In cases where to sides simultaneously send, indicates which
        # side should send first (the one with the greater priority).
        self._myPriority = myPriority;
        self._theirPriority = theirPriority;

        
    def copy(self):
        returner = _PongContext(self._myPriority,self._theirPriority);
        
        #note, may need to perform deep copies of these as well.
        returner.pingCounter = self.pingCounter;
        returner.pongCounter = self.pongCounter;
        returner.responses = self.responses;

        returner._myPriority = self._myPriority;
        returner._theirPriority = self._theirPriority;
        
        return returner;

    def generateEnvironmentData(self):
        '''
        NOT EXACT
        
        Should take all the shared variables and write them to a
        dictionary.  The context of the other endpoint should be able
        to take this dictionary and re-constitute the global variables
        from it from its updateEnvironmentData function.
        '''
        returner = {};

        returner['pingCounter'] = self.pingCounter;
        returner['pongCounter'] = self.pongCounter; 

        return returner;

    def updateEnvironmentData(self,sharedVarDict):
        '''
        EXACT
        
        @param {dict} sharedVarDict -- Keys of dictionary are names of
        global variables.  Values are the actual values of the
        associated global variables.
        '''

        # run through shared variables dictionary and update all
        # shared variables held by this context to those provided in
        # sharedVarDict.  (A lot of these clumsy eval forms stem from
        # wanting to make the code emitter of the compiler as easy to
        # write as possible.)
        for s in sharedVarDict.keys():
            toExecSetSharedStr = 'self.%s = sharedVarDict["%s"];' % (s,s);
            obj = compile(toExecSetSharedStr,'','exec');
            eval(obj);

            

        

class Ping():

    def __init__(self,connectionObject):
        '''
        EXACT, except for initialization stuff.  maybe think about
        that later.
        '''
        errMsg = '\nBehram FIXME: ignoring initial connection handshake ';
        errMsg += 'in favor of passing in a pre-existing connection.\n';
        print(errMsg);


        self.committed = _PingContext(1,0);
        self.intermediate = self.committed.copy();
        self.whichEnv = COMMITTED_CONTEXT;

        #should use different names for each endpoint
        self.name = 'some name'; #will actually be a string created from a random float.
        
        #lkjs may actually want to use underscores for all of these variables;        

        #for synchronization: lkjs: unclear if want recursive or
        #non-recursive here
        self.mutex = threading.RLock();
        

        ########## trace management code ########
        
        self.amInTrace = False;
        self.msgSendQueue = [];

        # must store details about the last outstanding send function
        # to handle cases where both I and the other side try to send
        # simultaneously.  (In these cases, one side will revert its
        # send.  It should then prepend the send it was performing to
        # the front of the msgSendQueue.
        self.outstandingSend = None;

        self.connectionObject = connectionObject;
        self.connectionObject.addEndpoint(self);


    def ready (self):
        #EXACT
        return self.connectionObject.ready();
        
    def _lock(self):
        #EXACT
        self.mutex.acquire();

    def _unlock(self):
        #EXACT
        self.mutex.release();
        
        
    def initiateSend(self):
        '''
        NOT EXACT
        
        Corresponds to public function specified in .wld file.
        '''

        DEBUG('ping', 'Got into initiateSend');

        
        # take lock on all points of entry
        self._lock(); 

        # any public function works from committed, not intermediate
        # data.
        self.whichEnv = COMMITTED_CONTEXT;


        '''
        user-specified code 
        '''
        self._msgSendOne();


        # any function that takes a lock should remember to unlock.
        self._unlock();




    def _sendMsg (self,msg,funcNameFrom):
        '''
        @param {dictionary} msg -- The data payload (should not
        include shared variables.  This function adds a separate field
        to the message for shared variable payload.

        @param {String} funcNameFrom -- The name of the function that
        called _sendMsg.  (Examples: _msgSendOne, _msgReceiveTwo,
        etc.)  This is used to determine the 'dispatchTo' field for
        the other endpoint to determine what to do with the message.

        
        NOT EXACT -- Highlighted the section of code that can't be
        exactly copied.  It has to do with specifying the function to
        dispatch to on the other side.
        '''

        DEBUG('ping', 'Actually sending message');
        # actual json-izable dict we will be sending to the other side
        msgToSend = {};

        iInitiated = True;
        if (self.outstandingSend == None):
            iInitiated = False;

        # keep track of who initiator of message stream was to handle
        # case of simultaneous stream start
        msgToSend['iInitiated'] = iInitiated;

        msgToSend['environmentData'] = self.intermediate.generateEnvironmentData();


        '''
        NOT EXACT PART: determine dispatchTo field based on what on
        this endpoint called this function.
        '''
        dispatchTo = None;
        if (funcNameFrom == '_msgSendOne'):
            dispatchTo = '_msgRecvTwo';
        elif(funcNameFrom == '_msgRecvThree'):
            dispatchTo = '_msgRecvFour';
        else:
            errMsg = '\nBehram Error.  Provided an invalid funcNameFrom argument.\n';
            print(errMsg);
            assert(False);

        '''
        END NOT EXACT PART
        '''

        msgToSend['data'] = msg;
        msgToSend['dispatchTo'] = dispatchTo;
        self.connectionObject.writeMsg(msgToSend,self.name);


    def _msgReceive(self,msg):
        '''
        EXACT
        
        called whenever receive message from other side.  performs
        dispatch, sending message to appropriate receiving function
        '''

        DEBUG('ping', 'Received a message');
        #thread safety
        self._lock();
        
        #check case for simultaneous open
        if (msg['iInitiated'] and self.outstandingSend != None):
            #means that we had a case of simultaneous open

            #endpoint with higher priority always wins
            if (self.committed._myPriority < self.committed._theirPriority):
                #we must back off our send, inserting outstanding back
                #into message queue.
                
                self._reset(); #flash the intermediate context back to committed
                self.msgSendQueue.insert(0,self.outstandingSend);
                self.outstandingSend = None;
                self._unlock();
                return;

            
        # update shared environment data in intermediate
        self.intermediate.updateEnvironmentData(msg['environmentData']);



        if (msg['dispatchTo'] == STREAM_TAIL_SENTINEL):
            # means that there is nothing to dispatch to on our side.
            # (ie, the other side performed the last operation
            # specified on the trace line.)  Send an empty dispatchTo
            # message to ensure that the shared variables get updated
            # correctly.

            # commit all outstanding changes to shared variables and
            # return after unlocking.  (Note: _commit also sets
            # self.amInTrace and self.outstandingSend for us.)
            self._commit();
            self._unlock();
            return;


        #choose who to dispatch received message to;
        dispatchSrcStr = 'self.%s (' % msg['dispatchTo'];
        dispatchSrcStr += 'msg["data"]);';

        #actually evaluate the receive message function
        obj = compile(dispatchSrcStr,'','exec');
        eval(obj);

        #thread safety
        self._unlock();


    def _msgSendOne(self):
        '''
        Corresponds to MsgSend function in pingPong.wld.
        '''

        DEBUG('ping', 'msgSend command');
        
        # means that we are already processing a trace stream.
        # schedule this for another time
        if (self.amInTrace):
            queueElementName = '_msgSendOne';
            queueElementArgs = []; # no args beyond self were passed into the send function.
            queueElement = _MessageSendQueueElement(queueElementName,queueElementArgs);

            self.msgSendQueue.append(queueElement);
            return;

        # blocks further send messages from executing
        self.amInTrace = True;

        #stores intermediate send function
        self.outstandingSend = _MessageSendQueueElement('_msgSendOne',[]);

        #sets environment for further calls
        self.whichEnv = INTERMEDIATE_CONTEXT;

        # I know it is stupid to do this check in a msgSend,
        # msgReceive, or Public function.  However, it will
        # be necessary in an internal function, and I would
        # prefer to have identical code paths/emissions to
        # start with.  Later, I can get rid of it in the
        # msgSend, msgRecv, and Public functions.
        if (self.whichEnv == INTERMEDIATE_CONTEXT):
            self.intermediate.pingCounter += 1;
            # construct data message
            msg = {};
            msg['responses'] = self.intermediate.responses;

            # actually send the message;
            self._sendMsg (msg,'_msgSendOne');

        else:
            self.committed.pingCounter += 1;
            # construct data message
            msg = {};
            msg['responses'] = self.committed.responses;            

            # actually send the message;
            self._sendMsg (msg,'_msgSendOne');
        


    def _msgRecvThree(self,msg):
        '''
        NOT EXACT
        '''
        DEBUG('ping', 'msgRecvThree');
        self.whichEnv = INTERMEDIATE_CONTEXT;

        if (self.whichEnv == INTERMEDIATE_CONTEXT):
            self.intermediate.pingCounter += 1;
            self.intermediate.responses += 1;

            msgResponse = {};
            msgResponse['responses'] = self.intermediate.responses;

            # actually send the message;
            self._sendMsg (msg,'_msgRecvThree');
            
        else:
            self.committed.pingCounter += 1;
            self.committed.responses += 1;
            
            msgResponse = {};
            msgResponse['responses'] = self.committed.responses;
            
            # actually send the message;
            self._sendMsg (msg,'_msgRecvThree');
            


    def _reset (self):
        '''
        EXACT

        Remove any changes made to intermediate.
        '''
        self.intermediate = self.commmited.copy();

        
        
    def _commit(self):
        '''
        EXACT

        All the changes that have been made to intermediate throughout
        the course of a message's being sent should be committed to
        self.committed.
        '''
        
        # expensive deep copy of full environment.  eventually,
        # may use deltas or some other strategy.

        self.committed = self.intermediate.copy();
        self.amInTrace = False;

        self.outstandingSend = None;

        # check if there's a queued function to send from one side to
        # other.
        self._trySendNext();


        

    def _trySendNext(self):
        '''
        EXACT
        
        Checks if there is an outstanding message in the queue to send.
        
        Should only be called from _commit, (ie after know that
        previously executing trace is done).
        '''
        if (self.outstandingSend != None):
            errMsg = '\nBehram error in _trySendNext of Ping.  ';
            errMsg += 'Should not have an outstanding message.\n';
            print(errMsg);
            assert(False);
            

        if (self.amInTrace == True):
            errMsg = '\nBehram error in _trySendNext of Ping.  ';
            errMsg += 'Should not already be in trace.\n';
            print(errMsg);
            assert(False);


        if (len(self.msgSendQueue) == 0):
            #no work to do.
            return;

        
        # means that we have to remove from front of queue and try to
        # execute a queued message send
        self.outstandingSend = self.msgSendQueue[0];
        self.msgSendQueue = self.msgSendQueue[1:];
     

        # re-perform send action
        funcName = self.outstandingSend.sendFuncName;
        args = self.outstandingSend.argsArray;

        
        # string to eval to replay send action
        commandString = 'self.%s (' % funcName;

        # pass args to function
        for s in range(0,len(args)):
            commandString += 'args[' + str(s) + ']';
            if (s != len(args) -1):
                commandString += ',';
                    
        commandString += ');'

        #actually re-exec function
        obj = compile(src,'','exec');
        eval(obj);
        
        
        









#############################PONG DEFINITION#######################
        

class Pong():

    def __init__(self,connectionObject):
        '''
        EXACT, except for initialization stuff.  maybe think about
        that later.
        '''
        errMsg = '\nBehram FIXME: ignoring initial connection handshake ';
        errMsg += 'in favor of passing in a pre-existing connection.\n';
        print(errMsg);


        self.committed = _PongContext(0,1);
        self.intermediate = self.committed.copy();
        self.whichEnv = COMMITTED_CONTEXT;

        #should use different names for each endpoint
        self.name = 'some name2'; #will actually be a string created from a random float.
        
        #lkjs may actually want to use underscores for all of these variables;        

        #for synchronization: lkjs: unclear if want recursive or
        #non-recursive here
        self.mutex = threading.RLock();
        

        ########## trace management code ########
        
        self.amInTrace = False;
        self.msgSendQueue = [];

        # must store details about the last outstanding send function
        # to handle cases where both I and the other side try to send
        # simultaneously.  (In these cases, one side will revert its
        # send.  It should then prepend the send it was performing to
        # the front of the msgSendQueue.
        self.outstandingSend = None;

        self.connectionObject = connectionObject;
        self.connectionObject.addEndpoint(self);


    def ready (self):
        #EXACT
        return self.connectionObject.ready();
        
    def _lock(self):
        #EXACT
        self.mutex.acquire();

    def _unlock(self):
        #EXACT
        self.mutex.release();
        

    def _sendMsg (self,msg,funcNameFrom):
        '''
        @param {dictionary} msg -- The data payload (should not
        include shared variables.  This function adds a separate field
        to the message for shared variable payload.

        @param {String} funcNameFrom -- The name of the function that
        called _sendMsg.  (Examples: _msgSendOne, _msgReceiveTwo,
        etc.)  This is used to determine the 'dispatchTo' field for
        the other endpoint to determine what to do with the message.

        
        NOT EXACT -- Highlighted the section of code that can't be
        exactly copied.  It has to do with specifying the function to
        dispatch to on the other side.
        '''

        DEBUG('pong', 'sendingMsg');
        # actual json-izable dict we will be sending to the other side
        msgToSend = {};

        iInitiated = True;
        if (self.outstandingSend == None):
            iInitiated = False;

        # keep track of who initiator of message stream was to handle
        # case of simultaneous stream start
        msgToSend['iInitiated'] = iInitiated;

        msgToSend['environmentData'] = self.intermediate.generateEnvironmentData();


        '''
        NOT EXACT PART: determine dispatchTo field based on what on
        this endpoint called this function.
        '''
        dispatchTo = None;
        if (funcNameFrom == '_msgRecvTwo'):
            dispatchTo = '_msgRecvThree';
        elif(funcNameFrom == '_msgRecvFour'):
            dispatchTo = STREAM_TAIL_SENTINEL;
        else:
            errMsg = '\nBehram Error.  Provided an invalid ';
            errMsg += 'funcNameFrom argument in Pong.\n';
            print(errMsg);
            assert(False);
            
        '''
        END NOT EXACT PART
        '''

        msgToSend['data'] = msg;
        msgToSend['dispatchTo'] = dispatchTo;
        self.connectionObject.writeMsg(msgToSend,self.name);
        

    def _msgReceive(self,msg):
        '''
        EXACT
        
        called whenever receive message from other side.  performs
        dispatch, sending message to appropriate receiving function
        '''
        DEBUG('pong', 'actually receiving message');        
        #thread safety
        self._lock();
        
        #check case for simultaneous open
        if (msg['iInitiated'] and self.outstandingSend != None):
            #means that we had a case of simultaneous open

            #endpoint with higher priority always wins
            if (self.committed._myPriority < self.committed._theirPriority):
                #we must back off our send, inserting outstanding back
                #into message queue.
                
                self._reset(); #flash the intermediate context back to committed
                self.msgSendQueue.insert(0,self.outstandingSend);
                self.outstandingSend = None;
                return;

            
        # update shared environment data in intermediate
        self.intermediate.updateEnvironmentData(msg['environmentData']);
        


        if (msg['dispatchTo'] == STREAM_TAIL_SENTINEL):
            # means that there is nothing to dispatch to on our side.
            # (ie, the other side performed the last operation
            # specified on the trace line.)  Send an empty dispatchTo
            # message to ensure that the shared variables get updated
            # correctly.

            # commit all outstanding changes to shared variables and
            # return after unlocking.  (Note: _commit also sets
            # self.amInTrace and self.outstandingSend for us.)
            self._commit();
            self._unlock();
            return;


        #choose who to dispatch received message to;
        dispatchSrcStr = 'self.%s (' % msg['dispatchTo'];
        dispatchSrcStr += 'msg["data"]);';

        #actually evaluate the receive message function
        obj = compile(dispatchSrcStr,'','exec');
        eval(obj);

        #thread safety
        self._unlock();


    def _msgRecvTwo(self,msg):
        '''
        NOT EXACT
        '''
        DEBUG('pong', 'msgRecvTwo');                
        self.whichEnv = INTERMEDIATE_CONTEXT;

        if (self.whichEnv == INTERMEDIATE_CONTEXT):
            self.intermediate.pongCounter += 1;
            self.intermediate.responses += 1;

            msgResponse = {};
            msgResponse['responses'] = self.intermediate.responses;

            # actually send the message;
            self._sendMsg (msg,'_msgRecvTwo');
            
        else:
            self.committed.pongCounter += 1;
            self.committed.responses += 1;
            
            msgResponse = {};
            msgResponse['responses'] = self.committed.responses;
            
            # actually send the message;
            self._sendMsg (msg,'_msgRecvTwo');
            


    def _msgRecvFour(self,msg):
        '''
        NOT EXACT
        '''
        DEBUG('pong', 'msgRecvFour');                        
        self.whichEnv = INTERMEDIATE_CONTEXT;

        if (self.whichEnv == INTERMEDIATE_CONTEXT):
            self.intermediate.pongCounter += 1;
            self.intermediate.responses += 1;

            msgResponse = {};
            msgResponse['responses'] = self.intermediate.responses;

            # actually send the message;
            self._sendMsg (msg,'_msgRecvFour');
            
        else:
            self.committed.pongCounter += 1;
            self.committed.responses += 1;
            
            msgResponse = {};
            msgResponse['responses'] = self.committed.responses;
            
            # actually send the message;
            self._sendMsg (msg,'_msgRecvFour');
            

            

    def _reset (self):
        '''
        EXACT

        Remove any changes made to intermediate.
        '''
        self.intermediate = self.commmited.copy();

        
        
    def _commit(self):
        '''
        EXACT

        All the changes that have been made to intermediate throughout
        the course of a message's being sent should be committed to
        self.committed.
        '''
        
        # expensive deep copy of full environment.  eventually,
        # may use deltas or some other strategy.

        self.committed = self.intermediate.copy();
        self.amInTrace = False;

        self.outstandingSend = None;

        # check if there's a queued function to send from one side to
        # other.
        self._trySendNext();


        

    def _trySendNext(self):
        '''
        EXACT
        
        Checks if there is an outstanding message in the queue to send.
        
        Should only be called from _commit, (ie after know that
        previously executing trace is done).
        '''
        if (self.outstandingSend != None):
            errMsg = '\nBehram error in _trySendNext of Pong.  ';
            errMsg += 'Should not have an outstanding message.\n';
            print(errMsg);
            assert(False);
            

        if (self.amInTrace == True):
            errMsg = '\nBehram error in _trySendNext of Pong.  ';
            errMsg += 'Should not already be in trace.\n';
            print(errMsg);
            assert(False);


        if (len(self.msgSendQueue) == 0):
            #no work to do.
            return;

        
        # means that we have to remove from front of queue and try to
        # execute a queued message send
        self.outstandingSend = self.msgSendQueue[0];
        self.msgSendQueue = self.msgSendQueue[1:];
     

        # re-perform send action
        funcName = self.outstandingSend.sendFuncName;
        args = self.outstandingSend.argsArray;

        
        # string to eval to replay send action
        commandString = 'self.%s (' % funcName;

        # pass args to function
        for s in range(0,len(args)):
            commandString += 'args[' + str(s) + ']';
            if (s != len(args) -1):
                commandString += ',';
                    
        commandString += ');'

        #actually re-exec function
        obj = compile(src,'','exec');
        eval(obj);
        
        
        





