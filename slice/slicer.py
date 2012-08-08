#!/usr/bin/env python

import sys;
import os;

curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','parser','ast'));

from astLabels import *;
from typeStack import TypeStack;
from functionDeps import FunctionDeps;

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

        typeStack1 = TypeStack(typeStack);
        typeStack2 = TypeStack(typeStack);
        # both typestacks should hold shared variables...so load each
        slicer(sharedSecNode,functionDeps,typeStack1);
        slicer(sharedSecNode,functionDeps,typeStack2);

        # now go through each endpoint node
        endpoint1Node = node.children[4];
        slicer(endpoint1Node,functionDeps,typeStack1);
        
        endpoint2Node = node.children[5];
        slicer(endpoint2Node,functionDeps,typeStack2);

        print('\nMore to do here\n');

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

        
    elif node.label == AST_PUBLIC_FUNCTION:
        funcName = node.children[0].value;
        funcBodyNode = node.children[2];

        fDep = FunctionDeps(funcName);
        functionDeps.append(fDep);

        print('\nBehram errror.  Should populate arguments to functions here.\n');

        typeStack.pushContext(TypeStack.IDENTIFIER_TYPE_LOCAL,fDep);
        for child in funcBodyNode.children:
            slicer(child,functionDeps,typeStack);

        typeStack.popContext();
        
        
    elif node.label == AST_DECLARATION:
        nodeTypeNode = node.children[0];
        nodeName = node.children[1].value;
        ntt = typeStack.addIdentifier(nodeName,isMutable(nodeTypeNode));
        if len(node.children) == 3:
            # means that we are initializing the declaration too.

            readIndex = typeStack.getReadIndex();
            writeIndex = typeStack.getWriteIndex();
            slicer(node.children[2],functionDeps,typeStack);

            initializationReads = typeStack.getReadsAfter(readIndex);
            initializationWrites = typeStack.getWritesAfter(writeIndex);

            # tell current function that this node exists.
            typeStack.addToVarReadSet(nodeName,ntt);
            # tell current function that this node has the read and
            # write sets below.
            typeStack.addReadsWritesToVarReadSet(
                nodeName,initializationReads,initializationWrites);

            
    else:
        print('\nBehram error: still need to process label for ' + node.label + '\n');
        for child in node.children:
            slicer(child,functionDeps,typeStack);
            
    return functionDeps;


def isMutable(nodeTypeNode):
    '''
    @returns{Bool} True if typeNode indicates this is a map or a list.
    False otherwise.
    '''
    print('\nBehram error, still need to define isMutable in slicer.py\n');
    return True;
