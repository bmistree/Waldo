#!/usr/bin/python

import emitHelper;
import emitFunctions;
import emitContext;
import random;    
        
class Endpoint():
    def __init__(self,name,myPriority,theirPriority):
        '''
        To handle cases where both sides try sending simultaneously,
        default to endpoint with higher priority.
        '''
        self.name = name;
        self.contextClassName = '_' + name + 'Context';

        self.myPriority = myPriority;
        self.theirPriority = theirPriority;

        # keep track of which function we are currently emitting: for
        # send statements, will need to refer to this value to know
        # what string token to pass to auto-generated _sendMsg
        # function.  Only the emitting functions set and reset this
        # variable.  It is read by runFunctionBodyInternalEmit of
        # emitHelper.py.
        self.currentlyEmittingFunction = None;

        #decided to make these arrays instead of dicts, because in
        #certain instances, order of declaration matters.  (for
        #instance, shared variables.)

        #Each element of these arrays should inherit from Function.
        self.publicMethods = [];
        self.internalMethods = [];
        
        self.msgReceiveMethods = [];
        self.msgSendMethods = [];

        #list of Variable objects
        self.sharedVariables = [];
        self.endpointVariables = [];

    def addInternalFunction(self,internalFuncName,internalFuncAstNode,protObj):
        internalFunc = emitFunctions.InternalFunction(internalFuncName,internalFuncAstNode,protObj);
        self.internalMethods.append(internalFunc);
        
    def addPublicFunction(self,pubFuncName,pubFuncAstNode,protObj):
        pubFunc = emitFunctions.PublicFunction(pubFuncName,pubFuncAstNode,protObj);
        self.publicMethods.append(pubFunc);


    def isGlobalOrShared(self,idName):
        '''
        @param {String} idName -- the user-defined Waldo name of a variable.
        
        @returns {Bool} True if idName is either an endpoint or shared variable.
                        False otherwise
        '''
        for s in self.sharedVariables:
            if (s.name == idName):
                return True;

        for s in self.endpointVariables:
            if (s.name == idName):
                return True;
            
        return False;

    def getPythonizedFunctionName(self,funcName):
        '''
        @param {String} funcName -- The user-defined Waldo name of a
        function he/she wants to reference.

        @returns {String} -- The way the function can be called in the
        translated version.  For instance, if a user had declared an
        internal function mFunc in Waldo, this function would return
        self._mFunc.

        @throws Throws error if funcName does not exist in public,
        internal, msgRev, or msgSend methods.
        '''

        for s in self.publicMethods:
            if (s.name == funcName):
                return s.pythonizeName();
            
        for s in self.internalMethods:
            if (s.name == funcName):
                return s.pythonizeName();

        for s in self.msgReceiveMethods:
            if (s.name == funcName):
                return s.pythonizeName();

        for s in self.msgSendMethods:
            if (s.name == funcName):
                return s.pythonizeName();


        errMsg = '\nBehram error: requesting a function name to call that ';
        errMsg += 'does not exist in this endpoint.\n';
        assert(False);



    def setMsgReceiveFunctionAstNode(self,msgReceiveFuncName,msgReceiveFuncAstNode):
        '''
        Not actually adding, looking up name in existing msgRecv
        methods, and setting astNode for it.  Should already have the
        node from running over trace lines.
        '''
        for s in self.msgReceiveMethods:
            if (s.name == msgReceiveFuncName):
                s.setAstNode(msgReceiveFuncAstNode);
                return;

        errMsg = '\nBehram error: could not find a message receive method when ';
        errMsg += 'trying to set its astNode.\n';
        print(errMsg);
        assert(False);
        
    def addMsgReceiveFunction(self,msgReceiveFuncName,protObj):
        print('\nWarning when adding msg receive: may not want to change name early.\n');
        # note: may not want to do the addvarorfuncnameto map, but
        # instead, use the pythonized version of the name;
        msgRecvFunc = emitFunctions.MsgReceiveFunction(msgReceiveFuncName,protObj);
        self.msgReceiveMethods.append(msgRecvFunc);
        return msgRecvFunc;

        
    def setMsgSendFunctionAstNode(self,msgSendFuncName,msgSendFuncAstNode):
        '''
        Not actually adding, looking up name in existing msgSend
        methods, and setting astNode for it.  Should already have the
        node from running over trace lines.
        '''
        for s in self.msgSendMethods:
            if (s.name == msgSendFuncName):
                s.setAstNode(msgSendFuncAstNode);
                return;

        errMsg = '\nBehram error: could not find a message send method when ';
        errMsg += 'trying to set its astNode.\n';
        print(errMsg);
        assert(False);

        
    def addMsgSendFunction(self,msgSendFuncName,protObj):
        print('\nWarning when adding msg receive: may not want to change name early.\n');
        # note: may not want to do the addvarorfuncnameto map, but
        # instead, use the pythonized version of the name;
        msgSendFunc = emitFunctions.MsgSendFunction(msgSendFuncName,protObj);
        self.msgSendMethods.append(msgSendFunc);
        return msgSendFunc;


    def addSharedVariable(self,varName,varVal):
        varToAdd = Variable(varName,self,varVal);
        self.sharedVariables.append(varToAdd);

    def addEndpointGlobalVariable(self,varName,varVal):
        varToAdd = Variable(varName,self,varVal);
        self.endpointVariables.append(varToAdd);


        
    def emit(self):
        '''
        @returns {String} class for this endpoint
        '''
        returnString = '\n\n';

