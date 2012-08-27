#!/usr/bin/env python
import sys;
import os;
import emitUtils;

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;

# so can get type checking helper functions to determine types
sys.path.append(os.path.join(curDir,'..','..','parser','ast','typeCheck'));
import templateUtil;

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
