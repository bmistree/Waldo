#!/usr/bin/python

from astLabels import *;


# pass one of these parameters to runFunctionBodyInternalEmit so that
# the function knows whether to prefix global and shared variables
# with "self.committed" or "self.intermediate" or "self." (for case of
# wanting to initialize variables themselves.
INTERMEDIATE_PREFIX = 'self.intermediate.';
COMMITTED_PREFIX = 'self.committed.';
SELF_PREFIX = 'self.'

def indentString(string,indentAmount):
    '''
    @param {String} string -- Each line in this string we will insert
    indentAmount number of tabs before and return the new, resulting
    string.
    
    @param {Int} indentAmount 

    @returns {String}
    '''
    splitOnNewLine = string.split('\n');
    returnString = '';

    indenter = '';
    for s in range(0,indentAmount):
        indenter += '    ';

    for s in splitOnNewLine:
        if (len(s) != 0):
            returnString += indenter + s + '\n';

    return returnString;


def getDefaultValForType(astTypedNode):
    '''
    @param astTypedNode should have valid type data.
    '''
    typeName = astTypedNode.type;

    if (typeName == TYPE_BOOL):
        decString = 'False';
    elif (typeName == TYPE_NUMBER):
        decString = '0';
    elif (typeName == TYPE_STRING):
        decString = '""';
    elif (typeName == TYPE_NOTHING):
        decString = 'None';
    elif (typeName == TYPE_MESSAGE):
        decString = '{}';
    else:
        errMsg = '\nBehram error.  Unknown declaration type when ';
        errMsg += 'emitting from runFunctionBodyInternalEmit.\n';
        print(errMsg);
        assert(False);

    return decString;