# lkjs;
# probably want to change order emit file so that public and message functions are at the top;
# lkjs;
        
        returnString += emitContext.emitContextClass(self);
        returnString += '\n\n';        
        returnString += self.emitClassHeader();
        returnString += '\n\n';
        returnString += self.emitClassInit();
        returnString += '\n\n';
        returnString += self.emitSmallHelperUtilities();
        returnString += '\n\n';

        
        returnString += self.emitGeneralReceiveMessageUtility();
        returnString += '\n\n';
        returnString += self.emitResetAndCommit();
        returnString += '\n\n';
        returnString += self.emitTrySendNext();

        returnString += self.emitGeneralSendMessageUtility();
        returnString += '\n\n';
        returnString += self.emitFunctions();
        return returnString;



    def emitFunctions(self):
        returnString = '';
        returnString += '\n#public methods\n';
        for s in self.publicMethods:
            returnString += s.emit();
            returnString += '\n';
            
        returnString += '\n#internal methods\n';
        for s in self.internalMethods:
            returnString += s.emit();
            returnString += '\n';

        returnString += '\n#msgReceive methods\n';            
        for s in self.msgReceiveMethods:
            returnString += s.emit();
            returnString += '\n';
            
        returnString += '\n#msgSend methods\n';                        
        for s in self.msgSendMethods:
            returnString += s.emit();
            returnString += '\n';

        return returnString;


        
    def emitClassHeader(self):
        returnString = '''
class %s:
''' % self.name;

        return returnString;


    
    def emitSmallHelperUtilities(self):
        '''
        Short functions used inside each endpoint.  
        '''

        # FIXME: lkjs;
        # name "ready" could conflict with public function name.
        readyHead = '\ndef ready (self):\n';
        readyBody = '#EXACT\nreturn self.connectionObject.ready();\n'
        readyStr = readyHead + emitHelper.indentString(readyBody,1);


        lockHead = '\ndef _lock(self):\n';
        lockBody = '#EXACT\nself.mutex.acquire();\n';
        lockStr = lockHead + emitHelper.indentString(lockBody,1);

        unlockHead = '\ndef _unlock(self):\n';
        unlockBody = '#EXACT\nself.mutex.release();\n';
        unlockStr = unlockHead + emitHelper.indentString(unlockBody,1);

        return emitHelper.indentString(readyStr + lockStr + unlockStr,1);

    
    def emitClassInit(self):
        
        initHeaderString = '''
def __init__(self,connectionObject):
'''

        # each endpoint needs a unique name for reference in
        # the current connection object implementation.
        # FIXME: does not actually guarantee
        # distinct names for each endpoint.  lkjs;
        fakeName = str(random.random());


        initBodyString = r"""
'''
EXACT, except for initialization stuff.  maybe think about
that later.
'''
errMsg = '\nBehram FIXME: ignoring initial connection handshake ';
errMsg += 'in favor of passing in a pre-existing connection.  ';
errMsg += 'Also, avoiding initializing variables correctly.  Handle later.\n';
print(errMsg);


self.committed = _PingContext(%s,%s);
self.intermediate = self.committed.copy();
self.whichEnv = COMMITTED_CONTEXT;

#should use different names for each endpoint
self.name = '%s'; #will actually be a string created from a random float.
        
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

""" % (str(self.myPriority),str(self.theirPriority),fakeName);

        
        returnString = emitHelper.indentString(initHeaderString,1);
        returnString += '\n';
        returnString += emitHelper.indentString(initBodyString,2);
        return returnString;



    def emitGeneralReceiveMessageUtility(self):

        msgReceiveHead = '''
def _msgReceive(self,msg):
''';
        msgReceiveBody = r"""
'''
EXACT
        
called whenever receive message from other side.  performs
dispatch, sending message to appropriate receiving function
'''

DEBUG('ping', 'Received a message');
# thread safety
self._lock();
        
#check case for simultaneous open
if (msg['iInitiated'] and self.outstandingSend != None): """

        externalIfBody = '''
#means that we had a case of simultaneous open

#endpoint with higher priority always wins
if (self.committed._myPriority < self.committed._theirPriority):
''';
        internalIfBody = '''
#we must back off our send, inserting outstanding back
#into message queue.
                
self._reset(); #flash the intermediate context back to committed
self.msgSendQueue.insert(0,self.outstandingSend);
self.outstandingSend = None;
self._unlock();
return;
''';
        externalIfBody += emitHelper.indentString(internalIfBody,1);
        msgReceiveBody += emitHelper.indentString(externalIfBody,1);

        msgReceiveBody += r"""
            
# update shared environment data in intermediate
self.intermediate.updateEnvironmentData(msg['environmentData']);

if (msg['dispatchTo'] == STREAM_TAIL_SENTINEL):
""";

        externalIfBody = r"""
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
""";

        msgReceiveBody += emitHelper.indentString(externalIfBody,1);

        msgReceiveBody += r"""
#choose who to dispatch received message to;
dispatchSrcStr = 'self.%s (' % msg['dispatchTo'];
dispatchSrcStr += 'msg["data"]);';

#actually evaluate the receive message function
obj = compile(dispatchSrcStr,'','exec');
eval(obj);

#thread safety
self._unlock();

""";
        
        indentedHead = emitHelper.indentString(msgReceiveHead,1);
        indentedBody = emitHelper.indentString(msgReceiveBody,2);
        return indentedHead + '\n' + indentedBody;


    
    def emitResetAndCommit(self):

        resetHead = '\ndef _reset(self):\n';
        resetBody = r"""
'''
EXACT

Remove any changes made to intermediate.
'''
self.intermediate = self.commmited.copy();
""";

        commitHead = '\ndef _commit(self):\n';
        commitBody = r"""
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
""";
        
        resetStr = emitHelper.indentString(resetHead,1) + emitHelper.indentString(resetBody,2);
        commitStr = emitHelper.indentString(commitHead,1) + emitHelper.indentString(commitBody,2);
        return resetStr + '\n' + commitStr;

        
        
    def emitTrySendNext(self):

        trySendNextHead = '\ndef _trySendNext(self):\n';

        trySendNextBody = r"""
'''
EXACT
        
Checks if there is an outstanding message in the queue to send.
        
Should only be called from _commit, (ie after know that
previously executing trace is done).
'''
if (self.outstandingSend != None):
""";
        ifBody =  r"""
errMsg = '\nBehram error in _trySendNext of Ping.  ';
errMsg += 'Should not have an outstanding message.\n';
print(errMsg);
assert(False);

""";
        trySendNextBody += emitHelper.indentString(ifBody,1);

        trySendNextBody += r"""
if (self.amInTrace == True):
""";
        ifBody = r"""
errMsg = '\nBehram error in _trySendNext of Ping.  ';
errMsg += 'Should not already be in trace.\n';
print(errMsg);
assert(False);

""";
        trySendNextBody += emitHelper.indentString(ifBody,1);

        trySendNextBody += r"""
if (len(self.msgSendQueue) == 0):
"""

        ifBody = r"""
#no work to do.
return;

""";
        trySendNextBody += emitHelper.indentString(ifBody,1);


        trySendNextBody += r"""
        
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
""";
        forBody = r"""
commandString += 'args[' + str(s) + ']';
if (s != len(args) -1):
""";
        ifBody = "commandString += ','\n";
        forBody += emitHelper.indentString(ifBody,1);

        trySendNextBody += emitHelper.indentString(forBody,1);

        trySendNextBody += r"""
commandString += ');'

#actually re-exec function
obj = compile(src,'','exec');
eval(obj);

""";
        
        
        indentedHead = emitHelper.indentString(trySendNextHead,1);
        indentedBody = emitHelper.indentString(trySendNextBody,2);
        return indentedHead + '\n' + indentedBody;


    def emitGeneralSendMessageUtility(self):
        sendMsgHead = '\ndef _sendMsg (self,msg,funcNameFrom):\n';
        
        sendMsgBody = r"""
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
""";

        ifBody = 'iInitiated = False;\n';
        sendMsgBody += emitHelper.indentString(ifBody,1);

        sendMsgBody += r"""
# keep track of who initiator of message stream was to handle
# case of simultaneous stream start
msgToSend['iInitiated'] = iInitiated;

msgToSend['environmentData'] = self.intermediate.generateEnvironmentData();


'''
NOT EXACT PART: determine dispatchTo field based on what on
this endpoint called this function.
'''
dispatchTo = None;
"""

        # Each message should be structured to include the name of the
        # function on the other endpoint that should handle it.  The
        # bit of code below handles adding the if-elif-else statements
        # for this message labeling.
        caseBasedDispatch = '';
        first = True;
        for s in self.msgSendMethods:
            caseBasedDispatch += s.caseBasedDispatch(first,0);
            first = False;
            
        for s in self.msgReceiveMethods:
            caseBasedDispatch += s.caseBasedDispatch(first,0);
            first = False;


            
        if (not first):
            # means we had some messages to send
            # add in a slip of compiler debugging code.
            caseBasedDispatch += 'else:\n';
            elseBody = r"""
errMsg = '\nBehram Error.  Provided an invalid ';
errMsg += 'funcNameFrom argument in Pong.\n';
print(errMsg);
assert(False);

""";
            caseBasedDispatch += emitHelper.indentString(elseBody,1);

            
        # actually add the caseBasedDispatch code onto the end of
        # sendMsgBody.
        sendMsgBody += caseBasedDispatch;


        sendMsgBody += r"""
'''
END NOT EXACT PART
'''

msgToSend['data'] = msg;
msgToSend['dispatchTo'] = dispatchTo;
self.connectionObject.writeMsg(msgToSend,self.name);
""";

        indentedHead = emitHelper.indentString(sendMsgHead,1);
        indentedBody = emitHelper.indentString(sendMsgBody,2);
        return indentedHead + '\n' + indentedBody;


class Variable():
    def __init__(self,name,endpoint,val=None):
        self.name = name;
        self.val = None;
        self.endpoint = endpoint;

    def getUsedName (self):
        return self.name;
        # return self.endpoint.varName(self.name);
    
    def emit(self,optionalVarPrefix=''):
        returnString = optionalVarPrefix + self.name;
        # returnString = optionalVarPrefix + self.endpoint.varName(self.name);
        returnString += ' = ';


        if (self.val == None):
            returnString += 'None';
        else:
            returnString += self.val;
        returnString += ';';
        
        return returnString;


