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
        
        #decided to make these arrays instead of dicts, because in
        #certain instances, order of declaration matters.  (for
        #instance, shared variables.)


        # takes a variable name and returns what the variable should
        # actually be named in the program text.
        self.mappings = {};
        
        #Each element of these arrays should inherit from Function.
        self.publicMethods = [];
        self.internalMethods = [];
        
        self.msgReceiveMethods = [];
        self.msgSendMethods = [];

        #list of Variable objects
        self.sharedVariables = [];
        self.endpointVariables = [];

    def addInternalFunction(self,internalFuncName,internalFuncAstNode,protObj):
        internalFuncName = self.addVarOrFuncNameToMap(internalFuncName);
        internalFunc = emitFunctions.InternalFunction(internalFuncName,internalFuncAstNode,protObj);
        self.internalMethods.append(internalFunc);
        
    def addPublicFunction(self,pubFuncName,pubFuncAstNode,protObj):
        pubFuncName = self.addVarOrFuncNameToMap(pubFuncName);
        pubFunc = emitFunctions.PublicFunction(pubFuncName,pubFuncAstNode,protObj);
        self.publicMethods.append(pubFunc);

    def addMsgReceiveFunction(self,msgReceiveFuncName,msgReceiveFuncAstNode,protObj):
        msgReceiveFuncName = self.addVarOrFuncNameToMap(msgReceiveFuncName);
        msgRecvFunc = emitFunctions.MsgReceiveFunction(msgReceiveFuncName,msgReceiveFuncAstNode,protObj);
        self.msgReceiveMethods.append(msgRecvFunc);
        
    def addMsgSendFunction(self,msgSendFuncName,msgSendFuncAstNode,protObj):
        msgSendFuncName = self.addVarOrFuncNameToMap(msgSendFuncName);
        msgSendFunc = emitFunctions.MsgSendFunction(msgSendFuncName,msgSendFuncAstNode,protObj);
        self.msgSendMethods.append(msgSendFunc);


    def addSharedVariable(self,varName,varVal):
        varName = self.addVarOrFuncNameToMap(varName);
        varToAdd = Variable(varName,self,varVal);
        self.sharedVariables.append(varToAdd);

    def addEndpointGlobalVariable(self,varName,varVal):
        varName = self.addVarOrFuncNameToMap(varName);
        varToAdd = Variable(varName,self,varVal);
        self.endpointVariables.append(varToAdd);

    def addVarOrFuncNameToMap(self,varName,root=True):
        '''
        self.mappings maps the name of the variable that the scripter
        used in Waldo source text to an internal name that does not
        conflict with any python keyword (eg, 'if', 'not', 'self', etc.)

        This function inserts the variable into this map, and returns
        with what name a variable with this name should take..
        '''
        if (emitHelper.isPythonReserved(varName) or self.isAlreadyUsed(varName)):
            newName = self.addVarOrFuncNameToMap('_' + varName,False);
            if (root):
                self.mappings[varName] = newName;
            return newName;

        return varName;

    def removeVarOrFuncNameFromMap(self,varName):
        if (varName in self.mappings):
            del self.mappings[varName];
            
    
    def isAlreadyUsed(self,varName):
        '''
        @returns True if another variable or function in the program
        within the current scope already uses the name varName.  False
        otherwise.

        We know if another variable in the program is using the name
        varName if one of the values in the self.mappings dict is the
        same as varName.
        '''
        #FIXME: Inefficient

        for s in self.mappings.keys():
            if (self.mappings[s] == varName):
                return True;

        return False;

        
    def varName(self,potentialName):
        '''
        @param {String} potentialName -- Waldo name of variable being
        used.

        @returns {String} either self.potentialName or potentialName,
        depending on whether the variable that is being assigned/used
        is a method of the endpoint's class or if it's not,
        respectively.
        '''
        #tradeoff of making the shared/endpoint/methods containers
        #arrays is that I actually have to iterate over full array to
        #check if potentialName exists in them.


        if (potentialName in self.mappings):
            potentialName = self.mappings[potentialName];
        
        for s in self.publicMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.internalMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.internalMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.msgReceiveMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;
            
        for s in self.msgSendMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        #list of strings of variables
        for s in self.sharedVariables:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.endpointVariables:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        return potentialName;

        
    def emit(self):
        '''
        @returns {String} class for this endpoint
        '''
        returnString = '\n\n';


        returnString += emitContext.emitContextClass(self);
        returnString += '\n\n';        
        returnString += self.emitClassHeader();
        returnString += '\n\n';
        returnString += self.emitClassInit();
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


