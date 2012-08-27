#!/usr/bin/env python

import sys;
import os;
import emitUtils;
import mainEmit;

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;

# so can get oncreate token name
sys.path.append(os.path.join(curDir,'..','..','lexer'));
from waldoLex import ONCREATE_TOKEN;



def emitEndpoints(astRootNode,fdepDict):
    '''
    @returns {String}
    '''
    returner = '';

    # get endpoint names to process
    endpointNames = _getEndpointNames(astRootNode);

    
    returner += _emitEndpoint(endpointNames[0],astRootNode,fdepDict,0);
    returner += _emitEndpoint(endpointNames[1],astRootNode,fdepDict,1);

    return returner;


def _emitEndpoint(endpointName,astRootNode,fdepDict,whichEndpoint):
    '''
    Emits the endpoint class associated with the endpoint named
    endpointName
    
    @param {String} endpointName
    @param {AstNode} astRootNode
    @param {dict} fdepDict
    
    @param {0 or 1} whichEndpoint --- There are a couple of
    assymetries in endpoint construction.  For example, one enpdoint
    assigns event ids that are even and one assigns event ids that are
    odd.  This bit allows me to distinguish which endpoint I am emitting.
    '''
    returner = 'class ' + endpointName + '(_Endpoint):\n';
    # handle init
    returner += emitUtils.indentString(
        _emitInit(endpointName,astRootNode,fdepDict,whichEndpoint),
        1);
    returner += '\n\n';

    # now handle each user-defined function
    functionSectionNode = _getFunctionSectionNode(
        endpointName,astRootNode);
    for funcNode in functionSectionNode.children:
        returner += emitUtils.indentString(
            _emitFunctionDefinition(funcNode,endpointName,astRootNode,fdepDict),
            1);
        returner += '\n\n';
    
    return returner;


def _emitFunctionDefinition(funcNode,endpointName,astRootNode,fdepDict):
    '''
    @param {AstNode} funcNode --- Should be the root node of the
    function we're trying to emit.  only valid labels are oncreate,
    public, private, message send, message receive.
    
    @param {String} endpointName --- The name of the endpoint that
    we're emitting this function for.
    
    @param {AstNode} astRootNode --- The root ast node of the entire
    program.
    '''

    if ((funcNode.label == AST_PUBLIC_FUNCTION) or
        (funcNode.label == AST_PRIVATE_FUNCTION) or
        (funcNode.label == AST_ONCREATE_FUNCTION)):
        return _emitPublicPrivateOnCreateFunctionDefinition(
            funcNode,endpointName,astRootNode,fdepDict);
    elif funcNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        print('\nBehram error: need to handle message send function.\n');
    elif funcNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        print('\nBehram error: need to handle message receive function.\n');
    else:
        errMsg = '\nBehram error: trying to emit a func def ';
        errMsg += 'for a non-function.\n';
        print(errMsg);
        assert(False);
        

