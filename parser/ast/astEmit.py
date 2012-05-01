#!/usr/bin/python
from astLabels import *;


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
        returnString += self.ept1.emit();
        returnString += '\n\n';
        returnString += self.ept2.emit();
        returnString += '\n';
        return returnString;


#From http://pentangle.net/python/handbook/node52.html
#I also personally added self.
PYTHON_RESERVED_WORD_DICT = {
    'self': True,
    'and':True,
    'assert':True,
    'break':True,
    'class':True,
    'continue':True,
    'def':True,
    'del':True,
    'elif':True,
    'else':True,
    'except':True,
    'exec':True,
    'finally':True,
    'for':True,
    'from':True,
    'global':True,
    'if':True,
    'import':True,
    'in':True,
    'is':True,
    'lambda':True,
    'not':True,
    'or':True,
    'pass':True,
    'print':True,
    'raise':True,
    'return':True,
    'try':True,
    'while':True,
    'Data':True,
    'Float':True,
    'Int':True,
    'Numeric':True,
    'Oxphys':True,
    'array': True,
    'close':True,
    'float':True,
    'int':True,
    'input':True,
    'open':True,
    'range':True,
    'type':True,
    'write':True,
    'zeros':True,
    'acos':True,
    'asin':True,
    'atan':True,
    'cos':True,
    'e':True,
    'exp':True,
    'fabs':True,
    'floor':True,
    'log':True,
    'log10':True,
    'pi':True,
    'sin':True,
    'sqrt':True,
    'tan':True
    }

def isPythonReserved(varName):
    '''
    @returns True if varName is a reserved word in python.  False
    otherwise.
    '''
    returner = varName in PYTHON_RESERVED_WORD_DICT;
    return returner;
    
    
        
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
        internalFunc = InternalFunction(internalFuncName,internalFuncAstNode,protObj);
        self.internalMethods.append(internalFunc);
        
    def addPublicFunction(self,pubFuncName,pubFuncAstNode,protObj):
        pubFuncName = self.addVarOrFuncNameToMap(pubFuncName);
        pubFunc = PublicFunction(pubFuncName,pubFuncAstNode,protObj);
        self.publicMethods.append(pubFunc);

    def addMsgReceiveFunction(self,msgReceiveFuncName,msgReceiveFuncAstNode,protObj):
        msgReceiveFuncName = self.addVarOrFuncNameToMap(msgReceiveFuncName);
        msgRecvFunc = MsgReceiveFunction(msgReceiveFuncName,msgReceiveFuncAstNode,protObj);
        self.msgReceiveMethods.append(msgRecvFunc);
        
    def addMsgSendFunction(self,msgSendFuncName,msgSendFuncAstNode,protObj):
        msgSendFuncName = self.addVarOrFuncNameToMap(msgSendFuncName);
        msgSendFunc = MsgSendFunction(msgSendFuncName,msgSendFuncAstNode,protObj);
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
        if (isPythonReserved(varName) or self.isAlreadyUsed(varName)):
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
        
        returnString = indentString(initHeaderString,1);
        returnString += indentString(initBodyString,2);
        return returnString;


def indentString(string,indentAmount):
    '''
    @param {String} string -- Each line in this string we will insert
    indentAmount number of tabs before and return the new, resulting
    string.
    
    @param {Int} indentAmount 

    @returns {String}
    '''
    splitOnNewLine = string.split('\n');
    returnString = '';

    indenter = '';
    for s in range(0,indentAmount):
        indenter += '    ';

    for s in splitOnNewLine:
        if (len(s) != 0):
            returnString += indenter + s + '\n';

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


class Function(object):
    def __init__(self,name,astNode,protObj,declArgListIndex):
        '''
        @param {String} name -- Should already be guaranteed not to
        collide with python variable and other global vars.
        
        @param {Int} declArgListIndex -- Each function astNode
        (public, msgReceive, ...) has many children.  declArgListIndex is
        the index of astNode.children that contains declArgList appears.
        '''
        self.name = name;
        self.astNode = astNode;
        self.protObj = protObj;
        self.endpoint = self.protObj.currentEndpoint;
        self.declArgListIndex = declArgListIndex;
        
    def emit():
        errMsg = '\nBehram error: pure virtual method emit of Function ';
        errMsg += 'called.\n';
        assert(False);

    def createMethodHeader(self):
        #already know that self.name does not conflict with python
        #because was checked before constructed.
        methodHeader = 'def %s(self' % self.name;

        
        #fill in arguments
        declArgsList = self.astNode.children[self.declArgListIndex];
        for s in declArgsList.children:
            #each s is a declArg
            if (len(s.children) == 0):
                continue;


            argName = s.children[1].value;
            argName = self.endpoint.varName(argName);
            methodHeader += ', ' + argName;
        
        methodHeader += '):\n';
        return methodHeader;


class InternalFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 2;        
        super(InternalFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);
    def emit(self):
        print('\nBehram error: in InternalFunction, need to finish emit method\n');
        methodHeader = self.createMethodHeader();
        methodBody = 'pass';
        
        returnString = indentString(methodHeader,1);
        returnString += indentString(methodBody,2);
        return returnString;


class PublicFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 2;
        super(PublicFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);

    def emit(self):
        print('\nBehram error: in PublicFunction, need to finish emit method\n');
        methodHeader = self.createMethodHeader();        

        methodBody = 'pass;';
        
        returnString = indentString(methodHeader,1);
        returnString += indentString(methodBody,2);
        return returnString;

        
class MsgSendFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 1;
        super(MsgSendFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);
        
        
    def emit(self):
        print('\nBehram error: in MsgSendFunction, need to finish emit method\n');

        methodHeader = self.createMethodHeader();
        
        funcBodyNode = self.astNode.children[2];
        methodBody = runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint);
        
        returnString = indentString(methodHeader,1);
        returnString += indentString(methodBody,2);
        return returnString;


        
class MsgReceiveFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 1;
        super(MsgReceiveFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);


    def emit(self):
        print('\nBehram error: in MsgReceiveFunction, need to finish emit method\n');
        methodHeader = self.createMethodHeader();                
        methodBody = 'pass;';
        
        returnString = indentString(methodHeader,1);
        returnString += indentString(methodBody,2);
        return returnString;

