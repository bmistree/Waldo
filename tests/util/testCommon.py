#!/usr/bin/env python

import os;
import sys;

WALDO_SUFFIX = '.wld';
OUTPUT_SUFFIX = '.out';


def runTests(testToRun,folderName):
    '''
    @param testToRunn @see runWaldoFile
    '''
    for root, dirnames, filenames in os.walk(folderName):
        for filename in filenames:
            if isWaldoFile(filename):
                runWaldoFile(root,filename,testToRun);

def runWaldoFile(folderName, filename,testToRun):
    '''
    @param {String} folderName ---
    
    @param {String} filename --- The filename of a Waldo file (ie, has
    .wld suffix).

    @param {Function} testToRun --- Function that takes a single
    argument (string source text) and outputs a string as a result.
    
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

    strToPrint = '\n';
    strToPrint += filename + '              ';
    if output.lstrip().rstrip() != expectedOutputText.lstrip().rstrip():
        strToPrint += 'FAILED \n\n';
        strToPrint += '\tEXPECTED: \n' + expectedOutputText;
        strToPrint += '\tACTUAL: \n' + output;
    else:
        strToPrint += 'PASSED';
    strToPrint+='\n\n';

    print(strToPrint);
    
    
def isWaldoFile(filename):
    if len(filename) < len(WALDO_SUFFIX):
        return False;

    potentialSuffix = filename[-len(WALDO_SUFFIX):];
    return potentialSuffix == WALDO_SUFFIX;
