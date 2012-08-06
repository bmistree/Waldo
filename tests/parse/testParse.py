#!/usr/bin/env python

import sys;
import os;
TEST_FOLDER_NAME = 'examples';

curPath = os.path.dirname(__file__);

binPath = os.path.join(curPath,'..','..','bin');
sys.path.append(binPath);
import head;


sys.path.append(os.path.join(curPath,'..','util'));
import testCommon;


def printUsage():
    usageMsg = '\n\n\t./testParse.py goes into examples folder and attempts ';
    usageMsg += 'to lex and parse all of the files with the .wld extension within it.  ';
    usageMsg += 'It then compares the parsed output with the .out version of the ';
    usageMsg += 'file.  Ie, it would parse test1.wld and compare the parsed output with ';
    usageMsg += 'test1.wld.out.  If they agree, pass.  If they do not, then fail.\n';
    print(usageMsg);


class FileLike(object):
    def __init__(self):
        self.msg = '';
    def write(self,msg):
        self.msg += msg;
    def flush(self):
        returner = self.msg;
        self.msg = '';
        return returner;
        
    
def parseTestToRun(progText):
    outputStream = FileLike();
    head.lexAndParse(progText, outputStream, 2);
    return outputStream.flush();
    

if __name__ == '__main__':
    if len(sys.argv) != 1:
        printUsage();
    else:
        testCommon.runTests(parseTestToRun,TEST_FOLDER_NAME);
        