def _emitPublicPrivateOnCreateFunctionDefinition(
            funcNode,endpointName,astRootNode,fdepDict):
    '''
    @see _emitFunctionDefinition for argument documentation.
    '''

    funcNameNode = funcNode.children[0];
    funcName = funcNameNode.value;
    funcArguments = _getArgumentNamesFromFuncNode(funcNode);
    functionBodyNode = _getFuncBodyNodeFromFuncNode(funcNode);    
    
    returner = '';
    
    if funcNode.label == AST_PUBLIC_FUNCTION:
        # means that we have to emit both a public version and a
        # hidden, internal version.
        # here we emit the public version.
        returner += 'def ' + funcName + '(self,';
        for argName in funcArguments:
            returner += argName + ',';
        returner += '):\n';

        publicMethodBody = '''
# passing in FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL
# ... that way know that the function call happened from
# external caller and don't have to generate new function
# calls for it.
_returner = self._%s(
    _Endpoint._FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL,
    None,None);

# should check if there are other active events
self._tryNextEvent();
return _returner;
''' % funcName;

        returner += emitUtils.indentString(publicMethodBody,1);
        returner += '\n';

        

    ####### now handle internal definition of function #########
    # every function should have a special key associated in the event
    # dict.  this is used so that we know where to re-start execution
    # after an event completes.  
    functionEventKey = _getFuncEventKey(funcName,endpointName,fdepDict);
    
    # actually emit the function    
    returner += 'def _%s(self,' % funcName;
    for argName in funcArguments:
        returner += argName + ',';

    returner += '_callType,_actEvent=None,_context=None):\n'

    funcBody = r"""
'''
@param{String} _callType ---

   _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED :
   means that anything that we return will not be set in
   return statement of context, but rather will just be
   returned.

   _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE :
   means that we should return anything that we get via the
   _context return queue, but that we should *not* create a
   new active event or context.

   _Endpoint._FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL :
   means that we should return anything that we get via the
   _context return queue, *and* we should create a new active
   event and context.


Note that the only time that _actEvent and _context should be
empty is on a FIRST_FROM_EXTERNAL call.

@param{_ActiveEvent object} _actEvent --- Pass into subsequent
functions that this function calls from its body.  Used only
directly for RESUME_POSTPONE.  It is used to signal to the
blocking execution loop that the internal execution of the
function has completed and can try to return its value, commit
its context, and unblock.

@param{_Context object} _context --- Each function can operate
on endpoint global, sequence global, and shared variables.
These are all stored in this _context object.

'''

# FIXME: need to actually generate logic for deep-copying
# arguments


#### DEBUG
if ((_callType != _Endpoint._FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL) and
    (_callType != _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED) and
    (_callType != _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE)):
    errMsg = '\nBehram error: invalid call type passed to function.\n';
    print(errMsg);
    assert(False);

if _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL:
    if _actEvent != None:
        errMsg = '\nBehram error: when issuing call from external, should ';
        errMsg += 'have an empty _actEvent argument.\n';
        print(errMsg);
        assert(False);

    if _context != None:
        errMsg = '\nBehram error: when issuing call from external, should ';
        errMsg += 'have an empty _context argument.\n';
        print(errMsg);
        assert(False);

if ((_callType ==  _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED) or
    (_callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE)):
    if _actEvent == None:
        errMsg = '\nBehram error: when issuing non-external call, should ';
        errMsg += '*not* have an empty _actEvent argument.\n';
        print(errMsg);
        assert(False);
    if _context == None:
        errMsg = '\nBehram error: when issuing non-external call, should ';
        errMsg += '*not* have an empty _context argument.\n';
        print(errMsg);
        assert(False);
#### END DEBUG


# need to create the event and either create its context and
# execute it if the required read/write variables are
# available, or schedule the event for the future if those
# resources are not available.
if _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL:
    # to get argument values
    # see http://stackoverflow.com/questions/582056/getting-list-of-parameters-inside-python-function
    _frame = _inspect.currentframe();
    _args, _, _, _values = _inspect.getargvalues(_frame);
    _functionArgs = [_values[i] for i in _args];

    # remove head argument (self) and tail default arguments
    # (_callType, _actEvent, and _context) off the
    # back, because these will be automatically filled when
    # function is called internally.
    _functionArgs = _functionArgs[1:];
    _functionArgs = _functionArgs[0: len(_functionArgs) - 3];

    self._lock(); # locking at this point, because call to
                  # generateActiveEvent, uses the committed dict.

    _actEvent = self._prototypeEventsDict['""" + functionEventKey + r"""'].generateActiveEvent();
    _actEvent.setToExecuteFrom('""" + functionEventKey + r"""'); # when postponed, will return to here
    _actEvent.setArgsArray(_functionArgs);

    _eventAdded,_context = _actEvent.addEventToEndpointIfCan();

    if not _eventAdded:
        # conflict with globals/shareds .... insert event into
        # toProcess array and block until function gets
        # executed.
        self._inactiveEvents.append(_actEvent);

    self._unlock();                                            

    if _eventAdded:

        self._executeActive(
            _actEvent,
            _context,
            # specified so that will use return queue when done, etc.
            _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE);                    

    # now block until we know that the event has been
    # completed....can block by waiting on thread safe return
    # queue.
    _returnQueueElement = _actEvent.returnQueue.get();
    return _returnQueueElement.returnVal;


####### ONLY GETS HERE IF CALL TYPE IS NOT FIRST_FROM_EXTERNAL
#### DEBUG
if _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL:
    errMsg = '\nBehram error: should not execute body of function ';
    errMsg += 'if first from external.\n';
    print(errMsg);
    assert(False);
#### END DEUBG.

# actual meat of the function
""";

    # start emitting actual body of the function.
    for statementNode in functionBodyNode.children:
        funcBody += mainEmit.emit(statementNode,fdepDict);
        funcBody += '\n';

    # force a return at end of function if did not encounter one
    # otherwise (eg. statement did not return anything).  This ensures
    # that code that had been blocking on completion of this function
    # gets called
    funcBody += """
# special-cased return statement
if _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE:
    # note that also commit outstanding changes to context here.
    _actEvent.setCompleted(None,_context);
    return;
elif _callType == _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED:
    return None;
""";
        
    returner += emitUtils.indentString(funcBody,1);
    return returner;
    

    

