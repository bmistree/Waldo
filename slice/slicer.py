#!/usr/bin/env python

import sys;
import os;

curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','parser','ast'));
sys.path.append(os.path.join(curDir,'..','parser','ast','typeCheck'));

from astLabels import *;
from typeStack import TypeStack;
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

        aliasSecNode = node.children[1];
        end1Name = aliasSecNode.children[0].value;
        end2Name = aliasSecNode.children[1].value;
        
        typeStack1 = TypeStack(typeStack);
        typeStack1.addEndpointName(end1Name);
        typeStack1.addEndpointName(end2Name);
        
        typeStack2 = TypeStack(typeStack);
        typeStack2.addEndpointName(end1Name);
        typeStack2.addEndpointName(end2Name);
        

        # both typestacks should hold shared variables...so load each
        slicer(sharedSecNode,functionDeps,typeStack1);
        slicer(sharedSecNode,functionDeps,typeStack2);

        # now go through each endpoint node
        endpoint1Node = node.children[4];
        slicer(endpoint1Node,functionDeps,typeStack1);
        
        endpoint2Node = node.children[5];
        slicer(endpoint2Node,functionDeps,typeStack2);

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
        fDep = FunctionDeps(funcName);
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
        
        typeStack.addFuncCall(funcCallName,funcArgReads);

        
    elif node.label == AST_ASSIGNMENT_STATEMENT:
        # left-hand side can only be a bracket statement or an
        # identifier according to type checking.
        lhsNode = node.children[0];
        rhsNode = node.children[1];
        if lhsNode.label == AST_IDENTIFIER:
            nodeName = lhsNode.value;
            readIndex = typeStack.getReadIndex();
            slicer(rhsNode,functionDeps,typeStack);
            
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
            typeStack.addIdentifier(nameNode.value,
                                    isMutable(typeNode),
                                    TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT,
                                    argumentNumber);
            argumentNumber +=1;

    elif node.label == AST_IDENTIFIER:
        identifierName = node.value;

        if not typeStack.isEndpointName(identifierName):
            ntt = typeStack.getIdentifier(identifierName);
            typeStack.addRead(ntt);

    elif node.label == AST_FUNCTION_CALL:
        # warnMsg = '\nBehram error: need to write something ';
        # warnMsg += 'intelligent for slicing function call.\n';
        # print(warnMsg);
        pass;
            
    elif node.label == AST_DECLARATION:
        nodeTypeNode = node.children[0];
        nodeName = node.children[1].value;
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

    else:
        print('\nBehram error: still need to process label for ' + node.label + '\n');
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    printWarning();
    return functionDeps;


HavePrinted = False;
def printWarning():
    global HavePrinted;
    if not HavePrinted:
        warnMsg = '\nBehram error: need to write something ';
        warnMsg += 'intelligent for slicing function call.\n';
        print(warnMsg);
        warnMsg = '\nBehram error: still need to write something ';
        warnMsg += 'intelligent for message sequences.\n';
        print(warnMsg);

        warnMsg = '\nBehram error: still need to handle returns\' ';
        warnMsg += 'subsequently being written to in mega-'
        warnMsg += 'constructor in functionDeps.py.\n';
        print(warnMsg);

        warnMsg = '\nBehram error: handle post-it problem on ';
        warnMsg += 'second monitor.\n';
        print(warnMsg);
        
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
