#!/usr/bin/python

import sys;
import os;

import d3.treeDraw as treeDraw;
from astLabels import *;
from astTypeCheckStack import TypeCheckContextStack;
from astTypeCheckStack import FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH;
from astTypeCheckStack import FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_SUCCEED;
from astTypeCheckStack import createFuncMatchObjFromJsonStr;
from parserUtil import errPrint;
from parserUtil import isFunctionType;
from parserUtil import isTemplatedType;
from parserUtil import isListType;
import json;


TYPE_ERROR_ENCOUNTERED = False;

def indentText(text,numIndents):
    returner = '';
    for s in range(0,numIndents):
        returner += '\t'
    returner += text;
    return returner;

def isEmptyAstNode(node):
    return (node.type == "EMPTY");

        
class AstNode():
    
    def __init__(self,_label,_lineNo=None,_linePos=None,_value=None):
        '''
        Only leaf nodes have values that are not None.
        (Things like Numbers, Strings, Identifiers, etc.)
        '''
        self.label    = _label;
        self.value    = _value;
        self.lineNo   = _lineNo;
        self.linePos  = _linePos;
        self.type     = None;
        self.note     = None;
        self.children = [];

    def setNote(self,note):
        self.note = note;
        
    def addChild(self, childToAdd):
        self.children.append(childToAdd);


    def prependChild(self,childToPrepend):
        self.children.insert(0,childToPrepend);
        
    def addChildren(self, childrenToAdd):
        for s in childrenToAdd:
            self.children.append(s);
        
    def getChildren(self):
        return self.children;

    def printAst(self,filename=None):
        text = self.toJSON();
        if (filename != None):
            filer = open(filename,'w');
            filer.write(text);
            filer.flush();
            filer.close();
        else:
            print(self.toJSON());


    def typeCheck(self,progText,typeStack=None):
        #based on types of children, check my type.  Also, pass up
        #line numbers.
        
        if ((self.label != AST_ROOT) and (typeStack == None)):
            errPrint('\nBehram error.  Must have typeStack unless root node\n');
            assert(False);
        elif(self.label == AST_ROOT):
            typeStack = TypeCheckContextStack();

            
        if ((self.label == AST_ROOT) or
            (self.label == AST_SHARED_SECTION) or
            (self.label == AST_ENDPOINT_GLOBAL_SECTION) or
            (self.label == AST_ENDPOINT_FUNCTION_SECTION)):
            #each of these create new contexts.  don't forget to
            #remove several of them at the bottom of the function.
            #note: do not have ast_function_body here because need to
            #create a new context before get into function body so
            #that we can catch arguments passed into the function.
            
            typeStack.pushContext();


        if(self.label == AST_ROOT):
            #top of program

            #getting protocol object name
            typeStack.protObjName = self.children[0].value;

            #handling alias section
            aliasSection = self.children[1];


            #endpoint 1
            typeStack.endpoint1 = aliasSection.children[0].value; 
            typeStack.endpoint1LineNo = aliasSection.children[0].lineNo;
            typeStack.endpoint1Ast = aliasSection.children[0];
            
            #endpoint 2
            typeStack.endpoint2 = aliasSection.children[1].value; 
            typeStack.endpoint2LineNo = aliasSection.children[1].lineNo;
            typeStack.endpoint2Ast = aliasSection.children[1];             
            
            if (typeStack.endpoint1 == typeStack.endpoint2):
                errorFunction('Cannot use same names for endpoints',[typeStack.endpoint1,typeStack.endpoint2],[typeStack.endpoint1LineNo,typeStack.endpoint2LineNo],progText);

                            
            #Do first level of type chcecking trace items.  see notes
            #in corresponding elif.
            self.children[2].typeCheck(progText,typeStack);

            #get into shared section
            #note: shared section should leave its context on the stack.
            self.children[3].typeCheck(progText,typeStack);

            #check one endpoint
            self.children[4].typeCheck(progText,typeStack);

            #check one endpoint
            self.children[5].typeCheck(progText,typeStack);

            #Checks if there were msgSends or msgReceives assumed in a
            #trace line that weren't actually defined in an endpoint
            #section.
            traceError = typeStack.checkUndefinedTraceItems();
            if (traceError != None):
                errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);

            # check that output of one trace line matched input of
            # another
            traceError =  typeStack.checkTraceItemInputOutput();
            if (traceError != None):
                errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);

            
        elif(self.label == AST_TRACE_SECTION):
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

            typeStack.setAstTraceSectionNode(self);
            
            # skip the first child, which is a name for the 
            for s in self.children:
                s.typeCheck(progText,typeStack);


        elif(self.label == AST_BRACKET_STATEMENT):
            #left node must be a message
            #right node must be a string if it's a message
            toReadFrom = self.children[0];
            index = self.children[1];
            toReadFrom.typeCheck(progText,typeStack);
            index.typeCheck(progText,typeStack);

            self.lineNo = index.lineNo;


            if (index.type != TYPE_STRING):
                errMsg = '\nTo index into a message, you must use ';
                errMsg += 'the name of the field you are looking for.  ';
                errMsg += 'This name must be a String.  However, you ';
                errMsg += 'provided a ' + index.type + '\n';
                astErrorNodes = [self];
                astLineNos = [self.lineNo];
                errorFunction(errMsg,astErrorNodes,astLineNos,progText);

            indexStr = index.value;
                
            if (toReadFrom.type == TYPE_INCOMING_MESSAGE):

                # checking if the referenced field exists in the
                # incoming message.  inserting a dummy type to ensure
                # that we will get back what the real type of the
                # field should be if the field name exists.
                result,expectedType = typeStack.fieldAgreesWithCurrentIncoming(indexStr,TYPE_NOTHING);
                checkResult = True;
                potentialErrNode = typeStack.currentIncoming;
                potentialErrMsg = 'incoming';
                
            elif(toReadFrom.type == TYPE_OUTGOING_MESSAGE):
                result,expectedType = typeStack.fieldAgreesWithCurrentOutgoing(indexStr,TYPE_NOTHING);
                checkResult = True;
                potentialErrNode = typeStack.currentOutgoing;
                potentialErrMsg = 'outgoing';
            else:
                checkResult = False;
                errMsg = '\nError when using "[" and "]".  Can only ';
                errMsg += 'look up an element from a Message.  The type ';
                errMsg += 'of ' + toReadFrom.value + ' is ' + toReadFrom.type;
                errMsg += '\n';
                astErrorNodes = [self];
                astLineNos = [self.lineNo];
                errorFunction(errMsg,astErrorNodes,astLineNos,progText);                                    


            if (checkResult):
                #means that it was an incoming or outgoing message
                #that we were indexing into.  actually check the
                #result of the indexing.
                if (result == MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST):
                    # means that this field does not exist in incoming
                    # message field, throw an error.
                    errMsg = '\nAccessing a field "' + indexStr + '" of an ';
                    errMsg += potentialErrMsg;
                    errMsg += ' message that does not exist.  Compare ';
                    errMsg += 'to the actual type of the incoming message before ';
                    errMsg += 'proceeding.\n';
                    astErrorNodes = [self,potentialErrNode];
                    astLineNos = [self.lineNo,potentialErrNode.lineNo];
                    errorFunction(errMsg,astErrorNodes,astLineNos,progText);

                    # assign to nothing type so can continue with type checking.
                    self.type = TYPE_NOTHING;
                    
                elif (result == MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH):
                    # expected because we used
                    # TYPE_NOTHING. expectedType now contains what the
                    # type of this statement should be.
                    self.type = expectedType;
                else:
                    errMsg = '\nBehram error.  Should have no data in a message that ';
                    errMsg += 'matches type nothing\n';
                    assert(False);

                
        elif(self.label == AST_TRACE_LINE):
            #first, checking that each trace item has an endpoint
            #prefix, and second that the prefixes alternate so that
            #messages are being sent between different endpoints.

            #add trace line to traceManager of typeStack so can do
            #type checks after endpoint bodies are type checked.
            typeStack.addTraceLine(self);
            
            
            #will hold the name of the last endpoint used in trace line.
            lastEndpoint = None;
            firstChild = True;
            for traceItem in self.children:
                
                # skip first item, because that is the potential name
                # of the trace line messsage sequence.
                if firstChild:
                    firstChild = False;
                    continue;

                
                endpointName = traceItem.children[0].value;
                currentLineNo = traceItem.children[0].lineNo;

                if (self.lineNo == None):
                    self.lineNo = currentLineNo;
                    
                funcName = traceItem.children[1].value;

                endpoint1Ast = typeStack.endpoint1Ast;
                endpoint2Ast = typeStack.endpoint2Ast;
                endpoint1Name = typeStack.endpoint1;
                endpoint2Name = typeStack.endpoint2;
                endpoint1LineNo = typeStack.endpoint1LineNo;
                endpoint2LineNo = typeStack.endpoint2LineNo;

                #check that are using declared endpoints.
                if (not typeStack.isEndpoint(endpointName)):
                    
                    errMsg = '\nError in trace declaration.  Each element ';
                    errMsg += 'in the trace line should have the form ';
                    errMsg += '<Endpoint Name>.<Function name>.  For <Endpoint Name>, ';
                    errMsg += 'you entered "' + endpointName + '".  You should have entered ';
                    errMsg += 'either "' + endpoint1Name + '" or "' + endpoint2Name;
                    errMsg += '" to agree with your endpoint declarations.\n';

                    astErrorNodes = [self,endpoint1Ast,endpoint2Ast];
                    astLineNos = [currentLineNo, endpoint1LineNo, endpoint2LineNo];
                    errorFunction(errMsg,astErrorNodes,astLineNos,progText);        
                    continue;

                #check for alternating between endpoints
                if (lastEndpoint != None):
                    if (lastEndpoint == endpointName):
                        #means that we had a repeat between the endpoints
                        errMsg = '\nError in trace declaration for item ';
                        errMsg += '"' + endpointName + '.' + funcName  +  '".  ';
                        errMsg += 'Messages in a trace should alternate which side ';
                        errMsg += 'receives them.  Instead of having "' + endpointName + '" ';
                        errMsg += 'receive two messages in a row, you should have "';
                        if (endpointName == endpoint1Name):
                            errMsg += endpoint2Name;
                        else:
                            errMsg += endpoint1Name;
                            
                        errMsg += '" receive a message in between.\n';
                        errorFunction(errMsg,[self],[currentLineNo],progText);        

                lastEndpoint = endpointName;


        elif (self.label == AST_SEND_STATEMENT):

            sendMsgNode = self.children[0];
            sendMsgNode.typeCheck(progText,typeStack);

            if (sendMsgNode.type != TYPE_OUTGOING_MESSAGE):
                errMsg = '\nError in send statement.  You can only ';
                errMsg += 'send an outgoing message.  You are trying ';
                errMsg += 'to send something with type ' + sendMsgNode.type;
                errMsg += '.\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);        

            self.type = TYPE_NOTHING;
                
        elif (self.label == AST_MESSAGE_LITERAL):
            # because a message literal can be either an incoming or
            # outgoing message, do not perform type check against
            # declared incoming/outgoing types.  We must wait until
            # assignment to perform these checks.

            # ensure that all the values in the literal do not have
            # type errors (eg, adding a bool to a string) and that
            # they are labeled with types.
            for literalLine in self.children:
                literalValueNode = literalLine.children[1];
                literalValueNode.typeCheck(progText,typeStack);
            
            self.type = TYPE_MESSAGE_LITERAL;

        elif (self.label == AST_PRINT):
            #check to ensure that it's passed a string
            argument = self.children[0];
            argument.typeCheck(progText,typeStack);
            if ((argument.type != TYPE_STRING) and (argument.type != TYPE_NUMBER) and
                (argument.type != TYPE_BOOL)):
                errorString = 'Print requires a Text, TrueFalse, or a Number ';
                errorString += 'to be passed in.  ';
                errorString += 'It seems that you passed in a ';
                errorString += argument.type + '.';
                errorFunction(errorString,[self],[self.lineNo],progText);

            self.type = TYPE_NOTHING;

        elif(self.label == AST_TOTEXT_FUNCTION):
            # check to ensure that it's passed a Text, TrueFalse, or a
            # Number.  If it is passed anything else, indicate that
            # can't handle it.
            argumentNode = self.children[0];
            argumentNode.typeCheck(progText,typeStack);
            if ((argumentNode.type != TYPE_STRING) and (argumentNode.type != TYPE_NUMBER) and
                (argumentNode.type != TYPE_BOOL)):
                errorString = 'ToText requires a Text, TrueFalse, or a Number ';
                errorString += 'to be passed in.  It seems that you passed in a ';
                errorString += argumentNode.type + '.';
                errorFunction(errorString,[self],[self.lineNo],progText);

            self.type = TYPE_STRING;

            
        elif(self.label == AST_SHARED_SECTION):
            #each child will be an annotated declaration.
            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif(self.label == AST_ANNOTATED_DECLARATION):
            # the type of this identifier
            #reset my type to it.
            self.type = self.children[1].value;
            currentLineNo = self.children[1].lineNo;
            if (len(self.children) == 4):
                #have an initializer too.
                self.children[3].typeCheck(progText,typeStack);
                assignType = self.children[3].type;
                if (assignType != self.type):
                    if (assignType == None):
                        assignType = '<None>';
                    errorString = 'Assigned type [' + assignType + '] does not ';
                    errorString += 'match declared type [' + self.type + '].';
                    errorFunction(errorString,[self],[currentLineNo],progText);

            #actually store the new type
            identifierName = self.children[2].value;
            existsAlready = typeStack.getIdentifierElement(identifierName);
            if (existsAlready != None):
                errorFunction('Already have an identifier named ' + identifierName,
                              [self],[currentLineNo, existsAlready.lineNo],progText);
            else:
                controlledByNode = self.children[0];
                idType = typeStack.getFuncIdentifierType(identifierName);
                if (idType):
                    errText = 'Already have a function named ' + identifierName;
                    errText += '.  Therefore, cannot name an identifier with this name.';
                    errorFunction(errText,
                                  [self,existsAlready.astNode],
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
                                  [self],
                                  [currentLineNo],
                                  progText);


                # actually add the shared variable.
                typeStack.addIdentifier(identifierName,
                                        self.type,
                                        controlledByStr,self,currentLineNo);

                
        elif(self.label == AST_NUMBER):
            self.type = TYPE_NUMBER;
        elif(self.label == AST_STRING):
            self.type = TYPE_STRING;
        elif(self.label == AST_BOOL):
            self.type = TYPE_BOOL;

        elif(self.label == AST_FUNCTION_CALL):
            funcName = self.children[0].value;
            self.lineNo = self.children[0].lineNo;
            
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
                    errorFunction(errMsg,[self],[self.lineNo],progText);            


            if (funcMatchObj.element.astNode.label == AST_ONCREATE_FUNCTION):
                errMsg = '\nError trying to call OnCreate function.  ';
                errMsg += 'You are not allowed to call OnCreate yourself.  ';
                errMsg += 'The Waldo system itself will call the function ';
                errMsg += 'when creating your endpoint.\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);            

            
            #set my type as that returned by the function
            self.type = funcMatchObj.getReturnType();

            #check the argument types passed into the function
            funcArgList = self.children[1].children;
            allArgTypes = [];
            for s in funcArgList:
                s.typeCheck(progText,typeStack);
                allArgTypes.append(s.type);


            argError = funcMatchObj.argMatchError(allArgTypes,self);
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

                    

        elif (self.label == AST_TYPE):

            if self.value == TYPE_FUNCTION:
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
                typeSignature = buildFuncTypeSignature(self,progText,typeStack);
                self.type = json.dumps(typeSignature);
                self.value = self.type;

            elif self.value == TYPE_LIST:
                # more complicated types for lists
                # create a dictionary for the list type
                # List (Element: Number)
                # becomes
                # { Type: 'List',
                #   Element: { Type: "Number" }}
                #
                typeSignature = buildListTypeSignature(self,progText,typeStack);
                self.type = json.dumps(typeSignature);
                self.value = self.type;

            else:
                # just assign the type directly since it is one of the
                # basic types Text, TrueFalse, or Number.
                self.type = self.value;

                                

        elif (self.label == AST_LIST):


            elementNodes = self.children[0];
            self.type = EMPTY_LIST_SENTINEL;
            allTypes = [];
            
            # get all types from element nodes
            for element in elementNodes.children:
                element.typeCheck(progText,typeStack);
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
                
                self.type = moreSpecificListType(self.type,potentialType);
                
                for subTypeCheckingIndex in range(typeCheckingIndex,len(allTypes)):

                    firstType = allTypes[typeCheckingIndex];
                    secondType = allTypes[subTypeCheckingIndex];
                    
                    if checkTypeMismatch(element,firstType,secondType,typeStack,progText):
                        errMsg = '\nError in list statement.  Different elements in the ';
                        errMsg += 'list have different types.  The ' + str(typeCheckingIndex+1);
                        errMsg += 'th element in the list has type [' + firstType + '].  The ';
                        errMsg += str(subTypeCheckingIndex + 1) + 'th has type [' + secondType + '].\n';
                        errorFunction(errMsg,[self], [self.lineNo], progText);

                        
                    
        elif (self.label == AST_CONDITION_STATEMENT):
            #type check all children.  (type checks if, elseif, and
            #else statements).
            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif ((self.label == AST_IF_STATEMENT) or
              (self.label == AST_ELSE_IF_STATEMENT)):
            boolCond = self.children[0];
            condBody = self.children[1];

            boolCond.typeCheck(progText,typeStack);
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
                condBody.typeCheck(progText,typeStack);


        elif(self.label == AST_BOOL_EQUALS) or (self.label == AST_BOOL_NOT_EQUALS):
            lhs = self.children[0];
            rhs = self.children[1];
            lhs.typeCheck(progText,typeStack);
            rhs.typeCheck(progText,typeStack);
            self.type = TYPE_BOOL;
            self.lineNo = lhs.lineNo;
            if (lhs.type == None):
                errMsg = '\nError when checking equality. ';
                errMsg += 'Cannot infer type of left-hand side of expression.\n';
                errorFunction(errMsg, [self],[self.lineNo],progText);
                return;
            if (rhs.type == None):
                errMsg = '\nError when checking equality. ';
                errMsg += 'Cannot infer type of right-hand side of expression.\n';
                errorFunction(errMsg, [self],[self.lineNo],progText);
                return;

            if (rhs.type != lhs.type):
                errMsg = '\nError when checking equality.  Both left-hand side ';
                errMsg += 'of expression and right-hand side of expression should ';
                errMsg += 'have same type.  Instead, left-hand side has type ';
                errMsg += lhs.type + ', and right-hand side has type ' + rhs.type;
                errMsg += '\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);

                
        elif ((self.label == AST_AND) or (self.label == AST_OR)):
            
            #keep track of separate expression types to simplify
            #error-reporting.
            expressionType = 'And';
            if (self.label == AST_OR):
                expressionType = 'Or';
            
            lhs = self.children[0];
            rhs = self.children[1];
            lhs.typeCheck(progText,typeStack);
            rhs.typeCheck(progText,typeStack);
            self.type = TYPE_BOOL;
            self.lineNo = lhs.lineNo;
            if (lhs.type == None):
                errMsg = '\nError when checking ' + expressionType + '. ';
                errMsg += 'Cannot infer type of left-hand side of expression.\n';
                errorFunction(errMsg, [self],[self.lineNo],progText);
                return;
            if (rhs.type == None):
                errMsg = '\nError when checking ' + expressionType + '. ';
                errMsg += 'Cannot infer type of right-hand side of expression.\n';
                errorFunction(errMsg, [self],[self.lineNo],progText);
                return;

            if (rhs.type != TYPE_BOOL):
                errMsg = '\nError whe checking ' + expressionType + '. ';
                errMsg += 'Right-hand side expression must be ' + TYPE_BOOL;
                errMsg += '.  Instead, has type ' + rhs.type + '\n';
                errorFunction(errMsg, [self],[self.lineNo],progText);

            if (lhs.type != TYPE_BOOL):
                errMsg = '\nError whe checking ' + expressionType + '. ';
                errMsg += 'Left-hand side expression must be ' + TYPE_BOOL;
                errMsg += '.  Instead, has type ' + lhs.type + '\n';
                errorFunction(errMsg, [self],[self.lineNo],progText);

        elif (self.label == AST_ELSE_STATEMENT):
            #type check else statement
            for s in self.children:
                if (s.label != AST_EMPTY):
                    s.typeCheck(progText,typeStack);

        elif(self.label == AST_PLUS):
            #perform plus separately from other math operations to
            #allow plus overload for concatenating strings.
            lhs = self.children[0];
            rhs = self.children[1];
            self.lineNo = lhs.lineNo;
            
            lhs.typeCheck(progText,typeStack);
            rhs.typeCheck(progText,typeStack);

            errSoFar = False;
            if ((lhs.type != TYPE_NUMBER) and (lhs.type != TYPE_STRING)):
                errMsg = '\nError with PLUS expression.  ';
                errMsg += 'Left-hand side should be a Number or a String.  Instead, ';
                if (lhs.type == None):
                    errMsg += 'could not infer type.\n';
                else:
                    errMsg += 'inferred type ' + lhs.type + '.\n';
                    
                errorFunction(errMsg, [self],[self.lineNo],progText);
                errSoFar = True;

            if ((rhs.type != TYPE_NUMBER) and (rhs.type != TYPE_STRING)):
                errMsg = '\nError with PLUS expression.  ';
                errMsg += 'Right-hand side should be a Number or a String.  Instead, ';
                if (lhs.type == None):
                    errMsg += 'could not infer type.\n';
                else:
                    errMsg += 'inferred type ' + rhs.type + '.\n';
                    
                errorFunction(errMsg, [self],[self.lineNo],progText);
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
                errorFunction(errMsg, [self],[self.lineNo],progText);

            self.type = rhs.type;

                
        elif ((self.label == AST_MINUS) or (self.label == AST_MULTIPLY) or
              (self.label == AST_DIVIDE) or (self.label == AST_GREATER_THAN) or
              (self.label == AST_GREATER_THAN_EQ) or (self.label == AST_LESS_THAN) or
              (self.label == AST_LESS_THAN_EQ)):
            #check type checking of plus, minus, times, divide;
            #left and right hand side should be numbers, returns a number.
            
            #for error reporting
            expressionType  = 'MINUS';
            self.type = TYPE_NUMBER;                
            if (self.label == AST_MULTIPLY):
                expressionType = 'MULTIPLY';
            elif(self.label == AST_DIVIDE):
                expressionType = 'DIVIDE';
            elif(self.label == AST_GREATER_THAN):
                expressionType = 'GREATER THAN';
                self.type = TYPE_BOOL;                
            elif(self.label == AST_GREATER_THAN_EQ):
                expressionType = 'GREATER THAN EQUAL';                
                self.type = TYPE_BOOL;                
            elif(self.label == AST_LESS_THAN):
                expressionType = 'LESS THAN';
                self.type = TYPE_BOOL;                
            elif(self.label == AST_LESS_THAN_EQ):
                expressionType = 'LESS THAN EQUAL';
                self.type = TYPE_BOOL;                

                
            lhs = self.children[0];
            rhs = self.children[1];
            self.lineNo = lhs.lineNo;
            
            lhs.typeCheck(progText,typeStack);
            rhs.typeCheck(progText,typeStack);


            
            if (lhs.type != TYPE_NUMBER):
                errMsg = '\nError with ' + expressionType + ' expression.  ';
                errMsg += 'Left-hand side should be a Number.  Instead, ';
                if (lhs.type == None):
                    errMsg += 'could not infer type.\n';
                else:
                    errMsg += 'inferred type ' + lhs.type + '.\n';
                    
                errorFunction(errMsg, [self],[self.lineNo],progText);
                    
            if (rhs.type != TYPE_NUMBER):
                errMsg = '\nError with ' + expressionType + ' expression.  ';
                errMsg += 'Right-hand side should be a Number.  Instead, ';
                if (lhs.type == None):
                    errMsg += 'could not infer type.\n';
                else:
                    errMsg += 'inferred type ' + rhs.type + '.\n';
                    
                errorFunction(errMsg, [self],[self.lineNo],progText);
                
                
        elif(self.label == AST_BOOLEAN_CONDITION):
            self.lineNo = self.children[0].lineNo;
            self.children[0].typeCheck(progText,typeStack);
            
            if (self.children[0].type != TYPE_BOOL):
                errMsg = '\nError in predicate of condition statement.  Should have ';
                errMsg += 'TrueFalse type.  Instead, ';
                if (self.children[0].type != None):
                    errMsg += 'has type ' + self.children[0].type;
                else:
                    errMsg += 'cannot infer type';
                errMsg += '.\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);
            else:
                self.type = self.children[0].type;

        elif(self.label == AST_ELSE_IF_STATEMENTS):
            for s in self.children:
                s.typeCheck(progText,typeStack);
                
        elif(self.label == AST_ENDPOINT):
            #check if endpoint name matches previous endpoint name
            endName = self.children[0].value;

            #tell typestack that we are currently in this endpoint
            #body section.  unset it at end of elif.
            typeStack.setCurrentEndpointName(endName);
            
            currentLineNo = self.children[0].lineNo;
            if (not typeStack.isEndpoint(endName)):
                errMsg = 'Endpoint named ' + endName + ' was not defined at top of file ';
                errMsg = ' are you sure your endpoints match?';
                errLineNos = [currentLineNo,typeStack.endpoint1LineNo,typeStack.endpoint2LineNo];
                errorFunction(errMsg,[self],errLineNos,progText);

            #check endpoint body section
            if (len(self.children) >= 2):
                self.children[1].typeCheck(progText,typeStack);

            #matches above set call.
            typeStack.unsetCurrentEndpointName();
            

        elif(self.label == AST_ENDPOINT_BODY_SECTION):            
            
            #typecheck global section
            self.children[0].typeCheck(progText,typeStack);
            #check function section.
            self.children[1].typeCheck(progText,typeStack);

            #note: perform extra pop for stack that endpoint global
            #section put on.
            typeStack.popContext();

        elif(self.label == AST_ENDPOINT_GLOBAL_SECTION):

            for s in self.children:
                s.typeCheck(progText,typeStack);

            
        elif(self.label == AST_DECLARATION):

            # type check the declared type statement (necessary
            # because of function statements).
            self.children[0].typeCheck(progText,typeStack);

            declaredType = self.children[0].value;
            self.lineNo = self.children[0].lineNo;
            
            if (self.children[1].label != AST_IDENTIFIER):
                errMsg = '\nError at declaration statement. ';
                errMsg += 'Must have an identifier for left hand ';
                errMsg += 'side of declaration.\n';
                errorFunction(errMsg,[self],[currentLineNo],progText);
                return;
            
            name = self.children[1].value;
            currentLineNo = self.children[0].lineNo;
            if (len(self.children) == 3):
                rhs = self.children[2];
                rhs.typeCheck(progText,typeStack);
                rhsType = rhs.type;

                if (checkTypeMismatch(rhs,declaredType,rhsType,typeStack,progText)):
                    errMsg = 'Type mismatch for variable named "' + name + '".';
                    errMsg += '  Declared with type [' + declaredType + '], but ';
                    errMsg += 'assigned to type [' + rhsType + '].';
                    errorFunction(errMsg,[self],[currentLineNo],progText);
                    
            else:
                # not initialization information.  There are several
                # types that require initialization information.  Most
                # importantly, user-defined functions do.  Throw an
                # error if user-defined function does not.
                if (isFunctionType(declaredType)):
                    errMsg = 'Error when declaring a user-defined function ';
                    errMsg += 'named "' + name + '".  Every user-defined ';
                    errMsg += 'requires that it should be initialized.  ';
                    errMsg += 'That means that you have to set ' + name + ' ';
                    errMsg += 'to a valid function when you declare it.';
                    errorFunction(errMsg,[self],[currentLineNo],progText);
                    
            #check if already have a function or variable with the
            #targetted name.
            prevId = typeStack.getIdentifierElement(name);
            prevFunc = typeStack.getFuncIdentifierType(name);
            if ((prevId != None) or (prevFunc != None)):
                nodes =[self];
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
                    
                    
            typeStack.addIdentifier(name,declaredType,None,self,currentLineNo);
            self.type = declaredType;

        elif(self.label == AST_RETURN_STATEMENT):
            self.children[0].typeCheck(progText,typeStack);
            
            typeCheckError = typeStack.checkReturnStatement(self);
            if (typeCheckError != None):
                errorFunction(typeCheckError.errMsg,typeCheckError.nodes,typeCheckError.lineNos,progText);
            self.type = TYPE_NOTHING;
            
            
        elif(self.label == AST_IDENTIFIER):
            name = self.value;
            typer,ctrldBy = typeStack.getIdentifierType(name);
            if (typer == None):
                # also check if it's an identifier for a non-variable
                # function.
                funcType = typeStack.getFuncIdentifierType(name);
                if (funcType == None):
                    errMsg = 'Cannot infer type of ' + name + '.  Are you sure it is valid?';
                    errorFunction(errMsg,[self],[self.lineNo],progText);
                    self.type = 'Undefined';
                else:
                    self.type = json.dumps(funcType.createJsonType());
            else:
                self.type = typer;

            
        elif(self.label == AST_ENDPOINT_FUNCTION_SECTION):
            # this just type checks the headers of each function.
            # Have to insert the header of each function
            for s in self.children:
                s.functionDeclarationTypeCheck(progText,typeStack);

            # now we type check the bodies of each function
            for s in self.children:
                s.typeCheck(progText,typeStack);


        elif ((self.label == AST_PUBLIC_FUNCTION) or
              (self.label == AST_PRIVATE_FUNCTION) or
              (self.label == AST_MSG_SEND_FUNCTION) or
              (self.label == AST_MSG_RECEIVE_FUNCTION) or
              (self.label == AST_ONCREATE_FUNCTION)):
            '''
            begins type check for body of the function, this code
            pushes arguments into context and then calls recursive
            type check on function body itself.
            '''

            ## create a new type context to insert intermediate data
            ## in.  context is popped at the end of the elif statement.
            typeStack.pushContext();
            funcName = self.children[0].value;            

            stackFunc = typeStack.getFuncIdentifierType(funcName);
            
            #set my line number to be the line number of when the
            #function type was declared.
            self.lineNo = self.children[0].lineNo;
            
            if (stackFunc == None):
                errMsg = 'Behram error: should have inserted function ';
                errMsg += 'with name "' + funcName + '" into type stack ';
                errMsg += 'before type checking function body.'
                errPrint('\n\n');
                errPrint(errMsg);
                errPrint('\n\n');
                assert(False);

            #when we are checking function body, any return statement
            #that we hit should return something of the type specfied
            #by the return type here.
            typeStack.setShouldReturn(stackFunc.getReturnType());


            #insert passed in arguments into context;
            
            if ((self.label == AST_PUBLIC_FUNCTION) or (self.label == AST_PRIVATE_FUNCTION)):
                funcDeclArgListIndex = 2;
                funcBodyIndex = 3;
            elif (self.label == AST_MSG_SEND_FUNCTION):
                funcDeclArgListIndex = 1;
                funcBodyIndex = 2;
            elif(self.label == AST_MSG_RECEIVE_FUNCTION):
                # 1 should contain name of the IncomingMessage;
                funcBodyIndex = 4;
                funcDeclArgListIndex = None;
            elif(self.label == AST_ONCREATE_FUNCTION):
                funcBodyIndex = 2;
                funcDeclArgListIndex = 1;
            else:
                errMsg = '\nBehram error: invalid function ';
                errMsg += 'type when type checking functions\n';
                errPrint(errMsg);
                

            if (funcDeclArgListIndex != None):
                #add all arguments passed in in function declaration to
                #current context.
                self.children[funcDeclArgListIndex].typeCheck(progText,typeStack);

            if (self.label == AST_MSG_RECEIVE_FUNCTION):
                # we are in the message receive function, and must
                # add the input argument name to current context
                incomingMessageNameNode = self.children[1];
                argName = incomingMessageNameNode.value;
                
                collisionObj = typeStack.checkCollision(argName,self);
                
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
                    typeStack.addIdentifier(argName,TYPE_INCOMING_MESSAGE,None,self,self.lineNo);

                # re-define type for IncomingMessage
                incomingTypeNode = self.children[2];
                typeStack.addIncoming(incomingTypeNode);
                
                # re-define type for OutgoingMessage
                outgoingTypeNode = self.children[3];
                typeStack.addOutgoing(outgoingTypeNode);
                
            elif(self.label == AST_MSG_SEND_FUNCTION):
                # re-define type for OutgoingMessage
                outgoingTypeNode = self.children[3];
                typeStack.addOutgoing(outgoingTypeNode);
            else:
                # both public and internal functions place their
                # return types in the second child slot.
                typeStack.addCurrentPublicInternalNode(self);

                
                
            # type check the actual function body
            self.children[funcBodyIndex].typeCheck(progText,typeStack);
            
            ## remove the created type context
            typeStack.popContext();


        elif(self.label == AST_FUNCTION_BODY):
            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif (self.label == AST_FUNCTION_DECL_ARGLIST):
            #iterate through each individual declared argument
            for s in self.children:
                s.typeCheck(progText,typeStack);


        elif (self.label == AST_FUNCTION_DECL_ARG):
            '''
            for declared argument, checks for its collision
            with existing variables and functions, and then inserts
            it into a typestack context.
            '''
            self.lineNo = self.children[0].lineNo;
            argType = self.children[0].value;
            argName = self.children[1].value;

            collisionObj = typeStack.checkCollision(argName,self);

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
                typeStack.addIdentifier(argName,argType,None,self,self.lineNo);


        elif (self.label == AST_FUNCTION_BODY_STATEMENT):
            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif (self.label == AST_STRING):
            self.type = TYPE_STRING;
        elif (self.label == AST_NUMBER):
            self.type = TYPE_NUMBER;
        elif (self.label == AST_BOOL):
            self.type = TYPE_BOOL;

            
        elif (self.label == AST_ASSIGNMENT_STATEMENT):

            lhs = self.children[0];
            self.lineNo = lhs.lineNo;
            
            if (lhs.label != AST_IDENTIFIER) and (lhs.label != AST_BRACKET_STATEMENT):
                errMsg = '\nError in assignment statement.  Can only assign ';
                errMsg += 'to a variable.  (Left hand side must be a variable)\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);
                return;

            
            rhs = self.children[1];

            if (lhs.label == AST_IDENTIFIER):
                lhsType,controlledBy = typeStack.getIdentifierType(lhs.value);
                lhs.type  = lhsType;
            else:
                lhs.typeCheck(progText,typeStack);
                lhsType = lhs.type;
                controlledBy = None;

            if (lhsType == None):
                errMsg = '\nError in assignment statement.  Left hand side ';
                errMsg += 'has no type information.\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);
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
                    errMsg += 'do not write to it in ' + typeStack.getOtherEndpointName();
                    errMsg += '.\n';
                    errorFunction(errMsg,[self],[self.lineNo],progText);
            
            
            rhs.typeCheck(progText,typeStack);
            rhsType = rhs.type;

            if (rhsType == None):
                errMsg = '\nError in assignment statement.  Right hand side ';
                errMsg += 'has no type information.\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);
                return;

            if (checkTypeMismatch(rhs,lhsType,rhsType,typeStack,progText)):
                #FIXME: this should really identify *why* we inferred
                #the type that we did.  Maybe where the variable was
                #decalred too.
                errMsg = '\nError in assignment statement.  Type of ';
                errMsg += 'left-hand side (' + lhsType + ') does not ';
                errMsg += 'match type of right-hand side (' + rhsType;
                errMsg += ').\n';
                errorFunction(errMsg,[self],[self.lineNo],progText);

                
        else:
            errPrint('\nLabels that still need type checking: ');
            errPrint('\t' + self.label);
                

            
            
        #remove the new context that we had created.  Note: shared
        #section is intentionally missing.  Want to maintain that 
        #context while type-checking the endpoint sections.
        #skip global section too.
        if ((self.label == AST_ROOT) or
            (self.label == AST_ENDPOINT_FUNCTION_SECTION)):
            
            typeStack.popContext();



    def functionDeclarationTypeCheck(self, progText,typeStack):
        '''
        Takes a node of type public function, ast function, message
        send function, or message receive function.  Does not set any
        types itself, but rather loads functions into the typeStack
        itself.
        '''
        if ((self.label != AST_PUBLIC_FUNCTION) and
            (self.label != AST_PRIVATE_FUNCTION) and
            (self.label != AST_MSG_SEND_FUNCTION) and
            (self.label != AST_MSG_RECEIVE_FUNCTION) and
            (self.label != AST_ONCREATE_FUNCTION)):
            errPrint('\n\n');
            errPrint(self.label);
            errPrint('\n\n');
            errPrint('\nBehram error, sending an incorrect tag to be loaded into functionDeclarationTypeCheck\n');
            assert(False);

            
        funcName = self.children[0].value;            
        self.lineNo = self.children[0].lineNo;

        if ((self.label == AST_PUBLIC_FUNCTION) or (self.label == AST_PRIVATE_FUNCTION)):
            #get declared return type (only applicable for functions and public functions)
            self.children[1].typeCheck(progText,typeStack);
            returnType = self.children[1].type;
            argDeclIndex = 2;
        elif(self.label == AST_MSG_SEND_FUNCTION):
            #msg send and msg receive functions do not have declared
            #return types (for now).  use the return type for each
            
            returnType = TYPE_MSG_SEND_FUNCTION;
            argDeclIndex = 1;
        elif(self.label == AST_MSG_RECEIVE_FUNCTION):
            #msg send and msg receive functions do not have declared
            #return types (for now).  use the return type for each
            
            returnType = TYPE_MSG_RECEIVE_FUNCTION;
            argDeclIndex = None;

        elif(self.label == AST_ONCREATE_FUNCTION):
            returnType = TYPE_NOTHING;
            argDeclIndex = 1;


        #get types of function arguments
            
        #add a context to type stack for arg declarations and pop it
        #later so that arg decl arguments do not persist after the
        #type check of arg text.
        typeStack.pushContext();
        if (argDeclIndex != None):
            self.children[argDeclIndex].typeCheck(progText,typeStack);
        typeStack.popContext();
        
        argTypeList = [];
        if (argDeclIndex != None):
            args = self.children[argDeclIndex].children;

            for t in args:
                #each t should now be of type FUNCTION_DECL_ARG
                
                if (len(t.children) == 0):
                    #means that we have a function that takes no arguments.
                    continue;
            
                #set the type of t to the type identifier of the argument.
                t.children[0].typeCheck(progText,typeStack);
                
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


            
        collisionObj = typeStack.checkCollision(funcName,self);
        if (collisionObj != None):
            #FIXME: for this error message, may want to
            #re-phrase with something about scope, so do not
            #take the wrong error message away.
            errMsg = 'Error trying to name a function "' + funcName;
            errMsg += '".  Already have a function or variable with ';
            errMsg += 'the same name.'

            errorFunction(errMsg,collisionObj.nodes,collisionObj.lineNos,progText);
        else:
            traceError = typeStack.addFuncIdentifier(funcName,returnType,argTypeList,self,self.lineNo);
            if (traceError != None):
                errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);

        

            
    def toJSON(self,indentLevel=0,drawHigh=False):
        '''
        JSON format:
        {
            "name": "<self.label>",
            "type": "<self.type>",
            "value": <self.value>,
            "drawHigh": drawHigh
            "children": [
                   //recurse
              ]
        }
        '''
        #name print
        returner = indentText('{\n',indentLevel);
        returner += indentText('"name": "',indentLevel+1);
        returner += self.label;
        returner += '"';


        if (self.value != None):
            returner += ',\n';
            returner += indentText('"value": "',indentLevel+1);
            returner += self.value;
            returner += '"'

        
        if (self.type != None):
            returner += ',\n';
            returner += indentText('"type": "',indentLevel+1);
            returner += self.type;
            returner += '"'


        #print drawHigh
        returner += ',\n';
        returner += indentText('"drawHigh": ',indentLevel+1);
        if (drawHigh):
            returner += 'true';
        else:
            returner += 'false';
            
            
        #child print
        if (len(self.children) != 0):
            returner += ',\n';
            returner += indentText('"children": [\n',indentLevel+1);

            for s in range(0,len(self.children)):
                drawHigh = not drawHigh;
                returner += self.children[s].toJSON(indentLevel+1,drawHigh);
                if (s != (len(self.children) -1 )):
                    returner += ',\n';
            returner += ']';

        #close object
        returner += '\n' + indentText('}',indentLevel);
        return returner;

    
    def drawPretty(self,filename,pathToD3='d3',width=5000,height=3000):
        '''
        For now, an ugly way of generating a pretty view 
        '''

        #default args did not work how I anticipated.
        if (pathToD3 == None):
            pathToD3 = 'd3';
        if(width == None):
            width = 5000;
        if(height==None):
            height = 3000;
            
        treeDraw.prettyDrawTree(filename=filename,data=self.toJSON(),pathToD3=pathToD3,width=width,height=height);



        
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

        if (rhsType==TYPE_MESSAGE_LITERAL):

            if (lhsType == TYPE_OUTGOING_MESSAGE):
                # check that the message literal has all the
                # expected fields of the outgoing message
                typeCheckError = typeStack.literalAgreesWithOutgoingMessage(rhs);
                errorTrue = False;
                if (typeCheckError != None):
                    errorTrue = True;
                    errorFunction(typeCheckError.errMsg,typeCheckError.nodes,typeCheckError.lineNos,progText);

            elif(lhsType == TYPE_INCOMING_MESSAGE):
                typeCheckError = typeStack.literalAgreesWithIncomingMessage(rhs);
                errorTrue = False;
                if (typeCheckError != None):
                    errorTrue = True;
                    errorFunction(typeCheckError.errMsg,typeCheckError.nodes,typeCheckError.lineNos,progText);


        else:
            # Must use special checks to type check lists.  For
            # instance, if one side presents empty_list and other is
            # [Number], should not produce typecheck error.

            # determine if lists are involved
            if (isListType(lhsType) and isListType(rhsType)):
                errorTrue = listTypeMismatch(lhsType,rhsType);
            else:
                # both sides were not lists and there types did not
                # match.  will throw an error.
                errorTrue = True;
             
    return errorTrue;


