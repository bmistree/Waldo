#!/usr/bin/env python
import util;
import os;
import sys;

from waldo.parser.ast.astLabels import *

class TypeStack(object):
    IDENTIFIER_TYPE_SHARED = 0;
    IDENTIFIER_TYPE_ENDPOINT_GLOBAL = 1;
    IDENTIFIER_TYPE_MSG_SEQ_GLOBAL = 2;
    IDENTIFIER_TYPE_FUNCTION_ARGUMENT = 3;
    IDENTIFIER_TYPE_LOCAL = 4;
    IDENTIFIER_TYPE_FUNCTION_CALL = 5;
    IDENTIFIER_TYPE_RETURN_STATEMENT = 6;

    # note that arguments to message sequence nodes are also globals
    # for the message sequence.
    IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT = 7;
    IDENTIFIER_TYPE_ENDPOINT_NAME = 8;

    IDENTIFIER_TYPE_ONCOMPLETE_NODE = 9;
    IDENTIFIER_TYPE_FUNCTION_OBJECT_CALL = 10
    
    def __init__(self,prevStack=None):
        self.stack  = []; #last element in array is always top of stack.
        self.endNames = {};
        self.mEndpointName = None;
        
        if prevStack != None:
            for ctx in prevStack.stack:
                self.stack.append(ctx);

            self.endNames = prevStack.endNames;

    def addMyEndpointName(self,endName):
        self.mEndpointName = endName;
        self._addEndpointName(endName);

    def addOtherEndpointName(self,endName):
        self._addEndpointName(endName);
    
    def _addEndpointName(self,endName):
        self.endNames[endName] = True;
        
    def isEndpointName (self,toTest):
        val = self.endNames.get(toTest,None);
        if val == None:
            return False;
        return True;

    def annotateNode(self,node,identifierName):
        '''
        For emitting stage, need to know whether to access an
        identifier from shared/global/sequenc global context, etc.

        Also, for emitting, need a naming scheme that prevents
        collisions (@see description in /example/v3).  This will write
        an annotation onto an astNode providing both of these.
        
        @param {AstNode} node
        @param {String} identifierName
        '''

        if self.isEndpointName(identifierName):
            annotateType = TypeStack.IDENTIFIER_TYPE_ENDPOINT_NAME;
            node.setSliceAnnotation(
                NameTypeTuple.uniqueNameForEndpoints(),
                annotateType,
                self._translateIdentifierTypeToHumanReadable(annotateType));
            return;
        
        ntt = self.getIdentifier(identifierName);
        if ntt == None:
            errMsg = '\nBehram error in annotateNode.  type stack ';
            errMsg += 'must contain identifier name.\n';
            print(errMsg);
            assert(False);

        node.setSliceAnnotation(
            ntt.getUniqueName(),
            ntt.varType,
            self._translateIdentifierTypeToHumanReadable(ntt.varType));


    def annotateOnComplete(self,node,srcName):
        '''
        Each on complete node is annotated with the name of the
        corresponding function to call in the emitted code to get it
        to execute.
        '''
        if node.label != AST_ONCOMPLETE_FUNCTION:
            errMsg = '\nBehram error: Require oncomplete node for annotation.\n';
            print(errMsg);
            assert(False);

        annotationType = TypeStack.IDENTIFIER_TYPE_ONCOMPLETE_NODE;
        node.setSliceAnnotation(
            srcName,
            annotationType,
            self._translateIdentifierTypeToHumanReadable(annotationType));
            

    def _translateIdentifierTypeToHumanReadable(self,annotateTypeHumanReadable):
        '''
        Convert an annotation type from an integer to a prose string.
        '''
        if annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_SHARED:
            return '_shared_';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL:
            return '_end_global_';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL:
            return '_msg_seq_glbal_';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT:
            return '_fun_arg_';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_LOCAL:
            return '_local_';            
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL:
            return '_fun_call_';            
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_RETURN_STATEMENT:
            return '_return_';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT:
            return '_msg_seq_global_and_func_arg';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_ENDPOINT_NAME:
            return '_endpoint_';
        elif annotateTypeHumanReadable == TypeStack.IDENTIFIER_TYPE_ONCOMPLETE_NODE:
            return '_on_complete_';        
        
            
        errMsg = '\nBehram error in _translateIdentifierTypeToHumanReadable.  ';
        errMsg += 'Received an unknown type to translate.\n';
        print(errMsg);
        assert(False);

    def getTopStackIdentifierDict(self):
        '''
        Should only be used to copy shared section labels.
        '''
        topStack = self.checkStackLen('getTopStackIdentifierDict');
        return topStack.dict;
        
    def hashFuncName(self,funcName):
        '''
        @param {String} funcName
        '''
        if self.mEndpointName == None:
            errMsg = '\nBehram error: cannot hash function name ';
            errMsg += 'without and endpoint name.\n';
            print(errMsg);
            assert(False);

        return self.mEndpointName + '_-_-_' + funcName;

    def onCompleteHashFuncName(
        self,nextMsgName,msgSeqIdentifierNode):
        '''
        @param {String} nextMsgName
        @param {AstNode} identifier

        Challenge with oncomplete functions is that we need to ensure
        that when they are being emitted they have unique names.
        Unlike other functions, onCompletes are named "onComplete,"
        and therefore, we must do additional work to distinguish them.  

        We can uniquely name an onComplete function using the
        three-tuple onComplete_<enpdoint name>_<message sequence
        name>, and that is what we return.
        '''
        msgSeqName = msgSeqIdentifierNode.value;
        return '_onComplete_' + self.mEndpointName + '_' + msgSeqName;
        
        

    
    def getLabelAs(self):
        topStack = self.checkStackLen('changeLabelAs');
        return topStack.labelAs;
    
    def changeLabelAs(self,newLabelAs):
        topStack = self.checkStackLen('changeLabelAs');
        topStack.labelAs = newLabelAs;
        
    def pushContext(self,labelAs,currentFunctionDep):
        self.stack.append(Context(labelAs,currentFunctionDep));

    def popContext(self):
        self.checkStackLen('popContext');
        self.stack.pop();

    def addIdentifier(
        self,identifierName,isMutable,astNode,identifierType=None,
        argPosition=None):
        '''
        @see Context.addIdentifier
        '''
        topStack = self.checkStackLen('addIdentifier');        
        return topStack.addIdentifier(
            identifierName,isMutable,identifierType,argPosition,astNode);

    def addIdentifierAsNtt(self,ntt):
        topStack = self.checkStackLen('addIdentifierAsNtt');
        return topStack.addIdentifierAsNtt(ntt);

    

    def getIdentifier(self,identifierName):
        topStack = self.checkStackLen('getIdentifier');

        backwardsRange = range(0,len(self.stack));
        backwardsRange.reverse();
        for contextIndex in backwardsRange:
            context = self.stack[contextIndex];
            exists  = context.getIdentifier(identifierName);
            if exists != None:
                return exists;
        return None;

    def addToVarReadSet(self,ntt):
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
            curFuncDep.addToVarReadSet(ntt);

    def addFuncArg(self,ntt):
        '''
        add the ntt to latest function dependency as a function argument.
        '''
        topStack = self.checkStackLen('addFuncArg');
        curFuncDep = topStack.currentFunctionDep;
        if curFuncDep != None:
            curFuncDep.addFuncArg(ntt);
        else:
            errMsg = '\nBehram error.  Require having a current function ';
            errMsg += 'dependency in order to process function arguments.\n';
            print(errMsg);
            assert(False);

        
            
    def addReadsToVarReadSet(self,ntt,reads):
        '''
        ntt is the node that we are adding the reads for.  Ie, ntt is
        being written to, and its writes at least partially depend on
        the ntt-s in the array reads.
        
        If we are inside of a function, then tell the function that
        variable with ntt ntt relies on reads and writes from
        the NodeNameTuples populating the arrays reads and writes.
        '''
        topStack = self.checkStackLen('addReadsWritesToVarReadSet');
        curFuncDep = topStack.currentFunctionDep;
        if curFuncDep != None:
            # happened inside a function instead of happening
            # inside of an endpoint global section.
            curFuncDep.addReadsToVarReadSet(ntt,reads);

    def addRead(self,ntt):
        '''
        If we are inside of a function, then tell the function that
        the function relies on the attached ntt.
        '''
        topStack = self.checkStackLen('addReadsWritesToVarReadSet');
        topStack.addRead(ntt);

    def addFuncObjectCall(self,ntt):
        '''
        '''
        topStack = self.checkStackLen('addReadsWritesToVarReadSet');
        topStack.addFuncObjectCall(ntt)

        
    def addFuncCall(self,nameOfFunc,funcArgReads):
        '''
        @see FuncCallNtt for description of arguments.

        Called whenever code in Waldo function calls another function.
        '''
        topStack = self.checkStackLen('addFuncCall');
        return topStack.addFuncCall(nameOfFunc,funcArgReads);

    def addReturnStatement(self,returnReads):
        '''
        @see ReturnStatementNtt
        
        Called whenever code in source has a return statement.
        '''
        topStack = self.checkStackLen('addReturnStatement');
        return topStack.addReturnStatement(returnReads);
        
    
    def getReadIndex(self):
        '''
        @see getReadIndex of Context
        '''
        stackTop = self.checkStackLen('getReadIndex');
        return stackTop.getReadIndex();

    def getReadsAfter(self,afterPoint):
        '''
        @see getReadIndex of Context
        '''
        stackTop = self.checkStackLen('getReadsAfter');
        return stackTop.getReadsAfter(afterPoint);

   
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
        # dict from identifier name to NameTypeTuple-s, these contain
        # only local variables and arguments passed into function
        self.dict = {};

        # also contains func calls.
        self.reads = [];
        self.labelAs = labelAs;
        self.currentFunctionDep = currentFunctionDep;

    def addFuncObjectCall(self,ntt):
        return self.addRead(ntt.copyFunctionObjectCall())

                          
    def addFuncCall(self,nameOfFunc,funcArgReads):
        '''
        @see FuncCallNtt for description of arguments.
        
        Currently, treat ntt associated with func call the same way we
        treat an ntt associated with a read.
                
        @returns {FuncCallNtt} 
        '''
        ntt = FuncCallNtt(nameOfFunc,funcArgReads);
        self.reads.append(ntt);

        if self.currentFunctionDep != None:
            # happened inside a function instead of happening
            # inside of an endpoint global section.
            self.currentFunctionDep.addFuncCall(ntt);

    def addReturnStatement(self,returnReads):
        '''
        @see ReturnStatement ntt for description of arguments.

        @returns {ReturnStatementNtt}
        '''
        ntt = ReturnStatementNtt(returnReads);
        self.reads.append(ntt);
        if self.currentFunctionDep != None:
            self.currentFunctionDep.addReturnStatement(ntt);
        else:
            errMsg = '\nBehram error.  Should never get return ';
            errMsg += 'statement outside of a function definition.\n';
            print(errMsg);
            assert(False);
            
        
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

        
    def addRead(self,ntt):
        '''
        @param {NameTypeTuple} ntt.
        '''
        self.reads.append(ntt);

        if self.currentFunctionDep != None:
            # happened inside a function instead of happening
            # inside of an endpoint global section.
            self.currentFunctionDep.addFuncReads([ntt]);


    def getIdentifier(self,identifierName):
        '''
        @returns None if identifierName does not exist in this context
                 NameTypeTuple otherwise
        '''
        val = self.dict.get(identifierName,None);
        return val;
        
    def addIdentifier(
        self,identifierName,isMutable,identifierType,argPosition,astNode):
        '''
        @param {String} identifierName
        
        @param {Int} One of TypeStack.IDENTIFIER_TYPE*-s Indicates
        what type of variable this is in the local context.  None if
        just supposed to use the label that is being saved in labelAs.

        @param {Int or None} argPosition --- If identifierType is
        TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT, then also save
        the argument's position in the name type tuple.  Otherwise,
        save None
        '''
        if identifierType == None:
            identifierType = self.labelAs;
        ntt = NameTypeTuple(identifierName,identifierType,
                            isMutable,argPosition,astNode);

        
        self.dict[identifierName] = ntt;
        return ntt;

    def addIdentifierAsNtt(self,ntt):
        self.dict[ntt.varName] = ntt;
        return ntt;

    
    
    