def runFunctionBodyInternalEmit(astNode,protObj,endpoint,prefix,indentLevel=0):
    '''
    @param {AstNode} astNode -- the ast node that we want evaluation
    to start from.  When called externally, this will generally have
    label AST_FUNCTION_BODY.  However, because this code also emits
    bool, string, and number literals, it may also be used to emit the
    initialization statement for shared and global variables.
    
    @param {ProtocolObject} protObj -- So that can check for
    appropriate variable names

    @param {Int} prefix -- Either INTERMEDIATE_PREFIX,
    COMMITTED_PREFIX, or SELF_PREFIX, (all defined at top of the
    file).  Referenced global or shared variables should be refered to
    through either self.intermediate.<var name>,self.commited.<var
    name>, or self.<varName> (for case of initializing shared and
    global vars) depending on which is set/passed through.
    

    @returns {String} with funcition text.  base indent level is 0.
    '''

    if ((prefix != INTERMEDIATE_PREFIX) and (prefix != COMMITTED_PREFIX) and
        (prefix != SELF_PREFIX)):
        
        errMsg = '\nBehram error: runFunctionBodyInternalEmit should be passed ';
        errMsg += 'a valid prefix.\n';
        print(errMsg);
        assert(False);

        
    
    returnString = '';
    if (astNode.label == AST_FUNCTION_BODY):
        for s in astNode.children:
            funcStatementString = runFunctionBodyInternalEmit(s,protObj,endpoint,prefix,indentLevel);
            if (len(funcStatementString) != 0):
                returnString += indentString(funcStatementString,indentLevel);
                returnString += '\n';
        if (len(returnString) == 0):
            returnString += indentString('pass;',indentLevel);

                
    elif (astNode.label == AST_DECLARATION):
        idName = astNode.children[1].value;

        # do not need to worry about case where endpoint equals None
        # because that only happens when we are in the Shared section.
        # In the shared section, there are no declarations, just
        # annotated declarations.
        if (endpoint.isGlobalOrShared(idName)):
            idName = prefix + idName;

        decString = idName + ' = ';            

        #check if have an initializer value
        if (len(astNode.children) == 3):
            #have an initializer value;
            rhsInitializer = runFunctionBodyInternalEmit(astNode.children[2],protObj,endpoint,prefix,0);
            decString += rhsInitializer;
        else:
            decString = getDefaultValForType(astNode);

        
        returnString += indentString(decString,indentLevel);
        returnString += '\n';

    elif (astNode.label == AST_BOOL):
        return ' ' + astNode.value + ' ';

    elif (astNode.label == AST_STRING):
        return ' "'  + astNode.value + '" ';

    elif (astNode.label == AST_NUMBER):
        return ' '  + astNode.value + ' ';

    elif ((astNode.label == AST_PLUS) or (astNode.label == AST_MINUS) or
          (astNode.label == AST_MULTIPLY) or (astNode.label == AST_DIVIDE) or 
          (astNode.label == AST_AND) or (astNode.label == AST_OR) or
          (astNode.label == AST_BOOL_EQUALS) or (astNode.label == AST_BOOL_NOT_EQUALS)):

        if (astNode.label == AST_PLUS):
            operator = '+';
        elif(astNode.label == AST_MINUS):
            operator = '-';
        elif(astNode.label == AST_MULTIPLY):
            operator = '*';
        elif(astNode.label == AST_DIVIDE):
            operator = '/';
        elif(astNode.label == AST_AND):
            operator = 'and';
        elif(astNode.label == AST_OR):
            operator = 'or';
        elif(astNode.label == AST_BOOL_EQUALS):
            operator = '==';
        elif(astNode.label == AST_BOOL_NOT_EQUALS):
            operator = '!=';

            
        else:
            errMsg = '\nBehram error.  Unknown operator type when ';
            errMsg += 'emitting from runFunctionBodyInternalEmit.\n'
            print(errMsg);
            assert(False);
            
        lhsNode = astNode.children[0];
        rhsNode = astNode.children[1];

        lhsText = runFunctionBodyInternalEmit(lhsNode,protObj,endpoint,prefix,0);
        rhsText = runFunctionBodyInternalEmit(rhsNode,protObj,endpoint,prefix,0);

        overallLine = lhsText + ' '+ operator + ' (' + rhsText + ') ';
        return overallLine;


    elif (astNode.label == AST_CONDITION_STATEMENT):
        returnString = '';
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,prefix,indentLevel);
            returnString += '\n';

    elif (astNode.label == AST_PRINT):
        #Print: line number, class name, print statement
        returnString += '_DEBUG_PRINT(' + str(astNode.lineNo);
        returnString += ','
        if (endpoint != None):
            returnString += '"' + endpoint.name + '"';
        else:
            returnString += 'None';
        returnString += ',';

        printArg = runFunctionBodyInternalEmit(astNode.children[0],protObj,endpoint,prefix,0);
        #now actually emit what the user wants to print
        returnString += printArg;
        returnString += ')';
        
        returnString = indentString(returnString,indentLevel);


        
    elif (astNode.label == AST_BOOLEAN_CONDITION):
        returnString = runFunctionBodyInternalEmit(astNode.children[0],protObj,endpoint,prefix,indentLevel);

    elif (astNode.label == AST_IDENTIFIER):
        idName = astNode.value;
        
        if ((endpoint == None) and (prefix == SELF_PREFIX)):
            # means that we are handling the shared section and we
            # have no endpoint and therefore, all identifers should
            # use the self prefix.
            idName = SELF_PREFIX + idName;
            
        elif (endpoint.isGlobalOrShared(idName)):
            idName = prefix + idName;     
        returnString = idName;

        
    elif (astNode.label == AST_ELSE_IF_STATEMENTS):
        returnString = '';
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,prefix,0);
            returnString += '\n';

        if (returnString != ''):
            returnString = indentString(returnString,indentLevel);

    elif ((astNode.label == AST_IF_STATEMENT) or
          (astNode.label == AST_ELSE_IF_STATEMENT)):

        if (astNode.label == AST_IF_STATEMENT):
            condHead = 'if ';
        elif(astNode.label == AST_ELSE_IF_STATEMENT):
            condHead = 'elif ';
        else:
            errMsg = '\nBehram error: got an unknown condition label ';
            errMsg += 'in runFunctionBodyInternalEmit.\n';
            print(errMsg);
            assert(False);
            
        booleanConditionNode = astNode.children[0];
        condBodyNode = astNode.children[1];

        boolCondStr = runFunctionBodyInternalEmit(booleanConditionNode,protObj,endpoint,prefix,0);
        condHead += boolCondStr + ':'

        # occasionally, have empty bodies for if/else if statements.
        condBodyStr = '';
        if (condBodyNode.label != AST_EMPTY):
            condBodyStr = runFunctionBodyInternalEmit(condBodyNode,protObj,endpoint,prefix,0);
        if (condBodyStr == ''):
            condBodyStr = 'pass;';


        indentedHead = indentString(condHead,indentLevel);
        indentedBody = indentString(condBodyStr, indentLevel +1);
        returnString = indentedHead + '\n' + indentedBody;

    elif(astNode.label == AST_ELSE_STATEMENT):
        if (len(astNode.children) == 0):
            return '';
        
        elseHead = 'else: \n';
        elseBody = astNode.children[0];

        # handles empty body for else statement
        elseBodyStr = '';
        if (elseBody.label != AST_EMPTY):
            elseBodyStr = runFunctionBodyInternalEmit(elseBody,protObj,endpoint,prefix,0);
        if (elseBodyStr == ''):
            elseBodyStr = 'pass;';

        indentedHead = indentString(elseHead,indentLevel);
        indentedBody = indentString(elseBodyStr, indentLevel +1);
        returnString = indentedHead + '\n' + indentedBody;


    elif (astNode.label == AST_FUNCTION_CALL):
        funcNameNode = astNode.children[0];

        funcCallPrefix = 'self.'
        if (prefix == SELF_PREFIX):
            # means that we are in the context object: need to use the
            # self.endpoint instead.
            funcCallPrefix = 'self._endpoint.';
        
        funcNameStr = funcCallPrefix + endpoint.getPythonizedFunctionName(funcNameNode.value);
        funcArgListNode = astNode.children[1];
        funcArgStr = runFunctionBodyInternalEmit(funcArgListNode,protObj,endpoint,prefix,0);
        returnString = indentString(funcNameStr + funcArgStr,indentLevel);

    elif (astNode.label == AST_FUNCTION_ARGLIST):
        returnString = '(';

        counter = 0;
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,prefix,0);
            counter +=1;
            
            if (counter != len(astNode.children)):
                returnString += ',';
        
        returnString += ')';
        returnString = indentString(returnString,indentLevel);

    elif(astNode.label == AST_MESSAGE_LITERAL):
        # each child is a message literal element, which has a left
        # child (identifier name) and a right child (identifier value)

        #creates a simple python dict.
        returnString = '{';
        for s in range(0,len(astNode.children)):
            msgLine = astNode.children[s];
            msgLineElementNameStr = msgLine.children[0].value;
            msgLineElementValueStr = runFunctionBodyInternalEmit(msgLine.children[1],protObj,endpoint,prefix,0);
            returnString += "'%s' : %s" % (msgLineElementNameStr,msgLineElementValueStr);

            if (s != len(astNode.children) -1):
                returnString += ',';
            
            
        returnString += '}';
        returnString = indentString(returnString,indentLevel);


    elif(astNode.label == AST_SEND_STATEMENT):

        if (endpoint.currentlyEmittingFunction == None):
            errMsg = '\nBehram error when processing send statement.  ';
            errMsg += 'Endpoint is not tracking a currentlyEmittingFunction.\n';
            print(errMsg);
            assert(False);

        msgNode = astNode.children[0];
        msgStr = runFunctionBodyInternalEmit(msgNode,protObj,endpoint,prefix,0);
        emittedSenderFuncName = endpoint.currentlyEmittingFunction.pythonizeName();
        returnString += '''self._sendMsg (%s,'%s');  # actually send the message;''' % (msgStr,emittedSenderFuncName);
        returnString = indentString(returnString,indentLevel);


        
    elif (astNode.label == AST_ASSIGNMENT_STATEMENT):
        assignTo = astNode.children[0];
        idName = assignTo.value;
        if (endpoint.isGlobalOrShared(idName)):
            idName = prefix + idName;

        lhsAssignString = idName + ' = ';
        

        rhsAssignString = runFunctionBodyInternalEmit(astNode.children[1],protObj,endpoint,prefix,0);
        returnString += indentString(lhsAssignString + rhsAssignString,indentLevel);
        returnString += '\n';

    elif (astNode.label == AST_FUNCTION_BODY_STATEMENT):
        for s in astNode.children:
            returnString += runFunctionBodyInternalEmit(s,protObj,endpoint,prefix,indentLevel);
        
    else:
        errMsg = '\nBehram error: in runFunctionBodyInternalEmit ';
        errMsg += 'do not know how to handle label ' + astNode.label + '\n';
        print(errMsg);


    return returnString;