def listTypeMismatch(listTypeA, listTypeB):
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

    elementTypeA = dictA['ElementType'];
    elementTypeB = dictB['ElementType'];


    elTypeA = elementTypeA;
    if (not isinstance(elementTypeA,basestring)):
        elTypeA = json.dumps(elementTypeA);

    elTypeB = elementTypeB;
    if (not isinstance(elementTypeB,basestring)):
        elTypeB = json.dumps(elementTypeB);
        
    
    if (not isListType(elTypeA)) or (not isListType(elTypeB)):
        # handles all cases where one or both are not lists
        return (elTypeA != elTypeB);

    # both elements are list types.  know that we can quit if one or other is a sentinel.
    if (elTypeA == EMPTY_LIST_SENTINEL) or (elTypeB == EMPTY_LIST_SENTINEL):
        return False;
    
    # turn them back into strings and recurse
    stringElA = json.dumps(elementTypeA);
    stringElB = json.dumps(elementTypeB);
    return listTypeMismatch(stringElA,stringElB);



ERROR_NUM_LINES_EITHER_SIDE = 4;

def setErrorEncountered():
    global TYPE_ERROR_ENCOUNTERED;
    TYPE_ERROR_ENCOUNTERED = True;

def getErrorEncountered():
    global TYPE_ERROR_ENCOUNTERED;
    return TYPE_ERROR_ENCOUNTERED;

