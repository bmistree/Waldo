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
    return toPrint,rootNode;
    
    
def run (filename,graphicalOutputFilename):
    '''
    @param {String} filename
    
    @param {string} graphicalOutputFilename --- None if we are not
    supposed to output an html file with ast tree (including slice
    labels).  If we are, it's a string with information on where to
    output to.
    '''
    filer = open(filename,'r');
    progText = filer.read();
    filer.close();
    textToPrint,astRoot = runText(progText);
    print(textToPrint);

    if graphicalOutputFilename != None:
        astRoot.drawPretty(graphicalOutputFilename,
                           '../parser/ast/d3/',   # FIXME: hard coded path to d3 from here
                           3000,
                           2000);
        
        
if __name__ == '__main__':

    filename = sys.argv[1];
    graphical = None;
    if len(sys.argv) == 3:
        graphical = sys.argv[2];
        
    run(filename,graphical);