def _emitInit(endpointName,astRootNode,fdepDict,whichEndpoint):
    '''
    For params, @see _emitEndpoint

    @returns {String} --- a non-indented raw text of init function for
    a single endpoint.
    '''
    sharedIdentifiersToDeclNodesDict = _getSharedIdsToDeclNodesDict(
        astRootNode);
    globalIdentifiersToDeclNodesDict = _getEndpointIdsToDeclNodesDict(
        endpointName,astRootNode);
    
    sharedVariableNames = sorted(
        sharedIdentifiersToDeclNodesDict.keys());
    
    endpointVariableNames = sorted(
        globalIdentifiersToDeclNodesDict.keys());


    onCreateNode = _getOnCreateNode(endpointName,astRootNode);
    onCreateArgumentNames = [];
    if onCreateNode != None:
        onCreateArgumentNames = _getArgumentNamesFromFuncNode(onCreateNode);

    initMethod = 'def __init__(self,_connectionObj,';
    for argName in onCreateArgumentNames:
        initMethod += argName + ',';
    initMethod += '):\n\n'
    
    initMethodBody = '';
    
    # create glob shared read vars dict: keeps track of number of
    # running events that are using one of the endpoint global or
    # shared variables for a read operation.
    globSharedVarsDict = {};
    for sharedVarName in sharedVariableNames:
        # each starts at 0 because there is no outstanding event that
        # is using the variable.
        globSharedVarsDict [ "'" + sharedVarName + "'"] = '0';
    for endpointVarName in endpointVariableNames:
        globSharedVarsDict [ "'" + endpointVarName + "'"] = '0';

    initMethodBody += emitUtils.createDictLiteralAssignment(
        '_globSharedReadVars',globSharedVarsDict);
    initMethodBody += '\n';

    # create glob shared write vars dict.  @see comment above for glob
    # shared read vars dict, except of writes.
    initMethodBody += emitUtils.createDictLiteralAssignment(
        '_globSharedWriteVars',globSharedVarsDict);
    initMethodBody += '\n\n';    


    # one endpoint can only assign even event ids the other can only
    # assign odd endpoint ids.
    evenOddEventId = whichEndpoint;
    otherEvenOdd = (evenOddEventId +1) % 2;
    initMethodBody += '# the other endpoint will have ' + str(otherEvenOdd) + '\n';
    initMethodBody += '_lastIdAssigned = ' + str(evenOddEventId) + ';\n\n';
    initMethodBody += '''# one side must be greater than the other
# used to resolve which side will back out its changes when
# there is a conflict.  (Currently though, these are unused.)
'''
    initMethodBody += '_myPriority = ' + str(evenOddEventId) + ';\n';
    initMethodBody += '_otherPriority = ' + str(otherEvenOdd) + ';\n\n';

    # handle context
    initMethodBody += '_committedContext = _Context();\n';


    # create a prototype events dict for this endpoint to copy active
    # events from.
    initMethodBody += '''
# make copy from base prototype events dict, setting myself as
# endpoint for each copied event.
_prototypeEventsDict = {};
for pEvtKey in _PROTOTYPE_EVENTS_DICT.keys():
    _pEvt = _PROTOTYPE_EVENTS_DICT[_pEvtKey];
    _prototypeEventsDict[pEvtKey] = _pEvt.copy(self);
''';



    # create execFromInternalFuncDict, which maps event names to the
    # internal functions to call for them.

    initMethodBody += '''
# every event needs to be able to map its name to the internal
# function that should be called to initiate it.
# string(<id>__<iniating function name>) : string ... string
# is name of function on endpoint to call.
''';
    endpointFunctionNamesEventDict = _getEndpointFunctionNamesFromEndpointName(
        endpointName,astRootNode,fdepDict);
    
    initMethodBody += emitUtils.createDictLiteralAssignment(
        '_execFromToInternalFuncDict',endpointFunctionNamesEventDict);

    initMethodBody += '\n\n';


    # now emit the base _Endpoint class initializer
    initMethodBody += '''

# invoke base class initializer
_Endpoint.__init__(
    self,_connectionObj,_globSharedReadVars,_globSharedWriteVars,
    _lastIdAssigned,_myPriority,_theirPriority,_committedContext,
    _execFromToInternalFuncDict,_prototypeEventsDict);
''';

    initMethodBody += '\n\n';

    
    # now emit global and shared variable dictionaries.  each contains
    # their default values.  After this, actually initialize their
    # values according to user-coded initialization statements.

    # shareds
    sharedDict = {};
    for sharedId in sorted(sharedIdentifiersToDeclNodesDict.keys()):
        declNode = sharedIdentifiersToDeclNodesDict[sharedId];
        defaultVal = emitUtils.getDefaultValueFromDeclNode(declNode);
        sharedDict[ "'" + sharedId + "'"] = defaultVal;
        
    initMethodBody += '# emitting local copies of shared variables\n';
    initMethodBody += '# with default args.  later section of code \n';
    initMethodBody += '# initializes these variables.\n';
    initMethodBody += emitUtils.createDictLiteralAssignment(
        'self._committedContext.shareds',sharedDict);
    initMethodBody += '\n\n';            

    # globals
    globalsDict = {};
    for globalId in sorted(globalIdentifiersToDeclNodesDict.keys()):
        declNode = globalIdentifiersToDeclNodesDict[globalId];
        defaultVal = emitUtils.getDefaultValueFromDeclNode(declNode);
        sharedDict[ "'" + globalId + "'"] = defaultVal;

    initMethodBody += '# emitting local copies of endpoint global variables\n';
    initMethodBody += '# with default args.  later section of code \n';
    initMethodBody += '# initializes these variables.\n';
    initMethodBody += emitUtils.createDictLiteralAssignment(
        'self._committedContext.endGlobals',sharedDict);
    initMethodBody += '\n\n';            

    # context should not have any sequence globals
    initMethodBody += '# committed context never has sequence globals in it.\n'
    initMethodBody += 'self._committedContext.seqGlobals = None;\n'
    

    # emit initialization of shared and endpoint global variables.
    initMethodBody += '\n# initialization of shared and global variables\n';

    # handles shared
    initMethodBody += _emitInitSharedGlobalVariables(
        sharedIdentifiersToDeclNodesDict,astRootNode,fdepDict);
    # handles endpoint global
    initMethodBody += _emitInitSharedGlobalVariables(
        globalIdentifiersToDeclNodesDict,astRootNode,fdepDict);
    initMethodBody += '\n\n';

    
    # on create function (if it exists)
    if onCreateNode != None:
        initMethodBody += '# call oncreate function for remaining initialization \n';
        initMethodBody += 'self._%s(' % ONCREATE_TOKEN;
        for argName in onCreateArgumentNames:
            initMethodBody += argName + ',';
        
        # now emit function control commands for oncreate
        initMethodBody += '_Endpoint.FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED,';
        initMethodBody += 'None,';
        initMethodBody += 'self._committtedContext);\n'
    else:
        initMethodBody += '# no oncreate function to call.\n';
    
    errMsg = '\nBehram error: still need to emit ';
    errMsg += ' functions.';
    print(errMsg);
    
    initMethod += emitUtils.indentString(initMethodBody,1);
    return initMethod;


