#!/usr/bin/env python


class TypeStack(object):
    IDENTIFIER_TYPE_SHARED = 0;
    IDENTIFIER_TYPE_ENDPOINT_GLOBAL = 1;
    IDENTIFIER_TYPE_MSG_SEQ_GLOBAL = 2;
    IDENTIFIER_TYPE_FUNCTION_ARGUMENT = 3;
    IDENTIFIER_TYPE_LOCAL = 4;
    
    def __init__(self,prevStack=None):
        self.stack  = []; #last element in array is always top of stack.

        if prevStack != None:
            for ctx in prevStack.stack:
                self.stack.append(ctx);

        
    def pushContext(self,labelAs,currentFunctionDep):
        self.stack.append(Context(labelAs,currentFunctionDep));


    def popContext(self):
        self.checkStackLen('popContext');
        self.stack.pop();

    def addIdentifier(self,identifierName,isMutable,identifierType=None):
        '''
        @see Context.addIdentifier
        '''
        topStack = self.checkStackLen('addIdentifier');        
        return topStack.addIdentifier(identifierName,isMutable,identifierType);


    def addToVarReadSet(self,nodeName,ntt):
        '''
        If we are inside a function, ensure that that function is
        labeled to know that variable with nodeName is a variable
        inside of it.  ntt is NameTypeTuple, which has information on
        the name of the variable, its type, and whether it's mutable
        or not.
        '''
        topStack = self.checkStackLen('addToVarReadSet');                
        curFuncDep = topStack.currentFunctionDep;
        if curFuncDep != None:
            # happened inside a function instead of happening
            # inside of an endpoint global section.
            curFuncDep.addToVarReadSet(nodeName,ntt);

            
    def addReadsWritesToVarReadSet(self,nodeName,reads,writes):
        '''
        If we are inside of a function, then tell the function that
        variable with name nodeName relies on reads and writes from
        the NodeNameTuples populating the arrays reads and writes.
        '''
        topStack = self.checkStackLen('addReadsWritesToVarReadSet');
        curFuncDep = topStack.currentFunctionDep;
        if curFuncDep != None:
            # happened inside a function instead of happening
            # inside of an endpoint global section.
            curFuncDep.addReadsWritesToVarReadSet(nodeName,reads,writes);


    def getReadIndex(self):
        '''
        @see getReadIndex of Context
        '''
        stackTop = self.checkStackLen('getReadIndex');
        return stackTop.getReadIndex();

    def getWriteIndex(self):
        '''
        @see getReadIndex of Context
        '''
        stackTop = self.checkStackLen('getWriteIndex');
        return stackTop.getWriteIndex();

    def getReadsAfter(self,afterPoint):
        '''
        @see getReadIndex of Context
        '''
        stackTop = self.checkStackLen('getReadsAfter');
        return stackTop.getReadsAfter(afterPoint);
    
    def getWritesAfter(self,afterPoint):
        '''
        @see getReadIndex of Context
        '''
        stackTop = self.checkStackLen('getWritesAfter');
        return stackTop.getWritesAfter(afterPoint);

    def checkStackLen(self,operatioName):
        if len(self.stack) <= 0:
            errMsg = '\nBehram error.  Stack underflow when trying ';
            errMsg += 'to perform operation ' + operationName + '.\n';
            print(errMsg);
            assert(False);
        return self.stack[-1];
    
    

class Context(object):
    def __init__(self,labelAs,currentFunctionDep):
        '''
        currentFunctionDep can be None if getting shared or globals.
        '''
        # dict from identifier name to NameTypeTuple-s, 
        self.dict = {};
        self.reads = [];
        self.writes = [];
        self.labelAs = labelAs;
        self.currentFunctionDep = currentFunctionDep;


    def getReadIndex(self):
        '''
        want to support the semantics: 'get all reads after some
        point'.  This let's us name that starting point.  Then, can
        call getReadsAfter to get all reads that happened between now
        and when getReadIndex was called.
        '''
        return len(self.reads);

    def getReadsAfter(self,afterPoint):
        '''
        @see getReadIndex
        '''
        return self.reads[afterPoint:];

    
    def getWriteIndex(self):
        '''
        @see getReadIndex
        '''
        return len(self.writes);

    def getWritesAfter(self,afterPoint):
        '''
        @see getReadIndex
        '''        
        return self.writes[afterPoint:];
        
    def addRead(self,ntt):
        self.reads.append(ntt);
    def addWrite(self,ntt):
        self.writes.append(ntt);
        
    def identifierExists(self,identifierName):
        '''
        @returns None if identifierName does not exist in this context
                 NameTypeTuple otherwise
        '''
        val = self.dict.get(identifierName,None);
        return val;
        
    def addIdentifier(self,identifierName,isMutable,identifierType):
        '''
        @param {String} identifierName
        
        @param {Int} One of TypeStack.IDENTIFIER_TYPE*-s Indicates
        what type of variable this is in the local context.  None if
        just supposed to use the label that is being saved in labelAs.
        '''
        if identifierType == None:
            identifierType = self.labelAs;
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
