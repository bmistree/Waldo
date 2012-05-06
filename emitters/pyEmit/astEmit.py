#!/usr/bin/python
from astLabels import *;
import emitHelper;
import emitFunctions;

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

        protObj.ept1 = Endpoint(ept1Name);
        protObj.ept2 = Endpoint(ept2Name);

        #run emitter over shared section
        sharedSection = astNode.children[3];
        runEmitter(sharedSection,protObj);

        #run emitter over one endpoint
        ept1 = astNode.children[4];
        runEmitter(ept1,protObj);

        #run emitter over other endpoint
        ept2 = astNode.children[5];
        runEmitter(ept2,protObj);


        
    elif(astNode.label == AST_SHARED_SECTION):
        #add the shared values to each endpoints class
        for s in astNode.children:
            #only annotated declarations are in children
            runEmitter(s,protObj);

    elif (astNode.label == AST_ANNOTATED_DECLARATION):
        #only place we see *annotated* declarations should be in
        #shared section.
        
        varName = astNode.children[2].value;
        varVal = None;
        if (len(astNode.children) == 4):
            #FIXME: Not handling initializers for annotated declarations correctly.
            #lkjs;
            errMsg = '\n\nNot handling initializers for annotated declarations correctly.\n\n';
            print(errMsg);

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
            varInitializerVal = None;
            if (len(s.children) == 3):
                #means there was an initializer for this variable.
                errMsg = '\n\nBehram error: Still do not know what to do with var ';
                errMsg += 'initializer data when emitting for endpoint ';
                errMsg += 'global section.\n\n';
                print(errMsg);

                #lkjs;
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
        protObj.addMsgSendFunction(msgSendFunctionName,msgSendFuncAstNode);

    elif (astNode.label == AST_MSG_RECEIVE_FUNCTION):
        msgReceiveFunctionName =  astNode.children[0].value;            
        msgReceiveFuncAstNode = astNode;
        protObj.addMsgReceiveFunction(msgReceiveFunctionName,msgReceiveFuncAstNode);



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

    def addMsgSendFunction(self,msgSendFunctionName,msgSendFuncAstNode):
        self.checkUsageError('msgSendFunction');
        self.checkCurrentEndpointUsage('msgSendFunction');
        self.currentEndpoint.addMsgSendFunction(msgSendFunctionName,msgSendFuncAstNode,self);

    def addMsgReceiveFunction(self,msgReceiveFunctionName,msgReceiveFuncAstNode):
        self.checkUsageError('msgReceiveFunction');
        self.checkCurrentEndpointUsage('msgReceiveFunction');
        self.currentEndpoint.addMsgReceiveFunction(msgReceiveFunctionName,msgReceiveFuncAstNode,self);


            
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
        returnString += '\n';
        returnString += self.emitHead();
        returnString += '\n';
        returnString += self.ept1.emit();
        returnString += '\n\n';
        returnString += self.ept2.emit();
        returnString += '\n';
        return returnString;


    def emitHead(self):
        '''
        Emit boiler plate code that must go at top of shared file
        '''

        emitString = r'''
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
        return emitString;


    
        
class Endpoint():
    def __init__(self,name):
        self.name = name;

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
        returnString = '';
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
def __init__(self):
'''
        initBodyString = '';
        initBodyString += '\n#shared variables section\n'
        for s in self.sharedVariables:
            initBodyString += s.emit() + '\n';

        initBodyString += '\n#endpoint global variables section\n'
        for s in self.endpointVariables:
            initBodyString += s.emit() + '\n';
        
        returnString = emitHelper.indentString(initHeaderString,1);
        returnString += emitHelper.indentString(initBodyString,2);
        return returnString;


    
class Variable():
    def __init__(self,name,endpoint,val=None):
        self.name = name;
        self.val = None;
        self.endpoint = endpoint;

    def emit(self):
        returnString = self.endpoint.varName(self.name);
        returnString += ' = ';


        if (self.val == None):
            returnString += 'None';
        else:
            returnString += self.val;
        returnString += ';';
        
        return returnString;


