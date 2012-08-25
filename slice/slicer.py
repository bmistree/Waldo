#!/usr/bin/env python

import sys;
import os;

curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','parser','ast'));
sys.path.append(os.path.join(curDir,'..','parser','ast','typeCheck'));

from astLabels import *;
from typeStack import TypeStack;
from typeStack import NameTypeTuple;
from functionDeps import FunctionDeps;
import templateUtil;

def slicer(node,functionDeps=None,typeStack=None):
    '''
    @param{AstNode} node --- An astNode
    
    @param{None or array} functionDeps --- An array of FunctionDep
    classes.  Each one mentions which variables the function depends
    on.  Should only be none for initial call.
    
    @returns{Array} (functionDeps).
    '''
    
    if functionDeps == None:
        if node.label != AST_ROOT:
            errMsg = '\nBehram error in slicer.  Should only ';
            errMsg += 'have empty functionDeps on root node.\n';
            print(errMsg);
            assert(False);
        functionDeps = [];
        
        
    if node.label == AST_ROOT:
        # create two separate type stacks for each endpoint
        sharedSecNode = node.children[3];

        endpoint1Node = node.children[4];
        endpoint2Node = node.children[5];
        
        end1Name = endpoint1Node.children[0].value;
        end2Name = endpoint2Node.children[0].value;
        
        typeStack1 = TypeStack(typeStack);
        typeStack1.addMyEndpointName(end1Name);
        typeStack1.addOtherEndpointName(end2Name);

        typeStack2 = TypeStack(typeStack);
        typeStack2.addMyEndpointName(end2Name);
        typeStack2.addOtherEndpointName(end1Name);

        # both typestacks should hold shared variables...so load each
        slicer(sharedSecNode,functionDeps,typeStack1);
        slicer(sharedSecNode,functionDeps,typeStack2);

        # now go through each endpoint node
        slicer(endpoint1Node,functionDeps,typeStack1);
        slicer(endpoint2Node,functionDeps,typeStack2);

        msgSeqSecNode = node.children[6];
        sliceMsgSeqSecNode(msgSeqSecNode,functionDeps,typeStack1,typeStack2);
        
    elif ((node.label == AST_ONCREATE_FUNCTION) or (node.label == AST_PUBLIC_FUNCTION) or
          (node.label == AST_PRIVATE_FUNCTION)):

        funcName = node.children[0].value;
        if node.label == AST_ONCREATE_FUNCTION:
            funcDeclArgsIndex = 1;
            funcBodyIndex = 2;
        elif (node.label == AST_PRIVATE_FUNCTION) or (node.label == AST_PUBLIC_FUNCTION):
            funcDeclArgsIndex = 2;
            funcBodyIndex = 3;
        else:
            errMsg = '\n\nBehram error.  Should only handle oncreate,private,public ';
            errMsg += 'functions in this branch of slicer.py.\n';
            print(errMsg);
            assert(False);

        # create a new function dependency on the stack.
        fDep = FunctionDeps(typeStack.hashFuncName(funcName));
        functionDeps.append(fDep);

        # set up new context so that identifiers that are added will
        # be added as function arguments.
        typeStack.pushContext(
            TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT,fDep);
        declArgsNode = node.children[funcDeclArgsIndex];
        slicer(declArgsNode,functionDeps,typeStack);

        # when go through function body, need to change label as of
        # type stack to be local so that subsequent identifiers that
        # are added are added as local.
        typeStack.changeLabelAs(TypeStack.IDENTIFIER_TYPE_LOCAL);
        funcBodyNode = node.children[funcBodyIndex];
        slicer(funcBodyNode,functionDeps,typeStack);
                
        typeStack.popContext();
        
    elif node.label == AST_ENDPOINT_GLOBAL_SECTION:
        # note: do not pop the context, because want globals to always
        # be available.
        typeStack.pushContext(TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL,None);
        for child in node.children:
            slicer(child,functionDeps,typeStack);
        
    elif node.label == AST_SHARED_SECTION:
        # add a context that never gets removed.
        typeStack.pushContext(TypeStack.IDENTIFIER_TYPE_SHARED,None);
        for sharedDeclNode in node.children:
            slicer(sharedDeclNode,functionDeps,typeStack);

            
    elif node.label == AST_ANNOTATED_DECLARATION:
        idName = node.children[2].value;
        typeNode = node.children[1];
        typeStack.addIdentifier(idName,isMutable(typeNode));

        # gets passed to emitter
        typeStack.annotateNode(node.children[2],idName);

        
    elif node.label == AST_RETURN_STATEMENT:
        # should keep track of all identifiers that could be touched
        # by returning.
        readIndex = typeStack.getReadIndex();
        for childNode in node.children:
            slicer(childNode,functionDeps,typeStack);
            
        returnStatementReads = typeStack.getReadsAfter(readIndex);
        typeStack.addReturnStatement(returnStatementReads);
        
    elif node.label == AST_FUNCTION_CALL:
        funcCallName = node.children[0].value;
        funcArgListNode = node.children[1];
        
        # an aray of arrays....each element array contains the reads
        # performed on the corresponding positional argument that gets
        # passed into the function.
        funcArgReads = [];
        for funcArgNode in funcArgListNode.children:

            readIndex = typeStack.getReadIndex();
            slicer(funcArgNode,functionDeps,typeStack);
            argumentReads = typeStack.getReadsAfter(readIndex);
            
            funcArgReads.append(argumentReads);
        
        typeStack.addFuncCall(
            typeStack.hashFuncName(funcCallName),funcArgReads);
        
    elif node.label == AST_ASSIGNMENT_STATEMENT:
        # left-hand side can only be a bracket statement or an
        # identifier according to type checking.
        lhsNode = node.children[0];
        
        rhsNode = node.children[1];
        if lhsNode.label == AST_IDENTIFIER:
            nodeName = lhsNode.value;
            readIndex = typeStack.getReadIndex();
            slicer(rhsNode,functionDeps,typeStack);

            # gets passed to emitter
            typeStack.annotateNode(lhsNode,nodeName);
            
            # contains all reads that may have been made from
            # executing rhs of code.
            readsMadeByRhs = typeStack.getReadsAfter(readIndex);

            # tell typeStack that this variable may get written to and
            # its written to value depends on the values that the rhs reads made.
            ntt = typeStack.getIdentifier(nodeName);
            typeStack.addToVarReadSet(ntt);
            typeStack.addReadsToVarReadSet(ntt,readsMadeByRhs);

        elif lhsNode.label == AST_BRACKET_STATEMENT:
            toReadFromNode = lhsNode.children[0];
            # toReadFromNode can either be an identifier or a function call
            if toReadFromNode.label == AST_IDENTIFIER:
                nodeName = toReadFromNode.value;
                readIndex = typeStack.getReadIndex();

                # gets passed to emitter
                typeStack.annotateNode(toReadFromNode,nodeName);
                
                slicer(rhsNode,functionDeps,typeStack);
                
                readsMadeByRhs = typeStack.getReadsAfter(readIndex);
                ntt = typeStack.getIdentifier(nodeName);
                typeStack.addToVarReadSet(ntt);
                typeStack.addReadsToVarReadSet(ntt,readsMadeByRhs);

                # add all identifiers to function that results from
                # accessing map identifier.
                # FIXME: lkjs; may add to read set.
                slicer(lhsNode,functionDeps,typeStack);
                indexNode = lhsNode.children[1];
                
            else:
                # NOTE: Based on current type checking rules in
                # typeCheck.py's switch statement for the assignment
                # statement, it is impossible to assign into an
                # element that is directly returned by a function
                # call.  (Eg.  funcCall()[1] = 2;) Therefore should
                # not go down this path.  If change rule in
                # typeCheck.py, then change this as well.
                errMsg = '\nBehram error: Type checking should have prevented ';
                errMsg += 'case where assigning to ';
                errMsg += "a function call's bracket index.\n";
                print(errMsg);
                assert(False);

        else:
            errMsg = '\nError in assignment statement.  LHS is only ';
            errMsg += 'allowed to be a bracket statement or identifier.\n';
            print(errMsg);
            assert(False);

    elif ((node.label == AST_STRING) or (node.label == AST_NUMBER) or
          (node.label == AST_BOOL)):
        # nothing to do on literals
        for child in node.children:
            slicer(child,functionDeps,typeStack);


    elif ((node.label == AST_AND) or (node.label == AST_OR) or
          (node.label == AST_BOOL_EQUALS) or (node.label == AST_BOOL_NOT_EQUALS) or
          (node.label == AST_GREATER_THAN) or (node.label == AST_GREATER_THAN_EQ) or
          (node.label == AST_LESS_THAN) or (node.label == AST_LESS_THAN_EQ) or
          (node.label == AST_PLUS) or (node.label == AST_MINUS) or
          (node.label == AST_MULTIPLY) or (node.label == AST_DIVIDE)):
        # nothing to do on binary operators
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif ((node.label == AST_PRINT) or (node.label == AST_CONDITION_STATEMENT) or
          (node.label == AST_IF_STATEMENT) or (node.label == AST_ELSE_IF_STATEMENTS) or
          (node.label == AST_ELSE_IF_STATEMENT) or (node.label == AST_ELSE_STATEMENT) or
          (node.label == AST_NOT_EXPRESSION) or (node.label == AST_BOOLEAN_CONDITION) or
          (node.label == AST_LIST)  or (node.label == AST_MAP) or
          (node.label == AST_BRACKET_STATEMENT)):
        # nothing to do on unary operators
        for child in node.children:
            slicer(child,functionDeps,typeStack);
            
    elif ((node.label == AST_FUNCTION_BODY_STATEMENT) or
          (node.label == AST_ENDPOINT) or
          (node.label == AST_ENDPOINT_BODY_SECTION) or
          (node.label == AST_ENDPOINT_BODY_SECTION) or
          (node.label == AST_ENDPOINT_FUNCTION_SECTION) or
          (node.label == AST_FUNCTION_BODY)):
        # nothing to do on these structural node labels.
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif node.label == AST_FUNCTION_DECL_ARGLIST:
        # actually add each argument to current type stack.
        argumentNumber = 0;
        for child in node.children:
            # each child is a function decl arg
            typeNode = child.children[0];
            nameNode = child.children[1];
            argName = nameNode.value;
            ntt = typeStack.addIdentifier(argName,
                                          isMutable(typeNode),
                                          TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT,
                                          argumentNumber);

            # gets passed to emitter
            typeStack.annotateNode(nameNode,argName);
            
            typeStack.addFuncArg(ntt);
            
            argumentNumber +=1;

            

    elif node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        # sliceMsgSeqSecNode already handles adding a function dep and
        # context.  so do not need to do that here.
        msgBodyNode = node.children[3];
        for childNode in msgBodyNode.children:
            slicer(childNode,functionDeps,typeStack);

    elif node.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        # sliceMsgSeqSecNode already handles adding a function dep and
        # context.  so do not need to do that here.
        msgBodyNode = node.children[2];
        for childNode in msgBodyNode.children:
            slicer(childNode,functionDeps,typeStack);
            
    elif node.label == AST_IDENTIFIER:
        identifierName = node.value;

        if not typeStack.isEndpointName(identifierName):
            ntt = typeStack.getIdentifier(identifierName);
            typeStack.addRead(ntt);

        # gets passed to emitter
        typeStack.annotateNode(node,identifierName);

            
    elif node.label == AST_DECLARATION:
        nodeTypeNode = node.children[0];
        nameNode = node.children[1];
        nodeName = nameNode.value;
        isMute = isMutable(nodeTypeNode);
        ntt = typeStack.addIdentifier(nodeName,isMute);
        if len(node.children) == 3:
            # means that we are initializing the declaration too.
            initializationNode = node.children[2];
            
            readIndex = typeStack.getReadIndex();
            slicer(initializationNode,functionDeps,typeStack);

            initializationReads = typeStack.getReadsAfter(readIndex);

            # tell current function that this node exists.
            typeStack.addToVarReadSet(ntt);
            
            # tell current function that this node has the read and
            # write sets below.
            ntt = typeStack.getIdentifier(nodeName);
            typeStack.addReadsToVarReadSet(
                ntt,initializationReads);
            
        # gets passed to emitter
        typeStack.annotateNode(nameNode,nodeName);


    else:
        print('\nBehram error: still need to process label for ' + node.label + '\n');
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    printWarning();
    return functionDeps;


