#!/usr/bin/env python

import sys;
import os;

curDir = os.path.dirname(__file__);
sys.path.append(os.path.join('..',curDir));

from astLabels import *;
from astTypeCheckStack import TypeCheckContextStack;
from astTypeCheckStack import FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH;
from astTypeCheckStack import FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_SUCCEED;
from astTypeCheckStack import createFuncMatchObjFromJsonStr;
from parserUtil import errPrint;

from typeCheckUtil import *;
from templateUtil import *;


def isEmptyAstNode(node):
    return (node.type == "EMPTY");


def typeCheck(node,progText,typeStack=None,avoidFunctionObjects=False):
    '''
    avoidFunctionObjects {Bool} --- True if should add function
    objects to typestack context, false otherwise.
    '''
    #based on types of children, check my type.  Also, pass up
    #line numbers.


    ####### basic checks and creating new context #########
    if ((node.label != AST_ROOT) and (typeStack == None)):
        errPrint('\nBehram error.  Must have typeStack unless root node\n');
        assert(False);
    elif(node.label == AST_ROOT):
        typeStack = TypeCheckContextStack();
            
    if ((node.label == AST_ROOT) or
        (node.label == AST_SHARED_SECTION) or
        (node.label == AST_ENDPOINT_GLOBAL_SECTION) or
        (node.label == AST_ENDPOINT_FUNCTION_SECTION)):
        #each of these create new contexts.  don't forget to
        #remove several of them at the bottom of the function.
        #note: do not have ast_function_body here because need to
        #create a new context before get into function body so
        #that we can catch arguments passed into the function.
        typeStack.pushContext();


    ###### MASSIVE SWITCH STATEMENT TO TYPECHECK BASED ON NODE #######

    if(node.label == AST_ROOT):
        #top of program

        typeStack.setRootNode(node);
        #getting protocol object name
        typeStack.protObjName = node.children[0].value;

        #handling alias section
        aliasSection = node.children[1];

        #endpoint 1 from alias section
        typeStack.endpoint1 = aliasSection.children[0].value; 
        typeStack.endpoint1LineNo = aliasSection.children[0].lineNo;
        typeStack.endpoint1Ast = aliasSection.children[0];

        #endpoint 2 from alias section
        typeStack.endpoint2 = aliasSection.children[1].value; 
        typeStack.endpoint2LineNo = aliasSection.children[1].lineNo;
        typeStack.endpoint2Ast = aliasSection.children[1];             
        
        if typeStack.endpoint1 == typeStack.endpoint2:
            errorFunction('Cannot use same names for endpoints',
                          [typeStack.endpoint1,typeStack.endpoint2],
                          [typeStack.endpoint1LineNo,typeStack.endpoint2LineNo],
                          progText);


        # #Do first level of type chcecking trace items.  see notes
        # #in corresponding elif.
        # node.children[2].typeCheck(progText,typeStack);
        sequencesSectionNode = node.children[2];
        sequencesSectionNode.typeCheck(progText,typeStack,avoidFunctionObjects);
        
        sharedSectionNode = node.children[3];
        endpoint1Node = node.children[4];
        endpoint2Node = node.children[5];
            
        #get into shared section
        #note: shared section should leave its context on the stack so
        #that can access all variables directly from it.
        sharedSectionNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        #check one endpoint
        endpoint1Node.typeCheck(progText,typeStack,avoidFunctionObjects);
        #check other endpoint
        endpoint2Node.typeCheck(progText,typeStack,avoidFunctionObjects);

        
        # check if there were elements of the message sequences that
        # weren't actually defined in a sequences section.
        traceError = typeStack.checkUndefinedTraceItems();
        if (traceError != None):
            errorFunction(traceError.errMsg,traceError.nodes,
                          traceError.lineNos,progText);

        # now check if have more than one sequence line with the same
        # name
        traceError = typeStack.checkRepeatedSequenceLine();
        if traceError != None:
            errorFunction(traceError.errMsg,traceError.nodes,
                          traceError.lineNos,progText);
        
        print('\nBehram note: skipping type checking of traces section.\n');
        
        # #Checks if there were msgSends or msgReceives assumed in a
        # #trace line that weren't actually defined in an endpoint
        # #section.
        # traceError = typeStack.checkUndefinedTraceItems();
        # if (traceError != None):
        #     errorFunction(traceError.errMsg,traceError.nodes,
        #                   traceError.lineNos,progText);

        # # check that output of one trace line matched input of
        # # another
        # traceError =  typeStack.checkTraceItemInputOutput();
        # if (traceError != None):
        #     errorFunction(traceError.errMsg,traceError.nodes,
        #                   traceError.lineNos,progText);
            

    elif(node.label == AST_TRACE_SECTION):
        '''
        All the type rules of an ast trace section are:
          Check:
            1) Trace line alternates between one side and other

            2) All functions in trace line exist

            3) There are no msgSend/msgReceive functions that are not
               in a traceline

            4) Each traceline begins with a msgSend

            5) Middles and ends of each traceline are msgReceives

            6) No two tracelines begin with the same msgSend

            7) Each trace item begins with a valid endpoint name.

         At this level of type checking, we only handle #1 and #7.
         Type checking in rest of body takes care of #3, #4, #5, and  #6.

         After type checking rest of body, then return check #2 by
         calling typeStack.checkUndefinedTraceItems in type check of astRoot.
        '''
        typeStack.setAstTraceSectionNode(node);

        # skip the first child, which is a name for the 
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif node.label == AST_BRACKET_STATEMENT:
        toReadFrom = node.children[0];
        index = node.children[1];
        toReadFrom.typeCheck(progText,typeStack,avoidFunctionObjects);
        index.typeCheck(progText,typeStack,avoidFunctionObjects);

        node.lineNo = index.lineNo;

        if isMapType(toReadFrom.type):

            typeError,statementType,typeErrorMsg,typeErrorNodes = typeCheckMapBracket(
                toReadFrom,index,typeStack,progText);

        elif isListType(toReadFrom.type):
            typeError,statementType,typeErrorMsg,typeErrorNodes = typeCheckListBracket(
                toReadFrom,index,typeStack,progText);

        else:
            typeError = True;
            typeErrorMsg = 'You can only index into a map type or list type.  ';
            typeErrorMsg += 'Instead, you are trying to index into a [ ';
            typeErrorMsg += toReadFrom.type + ' ].\n';
            typeErrorNodes = [toReadFrom];

        if typeError:
            node.type = TYPE_NOTHING;
            for node in typeErrorNodes:
                astLineNos = [node.lineNo];
                errorFunction(typeErrorMsg,typeErrorNodes,astLineNos,progText);
        else:
            # apply type 
            node.type = statementType;

    elif(node.label == AST_TRACE_LINE):
        #first, checking that each trace item has an endpoint
        #prefix, and second that the prefixes alternate so that
        #messages are being sent between different endpoints.

        #add trace line to traceManager of typeStack so can do
        #type checks after endpoint bodies are type checked.
        traceError = typeStack.addTraceLine(node);
        if traceError != None:
            errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);

        #will hold the name of the last endpoint used in trace line.
        lastEndpoint = None;
        firstChild = True;
        for traceItem in node.children:

            # skip first item, because that is the potential name
            # of the trace line messsage sequence.
            if firstChild:
                firstChild = False;
                continue;


            endpointName = traceItem.children[0].value;
            currentLineNo = traceItem.children[0].lineNo;

            if (node.lineNo == None):
                node.lineNo = currentLineNo;

            funcName = traceItem.children[1].value;

            endpoint1Ast = typeStack.endpoint1Ast;
            endpoint2Ast = typeStack.endpoint2Ast;
            endpoint1Name = typeStack.endpoint1;
            endpoint2Name = typeStack.endpoint2;
            endpoint1LineNo = typeStack.endpoint1LineNo;
            endpoint2LineNo = typeStack.endpoint2LineNo;

            #check that are using declared endpoints.
            if (not typeStack.isEndpoint(endpointName)):
                errMsg = '\nError in sequence declaration.  Each element ';
                errMsg += 'in the message sequence should have the form ';
                errMsg += '<Endpoint Name>.<Function name>.  For <Endpoint Name>, ';
                errMsg += 'you entered "' + endpointName + '".  You should have entered ';
                errMsg += 'either "' + endpoint1Name + '" or "' + endpoint2Name;
                errMsg += '" to agree with your endpoint declarations.\n';

                astErrorNodes = [node,endpoint1Ast,endpoint2Ast];
                astLineNos = [currentLineNo, endpoint1LineNo, endpoint2LineNo];
                errorFunction(errMsg,astErrorNodes,astLineNos,progText);        
                continue;

            #check for alternating between endpoints
            if (lastEndpoint != None):
                if (lastEndpoint == endpointName):
                    #means that we had a repeat between the endpoints
                    errMsg = '\nError in sequence declaration for item ';
                    errMsg += '"' + endpointName + '.' + funcName  +  '".  ';
                    errMsg += 'Messages in a sequence should alternate which side ';
                    errMsg += 'receives them.  Instead of having "' + endpointName + '" ';
                    errMsg += 'receive two messages in a row, you should have "';
                    if (endpointName == endpoint1Name):
                        errMsg += endpoint2Name;
                    else:
                        errMsg += endpoint1Name;

                    errMsg += '" receive a message in between.\n';
                    errorFunction(errMsg,[node],[currentLineNo],progText);        

            lastEndpoint = endpointName;

    elif (node.label == AST_PRINT):
        #check to ensure that it's passed a string
        argument = node.children[0];
        argument.typeCheck(progText,typeStack,avoidFunctionObjects);
        if ((argument.type != TYPE_STRING) and (argument.type != TYPE_NUMBER) and
            (argument.type != TYPE_BOOL)):
            errorString = 'Print requires a Text, TrueFalse, or a Number ';
            errorString += 'to be passed in.  ';
            errorString += 'It seems that you passed in a ';
            errorString += argument.type + '.';
            errorFunction(errorString,[node],[node.lineNo],progText);

        node.type = TYPE_NOTHING;

    elif(node.label == AST_TOTEXT_FUNCTION):
        # check to ensure that it's passed a Text, TrueFalse, or a
        # Number.  If it is passed anything else, indicate that
        # can't handle it.
        argumentNode = node.children[0];
        argumentNode.typeCheck(progText,typeStack,avoidFunctionObjects);
        if ((argumentNode.type != TYPE_STRING) and (argumentNode.type != TYPE_NUMBER) and
            (argumentNode.type != TYPE_BOOL)):
            errorString = 'ToText requires a Text, TrueFalse, or a Number ';
            errorString += 'to be passed in.  It seems that you passed in a ';
            errorString += argumentNode.type + '.';
            errorFunction(errorString,[node],[node.lineNo],progText);

        node.type = TYPE_STRING;

    elif(node.label == AST_SHARED_SECTION):
        #each child will be an annotated declaration.
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_ANNOTATED_DECLARATION):
        # the type of this identifier
        #reset my type to it.
        node.type = node.children[1].value;
        currentLineNo = node.children[1].lineNo;
        if (len(node.children) == 4):
            #have an initializer too.
            node.children[3].typeCheck(progText,typeStack,avoidFunctionObjects);
            assignType = node.children[3].type;
            if (assignType != node.type):
                if (assignType == None):
                    assignType = '<None>';
                errorString = 'Assigned type [' + assignType + '] does not ';
                errorString += 'match declared type [' + node.type + '].';
                errorFunction(errorString,[node],[currentLineNo],progText);

        #actually store the new type
        identifierName = node.children[2].value;
        existsAlready = typeStack.getIdentifierElement(identifierName);
        if (existsAlready != None):
            errorFunction('Already have an identifier named ' + identifierName,
                          [node],[currentLineNo, existsAlready.lineNo],progText);
        else:
            controlledByNode = node.children[0];
            idType = typeStack.getFuncIdentifierType(identifierName);
            if (idType):
                errText = 'Already have a function named ' + identifierName;
                errText += '.  Therefore, cannot name an identifier with this name.';
                errorFunction(errText,
                              [node,existsAlready.astNode],
                              [currentLineNo,existsAlready.lineNo],
                              progText);

            # check to ensure that specified a valid endpoint to
            # control the shared variable.
            controlledByStr = controlledByNode.value;
            end1Name = typeStack.endpoint1
            if ((controlledByStr != TYPE_NOTHING) and
                (controlledByStr != typeStack.endpoint1) and
                (controlledByStr != typeStack.endpoint2)):
                errText = 'Can only specify an endpoint or Nothing to control ';
                errText += 'a shared variable.  The available endpoint names are '
                errText += typeStack.endpoint1 + ' and ' + typeStack.endpoint2;
                errText += ', but you specified ' + controlledByStr + '.';
                errorFunction(errText,
                              [node],
                              [currentLineNo],
                              progText);


            # actually add the shared variable.
            typeStack.addIdentifier(identifierName,
                                    node.type,
                                    controlledByStr,node,currentLineNo);


    elif(node.label == AST_NUMBER):
        node.type = TYPE_NUMBER;
    elif(node.label == AST_STRING):
        node.type = TYPE_STRING;
    elif(node.label == AST_BOOL):
        node.type = TYPE_BOOL;

    elif(node.label == AST_FUNCTION_CALL):
        funcName = node.children[0].value;
        node.lineNo = node.children[0].lineNo;

        # first check if the function has been declared by the
        # programmer directly
        funcMatchObj = typeStack.getFuncIdentifierType(funcName);

        if (funcMatchObj == None):
            # the function has not been defined in the source file.
            # check if this is an identifier that points at a function.
            # ie. maybe the usef passed in an argument that was a function.
            idElement = typeStack.getIdentifierElement(funcName);
            if (idElement != None):
                funcType = idElement.identifierType;
                if (isFunctionType(funcType)):
                    # the coder is trying to call a function variable.  generate
                    # a function match object from that variable's type signature
                    # to perform type checking on the input arguments that the
                    # scripter provided
                    funcMatchObj = createFuncMatchObjFromJsonStr(funcType,idElement.astNode);
            else:
                errMsg = '\nError trying to call function named "' + funcName + '".  ';
                errMsg += 'That function is not defined anywhere.\n';
                errorFunction(errMsg,[node],[node.lineNo],progText);            


        if (funcMatchObj.element.astNode.label == AST_ONCREATE_FUNCTION):
            errMsg = '\nError trying to call OnCreate function.  ';
            errMsg += 'You are not allowed to call OnCreate yournode.  ';
            errMsg += 'The Waldo system itself will call the function ';
            errMsg += 'when creating your endpoint.\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);            

        #set my type as that returned by the function
        node.type = funcMatchObj.getReturnType();

        #check the argument types passed into the function
        funcArgList = node.children[1].children;
        allArgTypes = [];
        for s in funcArgList:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);
            allArgTypes.append(s.type);


        argError = funcMatchObj.argMatchError(allArgTypes,node);
        if (argError != None):
            #means that the types of the arguments passed into the
            #function do not match the arguments that the function
            #is declared with.

            argError.checkValid(); # just for debugging

            if (argError.errorType == FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH):
                #means that expected a different number of
                #arguments than what we called it with.
                errMsg = '\nError calling function "' + funcName + '".  ';
                errMsg += funcName + ' requires ' + str(argError.expected);
                errMsg += ' arguments.  Instead, you provided ' + str(argError.provided);
                errMsg += '.\n';

                errorFunction(errMsg,argError.astNodes,argError.lineNos,progText); 

            elif (argError.errorType == FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH):
                #means that although we got the correct number of
                #arguments, we had type mismatches on several of
                #them.
                errMsg = '\nError calling function "' + funcName + '".  ';
                for s in range (0, len(argError.argNos)):
                    errMsg += '\n\t';
                    errMsg += 'Argument number ' + str(argError.argNos[s]) + ' was expected ';
                    errMsg += 'to be of type ' + argError.expected[s] + ', but is inferrred ';
                    errMsg += 'to have type ' + argError.provided[s];

                errorFunction(errMsg,argError.astNodes,argError.lineNos,progText); 
            else:
                errMsg = '\nBehram error in AST_FUNCTION_CALL.  Have an error ';
                errMsg += 'type for a function that is not recognized.\n'
                errPrint(errMsg);
                assert(False);

    elif node.label == AST_FUNCTION_TYPE_LIST:
        print('\nBehram error: should never have gotten to type list\n');
        assert(False);

    elif (node.label == AST_TYPE):

        if node.value == TYPE_FUNCTION:
            # more compilcated types for functions

            # create a dictionary for the function type.
            # Function (In: Number, TrueFalse; Out: Text)
            # becomes:
            # { Type: 'Function',
            #    In: [
            #          {
            #            Type: "Number"
            #          },
            #          {
            #            Type: "TrueFalse"
            #          }],
            #    Returns: { Type: "Text"}
            # }
            typeSignature = buildFuncTypeSignature(node,progText,typeStack);
            node.type = json.dumps(typeSignature);
            node.value = node.type;

        elif node.value == TYPE_LIST:
            # more complicated types for lists
            # create a dictionary for the list type:
            # List (Element: Number)
            # becomes
            # { Type: 'List',
            #   ElementType: { Type: "Number" }}
            #
            typeSignature = buildListTypeSignature(node,progText,typeStack);
            node.type = json.dumps(typeSignature);
            node.value = node.type;

        elif node.value == TYPE_MAP:
            # more complicated types for maps
            # create a dictionary for the map type:
            # Map (From: Number, To: Text)
            # becomes
            # { Type: 'Map',
            #   From: { Type: 'Number'},
            #   To: {Type: 'Text'}
            #  }
            typeSignature,errMsg,errNodes = buildMapTypeSignature(node,progText,typeStack);

            if errMsg != None:
                # list comprehension!
                errLineNos = [ x.lineNo for x in errNodes];
                errorFunction(errMsg,errNodes, errLineNos, progText);


            node.type = json.dumps(typeSignature);
            node.value = node.type;

        else:
            # just assign the type directly since it is one of the
            # basic types Text, TrueFalse, or Number.
            node.type = node.value;

    elif (node.label == AST_LIST):
        node.type = EMPTY_LIST_SENTINEL;
        allTypes = [];

        # get all types from element nodes
        for element in node.children:
            element.typeCheck(progText,typeStack,avoidFunctionObjects);
            allTypes.append(element.type);


        # using nested for loop to ensure that all types are
        # tested against one another.  Type testing here is not
        # transitive (ie if a and b do not produce an error and b
        # and c do not produce an error, it does not mean that a
        # and c will not produce an error.  This is because of
        # empty lists: [] will match [Number] and [] will match
        # [TrueFalse], but [Number] will not match [TrueFalse].
        for typeCheckingIndex in range(0,len(allTypes)):

            potentialType = buildListTypeSignatureFromTypeName(
                allTypes[typeCheckingIndex]);

            potentialType = json.dumps(potentialType);

            node.type = moreSpecificListMapType(node.type,potentialType);

            for subTypeCheckingIndex in range(typeCheckingIndex+1,len(allTypes)):
                # now check that this type agrees with all subsequent types.
                firstType = allTypes[typeCheckingIndex];
                secondType = allTypes[subTypeCheckingIndex];

                if checkTypeMismatch(element,firstType,secondType,typeStack,progText):
                    errMsg = '\nError in list statement.  Different elements in the ';
                    errMsg += 'list have different types.  The ' + str(typeCheckingIndex+1);
                    errMsg += 'th element in the list has type [' + firstType + '].  The ';
                    errMsg += str(subTypeCheckingIndex + 1) + 'th has type [' + secondType + '].\n';
                    errorFunction(errMsg,[node], [node.lineNo], progText);


    elif node.label == AST_MAP:
        # type check all children
        node.type = EMPTY_MAP_SENTINEL;
        allIndexTypes = [];
        allValueTypes = [];

        for counterIndex in range(0,len(node.children)):
            item = node.children[counterIndex];
            index = item.children[0];
            value = item.children[1];

            index.typeCheck(progText,typeStack,avoidFunctionObjects);
            value.typeCheck(progText,typeStack,avoidFunctionObjects);

            if not isValueType(index.type):
                errMsg = '\nError in Map.  You can only index a map using ';
                errMsg += 'Number, Text, or TrueFalse.  However, the ' + str(counterIndex + 1);
                errMsg += 'th element in the map has type [' + index.type + '].';
                errorFunction(errMsg,[node,index],[node.lineNo,index.lineNo],progText);

            allIndexTypes.append(index.type);
            allValueTypes.append(value.type);

        for typeCheckingIndex in range(0,len(allIndexTypes)):
            indexType = allIndexTypes[typeCheckingIndex];
            valueType = allValueTypes[typeCheckingIndex];
            potentialType = buildMapTypeSignatureFromTypeNames(
                indexType,valueType);
            potentialType = json.dumps(potentialType);

            node.type = moreSpecificListMapType(node.type,potentialType);
            for subTypeCheckingIndex in range(typeCheckingIndex+1,len(allIndexTypes)):
                firstIndexType = allIndexTypes[typeCheckingIndex];
                secondIndexType = allIndexTypes[subTypeCheckingIndex];

                firstValueType = allValueTypes[typeCheckingIndex];
                secondValueType = allValueTypes[subTypeCheckingIndex];
                if checkTypeMismatch(index,firstIndexType,secondIndexType,typeStack,progText):
                    errMsg = '\nError in Map.  Different elements in the map ';
                    errMsg += 'have different types.  The ' + str(typeCheckingIndex + 1);
                    errMsg += 'th item in the map has an index of [' + firstIndexType + '].  ';
                    errMsg += 'However, the ' + str(subTypeCheckingIndex +1) + 'th has type [';
                    errMsg += secondIndexType + '].\n';
                    errorFunction(errMsg,[node],[node.lineNo],progText);

                if checkTypeMismatch(value,firstValueType,secondValueType,typeStack,progText):
                    errMsg = '\nError in Map.  Different elements in the map ';
                    errMsg += 'have different types.  The ' + str(typeCheckingIndex + 1);
                    errMsg += 'th item in the map has a value of [' + firstValueType + '].  ';
                    errMsg += 'However, the ' + str(subTypeCheckingIndex +1) + 'th has type [';
                    errMsg += secondValueType + '].\n';
                    errorFunction(errMsg,[node],[node.lineNo],progText);


    elif (node.label == AST_CONDITION_STATEMENT):
        #type check all children.  (type checks if, elseif, and
        #else statements).
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif ((node.label == AST_IF_STATEMENT) or
          (node.label == AST_ELSE_IF_STATEMENT)):
        boolCond = node.children[0];
        condBody = node.children[1];

        boolCond.typeCheck(progText,typeStack,avoidFunctionObjects);
        if (boolCond.type != TYPE_BOOL):
            errMsg = '\nError in If or ElseIf statement.  The condition ';
            errMsg += 'must evaluate to a TrueFalse type.  Instead, ';

            if (boolCond.type != None):
                errMsg += 'it evaluated to a type of ' + boolCond.type;
            else:
                errMsg += 'we could not infer the type';

            errMsg += '\n';
            errorFunction(errMsg,[boolCond],[boolCond.lineNo],progText);            

        if (condBody.label != AST_EMPTY):
            condBody.typeCheck(progText,typeStack,avoidFunctionObjects);


    elif(node.label == AST_BOOL_EQUALS) or (node.label == AST_BOOL_NOT_EQUALS):
        lhs = node.children[0];
        rhs = node.children[1];
        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        node.type = TYPE_BOOL;
        node.lineNo = lhs.lineNo;
        if (lhs.type == None):
            errMsg = '\nError when checking equality. ';
            errMsg += 'Cannot infer type of left-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;
        if (rhs.type == None):
            errMsg = '\nError when checking equality. ';
            errMsg += 'Cannot infer type of right-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;

        if (rhs.type != lhs.type):
            errMsg = '\nError when checking equality.  Both left-hand side ';
            errMsg += 'of expression and right-hand side of expression should ';
            errMsg += 'have same type.  Instead, left-hand side has type ';
            errMsg += lhs.type + ', and right-hand side has type ' + rhs.type;
            errMsg += '\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);


    elif ((node.label == AST_AND) or (node.label == AST_OR)):

        #keep track of separate expression types to simplify
        #error-reporting.
        expressionType = 'And';
        if (node.label == AST_OR):
            expressionType = 'Or';

        lhs = node.children[0];
        rhs = node.children[1];
        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        node.type = TYPE_BOOL;
        node.lineNo = lhs.lineNo;
        if (lhs.type == None):
            errMsg = '\nError when checking ' + expressionType + '. ';
            errMsg += 'Cannot infer type of left-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;
        if (rhs.type == None):
            errMsg = '\nError when checking ' + expressionType + '. ';
            errMsg += 'Cannot infer type of right-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;

        if (rhs.type != TYPE_BOOL):
            errMsg = '\nError whe checking ' + expressionType + '. ';
            errMsg += 'Right-hand side expression must be ' + TYPE_BOOL;
            errMsg += '.  Instead, has type ' + rhs.type + '\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);

        if (lhs.type != TYPE_BOOL):
            errMsg = '\nError whe checking ' + expressionType + '. ';
            errMsg += 'Left-hand side expression must be ' + TYPE_BOOL;
            errMsg += '.  Instead, has type ' + lhs.type + '\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);

    elif (node.label == AST_ELSE_STATEMENT):
        #type check else statement
        for s in node.children:
            if (s.label != AST_EMPTY):
                s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_PLUS):
        #perform plus separately from other math operations to
        #allow plus overload for concatenating strings.
        lhs = node.children[0];
        rhs = node.children[1];
        node.lineNo = lhs.lineNo;

        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);

        errSoFar = False;
        if ((lhs.type != TYPE_NUMBER) and (lhs.type != TYPE_STRING)):
            errMsg = '\nError with PLUS expression.  ';
            errMsg += 'Left-hand side should be a Number or a String.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + lhs.type + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);
            errSoFar = True;

        if ((rhs.type != TYPE_NUMBER) and (rhs.type != TYPE_STRING)):
            errMsg = '\nError with PLUS expression.  ';
            errMsg += 'Right-hand side should be a Number or a String.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + rhs.type + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);
            errSoFar = True;

        #won't be able to do anything further without appropriate
        #type information.
        if (errSoFar):
            return;

        if (rhs.type != lhs.type):
            errMsg = '\nError with PLUS expression.  Both the left- and ';
            errMsg += 'right-hand sides should have the same type.  Instead, ';
            errMsg += 'the left-hand side has type ' + lhs.type + ' and the ';
            errMsg += 'right-hand side has type ' + rhs.type + '.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);

        node.type = rhs.type;


    elif ((node.label == AST_MINUS) or (node.label == AST_MULTIPLY) or
          (node.label == AST_DIVIDE) or (node.label == AST_GREATER_THAN) or
          (node.label == AST_GREATER_THAN_EQ) or (node.label == AST_LESS_THAN) or
          (node.label == AST_LESS_THAN_EQ)):
        #check type checking of plus, minus, times, divide;
        #left and right hand side should be numbers, returns a number.

        #for error reporting
        expressionType  = 'MINUS';
        node.type = TYPE_NUMBER;                
        if (node.label == AST_MULTIPLY):
            expressionType = 'MULTIPLY';
        elif(node.label == AST_DIVIDE):
            expressionType = 'DIVIDE';
        elif(node.label == AST_GREATER_THAN):
            expressionType = 'GREATER THAN';
            node.type = TYPE_BOOL;                
        elif(node.label == AST_GREATER_THAN_EQ):
            expressionType = 'GREATER THAN EQUAL';                
            node.type = TYPE_BOOL;                
        elif(node.label == AST_LESS_THAN):
            expressionType = 'LESS THAN';
            node.type = TYPE_BOOL;                
        elif(node.label == AST_LESS_THAN_EQ):
            expressionType = 'LESS THAN EQUAL';
            node.type = TYPE_BOOL;                

        lhs = node.children[0];
        rhs = node.children[1];
        node.lineNo = lhs.lineNo;

        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);

        if (lhs.type != TYPE_NUMBER):
            errMsg = '\nError with ' + expressionType + ' expression.  ';
            errMsg += 'Left-hand side should be a Number.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + lhs.type + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);

        if (rhs.type != TYPE_NUMBER):
            errMsg = '\nError with ' + expressionType + ' expression.  ';
            errMsg += 'Right-hand side should be a Number.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + rhs.type + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);


    elif(node.label == AST_BOOLEAN_CONDITION):
        node.lineNo = node.children[0].lineNo;
        node.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);

        if (node.children[0].type != TYPE_BOOL):
            errMsg = '\nError in predicate of condition statement.  Should have ';
            errMsg += 'TrueFalse type.  Instead, ';
            if (node.children[0].type != None):
                errMsg += 'has type ' + node.children[0].type;
            else:
                errMsg += 'cannot infer type';
            errMsg += '.\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);
        else:
            node.type = node.children[0].type;

    elif(node.label == AST_ELSE_IF_STATEMENTS):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_ENDPOINT):
        # this will only check the body of endpoint functions. not the
        # global variables.

        #check if endpoint name matches previous endpoint name
        endName = node.children[0].value;

        #tell typestack that we are currently in this endpoint
        #body section.  unset it at end of elif.
        typeStack.setCurrentEndpointName(endName);

        currentLineNo = node.children[0].lineNo;
        if (not typeStack.isEndpoint(endName)):
            errMsg = 'Endpoint named ' + endName + ' was not defined at top of file ';
            errMsg = ' are you sure your endpoints match?';
            errLineNos = [currentLineNo,typeStack.endpoint1LineNo,typeStack.endpoint2LineNo];
            errorFunction(errMsg,[node],errLineNos,progText);

        #check endpoint body section
        if (len(node.children) >= 2):
            endpointBodySection = node.children[1];
            endpointBodySection.typeCheck(progText,typeStack,avoidFunctionObjects);
            
        #matches above set call.
        typeStack.unsetCurrentEndpointName();

    elif(node.label == AST_ENDPOINT_BODY_SECTION):            
        #typecheck global section
        node.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);
        #check function section.
        node.children[1].typeCheck(progText,typeStack,avoidFunctionObjects);

        #note: perform extra pop for stack that endpoint global
        #section put on.
        typeStack.popContext();

    elif(node.label == AST_ENDPOINT_GLOBAL_SECTION):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_DECLARATION):

        # type check the declared type statement (necessary
        # because of function statements).
        node.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);

        declaredType = node.children[0].value;
        node.lineNo = node.children[0].lineNo;

        if (node.children[1].label != AST_IDENTIFIER):
            errMsg = '\nError at declaration statement. ';
            errMsg += 'Must have an identifier for left hand ';
            errMsg += 'side of declaration.\n';
            errorFunction(errMsg,[node],[currentLineNo],progText);
            return;

        name = node.children[1].value;
        currentLineNo = node.children[0].lineNo;
        if (len(node.children) == 3):
            rhs = node.children[2];
            rhs.typeCheck(progText,typeStack,avoidFunctionObjects);
            rhsType = rhs.type;

            if (checkTypeMismatch(rhs,declaredType,rhsType,typeStack,progText)):
                errMsg = 'Type mismatch for variable named "' + name + '".';
                errMsg += '  Declared with type [' + declaredType + '], but ';
                errMsg += 'assigned to type [' + rhsType + '].';
                errorFunction(errMsg,[node],[currentLineNo],progText);

        else:
            # not initialization information.  There are several
            # types that require initialization information.  Most
            # importantly, user-defined functions do.  Throw an
            # error if user-defined function does not.
            if (isFunctionType(declaredType)):
                errMsg = 'Error when declaring a user-defined function ';
                errMsg += 'named "' + name + '".  Every user-defined ';
                errMsg += 'function requires that it should be initialized.  ';
                errMsg += 'That means that you have to set ' + name + ' ';
                errMsg += 'to a valid function when you declare it.';
                errorFunction(errMsg,[node],[currentLineNo],progText);

        #check if already have a function or variable with the
        #targetted name.
        prevId = typeStack.getIdentifierElement(name);
        prevFunc = typeStack.getFuncIdentifierType(name);
        if ((prevId != None) or (prevFunc != None)):
            nodes =[node];
            lineNos = [currentLineNo];
            if (prevId != None):
                nodes.append(prevId.astNode);
                lineNos.append(prevId.lineNum);
            if (prevFunc != None):
                nodes.append(prevFunc.element.astNode);
                lineNos.append(prevId.element.lineNum);

            errMsg = 'Error trying to name a variable "' + name;
            errMsg += '".  Already have a function or variable with ';
            errMsg += 'the same name.'
            errorFunction(errMsg,nodes,lineNos,progText);

        typeStack.addIdentifier(name,declaredType,None,node,currentLineNo);
        node.type = declaredType;

    elif(node.label == AST_RETURN_STATEMENT):
        node.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);

        typeCheckError = typeStack.checkReturnStatement(node);
        if (typeCheckError != None):
            errorFunction(typeCheckError.errMsg,typeCheckError.nodes,typeCheckError.lineNos,progText);
        node.type = TYPE_NOTHING;

    elif(node.label == AST_IDENTIFIER):
        name = node.value;
        typer,ctrldBy = typeStack.getIdentifierType(name);
        if (typer == None):
            # also check if it's an identifier for a non-variable
            # function.
            funcType = typeStack.getFuncIdentifierType(name);
            if (funcType == None):
                errMsg = 'Cannot infer type of ' + name + '.  Are you sure it is valid?';
                errorFunction(errMsg,[node],[node.lineNo],progText);
                node.type = 'Undefined';
            else:
                node.type = json.dumps(funcType.createJsonType());
        else:
            node.type = typer;


    elif(node.label == AST_ENDPOINT_FUNCTION_SECTION):
        # this just type checks the headers of each function.
        # Have to insert the header of each function
        for s in node.children:
            functionDeclarationTypeCheck(
                s,progText,typeStack,avoidFunctionObjects);

        # want to incorporate each messasge sequence function's
        # declaration into context as well.
        msgSeqSection = getMsgSeqSection(typeStack.rootNode);
        for msgSeq in msgSeqSection.children:
            # each msgSeq has label MessageSequence
            msgSeqFunctions = msgSeq.children[2];
            for msgSeqFunc in msgSeqFunctions.children:
                if isEndpointSequenceFunction(
                    msgSeqFunc,typeStack.currentEndpointName):
                    # ensure that this function's name gets mapped
                    # into current endpoint's function context.
                    functionDeclarationTypeCheck(
                        msgSeqFunc,progText,typeStack,avoidFunctionObjects);

        # now we type check the bodies of each function
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

        # now we type check the bodies of the message sequence
        # functions to ensure that they also are okay from type
        # checking.
        typeCheckMessageSequencesEndpoint(msgSeqSection,progText,typeStack);

            
    elif ((node.label == AST_PUBLIC_FUNCTION) or
          (node.label == AST_PRIVATE_FUNCTION) or
          (node.label == AST_ONCREATE_FUNCTION)):
        '''
        begins type check for body of the function, this code
        pushes arguments into context and then calls recursive
        type check on function body itself.
        '''
        ## create a new type context to insert intermediate data
        ## in.  context is popped at the end of the elif statement.
        typeStack.pushContext();
        funcName = node.children[0].value;            

        stackFunc = typeStack.getFuncIdentifierType(funcName);

        #set my line number to be the line number of when the
        #function type was declared.
        node.lineNo = node.children[0].lineNo;

        if (stackFunc == None):
            errMsg = 'Behram error: should have inserted function ';
            errMsg += 'with name "' + funcName + '" into type stack ';
            errMsg += 'before type checking function body.'
            errPrint('\n\n');
            errPrint(errMsg);
            errPrint('\n\n');
            assert(False);

        #insert passed in arguments into context;
        if ((node.label == AST_PUBLIC_FUNCTION) or (node.label == AST_PRIVATE_FUNCTION)):
            funcDeclArgListIndex = 2;
            funcBodyIndex = 3;
            funcNameIndex = 0;
        elif(node.label == AST_ONCREATE_FUNCTION):
            funcBodyIndex = 2;
            funcDeclArgListIndex = 1;
            funcNameIndex = 0;
        else:
            errMsg = '\nBehram error: invalid function ';
            errMsg += 'type when type checking functions\n';
            errPrint(errMsg);


        if (funcDeclArgListIndex != None):
            #add all arguments passed in in function declaration to
            #current context.
            node.children[funcDeclArgListIndex].typeCheck(
                progText,typeStack,avoidFunctionObjects);


        # when type check body, 
        typeStack.addCurrentFunctionNode(node);

        # type check the actual function body
        node.children[funcBodyIndex].typeCheck(progText,typeStack,avoidFunctionObjects);

        ## remove the created type context
        typeStack.popContext();

    elif(node.label == AST_FUNCTION_BODY):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif (node.label == AST_FUNCTION_DECL_ARGLIST):
        #iterate through each individual declared argument
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif (node.label == AST_FUNCTION_DECL_ARG):
        '''
        for declared argument, checks for its collision
        with existing variables and functions, and then inserts
        it into a typestack context.
        '''
        node.lineNo = node.children[0].lineNo;
        argType = node.children[0].value;
        argName = node.children[1].value;

        collisionObj = typeStack.checkCollision(argName,node);

        if (collisionObj != None):
            #FIXME: for this error message, may want to
            #re-phrase with something about scope, so do not
            #take the wrong error message away.

            errMsg = 'Error trying to name an argument "';
            errMsg += argName + '" in your function.  ';
            errMsg += 'You already have a function or variable ';
            errMsg += 'with the same name.';

            errorFunction(errMsg,collisionObj.nodes,collisionObj.lineNos,progText);
        else:
            if (isFunctionType(argType) or (argType == TYPE_FUNCTION)) and avoidFunctionObjects:
                pass;
            else:
                typeStack.addIdentifier(argName,argType,None,node,node.lineNo);


    elif (node.label == AST_FUNCTION_BODY_STATEMENT):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif (node.label == AST_STRING):
        node.type = TYPE_STRING;
    elif (node.label == AST_NUMBER):
        node.type = TYPE_NUMBER;
    elif (node.label == AST_BOOL):
        node.type = TYPE_BOOL;

    elif (node.label == AST_ASSIGNMENT_STATEMENT):
        lhs = node.children[0];
        node.lineNo = lhs.lineNo;
        
        if (lhs.label != AST_IDENTIFIER) and (lhs.label != AST_BRACKET_STATEMENT):
            errMsg = '\nError in assignment statement.  Can only assign ';
            errMsg += 'to a variable.  (Left hand side must be a variable)\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);
            return;

        rhs = node.children[1];

        if (lhs.label == AST_IDENTIFIER):
            lhsType,controlledBy = typeStack.getIdentifierType(lhs.value);
            lhs.type  = lhsType;
        else:
            lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
            lhsType = lhs.type;
            controlledBy = None;

        if (lhsType == None):
            errMsg = '\nError in assignment statement.  Left hand side ';
            errMsg += 'has no type information.\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);
            return;

        if (controlledBy != None) and (controlledBy != TYPE_NOTHING):
            # check if the variable that we are assigning to is
            # controlled by this endpoint or another endpoint.
            if (typeStack.currentEndpointName != controlledBy):
                errMsg = '\nError: you are trying to write to a ';
                errMsg += 'variable named "' + lhs.value + '" in ';
                errMsg += 'endpoint "' + typeStack.currentEndpointName + '".  ';
                errMsg += 'However, this variable is controlled by "';
                errMsg += typeStack.getOtherEndpointName() + '," which ';
                errMsg += 'means that only functions in ';
                errMsg += typeStack.getOtherEndpointName() + ' can assign ';
                errMsg += 'it values.  Either change who controls ';
                errMsg += lhs.value + ' in the Shared section, or ';
                errMsg += 'do not write to it in ' + typeStack.currentEndpointName;
                errMsg += '.\n';
                errorFunction(errMsg,[node],[node.lineNo],progText);

        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhsType = rhs.type;

        if (rhsType == None):
            errMsg = '\nError in assignment statement.  Right hand side ';
            errMsg += 'has no type information.\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);
            return;

        if (checkTypeMismatch(rhs,lhsType,rhsType,typeStack,progText)):
            #FIXME: this should really identify *why* we inferred
            #the type that we did.  Maybe where the variable was
            #decalred too.
            errMsg = '\nError in assignment statement.  Type of ';
            errMsg += 'left-hand side (' + lhsType + ') does not ';
            errMsg += 'match type of right-hand side (' + rhsType;
            errMsg += ').\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);

        # makes type checking declarations easier in sequence globals
        # section.
        node.type = lhs.type;
            
    else:
        errPrint('\nLabels that still need type checking: ');
        errPrint('\t' + node.label);




    #remove the new context that we had created.  Note: shared
    #section is intentionally missing.  Want to maintain that 
    #context while type-checking the endpoint sections 
    #skip global section too.
    if ((node.label == AST_ROOT) or
        (node.label == AST_ENDPOINT_FUNCTION_SECTION)):
        
        typeStack.popContext();
        

