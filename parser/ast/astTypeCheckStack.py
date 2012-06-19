#!/usr/bin/python

from astLabels import TYPE_BOOL;
from astLabels import TYPE_STRING;
from astLabels import TYPE_NUMBER;
from astLabels import TYPE_NOTHING;
from astLabels import TYPE_FUNCTION;
from astLabels import TYPE_INCOMING_MESSAGE;
from astLabels import TYPE_OUTGOING_MESSAGE;
from astLabels import TYPE_MSG_SEND_FUNCTION;
from astLabels import TYPE_MSG_RECEIVE_FUNCTION;
from astLabels import AST_TYPED_SENDS_STATEMENT;
from astLabels import AST_RETURN_STATEMENT;
from astLabels import AST_PUBLIC_FUNCTION;
from astLabels import AST_PRIVATE_FUNCTION;
from astLabels import AST_ONCREATE_FUNCTION;
from traceLine import TraceLineManager;
from traceLine import TypeCheckError;
from parserUtil import errPrint;
from parserUtil import isFunctionType;
import json;

FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH = 0;
FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH = 1;


# used as return values for fieldAgreesWithIncomingMessage and
# fieldAgreesWithOutgoingMessage.  TYPE_MISMATCH means that user is
# accessing a field and expecting an incorrect type.
# NAME_DOES_NOT_EXIST means that user is accessing a field that is not
# declared in this message.  SUCCEED means that the field and type
# agreed in the incoming/outgoing message with the name and type
# submitted.
MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH = 0;
MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST = 1;
MESSAGE_TYPE_CHECK_SUCCEED = 2;




