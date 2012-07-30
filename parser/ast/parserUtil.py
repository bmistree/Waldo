#!/usr/bin/python

import sys;
from  astLabels import *;
import json;

OutputErrsTo = sys.stderr;

JSON_TYPE_FIELD = 'Type';
JSON_FUNC_RETURNS_FIELD = 'Returns';
JSON_FUNC_IN_FIELD = 'In';

JSON_LIST_ELEMENT_TYPE_FIELD = 'ElementType';

JSON_MAP_FROM_TYPE_FIELD = 'From';
JSON_MAP_TO_TYPE_FIELD = 'To';


def isValueType(typeLabel):
    '''
    Text, TrueFalse, and Number are all value types.  Everything else is not
    '''
    return (typeLabel == TYPE_BOOL) or (typeLabel == TYPE_NUMBER) or (typeLabel == TYPE_STRING);

def isFunctionType(typeLabel):
    '''
    Nodes can have many different type labels.  Some are specified by
    strings (mostly nodes with basic types, eg. Number, String, etc.).

    Nodes for user-defined function types do not just have one
    annotation, but rather a json-ized type.  To check if a node's
    label is one of these user-defined function types, we check to
    exclude all of the other types it could be.

    Returns true if it is a user-defined function type, false otherwise.
    
    '''
    
    if ((typeLabel != TYPE_BOOL) and (typeLabel != TYPE_NUMBER) and
        (typeLabel != TYPE_STRING) and (typeLabel != TYPE_INCOMING_MESSAGE) and
        (typeLabel != TYPE_OUTGOING_MESSAGE) and (typeLabel != TYPE_NOTHING) and
        (typeLabel != EMPTY_LIST_SENTINEL) and (typeLabel != EMPTY_MAP_SENTINEL)):

        jsonType = json.loads(typeLabel);
        
        if (jsonType.get(JSON_TYPE_FIELD,None) == None):
            errMsg = '\nBehram error.  got a json object that did not have ';
            errMsg += 'a type field.\n';
            print(errMsg);
            assert (False);
            
        if (jsonType[JSON_TYPE_FIELD] == TYPE_FUNCTION):
            return True;

    return False;


def isListType(typeLabel):
    '''
    Automatically handles case of EMPTY_LIST_SENTINEL
    '''
    if not isTemplatedType(typeLabel):
        return False;


    # can only be a list type if not templated if it's an empty
    # list.
    if typeLabel == EMPTY_LIST_SENTINEL:
        return True;
    elif typeLabel == EMPTY_MAP_SENTINEL:
        return False;
    
    jsonType = json.loads(typeLabel);
        
    if jsonType.get(JSON_TYPE_FIELD,None) == None:
        errMsg = '\nBehram error.  got a json object that did not have ';
        errMsg += 'a type field.\n';
        print(errMsg);
        assert (False);
            
    if jsonType[JSON_TYPE_FIELD] == TYPE_LIST:
        return True;

    # either a map or a function.
    return False;

def getMapIndexType(typeLabel):
    if not isMapType(typeLabel):
        print('\n\n');
        print('Behram error, requested to get index type from non-map\n');
        print('\n\n');
        assert(False);
    dictLabel = json.loads(typeLabel);
    indType = dictLabel[JSON_MAP_FROM_TYPE_FIELD];
    if (not isinstance(indType,basestring)):
        indType = json.dumps(indType);
    return indType;


def getMapValueType(node):
    typeLabel = node.type;
    if not isMapType(typeLabel):
        print('\n\n');
        print('Behram error, requested to get value type from non-map\n');
        print('\n\n');
        assert(False);
    dictLabel = json.loads(typeLabel);
    valType = dictLabel[JSON_MAP_TO_TYPE_FIELD];
    if (not isinstance(valType,basestring)):
        valType = json.dumps(valType);
    return valType;


def isMapType(typeLabel):
    '''
    Automatically handles case of EMPTY_MAP_SENTINEL
    '''
    if not isTemplatedType(typeLabel):
        return False;

    # can only be a map if not templated if it's an empty
    # map
    if typeLabel == EMPTY_MAP_SENTINEL:
        return True;
    elif typeLabel == EMPTY_LIST_SENTINEL:
        return False;

    jsonType = json.loads(typeLabel);
        
    if jsonType.get(JSON_TYPE_FIELD,None) == None:
        errMsg = '\nBehram error.  got a json object that did not have ';
        errMsg += 'a type field.\n';
        print(errMsg);
        assert (False);
            
    if jsonType[JSON_TYPE_FIELD] == TYPE_MAP:
        return True;

    # either a list or a function.
    return False;



def isTemplatedType(typeLabel):
    '''
    @returns{bool} True if it's a function or list type, false otherwise.
    '''
    if ((typeLabel != TYPE_BOOL) and (typeLabel != TYPE_NUMBER) and
        (typeLabel != TYPE_STRING) and (typeLabel != TYPE_INCOMING_MESSAGE) and
        (typeLabel != TYPE_OUTGOING_MESSAGE) and (typeLabel != TYPE_NOTHING)):
        return True;

    return False;


def setOutputErrorsTo(toOutputTo):
    global OutputErrsTo;
    OutputErrsTo = toOutputTo;

def errPrint(toPrint):
    '''
    @param{String} toPrint
    Outputs toPrint on stderr
    '''
    global OutputErrsTo;
    print >> OutputErrsTo , toPrint;