def functionDeclarationTypeCheck(node, progText,typeStack,avoidFunctionObjects):
    '''
    Takes a node of type public function, private function,
    AST_MESSAGE_SEND_SEQUENCE_FUNCTION,
    AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION, ONCREATE_FUNCTION

    send function, or message receive function.  Does not set any
    types itself, but rather loads functions into the typeStack
    itself.
    '''
    if ((node.label != AST_PUBLIC_FUNCTION) and
        (node.label != AST_PRIVATE_FUNCTION) and
        (node.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION) and
        (node.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION) and
        (node.label != AST_ONCREATE_FUNCTION)):
        errPrint('\n\n');
        errPrint(node.label);
        errPrint('\n\n');
        errPrint('\nBehram error, sending an incorrect tag to be loaded into functionDeclarationTypeCheck\n');
        assert(False);


    if ((node.label == AST_PUBLIC_FUNCTION) or (node.label == AST_PRIVATE_FUNCTION)):
        #get declared return type (only applicable for functions and public functions)
        node.children[1].typeCheck(progText,typeStack,avoidFunctionObjects);
        returnType = node.children[1].type;
        argDeclIndex = 2;
        funcNameIndex = 0;
    elif(node.label == AST_ONCREATE_FUNCTION):
        returnType = TYPE_NOTHING;
        argDeclIndex = 1;
        funcNameIndex = 0;
    elif node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        argDeclIndex = 2;
        returnType = TYPE_NOTHING;
        funcNameIndex = 1;
    elif node.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        # does not take any arguments
        argDeclIndex = None;
        funcNameIndex = 1;
        returnType = TYPE_NOTHING;


    funcName = node.children[funcNameIndex].value;            
    node.lineNo = node.children[funcNameIndex].lineNo;

    #get types of function arguments

    #add a context to type stack for arg declarations and pop it
    #later so that arg decl arguments do not persist after the
    #type check of arg text.
    typeStack.pushContext();
    if (argDeclIndex != None):
        # fill in type information of all the arguments.
        node.children[argDeclIndex].typeCheck(
            progText,typeStack,avoidFunctionObjects);

    typeStack.popContext();

    # build the input argument type list for arguments.
    argTypeList = [];
    if (argDeclIndex != None):
        args = node.children[argDeclIndex].children;

        for t in args:
            #each t should now be of type FUNCTION_DECL_ARG

            if (len(t.children) == 0):
                #means that we have a function that takes no arguments.
                continue;

            #set the type of t to the type identifier of the argument.
            t.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);
            t.type = t.children[0].value;

            #add the argument type to the typeStack representation for this function.
            argTypeList.append(t.type);

    else:
        # means that we are a message receive fucntion.  we do not
        # actually need to be careful here, because you cannot
        # directly call a message receive function (the system
        # calls it for you when you receive a message).  So just
        # insert gibberish for argument.
        argTypeList.append(TYPE_NOTHING);

    collisionObj = typeStack.checkCollision(funcName,node);
    if collisionObj != None:
        #FIXME: for this error message, may want to
        #re-phrase with something about scope, so do not
        #take the wrong error message away.
        errMsg = 'Error trying to name a function "' + funcName;
        errMsg += '".  Already have a function or variable with ';
        errMsg += 'the same name.'
        errorFunction(errMsg,collisionObj.nodes,collisionObj.lineNos,progText);
    else:
        traceError = typeStack.addFuncIdentifier(funcName,returnType,argTypeList,node,node.lineNo);
        if traceError != None:
            errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);
            


