#!/usr/bin/env python


class TypeStack(object):
    IDENTIFIER_TYPE_SHARED = 0;
    IDENTIFIER_TYPE_ENDPOINT_GLOBAL = 1;
    IDENTIFIER_TYPE_MSG_SEQ_GLOBAL = 2;
    IDENTIFIER_TYPE_FUNCTION_ARGUMENT = 3;
    IDENTIFIER_TYPE_LOCAL = 4;
    
    def __init__(self):
        self.stack     = []; #last element in array is always top of stack.

    def pushContext(self):
        self.stack.append(Context());


    def popContext(self):
        if (len(self.stack) <= 0):
            print('\nBehram Error.  Empty type context stack.  Cannot pop\n');
            assert(False);
        self.stack.pop();


    def addIdentifier(self,identifierName,identifierType,isMutable):
        '''
        @see Context.addIdentifier
        '''
        if len(self.stack) <= 0:
            print('\nBehram Error.  Empty type context stack.  Cannot addId\n');
            assert(False);

        return self.stack[-1].addIdentifier(identifierName,identifierType,isMutable);
        

class Context(object):
    def __init__(self):
        # dict from identifier name to NameTypeTuple-s, 
        self.dict = {};
        
    def identifierExists(self,identifierName):
        '''
        @returns None if identifierName does not exist in this context
                 NameTypeTuple otherwise
        '''
        val = self.dict.get(identifierName,None);
        return val;
        
    def addIdentifier(self,identifierName,identifierType,isMutable):
        '''
        @param {String} identifierName
        
        @param {Int} One of TypeStack.IDENTIFIER_TYPE*-s Indicates
        what type of variable this is in the local context.
        '''
        ntt = NameTypeTuple(identifierName,identifierType,isMutable);
        self.dict[identifierName] = ntt;
        return ntt;
        


class NameTypeTuple(object):
    def __init__(self,varName,varType,isMutable):
        '''
        @param {String} varName
        @param {Int} varType --- TypeStack.IDENTIFIER_TYPE_*;
        
        @param {Bool} True if variable is a list or map, false
        otherwise.
        '''
        self.varName = varName;
        self.varType = varType;
        self.mutable = isMutable;