def resetErrorEncountered():
    global TYPE_ERROR_ENCOUNTERED;
    TYPE_ERROR_ENCOUNTERED = False;



def errorFunction(errorString,astNodes,lineNumbers,progText):
    setErrorEncountered();
    '''
    @param {String} errorString -- Text associated with error.
    @param {Array < AstNode>} astNodes -- Contains all ast nodes associated with the error.
    @param {Array < Int> } lineNumbers -- Contains all line numbers associated with error.
    @param {String} progText -- The source text of the program.
    '''
    
    # errPrint('\n\n');
    errPrint('*************************');
    # errPrint('Error in type checking:');

    # reformat errorString so that doesn't print off side
    errPrint(splitString(errorString,80));

    # errPrint('-------\nAST node labels:');
    # for s in astNodes:
    #     errPrint(s.label)
        
    errPrint('-------\nLine numbers:');
    for s in lineNumbers:
        errPrint(s);


    programTextArray = progText.split('\n');
    errPrint('-------\nProgram text:');
    for errorLine in lineNumbers:
        errPrint('\n\n');
        lowerLineNum = max(0,errorLine - ERROR_NUM_LINES_EITHER_SIDE);
        upperLineNum = min(len(programTextArray),errorLine + ERROR_NUM_LINES_EITHER_SIDE);

        for s in range(lowerLineNum, upperLineNum):
            errorText = '';
            errorText += str(s+1);

            if (s == errorLine -1):
                errorText += '*   ';
            else:
                errorText += '    ';
                    
            errorText += programTextArray[s];
            errPrint(errorText);

        
    errPrint('*************************');
    errPrint('\n\n');

    raise WaldoTypeCheckException('');


