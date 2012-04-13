#!/usr/bin/python

from astLabels import TYPE_BOOL;
from astLabels import TYPE_STRING;
from astLabels import TYPE_NUMBER;
from astLabels import TYPE_NOTHING;
from astLabels import TYPE_MSG_SEND_FUNCTION;
from astLabels import TYPE_MSG_RECEIVE_FUNCTION;



class TypeCheckContextStack():
    def __init__ (self):
        self.stack     = []; #last element in array is always top of stack.
        self.funcStack = [];
        
        #also contains additional data
        self.protObjName = None;
        self.endpoint1 = None;
        self.endpoint2 = None;
        self.endpoint1LineNo = None;
        self.endpoint2LineNo = None;
        
    def pushContext(self):
        self.stack.append(Context());
        self.funcStack.append(FuncContext());
    def popContext(self):
        if (len(self.stack) <= 0):
            print('\nError.  Empty type context stack.  Cannot pop\n');
            assert(False);
        self.stack.pop();
        self.funcStack.pop();
        
    def getIdentifierType(self,identifierName):
        '''
        @param {String} identifierName The name of the identifier that
        we're looking up in the memory store.

        @returns None if have no type information for that identifier.
        String with type name otherwise.  Typenames come from
        AST_LABELS file....maybe.
        '''
        for s in reversed(range(0,len(self.stack))):
            lookupType= self.stack[s].getIdentifierType(identifierName);
            if (lookupType != None):
                return lookupType;
        return None;


    def getIdentifierElement(self,identifierName):
        '''
        @param {String} identifierName The name of the identifier that
        we're looking up in the memory store.

        @returns None if have no type information for that identifier.
        Otherwise, returns ContextElement
        '''
        for s in reversed(range(0,len(self.stack))):
            lookupType= self.stack[s].getIdentifierElement(identifierName);
            if (lookupType != None):
                return lookupType;
        return None;


    def setShouldReturn(self,typeToReturn):
        '''
        @param {string} typeToReturn
        
        Any return statements that are made within the current context
        should have the type typeToReturn.
        '''
        if (len(self.stack) <= 0):
            errMsg = '\nError.  Empty type context stack.  ';
            errMsg += 'Cannot set value should be returning\n';
            print(errMsg);
            assert(False);

        self.stack[-1].setShouldReturn(typeToReturn);

    def getShouldReturn(self):
        if (len(self.stack) <= 0):
            errMsg = '\nError.  Empty type context stack.  ';
            errMsg += 'Cannot set value should be returning\n';
            print(errMsg);
            assert(False);
        
        return self.stack[-1].getShouldReturn();

    
    def getFuncIdentifierType(self,identifierName):
        '''
        @returns {FuncMatch object or None}
           -None if there is no declared function with same name
           -FuncMatch object if there is a function with the same name.
        '''
        for s in reversed(range(0,len(self.funcStack))):
            lookupType = self.funcStack[s].getFuncIdentifierType(identifierName);
            if (lookupType != None):
                return lookupType;

        return None;

    
    def addIdentifier(self,identifierName,identifierType,astNode,lineNum = None):

        if(len(self.stack) <= 1):
            print('\nError.  Cannot insert into type check stack because stack is empty.\n');
            assert(False);
            
        self.stack[-1].addIdentifier(identifierName,identifierType,astNode,lineNum);

    def isEndpoint(self,endpointName):
        return ((endpointName == self.endpoint1) or (endpointName == self.endpoint2));

    def addFuncIdentifier(self,functionName,functionType,functionArgTypes,astNode,lineNum=None):
        '''
        @param {string} functionName: name of function
        @param {string} functionType:
        @param {list} functionArgTypes: ordered (from left to right)
        list of types for function arguments.
        @param {int} lineNum: line number that function was declared on.
        '''
        if(len(self.funcStack) <= 1):
            print('\nError.  Cannot insert into type check stack because stack is empty.\n');
            assert(False);

        self.funcStack[-1].addFuncIdentifier(functionName,functionType,functionArgTypes,astNode,lineNum);

        
