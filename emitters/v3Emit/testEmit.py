#!/usr/bin/env python

import sys;
import os;
import astEmit;


curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','..','bin'));

import head;


class StreamObj(object):
    def __init__(self):
        self.msg = '';
    def write(self,msg):
        self.msg += msg;
    def flush(self):
        msg = self.msg;
        self.msg = '';
        return msg;

    
def runText(progText):
    outputErrStream = StreamObj();
    rootNode = head.lexAndParse(progText,outputErrStream,2);

    if rootNode == None:
        print('\nErrors encountered\n');
        print (outputErrStream.flush());
        return;

    return astEmit.astEmit(rootNode);

def run(srcFilename,compiledFilename):
    filer = open(srcFilename,'r');
    progText = filer.read();
    filer.close();

    compiled = runText(progText);
    if compiled == None:
        print('\nERROR COMPILING\n');
    else:
        filer = open(compiledFilename,'w');
        filer.write(compiled);
        filer.flush();
        filer.close();


if __name__ == '__main__':
    run(sys.argv[1],sys.argv[2]);