def splitString(string,maxLineLen):
    '''
    Inserts newlines into string to ensure that
    no line is longer than maxLineLen

    Warning: Performs poorly for case where words are much longer than maxLineLen
    '''

    strArray = string.split(' ');

    toReturn = '';
    lineCounter = 0;

    for index in range(0,len(strArray)):

        strToAdd = strArray[index] + ' ';

        if (len(strToAdd) + lineCounter > maxLineLen):
            toReturn += '\n';
            lineCounter = 0;

        toReturn += strToAdd;
        lineCounter += len(strToAdd);


    return toReturn;


def buildFuncTypeSignature(node,progText,typeStack):
    '''
    @see createJsonType of FuncMatchObject in
    astTypeCheckStack.py....needs to be consistent between both.
    
    @param {AstNode} node --- Has value of FUNCTION_TYPE and type of
    AST_TYPE.  (Similar to the node that is generated for each type.)
    For instance, when declare

    Function (In: TrueFalse; Returns: Nothing) a;

    The node corresponds to the node generated from

    Function (In: TrueFalse; Returns: Nothing)


    @returns {dictionary}.  For the above example, dictionary would look like this:

    {
       Type: 'Function',
       In: [ { Type: 'TrueFalse'} ],
       Returns: { Type: 'Nothing'}
    }
    '''
    returner = {};
    returner['Type'] = TYPE_FUNCTION;

    
    ##### HANDLE INPUT ARGS #####
    inArgNode = node.children[0];
    inputTypes = [];
    if (inArgNode.label != AST_EMPTY):
        # means that we have a node of type typelist.  each of its
        # children should be an independent type.
        for typeNode in inArgNode.children:
            
            typeNode.typeCheck(progText,typeStack);

            if (isTemplatedType(typeNode.type)):
                inputTypes.append(json.loads(typeNode.type));
            else:
                toAppend = {
                    'Type': typeNode.type
                    };
                inputTypes.append(toAppend);
                
    returner['In'] = inputTypes;

    ##### HANDLE OUTPUT ARGS #####
    outArgNode = node.children[1];
    outArgNode.typeCheck(progText,typeStack);
    if (isTemplatedType(outArgNode.type)):
        returner['Returns'] = json.loads(outArgNode.type);
    else:
        returner['Returns'] = {
            'Type': outArgNode.type
            };

    return returner;