def checkTypeMismatch(rhs,lhsType,rhsType,typeStack,progText):
    '''
    @returns {Bool} True if should throw type mismatch error.  False
    otherwise.

    Reasons not to indicate type mismatch error
    
       * lhsType and rhsType are the same
       
       * rhsType is a message literal and is being assigned to an
         outgoing or incoming message and all its fields agree with
         those.
    
    '''
    errorTrue = False;
    if (lhsType != rhsType):
        errorTrue = True;
        # message literals have indeterminate types until
        # they're assigned to an identifier that expects them
        # to have an OutgoingMessage or IncomingMessage type.
        # Here is where we check that.

        # Must use special checks to type check lists.  For
        # instance, if one side presents empty_list and other is
        # [Number], should not produce typecheck error.

        # determine if lists are involved
        if (isListType(lhsType) and isListType(rhsType)):
            errorTrue = listTypeMismatch(lhsType,rhsType,typeStack,progText);

        elif isMapType(lhsType) and isMapType(rhsType):
            errorTrue = mapTypeMismatch(lhsType,rhsType,typeStack,progText);
        else:
            # both sides were not lists and there types did not
            # match.  will throw an error.
            errorTrue = True;
             
    return errorTrue;


def mapTypeMismatch(mapTypeA, mapTypeB,typeStack,progText):
    '''
    @see listTypeMismatch
    '''
    if (mapTypeA == EMPTY_MAP_SENTINEL) or (mapTypeB == EMPTY_MAP_SENTINEL):
        # any time one side or the other side is an empty map, we
        # know we're okay because both sides have to be maps.
        return False;

    
    dictA = json.loads(mapTypeA);
    dictB = json.loads(mapTypeB);


    indexTypeA = dictA[JSON_MAP_FROM_TYPE_FIELD];
    indexTypeB = dictB[JSON_MAP_FROM_TYPE_FIELD];

    valueTypeA = dictA[JSON_MAP_TO_TYPE_FIELD];
    valueTypeB = dictB[JSON_MAP_TO_TYPE_FIELD];


    # these are the indices for 
    indTypeA = indexTypeA;
    if (not isinstance(indexTypeA,basestring)):
        indTypeA = json.dumps(indexTypeA);

    indTypeB = indexTypeB;
    if (not isinstance(indexTypeB,basestring)):
        indTypeB = json.dumps(indexTypeB);

    valTypeA = valueTypeA;
    if (not isinstance(valueTypeA,basestring)):
        valTypeA = json.dumps(valueTypeA);

    valTypeB = valueTypeB;
    if (not isinstance(valueTypeB,basestring)):
        valTypeB = json.dumps(valueTypeB);

    if checkTypeMismatch(None,indTypeA,indTypeB,typeStack,progText):
        # there's an error because the indices have to match.
        return True;

    if (not isMapType(valTypeA)) or (not isMapType(valTypeB)):
        # handles all cases where one or both values are not maps
        return checkTypeMismatch(None,valTypeA,valTypeB,typeStack,progText);

    # both values are maps.  know that we can quit with no error if
    # one or other is sentinel.
    if (valTypeA == EMPTY_MAP_SENTINEL) or (valTypeB == EMPTY_MAP_SENTINEL):
        return False;
    
    # recurse on map types
    return mapTypeMismatch(elTypeA,elTypeB,typeStack,progText);


