#!/usr/bin/env python


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
    


