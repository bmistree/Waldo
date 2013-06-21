#!/usr/bin/env python

from waldo.parser.ast.astLabels import *
from waldo.parser.ast.parserUtil import *


TYPE_ERROR_ENCOUNTERED = False;

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
    

    errPrint('*************************');

    # reformat errorString so that doesn't print off side
    errPrint(splitString(errorString,80));

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
                errorText += '*';
			
            errorText += '\t';
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


class WaldoTypeCheckException(Exception):

   def __init__(self, errMsg):
       self.value = errMsg;

   def __str__(node):
       return repr(self.value)
    
    


####
def getMsgSeqSection(rootNode):
    '''
    @param{AstNode} rootNode --- should have label AST_ROOT
    @returns {AstNode} --- should have label AST_MESSAGE_SEQUENCE_SECTION
    '''
    if rootNode.label != AST_ROOT:
        errMsg = '\nBehram error when calling getMsgSeqSection.  ';
        errMsg += 'Was not passed in root node.\n';
        print(errMsg);
        assert(False);

    if rootNode.children[6].label != AST_MESSAGE_SEQUENCE_SECTION:
        errMsg = '\nBehram error when calling getMsgSeqSection.  ';
        errMsg += 'Trying to return a something that is not a ';
        errMsg += 'message sequence.\n';
        print(errMsg);
        assert(False);
        
    return rootNode.children[6];

def isEndpointSequenceFunction(msgSeqFuncNode,currentEndpointName):
    '''
    @param {AstNode} msgSeqFuncNode --- labeled either
    Message_send_sequence_function,
    message_receive_sequence_function, or onComplete

    @param {String} currentEndpointName --- The name of the endpoint
    we are currently type checking.

    @returns{Bool} --- True if the message function represented by
    msgSeqFuncNode operates on the endpoint with currentEndpointName,
    False otherwise.  ie, True if

    msgSeqFuncNode represents
    End1.firstFunc(a,b)
    {

    }

    and currentEndpointName is "End1".  
    '''

    if ((msgSeqFuncNode.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION) and
        (msgSeqFuncNode.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION) and
        (msgSeqFuncNode.label != AST_ONCOMPLETE_FUNCTION)):
        errMsg = '\nBehram error when calling isEndpointSequenceFunction.  ';
        errMsg += 'Should have received a message send/receive/oncomplete sequence ';
        errMsg += 'function as first argument.  Instead got ';
        errMsg += msgSeqFuncNode.label + '.\n';
        print(errMsg);
        assert(False);

    funcName = msgSeqFuncNode.children[1].value;
    endName =  msgSeqFuncNode.children[0].value;
    return (endName == currentEndpointName);

