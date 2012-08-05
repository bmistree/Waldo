#!/usr/bin/env python

import sys;
import os;
curDir = os.path.dirname(__file__);
sys.path.append(os.path.join('..',curDir));
from  astLabels import *;
import json;


'''
Almost all of these utility functions are built to allow access to,
type check, and construct the three templated types that waldo
supports:
  * function objects
  * lists
  * maps
'''


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
        (typeLabel != TYPE_STRING) and (typeLabel != TYPE_NOTHING) and
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

def getListValueType(typeLabel):
    '''
    @param {String} typeLabel -- an ast node's .type field.
    
    Note: presupposes that this is a list.  otherwise asserts out.
    similarly, user must ensure that typeLabel is not
    EMPTY_LIST_SENTINEL.
    '''
    if not isListType(typeLabel):
        errMsg = '\nBehram error.  Asking for list value type ';
        errMsg += 'of non-list.\n';
        print(errMsg);
        assert(False);

    if typeLabel == EMPTY_LIST_SENTINEL:
        errMsg = '\nBehram error.  Cannot call getListValueType on ';
        errMsg += 'an empty map.  Should have checked this condition ';
        errMsg += 'before calling into function.\n';
        print(errMsg);
        assert(False);

    elemType = json.loads(typeLabel)[JSON_LIST_ELEMENT_TYPE_FIELD];
    if (not isinstance(elemType,basestring)):
        # list of lists for instance or list of maps or list of
        # functions.
        elemType = json.dumps(elemType);
    return elemType;


def getMapIndexType(typeLabel):
    '''
    @param {String} typeLabel --- an ast node's .type field.
    
    Note: should not put in EMPTY_MAP_SENTINEL for typeLabel.  User
    should pre-check for this.
    '''
    if not isMapType(typeLabel):
        print('\n\n');
        print('Behram error, requested to get index type from non-map\n');
        print('\n\n');
        assert(False);

    if typeLabel == EMPTY_MAP_SENTINEL:
        errMsg = '\nBehram error.  Cannot call getMapIndexType on ';
        errMsg += 'an empty map.  Should have checked this condition ';
        errMsg += 'before calling into function.\n';
        print(errMsg);
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
        
    if typeLabel == EMPTY_MAP_SENTINEL:
        errMsg = '\nBehram error.  Cannot call getMapValueType on ';
        errMsg += 'an empty map.  Should have checked this condition ';
        errMsg += 'before calling into function.\n';
        print(errMsg);
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
        (typeLabel != TYPE_STRING) and  (typeLabel != TYPE_NOTHING)):
        return True;

    return False;



def bothLists(a,b):
    if (not isinstance(a,basestring)):
        a = json.dumps(a);
    if (not isinstance(b,basestring)):
        b = json.dumps(b);        
    return isListType(a) and isListType(b);

def bothMaps(a,b):
    if (not isinstance(a,basestring)):
        a = json.dumps(a);
    if (not isinstance(b,basestring)):
        b = json.dumps(b);        
    return isMapType(a) and isMapType(b);

