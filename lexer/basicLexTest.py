#!/usr/bin/python
import sys;
import os;
import difflib;

import waldoLex;



    
def lexFile(filename):
    filer = open(filename, 'r');
    text = '';
    for s in filer:
        text += s;
    filer.flush();
    filer.close();

    lexer = waldoLex.constructLexer();
    lexer.input(text);
    returner = '';
    for tok in iter(lexer.token, None):
        returner += '\n';
        returner += str(tok.type) + '   ' + str(tok.value);
        
    return returner;


def lexFileAndPrint(filename):
    print(lexFile(filename));

def lexStringAndPrint(stringToLex):
    lexer = waldoLex.constructLexer();
    lexer.input(stringToLex)
    for tok in iter(lexer.token, None):
        print (str(tok.type) + '   ' +  str(tok.value));


    
def printUsage():
    '''
    Tells user options for calling this from the command line.
    '''
    usageString = '\nUsage: ';
    
    usageString += '\t-f <filename> prints output of lexer run on ';
    usageString += 'identified by <filename>.\n';
    
    usageString += '\t-s <string> prints output of lexer run on string.\n';

    usageString += '\t-h prints command line options (this).\n';
    print(usageString);


if __name__== '__main__':
    '''
    run ./basicLexTest.py -h for a list of options.
    '''
    #if user specifies no options, just runs command on known lext tests.

    stringArg = None;
    fileArg   = None;
    helpArg   = None;
    skipNext  = False;
    
    for s in range(1,len(sys.argv)):
        if (skipNext):
            skipNext = False;
            continue;
        #can lex just a single input string
        if (sys.argv[s] == '-s'):
            if (s+1 < len(sys.argv)):
                stringArg = sys.argv[s+1];
                skipNext = True;
        #can lex a single input file       
        elif (sys.argv[s] == '-f'):                
            if (s+1 < len(sys.argv)):
                fileArg = sys.argv[s+1];
                skipNext = True;
        elif (sys.argv[s] == '-h'):
            helpArg = True;
        else:
            helpArg = True;


            
    if (helpArg):
        printUsage();
    elif(stringArg != None):
        lexStringAndPrint(stringArg);
    elif(fileArg != None):
        lexFileAndPrint(fileArg);
    else:
        print('\nUnknown input\n');
        printUsage();
            
