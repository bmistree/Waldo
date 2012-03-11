#!/usr/bin/python

from astLabels import TYPE_BOOL;
from astLabels import TYPE_STRING;
from astLabels import TYPE_NUMBER;


class TypeCheckContextStack():
    def __init__ (self):
        self.stack = []; #last element in array is always top of stack.

        #also contains additional data
        self.protObjName = None;
        self.endpoint1 = None;
        self.endpoint2 = None;
        self.endpoint1LineNo = None;
        self.endpoint2LineNo = None;
        
    def pushContext(self):
        self.stack.append(Context());
    def popContext(self):
        if (len(self.stack) <= 0):
            print('\nError.  Empty type context stack.  Cannot pop\n');
            assert(False);
        self.stack.pop();

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

    def addIdentifier(self,identifierName,identifierType,lineNum = None):

        if(len(self.stack) <= 1):
            print('\nError.  Cannot insert into type check stack because stack is empty.\n');
            assert(False);

        self.stack[-1].addIdentifier(identifierName,identifierType,lineNum);



class Context():
    def __init__(self):
        self.dict = {};

    def getIdentifierType(self,identifierName):
        '''
        @returns None if doesn't exist.
        '''
        val = self.dict.get(identifierName,None);
        if (val == None):
            return val;
        
        return val.getType();

        
    def addIdentifier(self,identifierName,identifierType,lineNum):
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

        self.dict[identifierName] = ContextElement(identifierType,lineNum);

        
class ContextElement():
    def __init__ (self,identifierType,lineNum):
        self.identifierType = identifierType;
        self.lineNum = lineNum;

    def getType(self):
        return self.identifierType;

    def getLineNum(self):
        return self.lineNum;