class NameTypeTuple(object):

    # @see uniqueNameForEndpoints before changing initial value.
    # uniqueNameForEndpoints assumes that staticId can never be -1.
    staticId = 0;
    
    def __init__(self,varName,varType,isMutable,argPosition,astNode):
        '''
        @param {String} varName
        @param {Int} varType --- TypeStack.IDENTIFIER_TYPE_*;
        
        @param {Bool} isMutable --- True if variable is a list or map,
        false otherwise.

        @param {Int or None} argPosition --- If (and only if) this is
        a IDENTIFIER_TYPE_FUNCTION_ARGUMENT, then this will be an
        integer representing the zero-indexed position of the argument
        passed to the function.  Otherwise, it must be None.

        @param {AstNode} --- astNode...used to check if using external
        or not.
        '''
        self.varName = varName;
        self.varType = varType;
        self.mutable = isMutable;
        self.astNode = astNode;
        self._mark = False;

        self.id = NameTypeTuple.staticId;
        NameTypeTuple.staticId += 1;

        if ((argPosition != None) and
            (varType != TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT) and
            (varType != TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
            errMsg = '\nBehram error: should not receive an arg position ';
            errMsg += 'with a variable that is not a function argument.\n';
            print(errMsg);
            assert(False);

        self.argPosition = argPosition;

    def copyFunctionObjectCall(self):
        # make a copy of myself; should only be used for function
        # object calls
        returner = NameTypeTuple(
            self.varName,TypeStack.IDENTIFIER_TYPE_FUNCTION_OBJECT_CALL,
            self.mutable,self.argPosition, self.astNode)

        returner.id = self.id
        return returner
        
        
        
    @staticmethod
    def uniqueNameForEndpoints():
        '''
        Endpoint identifiers need unique names too.  (@see
        typeStack.annotateNode for a discussion of what a unique name
        does.)  What gets returned is guaranteed to not conflict with
        the unique name for any identifier that is not an endpoint
        name.
        '''
        return '-1__endpoint';
        
        
    def jsonize(self):
        returner = {};
        returner['id'] = self.id;
        returner['varName'] = self.varName;
        returner['varType'] = self.varType;
        returner['mutable'] = 1 if self.mutable else 0;
        returner['argPosition'] = -1 if self.argPosition == None else self.argPosition;
        
        return util.toJsonPretty(returner);

    def getUniqueName(self):
        return str(self.id) + '__' + self.varName;
        
    def mark(self):
        self._mark = True;
    def unmark(self):
        self._mark = False;
    def isMarked(self):
        return self._mark;

    
class ReturnStatementNtt(NameTypeTuple):
    def __init__(self,returnStatementReads):
        '''
        @param {Array} returnStatementReads --- each element is a
        NameTypeTuple.

        Corresponds to a return statement that 
        '''
        NameTypeTuple.__init__(
            self,'return statement',
            TypeStack.IDENTIFIER_TYPE_RETURN_STATEMENT,False,None,None);

        self.returnStatementReads = returnStatementReads;

        

class FuncCallNtt(NameTypeTuple):

    def __init__(self,nameOfFunc,funcArgReads):
        '''
        @param {String} nameOfFunc --- the name of a function that
        is being called.

        @param {Array of arrays} funcArgReads --- Each element of the
        array is an array that corresponds to the reads of the
        corresponding positional argument passed to the function call.
        For example, if funcArgReads is [a,b,c].  Then a is an array
        of NameTypeTuples that correspond to the reads made to provide
        this positional argument.
        '''
        NameTypeTuple.__init__(
            self,nameOfFunc,TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL,False,
            None,None);
        
        self.funcArgReads = funcArgReads;

    def hashSignature(self):
        '''
        @returns {String} --- generates a signature of this function
        call.  Only function calls to the same functions whose
        arguments have the read set should have the same signature.
        If two have the same signature, that means that the
        global/shared write and read sets of one will be the same as
        the global/shared write and read sets of the other.
        '''
        returner = str(self.varName) + '|_*_| ';
        for positionArgReads in self.funcArgReads:

            for readNtt in positionArgReads:
                if readNtt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL:
                    returner += readNtt.hashSignature();
                else:
                    returner += str(readNtt.id);
                returner += '-^-';

            
            returner += '&%&';
        
        return returner;
    
