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


def emit(endpointName,astNode,fdepDict):
    returner = '';


    if astNode.label == AST_ANNOTATED_DECLARATION:
        # it's a shared variable
        #   shared{ Nothing controls someNum = 0;}
        #   self._committedContext.shareds['1__someNum'];
        identifierNode = astNode.children[2];
        returner += emit(endpointName,identifierNode,fdepDict);
        
        if len(astNode.children) == 4:
            # means have initialization information
            returner += ' = ';
            returner += emit(endpointName,astNode.children[3],fdepDict);

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
        returner += _emitFunctionCall(endpointName,astNode,fdepDict);

            
    elif astNode.label == AST_ASSIGNMENT_STATEMENT:
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];
        returner += emit(endpointName,lhsNode,fdepDict);
        returner += ' = ';
        returner += emit(endpointName,rhsNode,fdepDict);

    elif astNode.label == AST_PRINT:
        toPrintNode = astNode.children[0];
        returner += 'print( ';
        returner += emit(endpointName,toPrintNode,fdepDict);
        returner += ')';
        
        
    elif astNode.label == AST_DECLARATION:
        # could either be a shared or local variable.  use annotation
        # to determine.
        identifierNode = astNode.children[1];
        returner += emit(endpointName,identifierNode,fdepDict);
        if len(astNode.children) == 3:
            # includes initialization information
            initializationNode = astNode.children[2];
            returner += ' = ';
            returner += emit(endpointName,initializationNode,fdepDict);

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
            returner += emit(endpointName,child,fdepDict);
            returner += ', ';
        returner += '] ';

    elif astNode.label == AST_MAP:
        # handle map literal
        returner += '{ ';
        for mapLiteralItem in astNode.children:
            returner += emit(endpointName,mapLiteralItem,fdepDict);
            returner += ', ';
        returner += '} ';

    elif astNode.label == AST_FUNCTION_BODY_STATEMENT:
        for child in astNode.children:
            returner += emit(endpointName,child,fdepDict);
        
    elif astNode.label == AST_MAP_ITEM:
        # individual entry of map literal
        keyNode = astNode.children[0];
        valNode = astNode.children[1];
        
        keyText = emit(endpointName,keyNode,fdepDict);
        valText = emit(endpointName,valNode,fdepDict);
        returner += keyText + ': ' + valText;

    elif astNode.label == AST_RETURN_STATEMENT:
        retStatementNode = astNode.children[0];

        if isEmptyNode(retStatementNode):
            toReturnStatementText = 'None';
        else:
            toReturnStatementText = emit(endpointName,retStatementNode,fdepDict);

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

        lhsText = emit(endpointName,lhsNode,fdepDict);
        rhsText = emit(endpointName,rhsNode,fdepDict);
        operatorText = _getBinaryOperatorFromLabel(astNode.label);

        returner += lhsText + operatorText + rhsText;

    elif astNode.label == AST_LEN:
        lenArgNode = astNode.children[0];
        returner += 'len( ';
        returner += emit(endpointName,lenArgNode,fdepDict);
        returner += ')';

    elif astNode.label == AST_RANGE:
        bottomRangeNode = astNode.children[0];
        upperRangeNode = astNode.children[1];
        incrementRangeNode = astNode.children[2];

        returner += 'range( ';
        returner += emit(endpointName,bottomRangeNode,fdepDict);
        returner += ',';
        returner += emit(endpointName,upperRangeNode,fdepDict);
        returner += ',';
        returner += emit(endpointName,incrementRangeNode,fdepDict);
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



def _emitFunctionCall(endpointName,funcCallNode,fdepDict):
    '''
    @param{AstNode} funcCallNode --- Should have label
    AST_FUNCTION_CALL

    @returns{String}
    '''
    if funcCallNode.label != AST_FUNCTION_CALL:
        assert(False);

    returner = '';

    funcNameNode = funcCallNode.children[0];
    funcName = funcNameNode.value;
    funcArgListNode = funcCallNode.children[1];


    if funcNameNode.sliceAnnotationName != None:
        # means that this is a function object that we are making call
        # on....use its reference either as a shared, arg, global, etc.
        returner += emit(endpointName,funcNameNode,fdepDict);
    else:
        # means that we are making a call to a statically, and
        # textually described function.
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

        returner += emit(endpointName,argNode,fdepDict);
        returner += ',\n';

    if funcNameNode.sliceAnnotationName != None:
        # handling calling a function object differently from calling function from source
        returner += indentStr + ')';
    else:
        returner += indentStr + '_Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED,\n'
        returner += indentStr + '_actEvent,\n';
        returner += indentStr + '_context)';



        if _isMessageSend(funcName,endpointName,fdepDict):
            # if this is a call to a message function, need to block
            # until completes.
            returner += '\n';
            returner += """
# wait on message reception notification from other side
# and check if we had to postpone the event
_msgReceivedContextId = _context.msgReceivedQueue.get();
if _msgReceivedContextId != _context.id:
    raise _PostponeException(); # event postponed

"""
    return returner;
    


def _isMessageSend(funcName,endpointName,fdepDict):
    '''
    @returns{Bool} --- True if this function is a message send, false
    otherwise
    '''
    for fdepKey in fdepDict.keys():
        fdep = fdepDict[fdepKey];

        if ((fdep.endpointName == endpointName) and
            (fdep.srcFuncName == funcName)):
            # same function as fdep.  check if the node is labeled as
            # a message sequence node.
            return fdep.funcNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION;

    # should always be able to find the function.
    errMsg = '\nBehram error: unable to find function in fdepDict when ';
    errMsg += 'checking if it is a message send.  Abortin.\n';
    print(errMsg);
    assert(False);
            
            