def moreSpecificListType(typeA,typeB,starter = None):
    '''
    @param {String} typeA --- string-ified version of json list type.
    @param {String} typeB --- string-ified version of json list type.

    @returns{String} typeA or typeB, depending on which is more
    specific.

    In particular, if
       typeA = []
       and
       typeB = [Number]
    will return typeB
    Similarly, if
       typeA = [ [] ]
       and
       typeB = [ [TrueFalse] ]
    will return typeB

    If both typeA and typeB are equally specific but conflict, returns
    either.  For example, if 
       typeA = [ Number ]
       and
       typeB = [ TrueFalse ]
    could return either typeA or typeB.
    '''

    if (typeA == EMPTY_LIST_SENTINEL):
        return typeB;

    if (typeB == EMPTY_LIST_SENTINEL):
        return typeA;

    
    dictA = json.loads(typeA);
    dictB = json.loads(typeB);

    # grab the types of elements for each list.
    elementTypeA = dictA['ElementType'];
    elementTypeB = dictB['ElementType'];

    
    if (elementTypeA == EMPTY_LIST_SENTINEL):
        # means that typeB is at least as specific
        return typeB;

    if (elementTypeB == EMPTY_LIST_SENTINEL):
        # means that typeA is at least as specific        
        return typeA;


    elTypeA = elementTypeA;
    if (not isinstance(elementTypeA,basestring)):
        elTypeA = json.dumps(elementTypeA);
        
    elTypeB = elementTypeB;
    if (not isinstance(elementTypeB,basestring)):
        elTypeB = json.dumps(elementTypeB);

        
    if ((not isListType(elTypeA) ) or
        (not isListType(elTypeB) )):
        # if one or both are not lists, that means that we've reached
        # the maximum comparison depth and we cannot get more
        # specific, so just return one or the other.
        return typeA;

    
    # each element itself is a list.  
    recursionResult = moreSpecificListType(
        json.dumps(elementTypeA),json.dumps(elementTypeB), 1);

    # must rebuild surrounding list type signature to match typeA or
    # typeB.
    jsonToReturn = buildListTypeSignatureFromTypeName(recursionResult);
    return json.dumps(jsonToReturn);
    


def buildListTypeSignatureFromTypeName(typeName):
    
    if (isTemplatedType(typeName)):
        if (typeName != EMPTY_LIST_SENTINEL):
            typeName = json.loads(typeName);

    return {
        'Type': TYPE_LIST,
        'ElementType': typeName
        };

def buildListTypeSignature(node, progText,typeStack):
    elementTypeNode = node.children[0];
    elementTypeNode.typeCheck(progText,typeStack);

    elementType = elementTypeNode.type;
    if isTemplatedType(elementTypeNode.type):
        elementType = json.loads(elementType);

    return buildListTypeSignatureFromTypeName(elementType);


class WaldoTypeCheckException(Exception):

   def __init__(self, errMsg):
       self.value = errMsg;

   def __str__(self):
       return repr(self.value)
    
    