def listTypeMismatch(listTypeA, listTypeB,typeStack,progText):
    '''
    @param{String} listTypeA, listTypeB: both are known to be list
    types.
    
    @returns{Bool} True if there is a mismatch, False otherwise.

    Note, that for list types it is inadequate to do a pure equality
    test type signatures (ie listTypeA == listTypeB) to determine if
    there is or is not a type mismatch.  This is because of the following case:

    List(Element: Number) l = [];

    The lhs has type [Number] and the rhs has type
    [EMPTY_LIST_SENTINEL].  However, the assignment is okay and should
    not produce a type mismatch.

    The following however should produce a type mismatch:
    
    List(Element: Number) l = [True];
        
    '''
    if (listTypeA == EMPTY_LIST_SENTINEL) or (listTypeB == EMPTY_LIST_SENTINEL):
        # any time one side or the other side is an empty list, we
        # know we're okay because both sides have to be lists.
        return False;

    
    dictA = json.loads(listTypeA);
    dictB = json.loads(listTypeB);

    elementTypeA = dictA[JSON_LIST_ELEMENT_TYPE_FIELD];
    elementTypeB = dictB[JSON_LIST_ELEMENT_TYPE_FIELD];


    elTypeA = elementTypeA;
    if (not isinstance(elementTypeA,basestring)):
        elTypeA = json.dumps(elementTypeA);

    elTypeB = elementTypeB;
    if (not isinstance(elementTypeB,basestring)):
        elTypeB = json.dumps(elementTypeB);
        
    
    if (not isListType(elTypeA)) or (not isListType(elTypeB)):
        # handles all cases where one or both are not lists
        return checkTypeMismatch(None,elTypeA,elTypeB,typeStack,progText);

    # both elements are list types.  know that we can quit if one or other is a sentinel.
    if (elTypeA == EMPTY_LIST_SENTINEL) or (elTypeB == EMPTY_LIST_SENTINEL):
        return False;
    
    # recurse on list types
    return listTypeMismatch(elTypeA,elTypeB,typeStack,progText);



