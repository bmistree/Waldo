#!/usr/bin/python
from astLabels import *;
import emitHelper;
import emitFunctions;
import emitEndpoint;

def runEmitter(astNode,protObj=None):
    '''
    @returns{String or None} -- See comments at end of function.
    '''
    
    if (astNode.label == AST_ROOT):
        #getting protocol

        #proto obj nmae
        protObjName = astNode.children[0].value;
        protObj = ProtocolObject(protObjName);

        
        #handling alias section
        aliasSection = astNode.children[1];
        
        #endpoint name
        ept1Name = aliasSection.children[0].value; 
        ept2Name = aliasSection.children[1].value;

        protObj.addEndpoint(ept1Name);
        protObj.addEndpoint(ept2Name);

        #run over trace section
        traceSection = astNode.children[2];
        runEmitter(traceSection,protObj);

        
        #run emitter over shared section
        sharedSection = astNode.children[3];
        runEmitter(sharedSection,protObj);

        #run emitter over one endpoint
        ept1 = astNode.children[4];
        runEmitter(ept1,protObj);

        #run emitter over other endpoint
        ept2 = astNode.children[5];
        runEmitter(ept2,protObj);

    elif(astNode.label == AST_TRACE_SECTION):
        for s in astNode.children:
            runEmitter(s,protObj);

    elif(astNode.label == AST_TRACE_LINE):
        # all children should have labels of AST_TRACE_ITEM.
        # first item in line should be the msg send

        if (len(astNode.children) == 0):
            errMsg = '\nBehram error: in astEmit, trace line is emtpy.\n';
            print(errMsg);
            assert(False);

        msgSendTraceItem = astNode.children[0];
        msgSendEndpointName = msgSendTraceItem.children[0].value;
        msgSendFuncName = msgSendTraceItem.children[1].value;

        # challenge is to ensure that each message function ends up
        # with a copy of the MessageReceiveFunction object that it
        # sends its message to.  (Set this value via setSendsTo.)
        # Purpose of this is so that each time send, specifies who
        # receives function, ensuring other endpoint can dispatch
        # directly from message.
        
        previousMsgFunc = protObj.addMsgSendFunction(msgSendEndpointName,msgSendFuncName);
        
        for s in range(1,len(astNode.children)):
            msgRecvTraceItem = astNode.children[s];
            msgRecvEndpointName = msgRecvTraceItem.children[0].value;
            msgRecvFuncName = msgRecvTraceItem.children[1].value;
            
            nextPreviousMsgFunc = protObj.addMsgReceiveFunction(msgRecvEndpointName,msgRecvFuncName);
            previousMsgFunc.setSendsTo(nextPreviousMsgFunc);
            previousMsgFunc = nextPreviousMsgFunc;
            
        
    elif(astNode.label == AST_SHARED_SECTION):
        #add the shared values to each endpoints class
        for s in astNode.children:
            #only annotated declarations are in children
            runEmitter(s,protObj);

    elif (astNode.label == AST_ANNOTATED_DECLARATION):
        #only place we see *annotated* declarations should be in
        #shared section.


        varName = astNode.children[2].value;
        varVal = emitHelper.getDefaultValForType(astNode);
        if (len(astNode.children) == 4):
            varVal = emitHelper.runFunctionBodyInternalEmit(astNode.children[3],protObj,None,emitHelper.SELF_PREFIX,0);
            
            
        protObj.addSharedVariable(varName,varVal);

    elif (astNode.label == AST_ENDPOINT):
        endName =  astNode.children[0].value;
        protObj.setCurrentEndpoint(endName);

        endBody = astNode.children[1];
        for s in endBody.children:
            #first iteration, runs over global variable section
            #second iteration, runs over declared functions.
            runEmitter(s,protObj);

        protObj.popCurrentEndpoint(endName);

        
    elif(astNode.label == AST_ENDPOINT_GLOBAL_SECTION):
        #each of the children here should be a global variable.
        for s in astNode.children:
            #each should be a declaration.
            varName = s.children[1].value;
            varInitializerVal = emitHelper.getDefaultValForType(s);
            
            if (len(s.children) == 3):
                varInitializerVal = emitHelper.runFunctionBodyInternalEmit(s.children[2],protObj,protObj.currentEndpoint,emitHelper.SELF_PREFIX,0);
                

            protObj.addEndpointGlobalVariable(varName,varInitializerVal);

        
    elif (astNode.label == AST_ENDPOINT_BODY_SECTION):
        for s in astNode.children:
            runEmitter(s,protObj);

    elif (astNode.label == AST_ENDPOINT_FUNCTION_SECTION):
        for s in astNode.children:
            runEmitter(s,protObj);

    elif (astNode.label == AST_PUBLIC_FUNCTION):
        publicFunctionName =  astNode.children[0].value;            
        publicFuncAstNode = astNode;
        protObj.addPublicFunction(publicFunctionName,publicFuncAstNode);

    elif(astNode.label == AST_FUNCTION):
        internalFunctionName =  astNode.children[0].value;            
        internalFuncAstNode = astNode;
        protObj.addInternalFunction(internalFunctionName,internalFuncAstNode);
        
    elif (astNode.label == AST_MSG_SEND_FUNCTION):
        msgSendFunctionName =  astNode.children[0].value;            
        msgSendFuncAstNode = astNode;
        protObj.setMsgSendFunctionAstNode(msgSendFunctionName,msgSendFuncAstNode);
        
    elif (astNode.label == AST_MSG_RECEIVE_FUNCTION):
        msgReceiveFunctionName =  astNode.children[0].value;            
        msgReceiveFuncAstNode = astNode;
        protObj.setMsgReceiveFunctionAstNode(msgReceiveFunctionName,msgReceiveFuncAstNode);


    else:
        print('\nIn emitter.  Not sure what to do with label ');
        print(astNode.label);
        print('\n\n');


        
    if (protObj == None):
        errMsg = '\nBehram error: protObj should be a protocolObject\n';
        print(errMsg);
        assert(False);


    if (astNode.label == AST_ROOT):
        # should only need to return text when asked to run on root ast
        # node.  cannot emit from partial tree.
        return  protObj.emit();
    
    return None;
        


