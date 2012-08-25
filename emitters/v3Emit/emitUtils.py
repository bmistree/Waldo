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