class TypeCheckContextStack():
    def __init__ (self):
        self.stack     = []; #last element in array is always top of stack.
        self.funcStack = [];
        
        #also contains additional data
        self.protObjName = None;
        self.endpoint1 = None;
        self.endpoint2 = None;
        self.endpoint1LineNo = None;
        self.endpoint2LineNo = None;
        self.endpoint1Ast = None;
        self.endpoint2Ast = None;

        #handles keeping track of msgSend and msgReceive functions
        #(both their specification in the trace section as well as
        #their definitions in endpoint sections.
        self.traceManager = TraceLineManager(self);

        #this keeps track of which endpoint body section we're type
        #checking through.  It's None if we are not currently type
        #checking an endpoint's body section.  It's a string
        #otherwise.  Used for type checking with trace lines (in 
        #self.traceManager).
        self.currentEndpointName = None;

        self.currentOutgoing = None;
        self.currentIncoming = None;

        # used to type check return statements to ensure that a
        # function actually returns the type that it says it will.
        self.currentPublicInternalNode = None;

    def getOtherEndpointName(self):
        if (self.currentEndpointName == None) or (self.endpoint1 == None) or (self.endpoint2 == None):
            errMsg = '\nBehram error: should not call getOtherEndpointName in ';
            errMsg += 'astTypeCheckStack.py unless we are currently in an endpoint ';
            errMsg += 'and all endpoints are defined.\n';
            errPrint(errMsg);
            assert(False);

        if (self.currentEndpointName != self.endpoint1):
            return self.endpoint1;
        return self.endpoint2;

        
    def addCurrentPublicInternalNode(self,node):
        if ((node.label != AST_PUBLIC_FUNCTION) and (node.label != AST_PRIVATE_FUNCTION) and
            (node.label != AST_ONCREATE_FUNCTION)):
            errMsg = '\nBehram error: adding internal or public node with incorrect ';
            errMsg += 'type.\n';
            errPrint(errMsg);
            assert(False);

        self.currentPublicInternalNode = node;

    def checkReturnStatement(self,returnNode):
        if (returnNode.label != AST_RETURN_STATEMENT):
            errMsg = '\nBehram error: trying to check a ';
            errMsg += 'return statement without a return statement node.\n';
            errPrint(errMsg);
            assert(False);


        if (self.currentPublicInternalNode == None):
            errMsg = '\nReturn error.  You are only allowed to put Return ';
            errMsg += 'statements in the body of a Public or Internal ';
            errMsg += 'function.\n';
            return TypeCheckError([returnNode],errMsg);


        returnsTypeNode = self.currentPublicInternalNode.children[1];
        declaredType = returnsTypeNode.value;
        returnStatementType = returnNode.children[0].type;


        if (declaredType != returnStatementType):
            funcName = self.currentPublicInternalNode.children[0].value;
            errMsg = '\nReturn error.  You have declared that the function ';
            errMsg += 'named "' + funcName + '" ';
            errMsg += 'should return type "' + declaredType + '", ';
            errMsg += 'but your Return statement actually returns type "';
            errMsg += returnStatementType + '".\n';
            nodes= [returnsTypeNode,returnNode];
            return TypeCheckError(nodes,errMsg);

        return None;
        
        
    def addOutgoing(self,node):
        '''
        @param {astNode} of type TypedSendsStatement

        Used whenever accessing a member from an OutgoingMessage to
        ensure that it has the field (and the type of the field is
        correct).
        '''
        if (node.label != AST_TYPED_SENDS_STATEMENT):
            errMsg = '\nBehram error: adding incoming node with incorrect ';
            errMsg += 'type.\n';
            errPrint(errMsg);
            assert(False);
            
        self.currentOutgoing = node;
        
    def addIncoming(self,node):
        '''
        @param {astNode} of type TypedSendsStatement

        Used whenever accessing a member from an IncomingMessage to
        ensure that it has the field (and the type of the field is
        correct).
        '''
        if (node.label != AST_TYPED_SENDS_STATEMENT):
            errMsg = '\nBehram error: adding incoming node with incorrect ';
            errMsg += 'type.\n';
            errPrint(errMsg);
            assert(False);
        
        self.currentIncoming = node;

    def checkTraceItemInputOutput(self):
        '''
        run through all trace lines to see if the message outputs
        match the message inputs.

        @return {None or TypeCheckError} -- None if inputs and outputs
        agree.  TypeCheckError if they do not.
        '''
        return self.traceManager.checkTraceItemInputOutput();

        
    def literalAgreesWithOutgoingMessage(self,literal):
        return self._literalAgreesWithMessage(self.currentOutgoing,literal,'outgoing');
    
    def literalAgreesWithIncomingMessage(self,literal):
        return self._literalAgreesWithMessage(self.currentIncoming,literal,'incoming');



    def _literalAgreesWithMessage(self,declaredTypedSendsNode,literal,toCompareToName):
        '''
        @param{AstNode} declaredTypedSendsNode -- ast node with label
        == AST_TYPED_SENDS_NODE

        @param{AstNode} literal -- ast node with label ==
        AST_MESSAGE_LITERAL

        @param{String} toCompareToName -- Used for error reporting.
        
        @returns {None or TypeCheckError}.  TypeCheckError object if
        several fields existed in the literal that did not exist in
        the declared type or their types did not match or several
        fields existed in the declared type that did not exist in the
        literal.

        None if no errors.
        '''

        # lkjs;
        if (declaredTypedSendsNode == None):
            errMsg = '\nBehram error: should have an incoming or outgoing node ';
            errMsg += 'if trying to check agreement.\n';
            errPrint(errMsg);
            assert(False);
        
        # first checks that everything that is in
        # declaredTypedSendsNode is in literal and types agree.
        for sendLine in declaredTypedSendsNode.children:
            lineType = sendLine.children[0].value;
            lineName = sendLine.children[1].value;

            found = False;
            # check that these appear in the literal
            for literalLine in literal.children:
                llineType = literalLine.children[1].type;
                llineName = literalLine.children[0].value;
                if (lineName == llineName):

                    if (lineType == llineType):
                        found = True;
                        break;
                    else:
                        errMsg = '\nType mismatch error: Both the message object that ';
                        errMsg += 'you are creating and the ' + toCompareToName + ' message ';
                        errMsg += 'type have a field named "' + llineName + '".  But the ';
                        errMsg += 'message object you are declaring has type "' + llineType + '", ';
                        errMsg += 'whereas it should have type "' + lineType + '" to agree ';
                        errMsg += 'with ' + toCompareToName + ' message type.\n';
                        nodes = [literal,declaredTypedSendsNode];
                        return TypeCheckError(nodes,errMsg);

            if (not found):
                errMsg = '\nMissing field error: When you are creating a new ';
                errMsg += toCompareToName + ' message, it must include all fields ';
                errMsg += 'specified in the ' + toCompareToName + ' declaration.  ';
                errMsg += 'The message that you are trying to ';
                errMsg += 'create should have a field named "' + lineName + '" to ';
                errMsg += 'agree with the ' + toCompareToName + ' message type that ';
                errMsg += 'you declared.\n';
                nodes = [literal,declaredTypedSendsNode];
                return TypeCheckError(nodes,errMsg);
                
                
        # now checks that there aren't any fields in literal that do
        # not appear in declaredTypeSendsNode.
        for literalLine in literal.children:
            llineType = literalLine.children[1].type;
            llineName = literalLine.children[0].value;
            exists,additional = self._fieldAgreesWithMessage(declaredTypedSendsNode,llineName,llineType);
            if (exists == MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST):
                errMsg = '\nAdditional field error: The message that you are trying to ';
                errMsg += 'create has a field named "' + llineName + '" that does not ';
                errMsg += 'exist with the ' + toCompareToName + ' message type that ';
                errMsg += 'you declared.\n';
                nodes = [literal,declaredTypedSendsNode];
                return TypeCheckError(nodes,errMsg);
                

        return None;
                
                    
                
        
    def fieldAgreesWithCurrentIncoming(self,fieldName,fieldType):
        '''
        @param{String} fieldName - 
        @param{String} fieldType - "Bool", "String", etc.

        We want to check in self.currentIncomingNode to see if the
        typedSendsStatement had a field in it named fieldName with
        type fieldType.

        @returns MESSAGE_TYPE_CHECK_SUCCEED, None if it does
        
                 MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH, type (String)
                 if the field existed, but had a different type.

                 MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST, None if
                 the field did not exist.
        '''
        return self._fieldAgreesWithMessage(self.currentIncoming,fieldName,fieldType);
    
    def fieldAgreesWithCurrentOutgoing(self,fieldName,fieldType):
        '''
        @see fieldAgreesWithCurrentIncoming
        '''
        return self._fieldAgreesWithMessage(self.currentOutgoing,fieldName,fieldType);
        
    def _fieldAgreesWithMessage(self,currentNode,fieldName,fieldType):
        if (currentNode == None):
            errMsg = '\nBehram error: incoming message is not defined ';
            errMsg += 'by the time that you want to check that a field ';
            errMsg += 'exists.\n';
            errPrint(errMsg);
            assert(False);

        for sendLine in currentNode.children:
            lineType = sendLine.children[0].value;
            lineName = sendLine.children[1].value;
            if (fieldName == lineName):
                
                if (fieldType != lineType):
                    # user error: using a name for a different type of
                    # value.
                    return MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH, lineType;
                else:
                    return MESSAGE_TYPE_CHECK_SUCCEED, None;

        return MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST, None;
                

        
    def pushContext(self):
        self.stack.append(Context());
        self.funcStack.append(FuncContext());

    def popContext(self):
        if (len(self.stack) <= 0):
            errPrint('\nBehram Error.  Empty type context stack.  Cannot pop\n');
            assert(False);
        self.stack.pop();
        self.funcStack.pop();
        self.currentOutgoing = None;
        self.currentIncoming = None;
        self.currentPublicInternalNode = None;

        
    def getIdentifierType(self,identifierName):
        '''
        @param {String} identifierName The name of the identifier that
        we're looking up in the memory store.

        @returns {tuple} (None,None) if have no type information for
        that identifier.  Otherwise, ( a, b).
        a:  String with type name.
        b:  String name of the endpoint that controls the shared
            variable (or None, if no one controls variable.
        '''
        for s in reversed(range(0,len(self.stack))):
            lookupType, controlledBy= self.stack[s].getIdentifierType(identifierName);
            if (lookupType != None):
                return lookupType,controlledBy;
        return None,None;


    def checkUndefinedTraceItems(self):
        '''
        Runs through all elements in trace line to ensure that if a
        msgSend or msgReceive is declared in the trace section, it was
        actually defined in an endpoint section.
        
        @return{None or TypeCheckError} -- None if no error,
        TypeCheckError otherwise.
        '''
        return self.traceManager.checkUndefinedMsgSendOrReceive();
    

    def checkCollision(self,identifierName,astNode):
        '''
        @param {string} identifierName -- The name of the
        variable/function we want to determine if there is a collision
        for.

        @param {AstNode} astNode -- Needed to pass into constructor of
        CollisionObject (returned if there is a collision; see below).
        
        @return none if no variable or function in the current or
        parent contexts has the same name as identifierName.
        Otherwise, returns a CollisionObject, from which can get error
        message information.
        '''

        if (identifierName == 'Print'):
            return CollisionObject(astNode,None,None);

        
        idElement = self.getIdentifierElement(identifierName);
        funcMatchObj = self.getFuncIdentifierType(identifierName);

        if (idElement == None) and (funcMatchObj == None):
            #no collision
            return None;

        funcElement = None;
        if (funcMatchObj != None):
            funcElement = funcMatchObj.element;

        #there was a collision: generate CollisionObject and return.
        return CollisionObject(astNode,idElement,funcElement);


    def getIdentifierElement(self,identifierName):
        '''
        Usage: should only be called internal to this class.
        
        @param {String} identifierName The name of the identifier that
        we're looking up in the memory store.

        @returns None if have no type information for that identifier.
        Otherwise, returns ContextElement
        '''
        for s in reversed(range(0,len(self.stack))):
            lookupType= self.stack[s].getIdentifierElement(identifierName);
            if (lookupType != None):
                return lookupType;
        return None;


    def setShouldReturn(self,typeToReturn):
        '''
        @param {string} typeToReturn
        
        Any return statements that are made within the current context
        should have the type typeToReturn.
        '''
        if (len(self.stack) <= 0):
            errMsg = '\nBehram Error.  Empty type context stack.  ';
            errMsg += 'Cannot set value should be returning\n';
            errPrint(errMsg);
            assert(False);

        self.stack[-1].setShouldReturn(typeToReturn);

    def getShouldReturn(self):
        if (len(self.stack) <= 0):
            errMsg = '\nBehram Error.  Empty type context stack.  ';
            errMsg += 'Cannot set value should be returning\n';
            errPrint(errMsg);
            assert(False);
        
        return self.stack[-1].getShouldReturn();

    
    def getFuncIdentifierType(self,identifierName):
        '''
        @returns {FuncMatch object or None}
           -None if there is no declared function with same name
           -FuncMatch object if there is a function with the same name.
        '''
        for s in reversed(range(0,len(self.funcStack))):
            lookupType = self.funcStack[s].getFuncIdentifierType(identifierName);
            if (lookupType != None):
                return lookupType;

        return None;

    
    def addIdentifier(self,identifierName,identifierType,controlledBy,astNode,lineNum = None):
        '''
        @param {String} controlledBy --- name of the endpoint that is
        authoritative for this variable if it's a shared variable.
        None if it's not a shared variable or if no one is
        authoritative for it.
        '''
        
        if(len(self.stack) <= 1):
            errPrint('\nBehram Error.  Cannot insert into type check stack because stack is empty.\n');
            assert(False);
        self.stack[-1].addIdentifier(identifierName,identifierType,controlledBy,astNode,lineNum);

    def isEndpoint(self,endpointName):
        return ((endpointName == self.endpoint1) or (endpointName == self.endpoint2));

    def addFuncIdentifier(self,functionName,functionType,functionArgTypes,astNode,lineNum=None):
        '''
        @param {string} functionName: name of function
        @param {string} functionType:
        @param {list} functionArgTypes: ordered (from left to right)
        list of types for function arguments.
        @param {int} lineNum: line number that function was declared on.

        @returns {None or TyepCheckError} -- None if nothing is wrong
        with trace, TypeCheckError otherwise.
        
        '''
        if(len(self.funcStack) <= 1):
            errMsg = '\nBehram Error.  Cannot insert into type ';
            errMsg += 'check stack because stack is empty.\n';
            errPrint(errMsg);
            assert(False);


        #if it's a msgSend function or msgReceive function, then
        #notify the traceLineManager that a msgSend or msgreceive
        #function has been defined;
        currentEndpointName = self.currentEndpointName;
        if (currentEndpointName == None):
            errMsg = '\nBehram error: should ony be adding a ';
            errMsg += 'func identifier in the body of an endpoint section.\n';
            errPrint(errMsg);
            assert(False);

        traceError = None;

        if (functionType == TYPE_MSG_SEND_FUNCTION):
            traceError = self.traceManager.addMsgSendFunction(astNode, currentEndpointName);
        elif (functionType == TYPE_MSG_RECEIVE_FUNCTION):
            traceError = self.traceManager.addMsgRecvFunction(astNode, currentEndpointName);

        if (traceError != None):
            return traceError;

        #add the function identifier itself to function context.
        traceError = self.funcStack[-1].addFuncIdentifier(
            functionName,functionType,functionArgTypes,astNode,lineNum);
        
        return traceError;
        
        

    def setCurrentEndpointName(self,endpointName):
        '''
        When begin type checking the body of an endpoint function,
        call this with the endpoint's name.  
        '''
        self.currentEndpointName = endpointName;

    def unsetCurrentEndpointName(self):
        '''
        After finished type checking the body of an endpoint function,
        call this function to unset currentEndpointname.
        '''
        self.currentEndpointName = None;

    def setAstTraceSectionNode(self,traceSectionAstNode):
        '''
        @param {AstNode} traceSectionAstNode
        '''
        self.traceManager.setAstTraceSectionNode(traceSectionAstNode);

        
    def addTraceLine(self,traceLineAstNode):
        '''
        @param{AstNode} traceLineAst
        '''
        self.traceManager.addTraceLine(traceLineAstNode);
        
        
        