def typeCheckMapBracket(toReadFrom,index,typeStack,progText):
    '''
    @param {astNode with label map} toReadFrom --- map ... already
    type checked before entering this function.
    
    @param {astNode} index ... already type checked before entering
    this function.

    @return (a,b,c,d)
      a {Bool} --- True if there is an error.  False otherwise.

      b {String or None} --- Type to apply to parent node or None if
        error.
      
      c {String or None} --- String with error message or none if no
        error.  
      
      d {Array of ast nodes or None} --- None if no error.  Otherwise,
        a list of nodes that caused the errors.
      '''
    if not isValueType(index.type):
        errMsg = '\nYou can only index into a map using Text, Numer, ';
        errMsg += 'or Number.  Instead, your index has type [ ' + index.type + ' ].\n';
        astErrorNodes = [ index ];
        return True,None,errMsg,astErrorNodes;

    if toReadFrom.type == EMPTY_MAP_SENTINEL:
        # reading from a value that is empty
        errMsg = '\nYou cannot read from an empty map.\n';
        astErrorNodes = [ toReadFrom ];
        return True, None, errMsg, astErrorNodes;

    # ensure that the type of the index we are reading from in
    # readingFrom matches the type of the index actually doing the
    # reading.
    toReadFromIndexType = getMapIndexType(toReadFrom.type);
    indexType = index.type;
    if checkTypeMismatch(index,toReadFromIndexType,indexType,typeStack,progText):
        errMsg = '\nError reading from map.  You were supposed to index into the ';
        errMsg += 'map with an indexer of type [ ' + toReadFromIndexType + ' ].  ';
        errMsg += 'Instead, you indexed in with type [ ' + indexType + ' ].\n';
        astErrorNodes = [ toReadFrom, index ];
        return True, None, errMsg, astErrorNodes;
    
    statementType = getMapValueType(toReadFrom);
    return False,statementType,None,None;