def sliceMsgSeqSecNode(msgSeqSecNode,functionDeps,typeStack1,typeStack2):
    '''
    @param {AstNode} msgSeqSecNode --- with label msgSequenceSection...

    Runs through all message sequence nodes and adds their functions
    to functionDeps as well as their reads and writes to globals,
    locals, and shareds.
    '''
    for msgSeqNode in msgSeqSecNode.children:

        # pop context before exiting for loop.
        typeStack1.pushContext(TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,None);
        typeStack2.pushContext(TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,None);

        msgSeqFunctionsNode = msgSeqNode.children[2];

        # add the identifiers of sequence global variables
        # directly to each type stack.
        msgSeqGlobalsNode = msgSeqNode.children[1];
        for declGlobNode in msgSeqGlobalsNode.children:
            identifierNode = declGlobNode.children[1];
            identifierName = identifierNode.value;
            identifierTypeNode = declGlobNode.children[0];
            isMute = isMutable(identifierTypeNode);

            newNtt = typeStack1.addIdentifier(
                identifierName,isMute,TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL);
            
            typeStack2.addIdentifierAsNtt(newNtt);
            
            # does not matter which type stack annotates the node
            typeStack1.annotateNode(identifierNode,identifierName);


        # now grab any arguments to first function and insert them as
        # sequence globals.
        firstFuncNode = msgSeqFunctionsNode.children[0];
        firstFuncDeclArgsNode = firstFuncNode.children[2];
        functionArgs = [];
        for funcDeclArgNode in firstFuncDeclArgsNode.children:
            typeNode = funcDeclArgNode.children[0];
            isMute = isMutable(typeNode);
            identifierNode = funcDeclArgNode.children[1];
            identifierName = identifierNode.value;
            newNtt = typeStack1.addIdentifier(
                identifierName,isMute,TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT);
            
            typeStack2.addIdentifierAsNtt(newNtt);
            functionArgs.append(newNtt);

            # does not matter which type stack annotates the node
            typeStack2.annotateNode(identifierNode,identifierName);

            
        
        # want to ensure that the first function has all the
        # read/write dependencies.  Need to know which type stack to
        # use for it.
        firstFuncEndpointName = firstFuncNode.children[0].value;
        if firstFuncEndpointName == typeStack1.mEndpointName:
            firstFuncEndpointTypeStack = typeStack1;
            secondFuncEndpointTypeStack = typeStack2;
        elif firstFuncEndpointName == typeStack2.mEndpointName:
            firstFuncEndpointTypeStack = typeStack2;
            secondFuncEndpointTypeStack = typeStack1;
        else:
            errMsg = '\nBehram error.  could not match enpdoint specified ';
            errMsg += 'by function as "' + firstFuncEndpointName + '" to ';
            errMsg += 'existing type stack.\n';
            print(errMsg);
            assert(False);


        # now, run through each function.  Importantly, ensure that
        # all initializations of msg seq globals happens in first
        # function.  note: do not need to specially add arguments
        # because they're already in the context.
        for funcIndex in range(0,len(msgSeqFunctionsNode.children)):
            # for each function, go through

            typeStack = firstFuncEndpointTypeStack;
            otherTypeStack = secondFuncEndpointTypeStack;
            if funcIndex % 2 != 0:
                typeStack = secondFuncEndpointTypeStack;
                otherTypeStack = firstFuncEndpointTypeStack;

            funcNode = msgSeqFunctionsNode.children[funcIndex];
            funcName = funcNode.children[1].value;
            
            fDep = FunctionDeps(typeStack.hashFuncName(funcName));
            functionDeps.append(fDep);

            typeStack.pushContext(TypeStack.IDENTIFIER_TYPE_LOCAL,fDep);
            
            if funcIndex == 0:
                # special case the first function so that it contains
                # all the initializations of sequence globals
                for declGlobNode in msgSeqGlobalsNode.children:
                    slicer(declGlobNode,functionDeps,typeStack);

                # also, ensure that first function gets loaded with
                # its proper arguments.
                for funcArgNtt in functionArgs:
                    typeStack.addFuncArg(funcArgNtt);
                    
            # handle rest of function and body in slicer.
            slicer(funcNode,functionDeps,typeStack);

            # if there is a message receive function coming, then make
            # a function call to it explicitly.
            if funcIndex != (len(msgSeqFunctionsNode.children) -1):
                nextMsgFuncNode = msgSeqFunctionsNode.children[funcIndex+1];
                nextMsgName = nextMsgFuncNode.children[1].value;
                
                typeStack.addFuncCall(
                    otherTypeStack.hashFuncName(nextMsgName),
                    []);  # note, message sequence functions do not
                          # take any arguments, so can just pass blank
                          # array.

            # remove the context added for latest function.
            typeStack.popContext();
            
        # pop the pushed contexts
        typeStack1.popContext();
        typeStack2.popContext();