class FuncContext():
    def __init__(self):
        # contains funcContextElement-s
        self.dict = {};

    def getFuncIdentifierType(self,funcIdentifierName):
        '''
        @returns None if doesn't exist
        '''
        val = self.dict.get(funcIdentifierName,None);
        if (val == None):
            return val;
        
        return val.getFuncMatchObject();

    def addFuncIdentifier(self,funcIdentifierName,funcIdentifierType,funcArgTypes,astNode,lineNum):
        '''
        @returns {None or TypeCheckError} -- If identifier already
        exists in this context, return TypeCheckError (cannot have
        re-definition of existing type).  Otherwise, return None to
        indicate no error.
        '''
        prevDecl = self.getFuncIdentifierType(funcIdentifierName);
        if (prevDecl != None):

            if (astNode.label == AST_ONCREATE_FUNCTION):
                errMsg = '\nOnCreate error.  You can only declare one ';
                errMsg += 'OnCreate function per endpoint.\n';
            else:
                errMsg =  '\nError.  You already declared a function named ';
                errMsg += '"' + funcIdentifierName + '".  You cannot declare another.\n';
                
            nodes = [astNode,prevDecl.astNode];
            return TypeCheckError(nodes,errMsg);


        self.dict[funcIdentifierName] = FuncContextElement(funcIdentifierType,funcArgTypes,astNode,lineNum);
        return None;
        

        
