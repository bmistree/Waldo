#!/usr/bin/env python

import sys;
import os;

curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','parser','ast'));

from astLabels import *;
from typeStack import TypeStack;

def slicer(node,functionDeps=None,typeStack=None,labelAs=None,reads=None,writes=None,currentFunctionDep=None):
    '''
    @param{AstNode} node --- An astNode
    
    @param{None or array} functionDeps --- An array of FunctionDep
    classes.  Each one mentions which variables the function depends
    on.  Should only be none for initial call.

    @param{Int or None} labelAs --- TypeStack.IDENTIFIER_TYPE_*.  
    
    @returns{Array} (functionDeps).
    '''
    
    if functionDeps == None:
        if node.label != AST_ROOT:
            errMsg = '\nBehram error in slicer.  Should only ';
            errMsg += 'have empty functionDeps on root node.\n';
            print(errMsg);
            assert(False);
        functionDeps = [];
        typeStack = TypeStack();
        
    if node.label == AST_ROOT:
        sharedSecNode = node.children[3];
        slicer(sharedSecNode,functionDeps,typeStack,labelAs,[],[],currentFunctionDep);
        print('\nMore to do here\n');
    elif node.label == AST_SHARED_SECTION:
        # add a context that never gets removed.
        typeStack.pushContext();
        prevLabelAs = labelAs;
        labelAs = TypeStack.IDENTIFIER_TYPE_SHARED;
        for sharedDeclNode in node.children:
            slicer(sharedDeclNode,functionDeps,typeStack,labelAs,[],[],currentFunctionDep);
        labelAs = prevLabelAs;

    elif node.label == AST_ANNOTATED_DECLARATION:
        idName = node.children[2].value;
        typeNode = node.children[1];
        typeStack.addIdentifier(idName,labelAs,isMutable(typeNode));

    elif node.label == AST_PUBLIC_FUNCTION:
        funcName = node.children[0].value;
        funcBodyNode = node.children[2];
        
        fDep = FunctionDeps(funcName);
        functionDeps.append(fDep);

        print('\nBehram errror.  Should populate arguments to functions here.\n');

        typeStack.pushContext();
        prevLabelAs = labelAs;
        prevReads = reads;
        prevWrites = writes;
        reads = [];
        writes = [];
        for child in funcBodyNode:

            slicer(child,functionDeps,typeStack,labelAs,TypeStack.IDENTIFIER_TYPE_LOCAL,
                   reads,writes,fDep);

        labelAs = prevLabelAs;
        reads = prevReads + reads;
        writes = prevWrites + writes;
        typeStack.popContext();
        
        
    elif node.label == AST_DECLARATION:
        if labelAs == None:
            errMsg = '\nBehram error: labelAs should not be None.\n';
            print(errMsg);
            assert(False);
        nodeTypeNode = node.children[0];
        nodeName = node.children[1].value;
        ntt = typeStack.addIdentifier(nodeName,labelAs,isMutable(nodeTypeNode));
        if len(node.children) == 3:
            # means that we are initializing it too.
            prevReads = reads;
            prevWrites = writes;
            
            reads = [];
            writes = [];
            slicer(node.chidlren[2],functionDeps,typeStack,labelAs,reads,writes,currentFucntionDep);
            if currentFunctionDep != None:
                # this declaration happened inside a function instead of happening
                # inside of an endpoint global section.
                currentFunctionDep.addToVarReadSet(nodeName,ntt);
                currentFunctionDep.addReadsWritesToVarReadSet(nodeName,reads,writes);

            if prevReads != None:
                reads = reads + prevReads;
            if prevWrites != None:
                writes = writes + prevWrites;
    else:
        print('\nBehram error: still need to process label for ' + node.label + '\n');
        for child in node.children:
            slicer(child,functionDeps,typeStack,labelAs,reads,writes,currentFunctionDep);
            
    return functionDeps;


def isMutable(nodeTypeNode):
    '''
    @returns{Bool} True if typeNode indicates this is a map or a list.
    False otherwise.
    '''
    print('\nBehram error, still need to define isMutable in slicer.py\n');
    return True;