HavePrinted = False;
def printWarning():
    global HavePrinted;
    if not HavePrinted:
        # all of these concern less conservative slicing algorithm.
        # when/if decide to switch back to that, then need to
        # re-consider all these problems.
        
        # warnMsg = '\nBehram error: need to write something ';
        # warnMsg += 'intelligent for slicing function call.\n';
        # print(warnMsg);
        # warnMsg = '\nBehram error: still need to write something ';
        # warnMsg += 'intelligent for message sequences.\n';
        # print(warnMsg);

        # warnMsg = '\nBehram error: still need to handle returns\' ';
        # warnMsg += 'subsequently being written to in mega-'
        # warnMsg += 'constructor in functionDeps.py.\n';
        # print(warnMsg);

        # warnMsg = '\nBehram error: handle post-it problem on ';
        # warnMsg += 'second monitor.\n';
        # print(warnMsg);
        
        HavePrinted = True;
    
def isMutable(nodeTypeNode):
    '''
    @returns{Bool} True if typeNode indicates this is a map or a list.
    False otherwise.
    '''
    if nodeTypeNode.label == AST_TYPE:
        if templateUtil.isListType(nodeTypeNode.value):
            return True;
        if templateUtil.isMapType(nodeTypeNode.value):
            return True;

    return False;


def reset():
    '''
    Ensures that all static variables are reset to their original values.
    '''
    NameTypeTuple.staticId = 0;