def _getOnCreateNode(endpointName,astRootNode):
    '''
    @return {None or AstNode} --- None if endpoint named endpointName
    does not have a node, AstNode if it does.
    '''
    functionSectionNode = _getFunctionSectionNode(
        endpointName,astRootNode);

    # find the oncreate function
    for funcNode in functionSectionNode.children:
        if funcNode.label == AST_ONCREATE_FUNCTION:
            # actually emit all function text for node.
            return funcNode;

    return None;

def _getFuncEventKey(funcName,endpointName,fdepDict):
    '''
    @param{String} funcName
    @param{String} endpointName

    @param{dict} fdepDict

    @returns{String}
    
    every function should have a special key associated in the event
    dict.  this is used so that we know where to re-start execution
    after an event completes.  This key should be the funcName of the
    functionDep object associated with the function.  In this
    function, we scan through the entire fdepDict for the function
    that matches the <endpointName,funcName> tuple.  Then we return
    that functionDep object's name as its key.
    '''
    
    for fdepKey in fdepDict.keys():
        fdep = fdepDict[fdepKey];

        if (funcName == fdep.srcFuncName) and (endpointName == fdep.endpointName):
            return fdep.funcName;
        
    # means that we didn't find a match.  this should cause an error.
    errMsg = '\nBehram error in _getFuncEventKey.  Could not find ';
    errMsg += 'a function with correct function name.\n';
    print(errMsg);
    assert(False);
    
    