class FuncContextElement():
    def __init__ (self,funcIdentifierType,funcArgTypes,astNode,lineNum):
        self.funcIdentifierType = funcIdentifierType;
        self.funcArgTypes = funcArgTypes;
        self.astNode = astNode;
        self.lineNum = lineNum;


    def getFuncMatchObject(self):
        '''
        @returns {FuncMatchObject} 
        '''
        return FuncMatchObject(self);
    
    #FIXME: make consistent with astNode.  In one place, using
    #lineNum, in another, lineNo.
    def getLineNum(self):
        return self.lineNum;


def createFuncMatchObjFromJsonStr(jsonStr,astNode):
    '''
    Now have types for functions, such as:

    Function (In: Number, TrueFalse; Returns: Text) someFunc;

    The nodes for these have types that are generated from
    buildFuncTypeSignature(node,progText,typeStack) in astNode.py.

    The above would have a string-ified type of :
    {
       Type: 'Function',
       In: [ { Type: 'Number'}, {Type: 'TrueFalse'} ],
       Returns: { Type: 'Text'}
    }

    This is passed in as jsonStr.  We take this jsonStr, and turn it
    into a FuncMatchObject.
    '''
    
    typeDict = json.loads(jsonStr);
    
    argTypes = [];
    for arg in typeDict['In']:
        aType = arg['Type'];
        if (not isinstance(aType,basestring)):
            
            # means that the actual argument is a more-deeply nested
            # function.  Instead of getting all the args for that
            # function, can just keep as string for comparison.
            aType = json.dumps(aType);
            
            
        argTypes.append(aType);

    returnType = typeDict['Returns'];
    if (not isinstance(returnType,basestring)):
        returnType = json.dumps(returnType);
        
    fce = FuncContextElement(returnType,argTypes,astNode,astNode.lineNo);
    return FuncMatchObject(fce);

    
