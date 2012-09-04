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


def emit(endpointName,astNode,fdepDict,emitContext):
    returner = '';

    if astNode.label == AST_ANNOTATED_DECLARATION:
        # it's a shared variable
        #   shared{ Nothing controls someNum = 0;}
        #   self._committedContext.shareds['1__someNum'];
        identifierNode = astNode.children[2];
        returner += emit(endpointName,identifierNode,fdepDict,emitContext);
        
        if len(astNode.children) == 4:
            # means have initialization information
            returner += ' = ';
            returner += emit(endpointName,astNode.children[3],fdepDict,emitContext);

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

    elif astNode.label == AST_FOR_STATEMENT:
        returner += '\n';
        if len(astNode.children) == 3:
            identifierNodeIndex = 0;
            toIterateNodeIndex = 1;
            forBodyNodeIndex = 2;
        
        elif len(astNode.children) == 4:
            identifierTypeNodeIndex = 0;
            identifierNodeIndex = 1;
            toIterateNodeIndex = 2;
            forBodyNodeIndex = 3;

            identifierNode = astNode.children[identifierNodeIndex];
            returner += emit(endpointName,identifierNode,fdepDict,emitContext);
            returner += ' = ';
            returner += emitUtils.getDefaultValueFromDeclNode(identifierNode);
            returner += '\n';

        forBodyNode = astNode.children[forBodyNodeIndex];
        toIterateNode = astNode.children[toIterateNodeIndex];
        identifierName = astNode.children[identifierNodeIndex].value;
        
        returner += 'for ' + identifierName + ' in ';
        returner += emit(endpointName,toIterateNode,fdepDict,emitContext);
        returner += ':\n';
        forBody = emit(endpointName,forBodyNode,fdepDict,emitContext);
        returner += emitUtils.indentString(forBody,1);
        returner += '\n';
        
            
    elif astNode.label == AST_JUMP_COMPLETE:

        if emitContext.msgSequenceNode == None:
            errMsg = '\nBehram error: require a message sequence node ';
            errMsg += 'when emitting a jump complete label.\n';
            print(errMsg);
            assert(False);

        # tell side to signal sequence complete and schedule oncompletes
        msgSeqNameNode = emitContext.msgSequenceNode.children[0];
        msgSeqName = msgSeqNameNode.value;
        returner += '\n# handling jump oncomplete \n'        
        returner += emitUtils.lastMessageSuffix(msgSeqName);
        returner += '\n';

    elif astNode.label == AST_APPEND_STATEMENT:
        toAppendToNode = astNode.children[0];
        toAppendNode = astNode.children[1];
        returner += emit(endpointName,toAppendToNode,fdepDict,emitContext);
        returner += '.append(';
        returner += emit(endpointName,toAppendNode,fdepDict,emitContext);
        returner += ')';
        
        
    elif astNode.label == AST_JUMP:
        if ((emitContext.msgSequenceNode == None) or
            (emitContext.msgSeqFuncNode == None)):
            errMsg = '\nBehram error: require a message sequence and message ';
            errMsg += 'sequence function node when emitting a jump label.\n';
            print(errMsg);
            assert(False);

        currentEndpointName = emitContext.msgSeqFuncNode.children[0].value;


        msgSeqNameNode = emitContext.msgSequenceNode.children[0];
        msgSeqName = msgSeqNameNode.value;
        jumpToEndpointName = astNode.children[0].value;
        jumpToFuncName = astNode.children[1].value;        

        nextFuncEventName = emitUtils.getFuncEventKey(
            jumpToFuncName,jumpToEndpointName,fdepDict);
        if currentEndpointName != jumpToEndpointName:
            returner += '\n# handling jump statement \n'
            jumpToSelf = False;
            returner += emitUtils.nextMessageSuffix(nextFuncEventName,msgSeqName);
        else:
            jumpToSelf = True;
            returner += '\n# handling jump to self statement \n'
            
        returner += emitUtils.nextMessageSuffix(nextFuncEventName,msgSeqName,jumpToSelf);
        returner += '\n';
            
            
    elif astNode.label == AST_FUNCTION_CALL:
        returner += _emitFunctionCall(endpointName,astNode,fdepDict,emitContext);

    elif astNode.label == AST_IN_STATEMENT:
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];

        returner += emit(endpointName,lhsNode,fdepDict,emitContext);
        returner += ' in ';
        returner += emit(endpointName,rhsNode,fdepDict,emitContext);

    elif astNode.label == AST_BRACKET_STATEMENT:
        indexedIntoNode = astNode.children[0];
        indexNode = astNode.children[1];
        returner += emit(endpointName,indexedIntoNode,fdepDict,emitContext);
        returner += '[';
        returner += emit(endpointName,indexNode,fdepDict,emitContext);
        returner += ']';
        
    elif astNode.label == AST_TOTEXT_FUNCTION:
        toTextArgNode = astNode.children[0];
        
        returner += 'str(';
        returner += emit(endpointName,toTextArgNode,fdepDict,emitContext);
        returner += ')'; # closes str opening

    elif astNode.label == AST_NOT_EXPRESSION:
        notArgNode = astNode.children[0];
        returner += 'not (';
        returner += emit(endpointName,notArgNode,fdepDict,emitContext);
        returner += ')';

        
    elif astNode.label == AST_CONDITION_STATEMENT:
        for child in astNode.children:
            returner += emit(endpointName,child,fdepDict,emitContext);

    elif ((astNode.label == AST_IF_STATEMENT) or
          (astNode.label == AST_ELSE_IF_STATEMENT)):

        if (astNode.label == AST_IF_STATEMENT):
            condHead = 'if ';
        elif(astNode.label == AST_ELSE_IF_STATEMENT):
            condHead = 'elif ';
        else:
            errMsg = '\nBehram error: got an unknown condition label ';
            errMsg += 'in runFunctionBodyInternalEmit.\n';
            errPrint(errMsg);
            assert(False);
            
        booleanConditionNode = astNode.children[0];
        condBodyNode = astNode.children[1];

        # handle putting togther the if/elif predicate
        boolCondStr = emit(
            endpointName,booleanConditionNode,fdepDict,emitContext);
        returner += condHead + boolCondStr + ':';

        # handle putting together the if/else if statement body
        condBodyStr = '';
        if not isEmptyNode(condBodyNode):
            # occasionally, have empty bodies for if/else if
            # statements.
            condBodyStr = emit(endpointName,condBodyNode,fdepDict,emitContext);
        if condBodyStr == '':
            condBodyStr = 'pass;';

        returner += '\n';
        returner += emitUtils.indentString(condBodyStr,1);

    elif astNode.label == AST_ELSE_STATEMENT:
        if (len(astNode.children) == 0):
            return '';
        
        elseHeadStr = 'else: \n';
        elseBodyNode = astNode.children[0];

        # handles empty body for else statement
        elseBodyStr = '';
        if not isEmptyNode(elseBodyNode):
            elseBodyStr = emit(endpointName,elseBodyNode,fdepDict,emitContext);
        if elseBodyStr == '':
            elseBodyStr = 'pass;';

        returner += elseHeadStr;
        returner += emitUtils.indentString(elseBodyStr,1);

    elif astNode.label == AST_ELSE_IF_STATEMENTS:
        for childNode in astNode.children:
            returner += emit(endpointName,childNode,fdepDict,emitContext);
            returner += '\n';


    elif astNode.label == AST_BOOLEAN_CONDITION:
        childNode = astNode.children[0];
        returner += emit(
            endpointName,childNode,fdepDict,emitContext);


    elif astNode.label == AST_FUNCTION_BODY_STATEMENT:
        for childNode in astNode.children:
            returner += emit(endpointName,childNode,fdepDict,emitContext);

    elif astNode.label == AST_FUNCTION_BODY:

        fromBodyString = '';
        for childNode in astNode.children:
            
            funcStatementString = emit(endpointName,childNode,fdepDict,emitContext);
            if (len(funcStatementString) != 0):
                fromBodyString += funcStatementString;
                fromBodyString += '\n';
                
        if len(fromBodyString) == 0:
            returner += 'pass;'; # takes care of blank function bodies.
        else:
            returner += fromBodyString;

    elif astNode.label == AST_ASSIGNMENT_STATEMENT:
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];
        returner += emit(endpointName,lhsNode,fdepDict,emitContext);
        returner += ' = ';
        returner += emit(endpointName,rhsNode,fdepDict,emitContext);

    elif astNode.label == AST_PRINT:
        toPrintNode = astNode.children[0];
        returner += 'print( ';
        returner += emit(endpointName,toPrintNode,fdepDict,emitContext);
        returner += ')';
        
    elif astNode.label == AST_REFRESH:
        returner += '\n';
        returner += '# do not need to honor refresh statement if \n';
        returner += '# have already sent a message during the course \n';
        returner += '# of this function, because final event release \n';
        returner += '# will ensure that shared/global data are consistent\n';
        returner += 'if not _context.messageSent:\n'
        ifBody = '_context.messageSent = True;\n';
        ifBody += 'self.%s' % emitUtils._REFRESH_SEND_FUNCTION_NAME;
        ifBody += '''(_Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED,
              _actEvent,
              _context)
''';

        # need to wait until sync has completed
        ifBody += '\n';
        ifBody +=  _messageSendBlockingCode();

        returner += emitUtils.indentString(ifBody,1);
        
        
        
    elif astNode.label == AST_DECLARATION:
        # could either be a shared or local variable.  use annotation
        # to determine.
        identifierNode = astNode.children[1];
        returner += emit(endpointName,identifierNode,fdepDict,emitContext);
        if len(astNode.children) == 3:
            # includes initialization information
            initializationNode = astNode.children[2];
            returner += ' = ';
            returner += emit(endpointName,initializationNode,fdepDict,emitContext);
        else:
            returner += ' = ';
            returner += emitUtils.getDefaultValueFromDeclNode(astNode);

        returner += '\n';

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
            returner += emit(endpointName,child,fdepDict,emitContext);
            returner += ', ';
        returner += '] ';

    elif astNode.label == AST_MAP:
        # handle map literal
        returner += '{ ';
        for mapLiteralItem in astNode.children:
            returner += emit(endpointName,mapLiteralItem,fdepDict,emitContext);
            returner += ', ';
        returner += '} ';

    elif astNode.label == AST_FUNCTION_BODY_STATEMENT:
        for child in astNode.children:
            returner += emit(endpointName,child,fdepDict,emitContext);
        
    elif astNode.label == AST_MAP_ITEM:
        # individual entry of map literal
        keyNode = astNode.children[0];
        valNode = astNode.children[1];
        
        keyText = emit(endpointName,keyNode,fdepDict,emitContext);
        valText = emit(endpointName,valNode,fdepDict,emitContext);
        returner += keyText + ': ' + valText;

    elif astNode.label == AST_RETURN_STATEMENT:
        retStatementNode = astNode.children[0];

        if isEmptyNode(retStatementNode):
            toReturnStatementText = 'None';
        else:
            toReturnStatementText = emit(endpointName,retStatementNode,fdepDict,emitContext);

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

        lhsText = emit(endpointName,lhsNode,fdepDict,emitContext);
        rhsText = emit(endpointName,rhsNode,fdepDict,emitContext);
        operatorText = _getBinaryOperatorFromLabel(astNode.label);

        returner += ' (' + lhsText + operatorText + rhsText + ')';

    elif astNode.label == AST_LEN:
        lenArgNode = astNode.children[0];
        returner += 'len( ';
        returner += emit(endpointName,lenArgNode,fdepDict,emitContext);
        returner += ')';

    elif astNode.label == AST_RANGE:
        bottomRangeNode = astNode.children[0];
        upperRangeNode = astNode.children[1];
        incrementRangeNode = astNode.children[2];

        returner += 'range( ';
        returner += emit(endpointName,bottomRangeNode,fdepDict,emitContext);
        returner += ',';
        returner += emit(endpointName,upperRangeNode,fdepDict,emitContext);
        returner += ',';
        returner += emit(endpointName,incrementRangeNode,fdepDict,emitContext);
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