def _getArgumentNamesFromFuncNode(funcNode):
    '''
    @param {AstNode} funcNode --- for private, public, oncreate,
    message receive, and message send functions.

    @returns {Array} --- Each element is a string representing the
    name of the argument that the user passed in.
    '''
    argNodeIndex = None;
    if funcNode.label == AST_PUBLIC_FUNCTION:
        argNodeIndex = 2;
    elif funcNode.label == AST_PRIVATE_FUNCTION:
        argNodeIndex = 2;
    elif funcNode.label == AST_ONCREATE_FUNCTION:
        argNodeIndex = 1;
    elif funcNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        argNodeIndex = 2;
    elif funcNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        return [];
    else:
        errMsg = '\nBehram error: cannot call argumentnamesfromfuncnode on ';
        errMsg += 'nodes that are not function nodes.\n';
        print(errMsg);
        assert(False);

    returner = [];
    funcDeclArgListNode = funcNode.children[argNodeIndex];
    for funcDeclArgNode in funcDeclArgListNode.children:
        nameNode = funcDeclArgNode.children[1];
        name = nameNode.value;
        returner.append(name);
        
    return returner;

def _getFuncBodyNodeFromFuncNode(funcNode):
    '''
    @param {AstNode} funcNode --- for private, public, oncreate,
    message receive, and message send functions

    @returns{AstNode} --- The ast node containing the function's body.
    '''
    bodyNodeIndex = None;
    if funcNode.label == AST_PUBLIC_FUNCTION:
        bodyNodeIndex = 3;
    elif funcNode.label == AST_PRIVATE_FUNCTION:
        bodyNodeIndex = 3;
    elif funcNode.label == AST_ONCREATE_FUNCTION:
        bodyNodeIndex = 2;
    elif funcNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        bodyNodeIndex = 3;
    elif funcNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        bodyNodeIndex = 2;
    else:
        errMsg = '\nBehram error: cannot get funcbodynode from ';
        errMsg += 'nodes that are not function nodes.\n';
        print(errMsg);
        assert(False);

    return funcNode.children[bodyNodeIndex];

    

def _getFunctionSectionNode(endpointName,astRootNode):
    endpointNode = _getEndpointNodeFromEndpointName(
        endpointName,astRootNode);

    bodySectionNode = endpointNode.children[1];
    functionSectionNode = bodySectionNode.children[1];
    return functionSectionNode;
    
    