class FuncMatchObject():
    def __init__(self,funcContextElement):
        self.element = funcContextElement;

    def matches(self,funcIdentifierType,funcArgTypes):
        '''
        @param {String} funcIdentifierType -- the type we assume the
        function is supposed to return.
        
        @param {List of Strings} funcArgTypes -- the types of each
        argument for the function.
        '''
        
        if (funcIdentifierType != self.element.funcIdentifierType):
            return False;

        if (self.argMatches(funcArgTypes) == None):
            return True;

        return False;

    def getReturnType(self):
        return self.element.funcIdentifierType;

    def createJsonType(self):
        returner = {
            'Type':TYPE_FUNCTION
            };

        # input args
        inArgs = [];
        for item in self.element.funcArgTypes:
            toAppend = { 'Type': item }
            if (isFunctionType(item)):
                toAppend = json.loads(item);

            inArgs.append(toAppend);

        returner["In"] = inArgs;

        # output args
        returnType = {
            'Type': self.element.funcIdentifierType
            };
        if (isFunctionType(self.element.funcIdentifierType)):
            returnType = json.loads(self.element.funcIdentifierType);
            
        returner["Returns"] = returnType;
        return returner;


    def argMatchError(self, funcArgTypes, callingAstNode):
        '''
        @param {List of Strings} funcArgTypes -- the types of each
        argument for the function.

        @param {AstNode} callingAstNode -- the astNode where the
        function call is actually being invoked.
        
        @return FuncCallArgMatchError object if the arguments do not
                match.
        
                None if the arguments match (ie, there is no type
                error in arguments).
                
        '''

        #check if have the same number of arguments
        numArgsExpected = len(self.element.funcArgTypes );
        numArgsProvided = len(funcArgTypes);
        if (numArgsExpected != numArgsProvided):
            returner = FuncCallArgMatchError(
                self.element.lineNum,self.element.astNode,
                FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH, callingAstNode);
            
            returner.setArgLengthMismatchError(numArgsExpected,numArgsProvided);
            return returner;


        #check if types match between arguments provided and expected.
        returner = None;

        for s in range(0,len(funcArgTypes)):
            expectedType = self.element.funcArgTypes[s];
            providedType = funcArgTypes[s];
            if (providedType != expectedType):
                #means had a type error mismatch
                if (returner == None):
                    #means it was our first type error mismatch, and
                    #we should craft a FuncCallArgMatchError object to
                    #return.
                    returner = FuncCallArgMatchError(
                        self.element.lineNum,self.element.astNode,
                        FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH,callingAstNode);

                #append an error
                returner.addMatchError(s+1,expectedType,providedType);

                    
        return returner;

        