def moreSpecificListMapType(typeA,typeB):
    '''
    @param {String} typeA --- string-ified version of json list/map type.
    @param {String} typeB --- string-ified version of json list/map type.

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

    if (typeA == EMPTY_LIST_SENTINEL) or (typeA == EMPTY_MAP_SENTINEL):
        return typeB;

    if (typeB == EMPTY_LIST_SENTINEL) or (typeB == EMPTY_MAP_SENTINEL):
        return typeA;

    dictA = json.loads(typeA);
    dictB = json.loads(typeB);


    twoMaps = False;
    if bothLists(typeA,typeB):
        # grab the types of elements for each list.
        valueTypeA = dictA[JSON_LIST_ELEMENT_TYPE_FIELD];
        valueTypeB = dictB[JSON_LIST_ELEMENT_TYPE_FIELD];

        # can just set these to any non-sentinel value
        indexTypeA = '';
        indexTypeB = '';
        
    elif bothMaps(typeA,typeB):
        twoMaps = True;
        valueTypeA = dictA[JSON_MAP_TO_TYPE_FIELD];
        valueTypeB = dictB[JSON_MAP_TO_TYPE_FIELD];

        indexTypeA = dictA[JSON_MAP_FROM_TYPE_FIELD];
        indexTypeB = dictB[JSON_MAP_FROM_TYPE_FIELD];
    else:
        # otherwise, type mismatch: return one or the other.
        return typeA;
        
    if (valueTypeA == EMPTY_LIST_SENTINEL) or (valueTypeA == EMPTY_MAP_SENTINEL):
        # means that typeB is at least as specific
        return typeB;

    if (valueTypeB == EMPTY_LIST_SENTINEL) or (valueTypeB == EMPTY_MAP_SENTINEL):
        # means that typeA is at least as specific        
        return typeA;

    if indexTypeA != indexTypeB:
        # mismatch, return either
        return typeA;

    elTypeA = valueTypeA;
    if (not isinstance(valueTypeA,basestring)):
        elTypeA = json.dumps(valueTypeA);
        
    elTypeB = valueTypeB;
    if (not isinstance(valueTypeB,basestring)):
        elTypeB = json.dumps(valueTypeB);

        
    if ( ((not isListType(elTypeA) ) and
          (not isMapType(elTypeA) ))
         
          or
         
        ((not isListType(elTypeB) ) and
          (not isMapType(elTypeB) ))):
        # if one or both are not lists or maps, that means that we've reached
        # the maximum comparison depth and we cannot get more
        # specific, so just return one or the other.
        return typeA;

    
    # each element itself is a list or a map
    recursionResult = moreSpecificListMapType(
        json.dumps(valueTypeA),json.dumps(valueTypeB));


    # must rebuild surrounding list type signature to match typeA or
    # typeB.
    if twoMaps:
        jsonToReturn = buildMapTypeSignatureFromTypeName(indexTypeA,recursionResult);
    else:
        jsonToReturn = buildListTypeSignatureFromTypeName(recursionResult);
        
    return json.dumps(jsonToReturn);



def buildListTypeSignatureFromTypeName(typeName):
    
    if (isTemplatedType(typeName)):
        if ((typeName != EMPTY_LIST_SENTINEL) and
            (typeName != EMPTY_MAP_SENTINEL)):
            typeName = json.loads(typeName);

    return {
        JSON_TYPE_FIELD: TYPE_LIST,
        JSON_LIST_ELEMENT_TYPE_FIELD: typeName
        };

def buildListTypeSignature(node, progText,typeStack):
    elementTypeNode = node.children[0];
    elementTypeNode.typeCheck(progText,typeStack);
    elementType = elementTypeNode.type;
    return buildListTypeSignatureFromTypeName(elementType);



def buildMapTypeSignatureFromTypeNames(fromTypeName,toTypeName):
    
    if isTemplatedType(fromTypeName):
        if ((fromTypeName != EMPTY_LIST_SENTINEL) and
            (fromTypeName != EMPTY_MAP_SENTINEL)):
            fromTypeName = json.loads(fromTypeName);

    if isTemplatedType(toTypeName):
        if ((toTypeName != EMPTY_LIST_SENTINEL) and
            (toTypeName != EMPTY_MAP_SENTINEL)):
            toTypeName = json.loads(toTypeName);
        

    return {
        JSON_TYPE_FIELD: TYPE_MAP,
        JSON_MAP_FROM_TYPE_FIELD: fromTypeName,
        JSON_MAP_TO_TYPE_FIELD: toTypeName
        };



def buildMapTypeSignature(node,progText,typeStack):
    '''
    @returns 3-tuple: (a,b,c)

    a: {json object} --- The actual type constructed
    
    b: {String or None} --- None if no error.  If there is an error,
       this text gives the error message.
    
    b: {list of ast nodes or None} --- None if no error.  Otherwise,
       returns the list of ast nodes that caused the error.
    '''
    fromTypeNode = node.children[0];
    fromTypeNode.typeCheck(progText,typeStack);
    toTypeNode = node.children[1];
    toTypeNode.typeCheck(progText,typeStack);

    fromType = fromTypeNode.type;

    errMsg = None;
    errNodeList = None;
    if not isValueType(fromType):
        # you can only map from Text,TrueFale,or Number to another value.
        errMsg = '\nError declaring function.  A map must map from a TrueFalse, ';
        errMsg += 'Text, or Number to any other type.  You are mapping from ';
        errMsg += 'a non-value type: ' + fromType + '.\n';
        errNodeList = [node,fromTypeNode];

    toType = toTypeNode.type;
    return buildMapTypeSignatureFromTypeNames(fromType,toType), errMsg,errNodeList;

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
    returner[JSON_TYPE_FIELD] = TYPE_FUNCTION;

    
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
                    JSON_TYPE_FIELD: typeNode.type
                    };
                inputTypes.append(toAppend);
                
    returner[JSON_FUNC_IN_FIELD] = inputTypes;

    ##### HANDLE OUTPUT ARGS #####
    outArgNode = node.children[1];
    outArgNode.typeCheck(progText,typeStack);
    if (isTemplatedType(outArgNode.type)):
        returner[JSON_FUNC_RETURNS_FIELD] = json.loads(outArgNode.type);
    else:
        returner[JSON_FUNC_RETURNS_FIELD] = {
            JSON_TYPE_FIELD: outArgNode.type
            };

    return returner;