def _emitInitSharedGlobalVariables(
    idsToDeclNodesDict,astRootNode,fdepDict):
    '''
    Inside of init function of each endpoint class, need to initialize
    shared variables and endpoint global variables with their initial
    values.
    '''
    returner = '';
    for _id in idsToDeclNodesDict:
        declNode = idsToDeclNodesDict[_id];
        returner += mainEmit.emit(declNode,fdepDict);
        returner += '\n';
    return returner;
    
def _getSharedIdsToDeclNodesDict(astRoot):
    '''
    @returns {dict} --- keys are identifiers (annotated by slicer
    code) for shared variables and values are the declaration nodes.
    '''
    returner = {};
    
    sharedSectionNode = astRoot.children[3];
    for annotatedDeclarationNode in sharedSectionNode.children:
        # have an annotatedDeclarationNode for each shared variable.
        identifierNode = annotatedDeclarationNode.children[2];
        identifierNode._debugErrorIfHaveNoAnnotation('_getSharedIdentifiersToTypeDict');
        returner[identifierNode.sliceAnnotationName] = annotatedDeclarationNode;

    return returner;


def _getEndpointNodeFromEndpointName(endpointName,astRootNode):
    endpoint1Node = astRootNode.children[4];
    endpoint1Name = endpoint1Node.children[0].value;
    
    endpoint2Node = astRootNode.children[5];
    endpoint2Name = endpoint2Node.children[0].value;
    
    toCheckEndpointNode = None;
    if endpointName == endpoint1Name:
        toCheckEndpointNode = endpoint1Node;
    elif endpointName == endpoint2Name:
        toCheckEndpointNode = endpoint2Node;
    else:
        errMsg = '\nBehram error: have no endpoint that ';
        errMsg += 'matches name "' + endpointName + '" to ';
        errMsg += 'get endpoint node from.\n';
        print(errMsg);
        assert(False);
        
    return toCheckEndpointNode;


def _getEndpointIdsToDeclNodesDict(endpointName,astRootNode):
    '''
    @returns {dict} --- Keys are identifiers for each of the values,
    which are endpoint global declaration nodes.
    '''
    endpointNode = _getEndpointNodeFromEndpointName(endpointName,astRootNode);

    returner = {};
    if endpointNode.label != AST_ENDPOINT:
        errMsg = '\nBehram error: Error _getEndpointVariableIdentifiersToTypeDict ';
        errMsg += 'expected an ast node labeled as an endpoint.\n';
        print(errMsg);
        assert(False);

    endpointBodyNode = endpointNode.children[1];
    endpointGlobalsSectionNode = endpointBodyNode.children[0];

    for declNode in endpointGlobalsSectionNode.children:
        identifierNode = declNode.children[1];
        identifierNode._debugErrorIfHaveNoAnnotation(
            '_getEndpointVariableIdentifiersFromEndpointNode');
        returner[identifierNode.sliceAnnotationName] = declNode;
        
    return returner;


def _getEndpointNames(astRoot):
    returner = [];
    aliasSection = astRoot.children[1];
    returner.append(aliasSection.children[0].value);
    returner.append(aliasSection.children[1].value);
    return returner;
    

def _getEndpointFunctionNamesFromEndpointName(
    endpointName,astRootNode,functionDepsDict):
    '''
    @param {String} endpointName
    @param {AstNode} astRootNode

    @return {dict} --- keys of dict are the identifiers that should
    use for each function and the values are the internal names that
    the function takes in the endpoint class

    # creates something like
    #   {
    #      "'Ping_-_-_incPing'" : "'_incPing'",
    #       ...
    #   }
    
    '''
    returner = {};
    for fdepKey in sorted(functionDepsDict.keys()):
        fdep = functionDepsDict[fdepKey];

        if fdep.endpointName != endpointName:
            continue;

        # means that this function occurrs within this endpoint.  list it.
        returner["'" + fdep.funcName + "'"] = "'" + _convertSrcFuncNameToInternal(fdep.srcFuncName) + "'";
        
    return returner;


def _convertSrcFuncNameToInternal(fname):
    '''
    @param {String} fname

    @returns {String} --- Takes a function name and returns the name
    that an endpoint class uses for its internal call.  For now, this
    means just pre-pending the input argument with an underscore, ie:
    "_<fname>"
    '''
    return '_' + fname;

