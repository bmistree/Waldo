#!/usr/bin/python
import sys;
import os;
import difflib;

sys.path.append('../');
import waldoLex;

SUCCESS_FOLDER = 'lexsuccesses/';
WALD_SUFFIX = '.wld';
WALD_OUTPUT = '.out';



def waldoSuffix(toCheck):
    '''
    @returns {bool} True if toCheck ends in ".wld".  False otherwise.
    '''
    if (len(toCheck) >= len(WALD_SUFFIX)):
        if (toCheck[-len(WALD_SUFFIX):] == WALD_SUFFIX):
            return True;

    return False;

    
def runSuccesses():
    successesToRun = [x for x in os.listdir(SUCCESS_FOLDER) if waldoSuffix(x)];

    successLexCheckOutput = '';
    for s in successesToRun:
        passed = False;
        notes = None;
        successLexCheckOutput += '\n\nRunning ' + s + ': ';
        try:
            result = lexFile(os.path.join(SUCCESS_FOLDER,s));
            passed, diffNotes = compareToFile(result,os.path.join(SUCCESS_FOLDER,s+WALD_OUTPUT));
            if (not passed):
                notes += '\n' + diffNotes;
                
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly

            passed = False;

        if(passed):
            successLexCheckOutput += 'PASSED';
        else:
            successLexCheckOutput += 'FAILED';

        if (notes != None):
            successLexCheckOutput += '\nNotes: ' + notes;
            
            
    return successLexCheckOutput;


def compareToFile(lexedOutput,filename):
    '''
    @param {bool} returns true if the output lexedOutput is identical
    to the contents of filename.
    '''
    text = '';
    filer = open(filename,'r');
    for s in filer:
        text += s;

    d = difflib.Differ()
    
    lexedOutput = lexedOutput.rstrip().lstrip();
    text = text.rstrip().lstrip();
    
    lexedNum = lexedOutput.count('\n');
    textNum  = text.count('\n');
    diff = d.compare(lexedOutput.splitlines(lexedNum), text.splitlines(textNum));
    return lexedOutput == text, ''.join(diff)



def runLexTests():
    '''
    Runs all <x>.wld files in SUCCESS_FOLDER and FAILURE_FOLDER,
    testing their output against their previous output
    (<x>.wld.out file).
    '''
    performance = runSuccesses();
    print('\n\n');
    print(performance);
    print('\n\n');
    

    
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
    usageString += '\tno arguments, runs test on existing lex files.\n';
    
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
    if (len(sys.argv) == 1):
        runLexTests();
    else:
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
            
