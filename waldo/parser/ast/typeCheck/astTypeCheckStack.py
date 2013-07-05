#!/usr/bin/python


from waldo.parser.ast.astLabels import *

from waldo.parser.ast.parserUtil import errPrint

from traceLine import TraceLineManager;
from traceLine import TypeCheckError;

from templateUtil import JSON_TYPE_FIELD;
from templateUtil import JSON_FUNC_RETURNS_FIELD;
from templateUtil import JSON_EXTERNAL_TYPE_FIELD
from templateUtil import JSON_FUNC_IN_FIELD;
from templateUtil import dict_type_to_str
from templateUtil import get_type_array_from_func_call_returned_tuple_type
from templateUtil import checkTypeMismatch
from templateUtil import is_external
from templateUtil import is_wildcard_type
from templateUtil import set_external
import pickle

FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH = 0;
FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH = 1;

ID = 'id';

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



class TypeCheckContextStack(object):
    def __init__ (self):
        self.stack     = []; #last element in array is always top of stack.
        self.funcStack = [];

        self.rootNode = None;
        #also contains additional data
        self.protObjName = None;
        # textual names of each endpoint
        self.endpoint1 = None;
        self.endpoint2 = None;
        # the line number that the names appear on
        self.endpoint1LineNo = None;
        self.endpoint2LineNo = None;
        # the ast nodes associated with each endpoint
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

        self.inOnComplete = False;
        self.inSequencesSection = False;
        # array of tuples: first element is string endpoint name,
        # second element is string function name.
        self.sequenceSectionNameTuples = [];
        
        # used to type check return statements to ensure that a
        # function actually returns the type that it says it will.
        #      msg_send_seq_func, msg_recv_seq_func, public_func,
        #      on_create, private_func
        self.currentFunctionNode = None;

        # allowed to have placeholder extAssigns and extCopies in lhs
        # of assignment statement to accommodate tuples.  Ie, you're
        # allowed to do extAssign _ to some_ext = some_func(); In the
        # rest of the code, you're not allowed to use and lhs_assign
        # statement.
        self.in_lhs_assign = False

        # indices are the struct names.  values are the types of the
        # struct with that name
        self.struct_type_dict = {}
        
        # initialize endpoint builtin methods
        self.initBuiltinMethods();

    def initBuiltinMethods(self):
        '''
        Initializes built-in endpoint methods by adding them to the 
        function stack.
        '''
        endpointBuiltinMethodContext = FuncContext();
        endpointBuiltinMethodContext.addFuncIdentifier(
            ID, [{JSON_TYPE_FIELD : TYPE_STRING}], [], None, None);
        self.funcStack.append(endpointBuiltinMethodContext);
        
    def setRootNode(self,root):
        if self.rootNode != None:
            errMsg = '\nBehram error: should not set root node after it has ';
            errMsg += 'already been set.\n';
            print(errMsg);
            assert(False);
        self.rootNode = root;

        
    def checkRepeatedSequenceLine(self):
        '''
        @return{None or TypeCheckError} -- None if no error,
        TypeCheckError if more than one trace line have the same name.
        '''
        return self.traceManager.checkRepeatedSequenceLine();
    

    def getCurrentEndpoint(self):
        if self.currentEndpointName == None:
            errMsg = '\nBehram error: should be type checking an endpoint ';
            errMsg += 'to call getCurrentEndpoint in typestack.\n';
            print(errMsg);
            assert(False);

        if self.currentEndpointName == self.endpoint1:
            return self.endpoint1Ast;
        elif self.currentEndpointName == self.endpoint2:
            return self.endpoint2Ast;

        errMsg = '\nBehram error: no matching endpoint for currentEndpointName.  ';
        errMsg += 'Cannot return current endpoint.\n';
        print(errMsg);
        assert(False);
        
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


    def add_struct_type(self,struct_name,struct_type):
        '''
        @returns {None or String} --- String if there's an error (the
        string is the error message).  None if there's no error.
        '''
        err_msg = None
        if struct_name in self.struct_type_dict:
            err_msg = 'Error.  Already have a struct named '
            err_msg += struct_name + '.'
        
        self.struct_type_dict[struct_name] = struct_type
        return err_msg

    def get_struct_type(self,struct_name,external):
        '''
        @param {bool} external
        
        @returns{type dict or None} --- None if struct_name has not
        been declared by user.  type dict if it has (where type dict
        is the declared type of that node).
        '''
        s_type = self.struct_type_dict.get(struct_name,None)
        if s_type == None:
            return s_type

        # deep copy type so that marking as external or not will not
        # affect any other type.
        s_type = pickle.loads(pickle.dumps(s_type))
        set_external(s_type,external)
        return s_type
        
    def addCurrentFunctionNode(self,node):
        '''
        Sets the current function we're in so that can check return
        types when we get to them.
        '''
        if ((node.label != AST_PUBLIC_FUNCTION) and (node.label != AST_PRIVATE_FUNCTION) and
            (node.label != AST_ONCREATE_FUNCTION) and
            (node.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION ) and
            (node.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION) and
            (node.label != AST_ONCOMPLETE_FUNCTION)):
            
            errMsg = '\nBehram error: adding internal or public node with incorrect ';
            errMsg += 'type.\n';
            errPrint(errMsg);
            assert(False);

        self.currentFunctionNode = node;
        
    def checkReturnStatement(self,returnNode,check_type_mismatch_func):
        '''
        @param {function} check_type_mismatch_func ... should just be
        typeCheck.checkTypeMismatch.
        '''
        if (returnNode.label != AST_RETURN_STATEMENT):
            errMsg = '\nBehram error: trying to check a ';
            errMsg += 'return statement without a return statement node.\n';
            errPrint(errMsg);
            assert(False);

            
        if self.currentFunctionNode == None:
            errMsg = '\nBehram error: any return statement should have a ';
            errMsg += 'currentFunctionNode to compare to.\n';
            print(errMsg);
            assert(False);


        return_tuple_node = returnNode.children[0]
        # list of the types that we're actually returning
        return_type_list = []
        for single_node in return_tuple_node.children:

            # takes care of case where we are returning a function
            # call
            if ((single_node.label == AST_FUNCTION_CALL) and
                (not is_wildcard_type(single_node.type))):
                func_returned_type_array = get_type_array_from_func_call_returned_tuple_type(
                    single_node.type)
                for ind_tuple_return_type in func_returned_type_array:
                    return_type_list.append(ind_tuple_return_type)
            else:
                return_type_list.append(single_node.type)
            
        returnStatementType = returnNode.children[0].type;
        if ((self.currentFunctionNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION) or
            (self.currentFunctionNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION)):

            if len(return_type) > 0:
                err_msg = 'Error.  Cannot return a value from a sequence function.'
                nodes= [returnNode];
                return TypeCheckError(nodes,err_msg);

            # no error because message sequences are not declared to
            # return anything and this return statement does not.
            return None

        # check public and privates for return statement...
        function_returns_type_node = self.currentFunctionNode.children[1];
        # the declared return type of this function
        function_returns_type_list = []
        for single_type in function_returns_type_node.children:
            function_returns_type_list.append(single_type.type)

        funcName = self.currentFunctionNode.children[0].value;

        if len(function_returns_type_list) != len(return_type_list):
            err_msg = 'Error.  ' + funcName + ' expects to return '
            err_msg += str(len(function_returns_type_list)) + ' arguments.  '
            err_msg += 'Instead, you returned ' + str(len(return_type_list))
            err_msg += ' arguments.'
            err_nodes = [returnNode, function_returns_type_node]
            return TypeCheckError(err_nodes,err_msg)

        
        for return_index in range(0,len(return_type_list)):
            
            declared_return_type = function_returns_type_list[return_index]
            actual_return_type = return_type_list[return_index]

            if check_type_mismatch_func(
                returnNode,declared_return_type,actual_return_type,self,''):

                err_msg = 'Incorrect return type in ' + funcName + '.  '
                if len(return_type_list) == 1:
                    err_msg += 'Expected type '
                    err_msg += dict_type_to_str(declared_return_type)
                    err_msg += ', but actually returned type '
                    err_msg += dict_type_to_str(actual_return_type)
                    err_msg += '.'
                else:
                    err_msg += 'The ' + str(return_index + 1) + ' tuple return '
                    err_msg += 'element expected a type of '
                    err_msg += dict_type_to_str(declared_return_type)
                    err_msg += ', but actually returned type of '
                    err_msg += dict_type_to_str(actual_return_type)
                    err_msg += '.'

                err_nodes = [returnNode, function_returns_type_node]
                return TypeCheckError(err_nodes, err_msg)

        return None;

    
    def checkTraceItemInputOutput(self):
        '''
        run through all trace lines to see if the message outputs
        match the message inputs.

        @return {None or TypeCheckError} -- None if inputs and outputs
        agree.  TypeCheckError if they do not.
        '''
        return self.traceManager.checkTraceItemInputOutput();

        
    def pushContext(self):
        self.stack.append(Context());
        self.funcStack.append(FuncContext());

    def popContext(self):
        if (len(self.stack) <= 0):
            errPrint('\nBehram Error.  Empty type context stack.  Cannot pop\n');
            assert(False);
        self.stack.pop();
        self.funcStack.pop();
        self.currentFunctionNode = None;

        
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

        @param{list of type dicts} functionType --- The return type of
        this function.  We're using a list to support returning
        tuples.  Each element of the list is the return type of that
        element of the tuple.
        

        @param {list} functionArgTypes: ordered (from left to right)
        list of types for function arguments.
        
        @param {int} lineNum: line number that function was declared on.

        @returns {None or TyepCheckError} -- None if nothing is wrong
        with trace, TypeCheckError otherwise.
        
        '''
        if len(self.funcStack) <= 1:
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

        

        if astNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
            traceError = self.traceManager.addMsgSendFunction(astNode,currentEndpointName);
        elif astNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
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
        return self.traceManager.addTraceLine(traceLineAstNode);
        
        
        
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


        self.dict[funcIdentifierName] = FuncContextElement(
            funcIdentifierType,funcArgTypes,astNode,lineNum);
        
        return None;
        

        
class FuncContextElement():
    def __init__ (self,funcIdentifierType,funcArgTypes,astNode,lineNum):
        # note this is a list of strings.  each element of the list is
        # the type of one of the elements in the tuple.
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


def createFuncMatchObjFromFuncTypeDict(func_type_dict,astNode):
    '''
    @param {type dict} func_type_dict --- 
    
    Have types for functions, such as:

    Function (In: Number, TrueFalse; Returns: Text) someFunc;

    The nodes for these have types that are generated from
    buildFuncTypeSignature(node,progText,typeStack) in astNode.py.

    The above would have a dict type of :
    {
       Type: 'Function',
       In: [ { Type: 'Number'}, {Type: 'TrueFalse'} ],
       Returns: { Type: 'Text'}
    }

    We take this dict and turn it into a FuncMatchObject.
    '''

    argTypes = [];
    for arg in func_type_dict[JSON_FUNC_IN_FIELD]:
        argTypes.append(arg)

    returnType = func_type_dict[JSON_FUNC_RETURNS_FIELD];
        
    fce = FuncContextElement(returnType,argTypes,astNode,astNode.lineNo);
    return FuncMatchObject(fce);

    
class FuncMatchObject():
    def __init__(self,funcContextElement):
        self.element = funcContextElement;

    def getReturnType(self):
        '''
        @returns{List of type dicts} --- List to support tuple return.
        '''
        return self.element.funcIdentifierType;

    def createTypeDict(self):
        returner = {
            JSON_TYPE_FIELD:TYPE_FUNCTION,
            JSON_EXTERNAL_TYPE_FIELD: False
            };

        # input args
        inArgs = [];
        for item in self.element.funcArgTypes:
            inArgs.append(item)

        returner[JSON_FUNC_IN_FIELD] = inArgs;

        # output args
        returnType = {
            JSON_TYPE_FIELD: self.element.funcIdentifierType
            };
            
        returner[JSON_FUNC_RETURNS_FIELD] = returnType;
        return returner;


    def argMatchError(self, funcArgTypes, callingAstNode):
        '''
        @param {List of type dicts} funcArgTypes -- the types of each
        argument for the function.

        @param {AstNode} callingAstNode -- the astNode where the
        function call is actually being invoked.
        
        @return FuncCallArgMatchError object if the arguments do not
                match.
        
                None if the arguments match (ie, there is no type
                error in arguments).
                
        '''

        # Check if the number of args expected matches the number of args
        # provided. Args of type Nothing should not be counted.
        numArgsExpected = sum([1 for type_dict in self.element.funcArgTypes if 
                type_dict[JSON_TYPE_FIELD] != TYPE_NOTHING])
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

            if ((is_external(expectedType) and (not is_external(providedType)))
                or checkTypeMismatch(self.element,expectedType,providedType,None,None)):

                # means that we expected an external and were provided
                # with a non-external
                if returner == None:
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
        @param {String} identifierName
        @param {String} identifierType
        
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
