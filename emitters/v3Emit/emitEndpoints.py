#!/usr/bin/env python

import sys;
import os;
import emitUtils;
import mainEmit;

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;


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
    returner += emitUtils.indentString(
        _createInit(endpointName,astRootNode,fdepDict,whichEndpoint),
        1);

    return returner;


def _createInit(endpointName,astRootNode,fdepDict,whichEndpoint):
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

    initMethod = 'def __init__(self,connectionObj):\n\n';
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
        'globSharedReadVars',globSharedVarsDict);
    initMethodBody += '\n';

    # create glob shared write vars dict.  @see comment above for glob
    # shared read vars dict, except of writes.
    initMethodBody += emitUtils.createDictLiteralAssignment(
        'globSharedWriteVars',globSharedVarsDict);
    initMethodBody += '\n\n';    


    # one endpoint can only assign even event ids the other can only
    # assign odd endpoint ids.
    evenOddEventId = whichEndpoint;
    otherEvenOdd = (evenOddEventId +1) % 2;
    initMethodBody += '# the other endpoint will have ' + str(otherEvenOdd) + '\n';
    initMethodBody += 'lastIdAssigned = ' + str(evenOddEventId) + ';\n\n';
    initMethodBody += '''# one side must be greater than the other
# used to resolve which side will back out its changes when
# there is a conflict.  (Currently though, these are unused.)
'''
    initMethodBody += 'myPriority = ' + str(evenOddEventId) + ';\n';
    initMethodBody += 'otherPriority = ' + str(otherEvenOdd) + ';\n\n';

    # handle context
    initMethodBody += 'committedContext = _Context();\n';


    # create a prototype events dict for this endpoint to copy active
    # events from.
    initMethodBody += '''
# make copy from base prototype events dict, setting myself as
# endpoint for each copied event.
prototypeEventsDict = {};
for pEvtKey in _PROTOTYPE_EVENTS_DICT.keys():
    pEvt = _PROTOTYPE_EVENTS_DICT[pEvtKey];
    prototypeEventsDict[pEvtKey] = pEvt.copy(self);
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
        'execFromToInternalFuncDict',endpointFunctionNamesEventDict);

    initMethodBody += '\n\n';
    
    # now emit global and shared variable dictionaries.  each contains
    # their default values.  Later in the __init__ function will
    # actually initialize their values according to user-coded
    # initialization statements.

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
    
    # now emit the base _Endpoint class initializer
    initMethodBody += '''

# invoke base class initializer
_Endpoint.__init__(
    self,connectionObj,globSharedReadVars,globSharedWriteVars,
    lastIdAssigned,myPriority,theirPriority,committedContext,
    execFromToInternalFuncDict,prototypeEventsDict);
''';

    initMethodBody += '\n\n';

    # emit initialization of shared and endpoint global variables.
    initMethodBody += '# initialization of shared and global variables\n';

    # handles shared
    initMethodBody += _emitInitSharedGlobalVariables(
        sharedIdentifiersToDeclNodesDict,astRootNode,fdepDict);
    # handles endpoint global
    initMethodBody += _emitInitSharedGlobalVariables(
        globalIdentifiersToDeclNodesDict,astRootNode,fdepDict);

    
    initMethodBody += '###### ON CREATE FUNCTION BODY ######\n';

    errMsg = '\nBehram error: still need to emit ';
    errMsg += ' on create, initializations of shared and global vars, and user-defined functions.\n';
    print(errMsg);
    
    initMethod += emitUtils.indentString(initMethodBody,1);
    return initMethod;


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