def typeCheckListBracket(toReadFrom,index,typeStack,progText):
    '''
    @see typeCheckMapBracket
    '''
    if toReadFrom.type == EMPTY_LIST_SENTINEL:
        errMsg = '\nError indexing into empty list.\n';
        astErrorNodes = [ toReadFrom ];
        return True, None, errMsg, astErrorNodes;

    if index.type != TYPE_NUMBER:
        errMsg = '\nError.  Can only index into a list using a number.  ';
        errMsg += 'Instead, you used a type [ ' + index.type + ' ].\n';
        astErrorNodes = [ index ];
        return True, None, errMsg, astErrorNodes;

    # no type error that we can catch.  Return that the statement will
    # have value of whatever is being accessed.
    listValType = getListValueType(toReadFrom.type);
    return False,listValType,None,None;



def typeCheckMessageSequencesEndpoint(msgSeqSectionNode,progText,typeStack):
    '''
    Type checks the bodies of all message sequences for the current
    endpoint.  For each sequence, create a typestack context, loading
    all shared variables into it (including those passed into message
    send function).

    Then, type check all functions for the current enpdoint name.

    When type checking, be careful to throw an error if a function
    object is tried to be used as shared.  Similarly, do not load
    function object into shared section of other endpoint.
    '''

    if msgSeqSectionNode.label != AST_MESSAGE_SEQUENCE_SECTION:
        errMsg = '\nBehram error: should pass message sequence ';
        errMsg += 'section node as first argument to ';
        errMsg += 'typeCheckMessageSequencesEndpoint.  Instead, got: "';
        errMsg += msgSeqSectionNode.label + '"\n';
        print(errMsg);
        assert(False);

    currentEndpointName = typeStack.currentEndpointName;
    
    # perform the type checking of function bodies for sequences
    for msgSeqNode in msgSeqSectionNode.children:
        addSequenceGlobals(msgSeqNode,progText,typeStack,currentEndpointName);
        typeCheckMessageFunctions(msgSeqNode,progText,typeStack,currentEndpointName);
        removeSequenceGlobals(typeStack);


