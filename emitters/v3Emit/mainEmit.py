#!/usr/bin/env python

import sys;
import os;
import emitUtils;

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;

sys.path.append(os.path.join(curDir,'..','..','slice','typeStack'));
from typeStack import TypeStack;


def emit(astNode,fdepDict):
    returner = '';


    if astNode.label == AST_ANNOTATED_DECLARATION:
        # it's a shared variable
        #   shared{ Nothing controls someNum = 0;}
        #   self._committedContext.shareds['1__someNum'];
        identifierNode = astNode.children[2];
        returner += emit(identifierNode,fdepDict);
        
        if len(astNode.children) == 4:
            # means have initialization information
            returner += ' = ';
            returner += emit(astNode.children[3],fdepDict);

    elif astNode.label == AST_IDENTIFIER:
        astNode._debugErrorIfHaveNoAnnotation(
            'mainEmit.emit: identifier');

        idAnnotationName = astNode.sliceAnnotationName;
        idAnnotationType = astNode.sliceAnnotationType;

        if idAnnotationType == TypeStack.IDENTIFIER_TYPE_LOCAL:
            returner += identifierNode.value + ' ';
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL:
            returner += "self._committedContext.endGlobals['";
            returner += idAnnotationName + "'] ";
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL:
            returner += "self._committedContext.seqGlobals['";
            returner += idAnnotationName + "'] ";
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_SHARED:
            returner += "self._committedContext.shareds['";
            returner += idAnnotationName + "'] ";            
        else:
            errMsg = '\nBehram error: incorrect annotation type for ';
            errMsg += 'declared variable in emit of mainEmit.\n';
            print(errMsg);
            assert(False);        

    elif astNode.label == AST_DECLARATION:
        # could either be a shared or local variable.  use annotation
        # to determine.
        identifierNode = astNode.children[1];
        returner += emit(identifierNode,fdepDict);
        if len(astNode.children) == 3:
            # includes initialization information
            initializationNode = astNode.children[2];
            returner += ' = ';
            returner += emit(initializationNode,fdepDict);

    elif astNode.label == AST_BOOL:
        returner +=  astNode.value + ' ';
        
    elif astNode.label == AST_STRING:
        returner += "'"  + astNode.value + "' ";
        
    elif astNode.label == AST_NUMBER:
        returner += astNode.value + ' ';

    elif astNode.label == AST_LIST:
        # handle list literal
        returner += '[ ';
        for child in astNode.children:
            returner += emit(child,fdepDict);
            returner += ', ';
        returner += '] ';

    elif astNode.label == AST_MAP:
        # handle map literal
        returner += '{ ';
        for mapLiteralItem in astNode.children:
            returner += emit(mapLiteralItem,fdepDict);
            returner += ', ';
        returner += '} ';
        
    elif astNode.label == AST_MAP_ITEM:
        # individual entry of map literal
        keyNode = astNode.children[0];
        valNode = astNode.children[1];
        
        keyText = emit(keyNode,fdepDict);
        valText = emit(valNode,fdepDict);
        returner += keyText + ': ' + valText;

    elif _isBinaryOperatorLabel(astNode.label):
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];

        lhsText = emit(lhsNode,fdepDict);
        rhsText = emit(rhsNode,fdepDict);
        operatorText = _getBinaryOperatorFromLabel(astNode.label);

        returner += lhsText + operatorText + rhsText;
        
    else:
        errMsg = '\nBehram error: emitting for unknown label: ';
        errMsg += astNode.label + '\n';
        print(errMsg);
    


    return returner;



def _isBinaryOperatorLabel(nodeLabel):
    '''
    @param {String} nodeLabel --- The label field of an ast node.

    @returns {Bool} True if the label represents a binary operation,
    False otherwise.

    '''
    
    if nodeLabel in _getBinaryOperatorLabelDict():
        return True;
    return False;


def _getBinaryOperatorFromLabel(nodeLabel):
    binOperatorDict =  _getBinaryOperatorLabelDict();
    operator = binOperatorDict.get(nodeLabel,None);
    if operator == None:
        errMsg = '\nBehram error: requesting binary operator ';
        errMsg += 'information for non-binary operator.\n';
        print(errMsg);
        assert(False);
    return operator;

def _getBinaryOperatorLabelDict():
    '''
    Helper function for _isBinaryOperatorLabel and
    _getBinaryOperatorFromLabel
    '''
    binaryOperatorLabels = {
        # arithmetic
        AST_PLUS: '+',
        AST_MINUS: '-',
        AST_DIVIDE: '/',
        AST_MULTIPLY: '*',

        # boolean
        AST_AND: 'and',
        AST_OR: 'or',
        
        # comparison
        AST_BOOL_EQUALS: '==',
        AST_BOOL_NOT_EQUALS: '!=',
        AST_GREATER_THAN: '>',
        AST_GREATER_THAN_EQ: '>=',
        AST_LESS_THAN: '<',
        AST_LESS_THAN_EQ: '<='
        };
    return binaryOperatorLabels;