def _emitFunctionCall(endpointName,funcCallNode,fdepDict,emitContext):
    '''
    @param{AstNode} funcCallNode --- Should have label
    AST_FUNCTION_CALL

    @param{EmitContext object} emitContext --- @see class EmitContext
    in emitUtils.py

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
        funcCallText = emit(endpointName,funcNameNode,fdepDict,emitContext);
    else:
        # means that we are making a call to a statically, and
        # textually described function.  note: if we are in 

        if _isMessageSend(funcName,endpointName,fdepDict) and (not emitContext.insideOnComplete):
            # set the context messageSent field to True.
            returner += "\n# set context's messageSent field to True.  ";
            returner += "\n# that way ensures that after event completes, ";
            returner += "\n# may notify other side to release the read/write ";
            returner += "\n# locks it is holding for event's variables, and also ";
            returner += "\n# to commit final context.\n";
            returner += '_context.messageSent = True;\n';
            
            if emitContext.collisionFlag:
                # we are trying to induce a collision for debugging
                # purposes.
                returner += '\n#### DEBUG';
                returner += '\n# compiled with collision flag.  inserting ';
                returner += '\n# a _time.sleep call to try to get transactions ';
                returner += '\n# to collide for debugging.';
                returner += '\n#### END DEBUG';
                returner += '\n_time.sleep(_COLLISION_TIMEOUT_VAL);\n\n';


        
        funcCallText = 'self.%s' % emitUtils._convertSrcFuncNameToInternal(funcName);
        if emitContext.insideOnComplete:
            funcCallText = 'self.%s' % funcName;
        
        

    funcCallText += '('
    returner += funcCallText;


    amtToIndent = len(funcCallText);
    indentStr = '';
    for counter in range(0,amtToIndent):
        indentStr += ' ';


    first = True;
    if funcNameNode.sliceAnnotationName  == None:
        # we are handling a call to a user-defined function, not a
        # funciton object.

        if not emitContext.insideOnComplete:
            # means that we are not inside an oncomplete function and
            # that we should call the internal version of the function
            first = False;
            returner +=  '_Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED,\n'
            returner += indentStr + '_actEvent,\n';
            returner += indentStr + '_context';

    
    # emit user-defined functions
    for argNode in funcArgListNode.children:
        if not first:
            returner += ',\n' + indentStr;
        else:
            first = False;
            
        returner += emit(endpointName,argNode,fdepDict,emitContext);


    returner +=  ')'

    if funcNameNode.sliceAnnotationName == None:
        if _isMessageSend(funcName,endpointName,fdepDict) and (not emitContext.insideOnComplete):
            # if this is a call to a message function, need to block
            # until completes.
            returner += '\n';
            returner += _messageSendBlockingCode();
            
    return returner;

def _messageSendBlockingCode():
    '''
    Whenever we call a message send function (either user-defined or
    from a refresh call), the function that calls it needs to wait
    until the message sequence has finished.  This code handles the
    wait.
    '''
    return """
# wait on message reception notification from other side
# and check if we had to postpone the event
_msgReceivedContextId = _context.msgReceivedQueue.get();
if _msgReceivedContextId != _context.id:
    raise _PostponeException(); # event postponed

""";    


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
            
            
