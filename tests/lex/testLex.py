#!/usr/bin/env python

import sys;
import os;
TEST_FOLDER_NAME = 'examples';
WALDO_SUFFIX = '.wld';
OUTPUT_SUFFIX = '.out';

curPath = os.path.dirname(__file__);
lexPath = os.path.join(curPath,'..','..','lexer');
sys.path.append(lexPath);
import basicLexTest;


def runTests(toRun):

    for root, dirnames, filenames in os.walk(TEST_FOLDER_NAME):
        for filename in filenames:
            if isWaldoFile(filename):
                runWaldoFile(root,filename,toRun);

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
                
def printUsage():
    usageMsg = '\n\n\t./testLex.py goes into examples folder and attempts ';
    usageMsg += 'to lex all of the files with the .wld extension within it.  ';
    usageMsg += 'It then compares the lexed output with the .out version of the ';
    usageMsg += 'file.  Ie, it would lex test1.wld and compare the lex output with ';
    usageMsg += 'test1.wld.out.  If they agree, pass.  If they do not, then fail.\n';
    print(usageMsg);


if __name__ == '__main__':
    if len(sys.argv) != 1:
        printUsage();
    else:
        runTests(basicLexTest.lexText);
