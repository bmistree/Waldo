#!/usr/bin/python

import sys;
import os;
# sys.path.append(os.path.join('..','..','parser','ast'));
astParserPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','parser','ast');
sys.path.insert(0, astParserPath);
from astBuilder import getParser;
from astBuilder import getErrorEncountered;
from astBuilder import resetErrorEncountered;

from astNode import WaldoTypeCheckException;

import json;
astEmitPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),'..', 'emitters','pyEmit');
sys.path.insert(0, astEmitPath);
import astEmit;


class GraphicalOutArg():
    def __init__(self,jsonDict):
        ##checks before hand if have file in dict, and if don't throws exception.
        self.outFile = jsonDict['file'];
        self.width = jsonDict.get('w',None);
        self.height = jsonDict.get('h',None);
        self.d3 = jsonDict.get('d3','../parser/ast/d3');


def getFileText(inputFile):
    filer = open(inputFile,'r');
    returner = '';
    for s in filer:
        returner += s;
    filer.close();
    return returner;


def runTests():
    print('Still to fill in');


def genAstFromFile(inputFilename,outputErrsTo):
    fileText = getFileText(inputFilenameArg);
    return genAst(fileText,outputErrsTo);


def astProduceTextOutput(astNode,textOutFilename):
    astNode.printAst(textOutFilename);
    return astNode;

def astProducePrintOutput(astNode):
    astNode.printAst();
    return astNode;

def astProduceGraphicalOutput(astNode,graphOutArg):
    '''
    @param graphOutArg is of type class GraphicalOutArg
    '''
    astNode.drawPretty(graphOutArg.outFile,graphOutArg.d3,graphOutArg.width,graphOutArg.height);
    return astNode;


def genAst(progText,outputErrsTo):
    parser = getParser(progText,outputErrsTo);
    astNode = parser.parse(progText);
    return astNode,progText;

def compileText(progText,outputErrStream):
    '''
    Mostly will be used when embedding in another project.  
    
    @param {String} progText -- The source text that we are trying to
    compile.

    @param{File-like object} outputErrStream -- The stream that we should use to output
    error messages to.

    @returns {String or None} -- if no errors were encountered,
    returns the compiled source of the file.  If compile errors were
    encountered, then returns None.
    '''

    astRootNode, other = genAst(progText,outputErrStream);
    if (astRootNode == None):
        # means there was an error
        resetErrorEncountered();
        return None;

    try:
        astRootNode.typeCheck(progText);
    except WaldoTypeCheckException as excep:
        resetErrorEncountered();
        return None;

    
    if (getErrorEncountered()):
        resetErrorEncountered();

        
        # means there was a type error.  should not continue.
        return None;

    resetErrorEncountered();
    emitText = astEmit.runEmitter(astRootNode,None,outputErrStream);
    return emitText; # will be none if encountered an error during
                     # emit.  otherwise, file text.


        
def handleArgs(inputFilename,graphicalOutputArg,textOutputArg,printOutputArg,typeCheckArg,emitArg):
    errOutputStream = sys.stderr;
    
    ast,fileText = genAstFromFile(inputFilename,errOutputStream);
    if (ast == None):
        print >> errOutputStream, '\nError with program.  Please fix and continue\n';
    else:
        performedOperation = False;
        if (textOutputArg != None):
            astProduceTextOutput(ast,textOutputArg);
            performedOperation = True;
        if (printOutputArg != None):
            astProducePrintOutput(ast);
            performedOperation = True;
        if(graphicalOutputArg != None):
            astProduceGraphicalOutput(ast,graphicalOutputArg);
            performedOperation = True;

        
        if(typeCheckArg):
            try:
                ast.typeCheck(fileText);
            except WaldoTypeCheckException as excep:
                pass;

            
        if (emitArg != None):
            
            if (getErrorEncountered()):
                # do not emit any code if got a type error when tyring
                # to compile.
                errMsg = '\nType error: cancelling code emit\n';
                print >> errOutputStream, errMsg;
            else:
                emitText = astEmit.runEmitter(ast,None,errOutputStream);
                if (emitText == None):
                    errMsg = '\nBehram error when requesting emission of ';
                    errMsg += 'source code from astHead.py.\n';
                    print >> errOutputStream, errMsg;
                    assert(False);
                
                filer = open(emitArg,'w');
                filer.write(emitText);
                filer.flush();
                filer.close();






def parseGraphicalOutputArg(goJSON):
    '''
    @param {String} in form of JSON_OBJECT in printUsage.
    @throws exception if incorrectly formatted.
    @returns GraphicalOutArg object
    '''
    pyDict = json.loads(goJSON);

    if (pyDict.get('file',None) == None):
        printUsage();
        assert(False);

    return GraphicalOutArg(pyDict);



def printUsage():
    print(    '''
    -f <filename> input file to generate ast for.

    -go <JSON_OBJECT> (go = graphical output).

    JSON_OBJECT
    {
       file: <filename to output to>,
       d3: (optional) <path to d3 so output html can link to it>,
       h: (optional) <int> height of image to be drawn onto output html (default 1000),
       w: (optional) <int> width of image to be drawn onto output html (default 1000)

    }
    
    -tc  (optional) true/false whether to type check the function or not. defaults to True.

    -to <filename> spits printed json ast out. (text out)

    -p print the json ast directly to screen

    -h print options

    -e <filename> Emit the generated code to filename

    no args ... run ast tests
    
    ''');



    
if __name__ == '__main__':

    inputFilenameArg = None;
    graphicalOutputArg = None;
    textOutputArg = None;
    helpArg = None;
    printOutputArg = None;
    emitArg = None;
    typeCheckArg = True;
    skipNext = False;

    
    
    for s in range(0,len(sys.argv)):
        if (skipNext):
            skipNext = False;
            continue;

        if (sys.argv[s] == '-f'):
            if (s + 1< len(sys.argv)):
                inputFilenameArg =  sys.argv[s+1];
                skipNext = True;
            else:
                #will force printing usage without doing any work.
                helpArg = True;
                
        if (sys.argv[s] == '-go'):
            if (s+1 < len(sys.argv)):
                graphicalOutputArg = parseGraphicalOutputArg(sys.argv[s+1]);
                skipNext = True;
            else:
                #will force printing usage without doing any work.
                helpArg = True;

        if (sys.argv[s] == '-tc'):
            if (s+1 < len(sys.argv)):
                
                typeCheckArg = sys.argv[s+1];
                skipNext = True;
                if((typeCheckArg == 'true') or (typeCheckArg == 'True')):
                    typeCheckArg = True;
                elif((typeCheckArg == 'false') or (typeCheckArg == 'False')):
                    typeCheckArg = False;
                else:
                    helpArg = True;
                    print('\nCannot parse type check option.\n');
                    break;

                
        if (sys.argv[s] == '-to'):
            if (s+1 < len(sys.argv)):
                textOutputArg = sys.argv[s+1];
                skipNext = True;
            else:
                #will force printing usage without doing any work.
                helpArg = True;

        if (sys.argv[s] == '-h'):
            helpArg = True;

        if (sys.argv[s] == '-p'):
            printOutputArg = True;

        if (sys.argv[s] == '-e'):
            if (s+1 < len(sys.argv)):
                emitArg = sys.argv[s+1]
                skipNext = True;
            else:
                helpArg = True;

            

    if (helpArg):
        printUsage();
    else:
        if (inputFilenameArg == None):
            runTests();
        else:
            handleArgs(inputFilenameArg,graphicalOutputArg,textOutputArg,printOutputArg,typeCheckArg,emitArg);
            
