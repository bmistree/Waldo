#!/usr/bin/env python
import sys;
import os;


curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;

# so can get type checking helper functions to determine types
sys.path.append(os.path.join(curDir,'..','..','parser','ast','typeCheck'));
import templateUtil;


_REFRESH_KEY = '______REFRESH_REQUEST_____';
_REFRESH_RECEIVE_KEY = '______REFRESH_RECEIVE_REQUEST_____';
_REFRESH_SEND_FUNCTION_NAME = '_refresh';
_REFRESH_RECEIVE_FUNCTION_NAME = '_Text';


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


    for s in range(0,len(splitOnNewLine)):
        if (len(splitOnNewLine[s]) != 0):
            returnString += indenter + splitOnNewLine[s];
        if (s != len(splitOnNewLine) -1):
            returnString += '\n';

    return returnString;


def createDictLiteralAssignment(assignToStatement,dictToCreate):
    '''
    @param{String} assignToStatement --- Left-hand side of assignment

    @param{dict} dictToCreate --- Indexes are strings that should
    appear as indices in the returned string, values are those values
    
    @returns {String} ---
    
    "globSharedReadVars = {
            '0__pingNum' : 0,
            '1__otherPingNum' : 0,
            '5__nothingShared' : 0
            };"

    would be returned if we passed in:
    createDictLiteralAssignment(
        'globSharedReadVars',
        {
            "'0__pingNum'" : '0',
            "'1__otherPingNum'" : '0',
            ....
        });
    '''
    returner = assignToStatement + ' = {\n';
    dictBody ='';
    for dictKey in sorted(dictToCreate.keys()):
        dictVal = dictToCreate[dictKey];
        dictBody += dictKey  + ': '  + dictVal + ',\n';
    returner += indentString(dictBody,1);
    returner += '};';
    return returner;
    

def getDefaultValueFromDeclNode(astDeclNode):
    '''
    @param {AstNode} astDeclNode --- The node specifying the
    declaration of an identifier.  The type of the node specifies the
    default value to use.  

    For instance,
    Number someNum = 0;
    astDeclNode would be the node formed from the entire statement.
    
    @returns {String} --- The default value that a node of this type
    should have.  For instance, the default value for a number type is
    0 (returns "0"), the default value for a string is '' (returns
    "''"), etc.
    '''
    # typeLabel = astTypeNode.label;
    typeLabel = astDeclNode.type;
    
    if typeLabel == TYPE_BOOL:
        returner = 'False';
    elif typeLabel == TYPE_NUMBER:
        returner = '0';
    elif typeLabel == TYPE_STRING:
        returner = "''";
    elif typeLabel == TYPE_NOTHING:
        returner = 'None';
    elif templateUtil.isListType(typeLabel):
        returner = '[]';
    elif templateUtil.isFunctionType (typeLabel):
        returner = '_defaultFunction';
    elif templateUtil.isMapType(typeLabel):
        returner = '{}';
    else:
        errMsg = '\nBehram error: unrecognized type name when writing ';
        errMsg += 'default value for node.\n';
        print(errMsg);
        assert(False);

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

def getEndpointNames(astRoot):
    returner = [];
    aliasSection = astRoot.children[1];
    returner.append(aliasSection.children[0].value);
    returner.append(aliasSection.children[1].value);
    return returner;
    

def lastMessageSuffix(sequenceName):
    '''
    Provides the code to conclude the message sequence and call
    onComplete.

    @param {String} sequenceName --- the name of the sequence that
    is completing

    @returns {String} --- code to execute
    '''
    return """
#### 
# tell other side that the sequence is finished and tell our
# event that it should no longer wait on the message sequence
# to complete.  Note that should not have to do two of these.
# Should only have to do one.  But does not hurt to do both.
self._writeMsg(
    _Message._endpointMsg(
        _context,_actEvent,
        _Message.MESSAGE_SEQUENCE_SENTINEL_FINISH,
        '%s'));

_onCompleteNameToLookup = self._generateOnCompleteNameToLookup(
   # hard-coded sequence name
   '%s');
_onCompleteFunction = _OnCompleteDict.get(_onCompleteNameToLookup,None);

if not self._iInitiated(_actEvent.id):
   # means that I need to check if I should add an oncomplete
   # to context
   if _onCompleteFunction != None:
       _context.addOnComplete(
           _onCompleteFunction,_onCompleteNameToLookup,self);
else:
    _context.signalMessageSequenceComplete(
        _context.id,_onCompleteFunction,_onCompleteNameToLookup,
        self);

return; # if this was because of a jump, abort, etc., having
        # return here ensures that the function does not
        # execute further.
""" % (sequenceName,sequenceName);


def nextMessageSuffix(nextFuncEventName,sequenceName,toSelf=False):
    writeFuncName = '_writeMsg';
    if toSelf:
        writeFuncName = '_writeMsgSelf';
    
    return """
# note that we may have postponed this event before we got to
# writing the message.  This check ensures that we do not use
# the network extra when we do not have to.
if _actEvent.contextId != _context.id:
    raise _PostponeException();

# request the other side to perform next action.
self.%s(_Message._endpointMsg(_context,_actEvent,'%s','%s'));
return; # if this was because of a jump, having
        # return here ensures that the function does
        # not execute further.
""" % (writeFuncName,nextFuncEventName,sequenceName);
    


def getFuncEventKey(funcName,endpointName,fdepDict):
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



class EmitContext(object):
    '''
    Gets passed around in actual emitting code.  The flags that it
    wraps are used to change behavior of emitter.  (For instance, if
    we see a collision flag, then we insert time.sleeps into the code
    after message sends to try to increase likelihood that two
    transactions will collide and one will have to be backed out.)
    '''

    def __init__(self,collisionFlag):
        '''
        @param {bool} collisionFlag --- If true, then insert
        time.sleeps into the code after message sends to try to
        increase likelihood that two transactions will collide and one
        will have to be backed out.
        '''
        self.collisionFlag = collisionFlag;
        self.insideOnComplete = False;

        # if emitting for inside of message sequence, this node is
        # non-none.  important for jump statements.
        self.msgSequenceNode = None;
        self.msgSeqFuncNode = None;
        
    def outOfOnComplete(self):
        self.insideOnComplete = False;

    def inOnComplete(self):
        self.insideOnComplete = True;
