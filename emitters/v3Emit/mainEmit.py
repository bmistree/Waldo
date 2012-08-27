#!/usr/bin/env python

import sys;
import os;
import emitUtils;

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;
from astBuilderCommon import isEmptyNode;

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

        if ((idAnnotationType == TypeStack.IDENTIFIER_TYPE_LOCAL) or
            (idAnnotationType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT)):
            returner += astNode.value + ' ';
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL:
            returner += "_context.endGlobals['";
            returner += idAnnotationName + "'] ";
        elif ((idAnnotationType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL) or
              (idAnnotationType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
            returner += "_context.seqGlobals['";
            returner += idAnnotationName + "'] ";
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_SHARED:
            returner += "_context.shareds['";
            returner += idAnnotationName + "'] ";
        else:
            errMsg = '\nBehram error: incorrect annotation type for ';
            errMsg += 'declared variable in emit of mainEmit.\n';
            print(errMsg);
            print(idAnnotationType);
            assert(False);        

    elif astNode.label == AST_FUNCTION_CALL:
        returner += _emitFunctionCall(astNode,fdepDict);

            
    elif astNode.label == AST_ASSIGNMENT_STATEMENT:
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];
        returner += emit(lhsNode,fdepDict);
        returner += ' = ';
        returner += emit(rhsNode,fdepDict);

    elif astNode.label == AST_PRINT:
        toPrintNode = astNode.children[0];
        returner += 'print( ';
        returner += emit(toPrintNode,fdepDict);
        returner += ')';
        
        
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

    elif astNode.label == AST_FUNCTION_BODY_STATEMENT:
        for child in astNode.children:
            returner += emit(child,fdepDict);
        
    elif astNode.label == AST_MAP_ITEM:
        # individual entry of map literal
        keyNode = astNode.children[0];
        valNode = astNode.children[1];
        
        keyText = emit(keyNode,fdepDict);
        valText = emit(valNode,fdepDict);
        returner += keyText + ': ' + valText;

    elif astNode.label == AST_RETURN_STATEMENT:
        retStatementNode = astNode.children[0];

        if isEmptyNode(retStatementNode):
            toReturnStatementText = 'None';
        else:
            toReturnStatementText = emit(retStatementNode,fdepDict);

        # need to special-case return statement so that can notify
        # waiting blocking statement through return queue.
        returner +='''
# special-cased return statement
if _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE:
    # note that also commit outstanding changes to context here.
    _actEvent.setCompleted(%s,_context);
    return;
elif _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED:
    return %s;
''' % (toReturnStatementText,toReturnStatementText);
        
    elif _isBinaryOperatorLabel(astNode.label):
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];

        lhsText = emit(lhsNode,fdepDict);
        rhsText = emit(rhsNode,fdepDict);
        operatorText = _getBinaryOperatorFromLabel(astNode.label);

        returner += lhsText + operatorText + rhsText;

    elif astNode.label == AST_LEN:
        lenArgNode = astNode.children[0];
        returner += 'len( ';
        returner += emit(lenArgNode,fdepDict);
        returner += ')';

    elif astNode.label == AST_RANGE:
        bottomRangeNode = astNode.children[0];
        upperRangeNode = astNode.children[1];
        incrementRangeNode = astNode.children[2];

        returner += 'range( ';
        returner += emit(bottomRangeNode,fdepDict);
        returner += ',';
        returner += emit(upperRangeNode,fdepDict);
        returner += ',';
        returner += emit(incrementRangeNode,fdepDict);
        returner += ')';
        
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



def _emitFunctionCall(funcCallNode,fdepDict):
    '''
    @param{AstNode} funcCallNode --- Should have label
    AST_FUNCTION_CALL

    @returns{String}
    '''
    if funcCallNode.label != AST_FUNCTION_CALL:
        assert(False);

    returner = '';
        
    funcName = funcCallNode.children[0].value;
    funcArgListNode = funcCallNode.children[1];

    errMsg = '\nBehram error: right now, not handling ';
    errMsg += 'function calls from function objects.\n';
    print(errMsg);
    
    returner += 'self.%s' % emitUtils._convertSrcFuncNameToInternal(funcName);
    returner += '(';

    amtToIndent = len(returner);
    indentStr = '';
    for counter in range(0,amtToIndent):
        indentStr += ' ';

    first = True;
    for argNode in funcArgListNode.children:
        if not first:
            returner += indentStr;
        else:
            first = False;

        returner += emit(argNode,fdepDict);
        returner += ',\n';

    returner += indentStr + '_Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED,\n'
    returner += indentStr + '_actEvent,\n';
    returner += indentStr + '_context)';

    errMsg = '\nBehram error: still need to handle case of calling a message ';
    errMsg += 'function...wait for it to say that it has returned.\n';
    print(errMsg);
    return returner;
    
# _emitFunctionCall(astNode,fdepDict);
