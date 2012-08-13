#!/usr/bin/env python

import sys;
import os;

curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'..','bin'));

import head;
from slicer import slicer;
from slicer import reset;

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
    # ensures that we reset the name type tuple id between runs.
    reset();
    
    outputErrStream = StreamObj();
    rootNode = head.lexAndParse(progText,outputErrStream,2);

    if rootNode == None:
        print('\nErrors encountered\n');
        print (outputErrStream.flush());
        return;

    fDeps = slicer(rootNode);

    # turn fDeps into a dictionary
    allDepsDict = {};
    for dep in fDeps:
        allDepsDict[dep.funcName] = dep;

    toPrint = '\n\n';
    for dep in fDeps:
        toPrint += dep.jsonize(allDepsDict);
        toPrint += '\n\n';

    toPrint += '\n\n\n';
    return toPrint;
    
    
def run (filename):
    filer = open(filename,'r');
    progText = filer.read();
    filer.close();
    print(runText(progText));
        
        
if __name__ == '__main__':
    run(sys.argv[1]);