def runFunctionBodyInternalEmit(astNode,protObj,endpoint,indentLevel=0):
    '''
    @param {AstNode} astNode -- the ast node that we want evaluation
    to start from.  When called externally, this will generally have
    label AST_FUNCTION_BODY.  However, because this code also emits
    bool, string, and number literals, it may also be used to emit the
    initialization statement for shared and global variables.
    
    @param {ProtocolObject} protObj -- So that can check for
    appropriate variable names

    @returns {String} with funcition text.  base indent level is 0.
    '''
    returnString = '';
    if (astNode.label == AST_FUNCTION_BODY):
        for s in astNode.children:
            funcStatementString = runFunctionBodyInternalEmit(s,protObj,endpoint,indentLevel);
            if (len(funcStatementString) != 0):
                returnString += indentString(funcStatementString,indentLevel);
                returnString += '\n';
        if (len(returnString) == 0):
            returnString += indentString('pass;',indentLevel);

                
    elif (astNode.label == AST_DECLARATION):
        idName = astNode.children[1].value;
        idName = endpoint.varName(idName);
        decString = idName + ' = ';

        #check if have an initializer value
        if (len(astNode.children) == 3):
            #have an initializer value;
            rhsInitializer = runFunctionBodyInternalEmit(astNode.children[2],protObj,endpoint,0);
            decString += rhsInitializer;
        else:
            #no initializer value, specify defaults.
            typeName = astNode.type;        
            if (typeName == TYPE_BOOL):
                decString += 'False;';
            elif (typeName == TYPE_NUMBER):
                decString += '0;';
            elif (typeName == TYPE_STRING):
                decString += '"";';
            elif (typeName == TYPE_NOTHING):
                decString += 'None;';
            else:
                errMsg = '\nBehram error.  Unknown declaration type when ';
                errMsg += 'emitting from runFunctionBodyInternalEmit.\n';
                print(errMsg);
                decString += 'None;';

        
        returnString += indentString(decString,indentLevel);
        returnString += '\n';

    elif (astNode.label == AST_BOOL):
        return ' ' + astNode.value + ' ';

    elif (astNode.label == AST_STRING):
        return ' "'  + astNode.value + '" ';

    elif (astNode.label == AST_NUMBER):
        return ' '  + astNode.value + ' ';

    elif ((astNode.label == AST_PLUS) or (astNode.label == AST_MINUS) or
          (astNode.label == AST_MULTIPLY) or (astNode.label == AST_DIVIDE) or 
          (astNode.label == AST_AND) or (astNode.label == AST_OR) or
          (astNode.label == AST_BOOL_EQUALS) or (astNode.label == AST_BOOL_NOT_EQUALS)):

        if (astNode.label == AST_PLUS):
            operator = '+';
        elif(astNode.label == AST_MINUS):
            operator = '-';
        elif(astNode.label == AST_MULTIPLY):
            operator = '*';
        elif(astNode.label == AST_DIVIDE):
            operator = '/';
        elif(astNode.label == AST_AND):
            operator = 'and';
        elif(astNode.label == AST_OR):
            operator = 'or';
        elif(astNode.label == AST_BOOL_EQUALS):
            operator = '==';
        elif(astNode.label == AST_BOOL_NOT_EQUALS):
            operator = '!=';

            
        else:
            errMsg = '\nBehram error.  Unknown operator type when ';
            errMsg += 'emitting from runFunctionBodyInternalEmit.\n'
            print(errMsg);
            assert(False);
            
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];

        lhsText = runFunctionBodyInternalEmit(lhsNode,protObj,endpoint,0);
        rhsText = runFunctionBodyInternalEmit(rhsNode,protObj,endpoint,0);

        overallLine = lhsText + ' '+ operator + ' (' + rhsText + ') ';
        return overallLine;


    elif (astNode.label == AST_CONDITION_STATEMENT):
        returnString = '';
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,indentLevel);
            returnString += '\n';
            

    elif (astNode.label == AST_BOOLEAN_CONDITION):
        returnString = runFunctionBodyInternalEmit(astNode.children[0],protObj,endpoint,indentLevel);

    elif (astNode.label == AST_IDENTIFIER):
        returnString = astNode.value;

    elif (astNode.label == AST_ELSE_IF_STATEMENTS):
        returnString = '';
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,0);
            returnString += '\n';

        if (returnString != ''):
            returnString = indentString(returnString,indentLevel);

    elif ((astNode.label == AST_IF_STATEMENT) or
          (astNode.label == AST_ELSE_IF_STATEMENT)):

        if (astNode.label == AST_IF_STATEMENT):
            condHead = 'if ';
        elif(astNode.label == AST_ELSE_IF_STATEMENT):
            condHead = 'elif ';
        else:
            errMsg = '\nBehram error: got an unknown condition label ';
            errMsg += 'in runFunctionBodyInternalEmit.\n';
            print(errMsg);
            assert(False);
            
        booleanConditionNode = astNode.children[0];
        condBodyNode = astNode.children[1];

        boolCondStr = runFunctionBodyInternalEmit(booleanConditionNode,protObj,endpoint,0);
        condHead += boolCondStr + ':'
        
        condBodyStr = runFunctionBodyInternalEmit(condBodyNode,protObj,endpoint,0);
        if (condBodyStr == ''):
            condBodyStr = 'pass;';


        returnString = indentString(condHead,indentLevel) + '\n' + indentString(condBodyStr, indentLevel +1);

    elif(astNode.label == AST_ELSE_STATEMENT):
        if (len(astNode.children) == 0):
            return '';
        
        elseHead = 'else: \n';
        elseBody = astNode.children[0];

        elseBodyStr = runFunctionBodyInternalEmit(elseBody,protObj,endpoint,0);

        if (elseBodyStr == ''):
            elseBodyStr = 'pass;';
        
        returnString = indentString(elseHead,indentLevel) + '\n' + indentString(elseBodyStr, indentLevel +1);

    elif (astNode.label == AST_FUNCTION_CALL):
        funcNameNode = astNode.children[0];
        funcNameStr = endpoint.varName(funcNameNode.value);
        funcArgListNode = astNode.children[1];
        funcArgStr = runFunctionBodyInternalEmit(funcArgListNode,protObj,endpoint,0);
        returnString = indentString(funcNameStr + funcArgStr,indentLevel);

    elif (astNode.label == AST_FUNCTION_ARGLIST):
        returnString = '(';

        counter = 0;
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,0);
            counter +=1;
            
            if (counter != len(astNode.children)):
                returnString += ',';
        
        returnString += ')';
        returnString = indentString(returnString,indentLevel);

        
    elif (astNode.label == AST_ASSIGNMENT_STATEMENT):
        assignTo = astNode.children[0];
        idName = assignTo.value;
        idName = endpoint.varName(idName);
        lhsAssignString = idName + ' = ';
        

        rhsAssignString = runFunctionBodyInternalEmit(astNode.children[1],protObj,endpoint,0);
        returnString += indentString(lhsAssignString + rhsAssignString,indentLevel);
        returnString += '\n';

    elif (astNode.label == AST_FUNCTION_BODY_STATEMENT):
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,indentLevel);
        
    else:
        errMsg = '\nBehram error: in runFunctionBodyInternalEmit ';
        errMsg += 'do not know how to handle label ' + astNode.label + '\n';
        print(errMsg);


    return returnString;