class FuncContext():
    def __init__(self):
        self.dict = {};

    def getFuncIdentifierType(self,funcIdentifierName):
        '''
        @returns None if doesn't exist
        '''
        val = self.dict.get(funcIdentifierName,None);
        if (val == None):
            return val;
        
        return val.getFuncMatchObject();


    def addFuncIdentifier(self,funcIdentifierName,funcIdentifierType,funcArgTypes,astNode,lineNum):
        '''
        If identifier already exists in this context, throw an error.
        Cannot have re-definition of existing type.
        '''
        if (self.getFuncIdentifierType(funcIdentifierName) != None):
            #Fixme: this should turn into a more formal error-reporting system.
            print('\nError, overwriting existing type with name ' + funcIdentifierName + '\n');
            assert(False);

        #note: if appending to this condition, will have to import
        #additional types at top of file.
        if ((funcIdentifierType != TYPE_BOOL)   and
            (funcIdentifierType != TYPE_NUMBER) and
            (funcIdentifierType != TYPE_STRING) and
            (funcIdentifierType != TYPE_NOTHING) and
            (funcIdentifierType != TYPE_MSG_SEND_FUNCTION) and
            (funcIdentifierType != TYPE_MSG_RECEIVE_FUNCTION)):
            
            print('\nError.  Unrecognized identifierType insertion: ' + funcIdentifierType + '\n');
            assert(False);

        self.dict[funcIdentifierName] = FuncContextElement(funcIdentifierType,funcArgTypes,astNode,lineNum);


        
class FuncContextElement():
    def __init__ (self,funcIdentifierType,funcArgTypes,astNode,lineNum):
        self.funcIdentifierType = funcIdentifierType;
        self.funcArgTypes = funcArgTypes;
        self.astNode = astNode;
        self.lineNum = lineNum;


    def getFuncMatchObject(self):
        '''
        @returns {FuncMatchObject} 
        '''
        return FuncMatchObject(self);


    #FIXME: make consistent with astNode.  In one place, using
    #lineNum, in another, lineNo.
    def getLineNum(self):
        return self.lineNum;

class FuncMatchObject():
    def __init__(self,funcContextElement):
        self.element = funcContextElement;

    def matches(self,funcIdentifierType,funcArgTypes):

        if (funcIdentifierType != self.element.funcIdentifierType):
            return False;

        if (len(funcArgTypes) != len(self.element.funcArgTypes)):
            return False;

        for s in range(0,len(funcArgTypes)):
            if (funcArgTypes[s] != self.element.funcArgTypes[s]):
                return False;
        
        return True;

    def getReturnType(self):
        return self.element.funcIdentifierType;
    
        
        
class Context():
    def __init__(self):
        self.dict = {};
        self.typeToReturn = None;


    def setShouldReturn(self,typeToReturn):
        self.typeToReturn = typeToReturn;

    def getShouldReturn(self):
        return self.typeToReturn;

        
    def getIdentifierElement(self,identifierName):
        '''
        @returns None if doesn't exist.
        '''
        val = self.dict.get(identifierName,None);
        return val;

        
    def getIdentifierType(self,identifierName):
        '''
        @returns None if doesn't exist.
        '''

        returner = self.getIdentifierElement(identifierName);
        if (returner):
            return returner.getType();
        return returner;
        
        
    def addIdentifier(self,identifierName,identifierType,astNode,lineNum):
        '''
        If identifier already exists in this context, throw an error.
        Cannot have re-definition of existing type.
        '''
        if (self.getIdentifierType(identifierName) != None):
            #Fixme: this should turn into a more formal error-reporting system.
            print('\nError, overwriting existing type with name ' + identifierName + '\n');
            assert(False);

        #note: if appending to this condition, will have to import
        #additional types at top of file.
        if ((identifierType != TYPE_BOOL) and (identifierType != TYPE_NUMBER) and (identifierType != TYPE_STRING)):
            print('\nError.  Unrecognized identifierType insertion: ' + identifierType + '\n');
            assert(False);

        self.dict[identifierName] = ContextElement(identifierType,astNode,lineNum);

        
class ContextElement():
    def __init__ (self,identifierType,astNode,lineNum):
        self.identifierType = identifierType;
        self.astNode = astNode;
        self.lineNum = lineNum;


    def getType(self):
        return self.identifierType;

    def getLineNum(self):
        return self.lineNum;
