#!/usr/bin/env python

import os;
import sys;

WALDO_SUFFIX = '.wld';
OUTPUT_SUFFIX = '.out';



class StreamLike(object):
    def __init__(self):
        self.msg = '';
    def write(self,msg):
        self.msg += msg;
    def flush(self):
        returner = self.msg;
        self.msg = '';
        return returner;
        

def runTests(testToRun,folderName,detailsStream):
    '''
    @param testToRunn @see runWaldoFile
    @param detailsStream @see runWaldoFile
    '''
    for root, dirnames, filenames in os.walk(folderName):
        for filename in filenames:
            if isWaldoFile(filename):
                runWaldoFile(root,filename,testToRun,detailsStream);

def runWaldoFile(folderName,filename,testToRun,detailsStream):
    '''
    @param {String} folderName ---
    
    @param {String} filename --- The filename of a Waldo file (ie, has
    .wld suffix).

    @param {Function} testToRun --- Function that takes a single
    argument (string source text) and outputs a string as a result.

    @param {stream} detailsStream --- Should be able to call write,
    close, and flush on this.  writes detailed data to about test
    cases (beyond just test passed/failed).  (Likely just a StreamLike
    object.)
    
    Runs the file folderName/filename through the lexer.  Compares the
    output of doing this with the saved output in file
    folderName/filename.out.  If they agree, then pass.  Otherwise,
    fail.
    '''
    filer = open(os.path.join(folderName,filename),'r');
    progText = filer.read();
    filer.close();

    
    filer = open(os.path.join(folderName,filename + OUTPUT_SUFFIX),'r');
    expectedOutputText = filer.read();
    filer.close();
    output = testToRun(progText);


    toPrintStr = '\n******\n';
    toPrintStr += rightPadWord(filename);
    if output.lstrip().rstrip() != expectedOutputText.lstrip().rstrip():
        toPrintStr += 'FAILED';

        # only the detailed stream will output the reason for failure
        detailsStream.write(toPrintStr);
        detailsStream.write(
            indentString('\nEXPECTED\n',1) + indentString(expectedOutputText,2));

        detailsStream.write(
            indentString('ACTUAL\n',1) + indentString(output,2));
    else:
        toPrintStr += 'PASSED';
        detailsStream.write(toPrintStr);

    endingLine = '';
    toPrintStr +=endingLine
    detailsStream.write(endingLine + '\n');
    print(toPrintStr);


def indentString(string,indentAmount):
    '''
    @param {String} string -- Each line in this string we will insert
    indentAmount number of tabs before and return the new, resulting
    string.
    
    @param {Int} indentAmount ---- Inserts a tab for each integer.

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

    
LINE_WIDTH = 60;
def rightPadWord(word):
    '''
    Inserts spaces after the word until the full width of the line is
    LINE_WIDTH
    '''
    # should also handle case where word is longer than LINE_WIDTH
    for counter in range(0,LINE_WIDTH - len(word)):
        word += ' ';
    return word;
    
            
    
def isWaldoFile(filename):
    if len(filename) < len(WALDO_SUFFIX):
        return False;

    potentialSuffix = filename[-len(WALDO_SUFFIX):];
    return potentialSuffix == WALDO_SUFFIX;