class FuncCallArgMatchError():
    
    '''
    Stores data used for error reporting when try to call a function
    but either have incorrect number of arguments or have mismatched
    arguments.

    It is good form to make a call to checkValid before trying to use
    internal fields, and after you think the object is completely
    constructed.

    See more documentation in init method's docstring to get a sense
    of what internal data looks like/can be used for.
    
    '''
    def __init__ (self,funcLineNo,funcAstNode, errorType,callAstNode):
        '''
        
        @param {int} funcLineNo -- line where the actual function
        signature is declared.

        @param {AstNode} funcAstNode -- ast node corresponding to
        actual function.

        @param {int} errorType --
        FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH if error is
        mismatched number of arguments (in which case, creator of
        error must subsequently call setArgLengthMismatchError before
        using object).  Error objects of this type place the required
        number of arguments in self.expected (as a number) and the
        provided number of arguments (as a number) in self.provided.

        FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH if error is that got
        the correct number of arguments, but some of the arguments had
        the wrong type.  In this case, user specifies which arguments
        were incorrect through calls to addMatchError.  In this case,
        self.argNos is a list whose elements are the index of the
        arguments that disagreed.  self.expected is a list whose
        elements are the types that the function required for those
        arguments that mismatched.  self.provided is a list whose
        elements are the types that the function call was provided
        with for those arguments that mismatched.

        More concretely, if I have a function:
        
        function foo (Number a, Bool b)
        and I call it as
        foo (1, 20);

        I should have
        self.argNos = [2];
        self.expected = [Bool];
        self.provided = [Number];

        @param {AstNode} callAstNode -- The ast node corresponding to
        where the actual function call was performed.
        
        '''
        self.lineNos = [callAstNode.lineNo , funcLineNo];
        self.astNodes = [callAstNode,funcAstNode];
        
        self.errorType = errorType;

        self.valid = False;
        
        self.argNos = None;
        self.expected = None;
        self.provided = None;

    def checkValid(self):
        '''
        Should only call when trying to use (not set) internal data of
        object.  Just ensures that actual data for different types of
        errors has actually been set before being used.
        '''
        if (not self.valid):
            errPrint('\nValidity check for FuncCallArgMatchError object failed.\n');
            assert(False);
        
        
    def setArgLengthMismatchError(self,numArgsExpected,numArgsProvided):
        '''
        @param {int} numArgsExpected
        @param {int} numArgsProvided
        
        Called to set the number of arguments expected vs the number
        provided when have an argument length mismatch error.
        '''
        if (self.errorType != FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH):
            errMsg = '\nBehram error: should not be setting a num arguments '
            errMsg += 'mismatch error if have declared the error type as a ';
            errMsg += 'type mismatch error.';
            errMsg += '\n';
            errPrint(errMsg);
            assert(False);
            
        self.expected = numArgsExpected;
        self.provided = numArgsProvided;
        self.valid = True;
        
    def addMatchError(self,argNo,expectedType,providedType):
        '''
        @param {int} argNo
        @param {String} expectedType
        @param {String} providedType
        '''
        
        if (self.errorType != FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH):
            errMsg = '\nBehram error: should not add a specific argument ';
            errMsg += 'type mismatch error when already specified that ';
            errMsg += 'error was a length mismatch.\n';
            errPrint(errMsg);
            assert(False);

        #first error added
        if (self.argNos == None):
            self.argNos = [];
            self.expected = [];
            self.provided = [];

        self.argNos.append(argNo);
        self.expected.append(expectedType);
        self.provided.append(providedType);
        self.valid = True;

    
        
        
