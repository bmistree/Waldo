#!/usr/bin/env python

import sys;
import os;
import astEmit;


curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','..','bin'));

import head;
from emitUtils import EmitContext;


DEBUG_COLLISIONS_FLAG = '-c';
INPUT_FILENAME_FLAG = '-f';
EMIT_FILENAME_FLAG = '-e';


class StreamObj(object):
    def __init__(self):
        self.msg = '';
    def write(self,msg):
        self.msg += msg;
    def flush(self):
        msg = self.msg;
        self.msg = '';
        return msg;

    
def runText(progText,emitContext):
    outputErrStream = StreamObj();
    rootNode = head.lexAndParse(progText,outputErrStream,2);

    if rootNode == None:
        print('\nErrors encountered\n');
        print (outputErrStream.flush());
        return;

    return astEmit.astEmit(rootNode,emitContext);

def run(srcFilename,compiledFilename,emitContext):
    filer = open(srcFilename,'r');
    progText = filer.read();
    filer.close();

    compiled = runText(progText,emitContext);
    if compiled == None:
        print('\nERROR COMPILING\n');
    else:
        filer = open(compiledFilename,'w');
        filer.write(compiled);
        filer.flush();
        filer.close();



def printUsage():
    printStr = '\n\nUsage: \n\n'
    printStr += './testEmit.py  <options>\n';
    printStr += '\t REQUIRED:\n';
    printStr += '\t\t-f <waldo filename to compile>\n';
    printStr += '\t\t-e <name of file to emit to>\n';
    printStr += '\t OPTIONAL:\n';
    
    printStr += '\t\t-c  : Add in time sleeps after message sequences ';
    printStr += 'return to help debug transaction collisions\n\n';

    print(printStr);

    

        
if __name__ == '__main__':

    inputFilename = None;
    toEmitToFilename = None;
    debugCollisionsFlag = False;

    skipNext = False;
    counter = 0;
    for clArg in sys.argv:
        counter += 1;
        
        if skipNext:
            skipNext = False;
            continue;

        if clArg == DEBUG_COLLISIONS_FLAG:
            debugCollisionsFlag = True;
        elif clArg == INPUT_FILENAME_FLAG:
            if len(sys.argv) == counter:
                printUsage();
                break;
            inputFilename = sys.argv[counter];
            skipNext = True;
        elif clArg == EMIT_FILENAME_FLAG:
            if len(sys.argv) == counter:
                printUsage();
                break;
            toEmitToFilename = sys.argv[counter];
            skipNext = True;            
        

    if (inputFilename == None) or (toEmitToFilename == None):
        printUsage();
    else:
        run(inputFilename,toEmitToFilename,EmitContext(debugCollisionsFlag));

    