def typeCheckMessageFunctions(msgSeqNode,progText,typeStack,currentEndpointName):
    '''
    For each message function in the message sequence that belongs to
    currentEndpointName, type check its body.
    '''
    msgSeqFunctionsNode = msgSeqNode.children[2];
    for msgSeqFuncNode in msgSeqFunctionsNode.children:
        # keeps line numbers straight
        msgSeqFuncNode.lineNo = msgSeqFuncNode.children[0].lineNo;
        if isEndpointSequenceFunction(msgSeqFuncNode,currentEndpointName):
            name = msgSeqFuncNode.children[1].value;

            msgBodyNode = msgSeqFuncNode.children[2];
            if msgSeqFuncNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
                msgBodyNode = msgSeqFuncNode.children[3];
            typeStack.pushContext();
            
            # when type check body, need to keep track of current
            # function so can ensure return type is valid.
            typeStack.addCurrentFunctionNode(msgSeqFuncNode);
            msgBodyNode.typeCheck(progText,typeStack,False);
            typeStack.popContext();

            
def removeSequenceGlobals(typeStack):
    '''
    Complements addSequenceGlobals.  Discards extra context that
    addSequenceGlobals creates.
    '''
    typeStack.popContext();


    
def addSequenceGlobals(msgSeqNode,progText,typeStack,currentEndpointName):
    '''
    @param {AstNode} msgSeqNode --- Should have label
    AST_MESSAGE_SEQUENCE.

    @param {AstTypeStack} typeStack

    @param {String} currentEndpointName

    Runs through variables whose lifetimes are only for the scope of
    the message sequence and adds them to context.  (Note: this
    includes any variables that are passed in through the initial
    message send function, however, the proscription against function
    objects does not apply if the function object is used by the same
    endpoint as uses it later.)

    Remember to call removeSequenceGlobals after calling this
    function, or you'll end up with a garbage context on the
    typeStack.
    '''
    typeStack.pushContext();

    if msgSeqNode.label != AST_MESSAGE_SEQUENCE:
        errMsg = '\nBehram error: should only add globals to a sequence.\n';
        print(errMsg);
        assert(False);

    # add variables from variables explicitly shared at top of sequence.
    globalsSectionNode = msgSeqNode.children[1];
    for declNode in globalsSectionNode.children:
        warnMsg = '\nBehram error: need to ensure that the sequence global ';
        warnMsg += 'nodes are not initialized using inaccessible parameters.  ';
        warnMsg += 'Such as endpoint global variables.\n';
        print(warnMsg);

        # should add the node to the newly-pushed context.
        declNode.typeCheck(progText,typeStack,False);

        if (declNode.type == TYPE_FUNCTION) or isFunctionType(declNode.type):
            errMsg = 'Error with sequence shared variables.  You cannot share ';
            errMsg += 'a function object across multiple nodes.';
            errNodes = [declNode];
            astLineNos = [declNode.lineNo];
            errorFunction(errMsg,errNodes,astLineNos,progText);

    # add variables from variables that are shared by being arguments
    # to send message.
    msgSequenceFunctionsNode = msgSeqNode.children[2];
    msgSendNode = msgSequenceFunctionsNode.children[0];
    msgSendNodeEndpointName = msgSendNode.children[0];
    msgSendEndpointName = msgSendNodeEndpointName.value;
    argList = msgSendNode.children[2];

    # include each of the arguments to the message send function as
    # sequence-global variables.
    if msgSendEndpointName == currentEndpointName:
        # do not add function objects to context when type check them
        argList.typeCheck(progText,typeStack,False);
    else:
        # add function objects to context when type check them
        argList.typeCheck(progText,typeStack,True);