class ProtocolObject():
    def __init__(self, name):
        self.name = name;
        self.ept1 = None;
        self.ept2 = None;

        #keep track of which endpoint section we're parsing so we know
        #which endpoint class to save new variables and functions to.
        self.currentEndpointName =None;
        self.currentEndpoint = None;
        

    def addEndpoint(self,eptName):

        if (self.ept1 == None):
            self.ept1 = emitEndpoint.Endpoint(eptName,0,1);
        elif(self.ept2 == None):
            self.ept2 = emitEndpoint.Endpoint(eptName,1,0);
        else:
            errMsg = '\nBehram error: Trying to add too many endpoints to ';
            errMsg += 'message stream in addEndpoint of ProtocolObject.\n';
            print(errMsg);
            assert(False);
                # protObj.ept2 = emitEndpoint.Endpoint(ept2Name);

    def popCurrentEndpoint(self,endName):
        if (self.currentEndpointName != endName):
            errMsg = '\nBehram error.  Requesting invalid endpoint ';
            errMsg += 'name to pop.\n';
            print (errMsg);
            assert(False);
        self.currentEndpointName = None;
        self.currentEndpoint = None;
        
    def setCurrentEndpoint(self,endpointName):
        if (self.currentEndpointName != None):
            errMsg = '\nBehram error.  Cannot setCurrentEndpoint in ';
            errMsg += 'emit before having popped previous.\n';
            print(errMsg);
            assert(False);
            
        #ensures that ept1 and ept2 are not None and also that they
        #agree with endpointName.
        self.currentEndpointName = endpointName;
        if (self.ept1.name == endpointName):
            self.currentEndpoint = self.ept1;
        elif(self.ept2.name == endpointName):
            self.currentEndpoint = self.ept2;
        else:
            errMsg = '\nBehram error: attempting to set current endpoint ';
            errMsg += 'to an unknown value.\n';
            print(errMsg);
            assert(False);


    def addPublicFunction(self,publicFunctionName,publicFuncAstNode):
        self.checkUsageError('addPublicFunction');
        self.checkCurrentEndpointUsage('addPublicFunction');
        self.currentEndpoint.addPublicFunction(publicFunctionName,publicFuncAstNode,self);

    def addInternalFunction(self,internalFunctionName,internalFuncAstNode):
        self.checkUsageError('addInternalFunction');
        self.checkCurrentEndpointUsage('addInternalFunction');
        self.currentEndpoint.addInternalFunction(internalFunctionName,internalFuncAstNode,self);


    def addMsgSendFunction(self,msgSendEndpointName,msgSendFunctionName):
        self.checkUsageError('addMsgSendFunction');
        whichEndpoint = None;
        if (self.ept1.name == msgSendEndpointName):
            whichEndpoint = self.ept1;
        elif(self.ept2.name == msgSendEndpointName):
            whichEndpoint = self.ept2;
        else:
            errMsg = '\nBehram error: should not be trying to add a ';
            errMsg += 'message send function for an endpoint that does ';
            errMsg += 'not exist.\n';
            print(errMsg);
            assert(False);

        return whichEndpoint.addMsgSendFunction(msgSendFunctionName,self);


    def addMsgReceiveFunction(self,msgReceiveEndpointName,msgReceiveFunctionName):
        self.checkUsageError('addMsgReceiveFunction');
        whichEndpoint = None;
        if (self.ept1.name == msgReceiveEndpointName):
            whichEndpoint = self.ept1;
        elif(self.ept2.name == msgReceiveEndpointName):
            whichEndpoint = self.ept2;
        else:
            errMsg = '\nBehram error: should not be trying to add a ';
            errMsg += 'message receive function for an endpoint that does ';
            errMsg += 'not exist.\n';
            print(errMsg);
            assert(False);

        return whichEndpoint.addMsgReceiveFunction(msgReceiveFunctionName,self);

    
    def setMsgSendFunctionAstNode(self,msgSendFunctionName,msgSendFuncAstNode):
        self.checkUsageError('setAstNodeForMsgSend');
        self.checkCurrentEndpointUsage('setAstNodeForMsgSend');
        self.currentEndpoint.setMsgSendFunctionAstNode(msgSendFunctionName,msgSendFuncAstNode);

    def setMsgReceiveFunctionAstNode(self,msgReceiveFunctionName,msgReceiveFuncAstNode):
        self.checkUsageError('setAstNodeForMsgReceive');
        self.checkCurrentEndpointUsage('setAstNodeForMsgReceive');
        self.currentEndpoint.setMsgReceiveFunctionAstNode(msgReceiveFunctionName,msgReceiveFuncAstNode);



            
    def addEndpointGlobalVariable(self,globalName,globalVal):
        '''
        @param {String} globalName
        @param {String or None} globalVal ---> What the variable will
        be initialized with.
        '''
        self.checkUsageError('addEndpointGlobalVariable');
        self.checkCurrentEndpointUsage('addEndpointGlobalVariable');
        self.currentEndpoint.addEndpointGlobalVariable(globalName,globalVal);

    def checkCurrentEndpointUsage(self,functionFrom):
        if (self.currentEndpointName == None):
            errMsg = '\nBehram error: attempting to perform an emit '
            errMsg += 'operation on an endpoint when have no current ';
            errMsg += 'endpoint in function ' + functionFrom + '.\n';
            print(errMsg);
            assert(False);
        

    def addSharedVariable(self,sharedName,sharedVal):
        '''
        @param {String} sharedName
        @param {String or None} sharedVal ---> What the variable will
        be initialized with.
        '''
        self.checkUsageError('addSharedVariable');

        self.ept1.addSharedVariable(sharedName,sharedVal);
        self.ept2.addSharedVariable(sharedName,sharedVal);


        
        
    def checkUsageError(self,whichFunc):
        '''
        For sanity-checking/debugging.
        '''
        if ((self.ept1 == None) or (self.ept2 == None)):
            errMsg = '\n\nBehram error: should have set ';
            errMsg += 'both endpoints before calling ';
            errMsg += whichFunc + '.\n\n';
            print(errMsg);
            assert(False);
        
    def emit(self):
        self.checkUsageError('emit');
        returnString = '';
        returnString += self.emitHead();
        returnString += '\n';
        returnString += self.ept1.emit();
        returnString += '\n\n';
        returnString += self.ept2.emit();
        returnString += '\n';
        return returnString;


    def _DEBUG_PRINT(lineNo, endpointClassName,toPrint):
        if (endpointClassName == None):
            endpointClassName = 'Unknown class name';

        printStr = str(lineNo);
        printStr += ':   ' + endpointClassName;
        printStr += '\n';
        printStr += toPrint;

    
    def emitHead(self):
        '''
        Emit boiler plate code that must go at top of shared file
        '''

        emitString = r"""#!/usr/bin/python


#EXACT
import threading;
import time;
    
INTERMEDIATE_CONTEXT = 0;
COMMITTED_CONTEXT = 1;

# When last message fires, it sends a message back to other endpoint.
# This message is used to synchronize shared variables between two
# endpoints.  Gets passed in dispatchTo field of received messages.
STREAM_TAIL_SENTINEL = 'None';

def _DEBUG_PRINT(lineNo, endpointClassName, toPrint):
"""
        debugPrintBody = r"""
if (endpointClassName == None):
"""
        ifBody = "endpointClassName = 'Unknown class name';\n"
        debugPrintBody += emitHelper.indentString (ifBody,1);
        debugPrintBody += r"""
# printStr = str(lineNo);
# printStr += ':   ' + endpointClassName;
# printStr += '\n';
# printStr += str(toPrint);
printStr = str(toPrint);
print printStr;
"""
        emitString += emitHelper.indentString(debugPrintBody,1);


        emitString += 'class _MessageSendQueueElement():\n';

        classBody = r"""
'''
EXACT -- may want to rename to prevent conflicts with
endpoint...eg, use underscore prefix.
    
_MessageSendQueueElements store calls that could not be processed
because we were already in a trace, or that were reverted because
two messages collided.
'''

def __init__ (self,sendFuncName, argsArray):
"""
        
        initBody = r"""
'''
@param {String} sendFuncName -- An identifier to use to
distinguish which message send function was queued.

@param {Array} argsArray -- All arguments that were passed
into the function (excluding self).
'''
self.sendFuncName = sendFuncName;
self.argsArray = argsArray;

""";

        classBody += emitHelper.indentString(initBody,1);
        emitString += emitHelper.indentString(classBody,1);

        #emit the delay code
        emitString += r"""
HOW_LONG_TO_DELAY_IN_SECONDS = .01;
class _Delay(threading.Thread):
""";

        classBody = r"""
def __init__(self,endpoint,msg,funcNameFrom):
""";
        initBody = r"""
threading.Thread.__init__(self);
self.endpoint = endpoint;
self.msg = msg;
self.funcNameFrom = funcNameFrom;
""";
        classBody += emitHelper.indentString(initBody,1);

        classBody += r"""
def run(self):
""";

        runBody = r"""
time.sleep(HOW_LONG_TO_DELAY_IN_SECONDS);
self.endpoint._internalSendMsg(self.msg,self.funcNameFrom);
""";
        classBody += emitHelper.indentString(runBody,1);
    

        emitString += emitHelper.indentString(classBody,1);
        
        return emitString;


    
