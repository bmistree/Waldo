#!/usr/bin/python

from astLabels import TYPE_BOOL;
from astLabels import TYPE_STRING;
from astLabels import TYPE_NUMBER;
from astLabels import TYPE_NOTHING;
from astLabels import TYPE_INCOMING_MESSAGE;
from astLabels import TYPE_OUTGOING_MESSAGE;
from astLabels import TYPE_MSG_SEND_FUNCTION;
from astLabels import TYPE_MSG_RECEIVE_FUNCTION;
from astLabels import AST_TYPED_SENDS_STATEMENT;

from traceLine import TraceLineManager;

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
            assert(False);
        
        self.currentIncoming = node;

    def checkTraceItemInputOutput(self):
        # run through all trace lines to see if the message outputs
        # match the message inputs.
        self.traceManager.checkTraceItemInputOutput();

        
    def literalAgreesWithOutgoingMessage(self,literal):
        return self._literalAgreesWithMessage(self.currentOutgoing,literal);
    
    def literalAgreesWithIncomingMessage(self,literal):
        return self._literalAgreesWithMessage(self.currentIncoming,literal);

    def _literalAgreesWithMessage(self,declaredTypedSendsNode,literal):
        '''
        '''
        if (declaredTypedSendsNode == None):
            errMsg = '\nBehram error: should have an incoming or outgoing node ';
            errMsg += 'if trying to check agreement.\n';
            print(errMsg);
            return;
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
                        print('\nHad same fields but incorrect types.\n');
                        assert(False);

            if (not found):
                print('\nLiteral is missing field named ' + lineName);
                assert(False);
                
        # now checks that there aren't any fields in literal that do
        # not appear in declaredTypeSendsNode.
        for literalLine in literal.children:
            llineType = literalLine.children[1].type;
            llineName = literalLine.children[0].value;
            exists,additional = self._fieldAgreesWithMessage(declaredTypedSendsNode,llineName,llineType);
            if (exists == MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST):
                print('\nLiteral contains a field that declared does not named ' + llineName);
                assert(False);

        print('\nFix error reporting on literalAgreesWithMessage');
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
            print(errMsg);
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
            print('\nError.  Empty type context stack.  Cannot pop\n');
            assert(False);
        self.stack.pop();
        self.funcStack.pop();
        self.currentOutgoing = None;
        self.currentIncoming = None;        
        
    def getIdentifierType(self,identifierName):
        '''
        @param {String} identifierName The name of the identifier that
        we're looking up in the memory store.

        @returns None if have no type information for that identifier.
        String with type name otherwise.  Typenames come from
        AST_LABELS file....maybe.
        '''
        for s in reversed(range(0,len(self.stack))):
            lookupType= self.stack[s].getIdentifierType(identifierName);
            if (lookupType != None):
                return lookupType;
        return None;


    def checkUndefinedTraceItems(self):
        '''
        Runs through all elements in trace line to ensure that if a
        msgSend or msgReceive is declared in the trace section, it was
        actually defined in an endpoint section.
        '''
        self.traceManager.checkUndefinedMsgSendOrReceive();
    

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
            errMsg = '\nError.  Empty type context stack.  ';
            errMsg += 'Cannot set value should be returning\n';
            print(errMsg);
            assert(False);

        self.stack[-1].setShouldReturn(typeToReturn);

    def getShouldReturn(self):
        if (len(self.stack) <= 0):
            errMsg = '\nError.  Empty type context stack.  ';
            errMsg += 'Cannot set value should be returning\n';
            print(errMsg);
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

    
    def addIdentifier(self,identifierName,identifierType,astNode,lineNum = None):

        if(len(self.stack) <= 1):
            print('\nError.  Cannot insert into type check stack because stack is empty.\n');
            assert(False);
            
        self.stack[-1].addIdentifier(identifierName,identifierType,astNode,lineNum);

    def isEndpoint(self,endpointName):
        return ((endpointName == self.endpoint1) or (endpointName == self.endpoint2));

    def addFuncIdentifier(self,functionName,functionType,functionArgTypes,astNode,lineNum=None):
        '''
        @param {string} functionName: name of function
        @param {string} functionType:
        @param {list} functionArgTypes: ordered (from left to right)
        list of types for function arguments.
        @param {int} lineNum: line number that function was declared on.
        '''
        if(len(self.funcStack) <= 1):
            print('\nError.  Cannot insert into type check stack because stack is empty.\n');
            assert(False);


        #if it's a msgSend function or msgReceive function, then
        #notify the traceLineManager that a msgSend or msgreceive
        #function has been defined;
        currentEndpointName = self.currentEndpointName;
        if (currentEndpointName == None):
            errMsg = '\nBehram error: should ony be adding a ';
            errMsg += 'func identifier in the body of an endpoint section.\n';
            print(errMsg);
            assert(False);

        if (functionType == TYPE_MSG_SEND_FUNCTION):
            self.traceManager.addMsgSendFunction(astNode, currentEndpointName);
        elif (functionType == TYPE_MSG_RECEIVE_FUNCTION):
            self.traceManager.addMsgRecvFunction(astNode, currentEndpointName);


        #add the function identifier itself to function context.
        self.funcStack[-1].addFuncIdentifier(functionName,functionType,functionArgTypes,astNode,lineNum);


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
        If identifier already exists in this context, throw an error.
        Cannot have re-definition of existing type.
        '''
        if (self.getFuncIdentifierType(funcIdentifierName) != None):
            #Fixme: this should turn into a more formal error-reporting system.
            print('\nError, overwriting existing type with name ' + funcIdentifierName + '\n');
            assert(False);

        #note: if appending to this condition, will have to import
        #additional types at top of file.
        if ((funcIdentifierType != TYPE_BOOL)   and
            (funcIdentifierType != TYPE_NUMBER) and
            (funcIdentifierType != TYPE_STRING) and
            (funcIdentifierType != TYPE_NOTHING) and
            (funcIdentifierType != TYPE_INCOMING_MESSAGE) and
            (funcIdentifierType != TYPE_OUTGOING_MESSAGE) and
            (funcIdentifierType != TYPE_MSG_SEND_FUNCTION) and
            (funcIdentifierType != TYPE_MSG_RECEIVE_FUNCTION)):
            
            print('\nError.  Unrecognized identifierType insertion: ' + funcIdentifierType + '\n');
            assert(False);

        self.dict[funcIdentifierName] = FuncContextElement(funcIdentifierType,funcArgTypes,astNode,lineNum);


        
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

        if (self.argMathces(funcArgTypes) == None):
            return True;

        return False;

    def getReturnType(self):
        return self.element.funcIdentifierType;


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
            print('\nValidity check for FuncCallArgMatchError object failed.\n');
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
            print(errMsg);
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
            print(errMsg);
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
        @returns None if doesn't exist.
        '''

        returner = self.getIdentifierElement(identifierName);
        if (returner):
            return returner.getType();
        return returner;
        
        
    def addIdentifier(self,identifierName,identifierType,astNode,lineNum):
        '''
        If identifier already exists in this context, throw an error.
        Cannot have re-definition of existing type.
        '''
        if (self.getIdentifierType(identifierName) != None):
            #FIXME: this should turn into a more formal error-reporting system.
            print('\nError, overwriting existing type with name ' + identifierName + '\n');
            assert(False);

        #note: if appending to this condition, will have to import
        #additional types at top of file.
        if ((identifierType != TYPE_BOOL) and (identifierType != TYPE_NUMBER) and
            (identifierType != TYPE_STRING) and (identifierType != TYPE_INCOMING_MESSAGE) and
             (identifierType != TYPE_OUTGOING_MESSAGE)):
            print('\nError.  Unrecognized identifierType insertion: ' + identifierType + '\n');
            assert(False);

        self.dict[identifierName] = ContextElement(identifierType,astNode,lineNum);

        
class ContextElement():
    def __init__ (self,identifierType,astNode,lineNum):
        self.identifierType = identifierType;
        self.astNode = astNode;
        self.lineNum = lineNum;


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
