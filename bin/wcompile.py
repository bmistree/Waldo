#!/usr/bin/env python

import sys, os


base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.insert(0, base_path)

import waldo.parser
import waldo.parser.ast.canonicalize as canonicalize
from waldo.parser.ast.astBuilder import getParser as v2GetParser
from waldo.parser.ast.astBuilder import getErrorEncountered as v2GetErrorEncountered
from waldo.parser.ast.astBuilder import resetErrorEncountered as v2ResetErrorEncountered

def getParser(suppress_warnings,progText,outputErrsTo,versionNum):
    return v2GetParser(suppress_warnings,progText,outputErrsTo);

def getErrorEncountered(versionNum):
    return v2GetErrorEncountered();

def resetErrorEncountered(versionNum):
    return v2ResetErrorEncountered();

import re
import json
from waldo.emitters.v4Emit.emitter import ast_emit as v4Emit


from waldo.parser.ast.astBuilder import WaldoParseException;
from waldo.lexer.waldoLex import WaldoLexException


def getEmitter(versionNum):
    return v4Emit



class GraphicalOutArg():
    def __init__(self,jsonDict):
        # checks before hand if have file in dict, and if don't throws
        # exception.
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
    returner = stripWindowsLineEndings(returner);
    return returner;

def stripWindowsLineEndings(textToStripFrom):
    return re.sub(r'\r','',textToStripFrom)


def genAstFromFile(inputFilename,outputErrsTo,versionNum,suppress_warnings):
    fileText = getFileText(inputFilenameArg);
    return genAst(fileText,outputErrsTo,versionNum,suppress_warnings);

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

def genAst(progText,outputErrsTo,versionNum,suppress_warnings):
    '''
    @param {bool} suppress_warnings --- True if we tell the parser not
    to emit parsing warnings, False otherwise.
    '''
    progText = stripWindowsLineEndings(progText)
    parser = getParser(suppress_warnings,progText,outputErrsTo,versionNum)
    astNode = parser.parse(progText)
    if versionNum == 1:
        pass;
    elif (versionNum == 2) or (versionNum == 4): 
        if (not getErrorEncountered(versionNum)):
            canonicalize.preprocess(astNode,progText);
    else:
        print('\nError, no version information provided\n');
        assert(False);
    return astNode,progText

def compileText(progText,outputErrStream,versionNum,suppress_warnings):
    '''
    Mostly will be used when embedding in another project.  
    
    @param {String} progText -- The source text that we are trying to
    compile.

    @param{File-like object} outputErrStream -- The stream that we
    should use to output error messages to.

    @param {Int} versionNum 1 or 2.
    
    @returns {String or None} -- if no errors were encountered,
    returns the compiled source of the file.  If compile errors were
    encountered, then returns None.
    '''
    astRootNode = lexAndParse(
        progText,outputErrStream,versionNum,suppress_warnings)
    if astRootNode == None:
        return None;
    
    resetErrorEncountered(versionNum);
    emitText = getEmitter(versionNum).astEmit(astRootNode)
    return emitText; # will be none if encountered an error during
                     # emit.  otherwise, file text.


def lexAndParse(progText,outputErrStream,versionNum,suppress_warnings):
    '''
    Returns None if there was an error (either in lexing, parsing, or
    type checking).  Returns astRootNode if there was not an error.
    '''
    try:
        astRootNode, other = genAst(
            progText,outputErrStream,versionNum,suppress_warnings)
    except WaldoLexException as excep:
        print >> outputErrStream, excep.value;
        return None;
    except WaldoParseException as excep:
        print >> outputErrStream, excep.value;
        return None;
    except waldo.parser.ast.typeCheck.typeCheckUtil.WaldoTypeCheckException as excep:
        print >> errOutputStream, excep.value;
        return None;

    
    if (astRootNode == None):
        # means there was an error
        resetErrorEncountered(versionNum);
        return None;

    try:
        astRootNode.typeCheck(progText);
    except waldo.parser.ast.typeCheck.typeCheckUtil.WaldoTypeCheckException as excep:
        resetErrorEncountered(versionNum);
        return None;

    
    if (getErrorEncountered(versionNum)):
        resetErrorEncountered(versionNum);
        # means there was a type error.  should not continue.
        return None;

    # no error
    return astRootNode;

        
def handleArgs(
    inputFilename,graphicalOutputArg,textOutputArg,printOutputArg,
    typeCheckArg,emitArg,versionNum,suppress_warnings):

    errOutputStream = sys.stderr;

    try:
        astRootNode,fileText = genAstFromFile(
            inputFilename,errOutputStream,versionNum,suppress_warnings)
    except WaldoLexException as excep:
        print >> errOutputStream, excep.value;
        return;
    except WaldoParseException as excep:
        print >> errOutputStream, excep.value;
        return;
    except waldo.parser.ast.typeCheck.typeCheckUtil.WaldoTypeCheckException as excep:
        print >> errOutputStream, excep.value;
        return;
    
    if (astRootNode == None):
        print >> errOutputStream, '\nError with program.  Please fix and continue\n';
    else:
        performedOperation = False;
        if (textOutputArg != None):
            astProduceTextOutput(astRootNode,textOutputArg);
            performedOperation = True;
        if (printOutputArg != None):
            astProducePrintOutput(astRootNode);
            performedOperation = True;
        if(graphicalOutputArg != None):
            astProduceGraphicalOutput(astRootNode,graphicalOutputArg);
            performedOperation = True;

        
        if(typeCheckArg):
            try:
                astRootNode.typeCheck(fileText)
            except waldo.parser.ast.typeCheck.typeCheckUtil.WaldoTypeCheckException as excep:
                pass;
                
        if (emitArg != None):
            
            if (getErrorEncountered(versionNum)):
                # do not emit any code if got a type error when tyring
                # to compile.
                errMsg = '\nType error: cancelling code emit\n';
                print >> errOutputStream, errMsg;
            else:
                emitText = getEmitter(versionNum).astEmit(astRootNode)
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

    -e <filename> Emit the generated code to filename.  

    -ne No emit: don't emit 

    -w Turn parse and lex warnings on.  Otherwise, they are off.

    single arg (filename) .... try compiling the file to emitted.py

    
    ''');

    
if __name__ == '__main__':

    inputFilenameArg = None;
    graphicalOutputArg = None;
    textOutputArg = None;
    helpArg = None;
    printOutputArg = None;
    emitArg = 'emitted.py'
    typeCheckArg = True
    skipNext = False
    versionNum = 4
    suppress_warnings = True
    
    for s in range(0,len(sys.argv)):
        if (skipNext):
            skipNext = False;
            continue;

        if (sys.argv[s] == '-f'):
            if (s + 1< len(sys.argv)):
                inputFilenameArg = sys.argv[s+1];
                skipNext = True;
            else:
                # will force printing usage without doing any work.
                helpArg = True;

        if sys.argv[s] == '-ne':
            emitArg = None

        if sys.argv[s] == '-w':
            suppress_warnings = False

            
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

            
    if inputFilenameArg == None:
        if len(sys.argv) == 2:
            inputFilenameArg = sys.argv[1]
            emitArg = 'emitted.py'
                
    if (helpArg):
        printUsage();
    else:
        if (inputFilenameArg == None):
            printUsage()
        else:
            handleArgs(
                inputFilenameArg,graphicalOutputArg,textOutputArg,
                printOutputArg,typeCheckArg,emitArg,versionNum,suppress_warnings)
            