class Context():
    def __init__(self):
        self.dict = {};
        self.typeToReturn = None;


    def setShouldReturn(self,typeToReturn):
        self.typeToReturn = typeToReturn;

        
    def getShouldReturn(self):
        return self.typeToReturn;

        
    def getIdentifierElement(self,identifierName):
        '''
        @returns None if doesn't exist.
        '''
        val = self.dict.get(identifierName,None);
        return val;


    def getIdentifierType(self,identifierName):
        '''
        @returns {tuple} (None,None) if does not exist.
        Otherwise, ( a, b).
        
        a:  String with type name.
        b:  String name of the endpoint that controls the shared
            variable (or None, if no one controls variable.
        @returns None if doesn't exist.
        '''

        returner = self.getIdentifierElement(identifierName);
        if (returner):
            return returner.getType(), returner.getControlledBy();
        return None,None;


        
    def addIdentifier(self,identifierName,identifierType,controlledBy,astNode,lineNum):
        '''
        If identifier already exists in this context, throw an error.
        Cannot have re-definition of existing type.
        '''
        exists,ctrldBy  = self.getIdentifierType(identifierName);
        if (exists != None):
            #FIXME: this should turn into a more formal error-reporting system.
            errPrint('\nError, overwriting existing type with name ' + identifierName + '\n');
            assert(False);

        prevDecl,ctrldBy = self.getIdentifierType(identifierName);
        if (prevDecl != None):
            errMsg =  '\nError.  You already declared a variable named ';
            errMsg += '"' + identifierName + '".  You cannot declare another.\n';
            nodes = [astNode,prevDecl.astNode];
            return TypeCheckError(nodes,errMsg);

        self.dict[identifierName] = ContextElement(identifierType,controlledBy,astNode,lineNum);

        
class ContextElement():
    def __init__ (self,identifierType,controlledBy,astNode,lineNum):
        self.identifierType = identifierType;
        self.astNode = astNode;
        self.lineNum = lineNum;
        self.controlledBy = controlledBy;

    def getControlledBy(self):
        '''
        @returns {String} name of the endpoint that is authoritative
        for this variable if it's a shared variable.  None if it's not
        a shared variable or if no one is authoritative for it.
        '''
        return self.controlledBy;

        
    def getType(self):
        return self.identifierType;

    def getLineNum(self):
        return self.lineNum;



class CollisionObject():
    '''
    Holds data for error message print outs when there is a collision
    between variable/function names in declarations.
    '''
    def __init__(self,astNode,idElement,funcElement):
        '''
        @param {ContextElement or None} idElement
        @param {FuncContextElement or None} funcElement

        Elements that the declaration in astNode collided with.
        '''
        self.nodes = [astNode];
        self.lineNos = [astNode.lineNo];
        
        if (idElement != None):
            self.nodes.append(idElement.astNode);
            self.lineNos.append(idElement.lineNum);

        if (funcElement != None):
            self.nodes.append(funcElement.astNode);
            self.lineNos.append(funcElement.lineNum);
