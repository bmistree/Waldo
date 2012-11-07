#!/usr/bin/env python

import sys;
import os;
TEST_FOLDER_NAME = 'examples';
DETAILS_FILE = 'details.txt';


curPath = os.path.dirname(__file__);

slicePath = os.path.join(curPath,'..','..','slice');
sys.path.append(slicePath);
import testSlicer;


sys.path.append(os.path.join(curPath,'..','util'));
import testCommon;


def printUsage():
    usageMsg = '\n\n\t./testSlice.py goes into examples folder and attempts ';
    usageMsg += 'to slice all of the files with the .wld extension within it.  ';
    usageMsg += 'It then compares the sliced output with the .out version of the ';
    usageMsg += 'file.  Ie, it would lex, parse, and slice test1.wld and compare the sliced output with ';
    usageMsg += 'test1.wld.out.  If they agree, pass.  If they do not, then fail.\n';
    print(usageMsg);


    
def sliceTestToRun(progText):
    outputStream = testCommon.StreamLike();
    return testSlicer.runText(progText);
    

if __name__ == '__main__':
    if len(sys.argv) != 1:
        printUsage();
    else:
        detailsStream = testCommon.StreamLike();
        testCommon.runTests(sliceTestToRun,TEST_FOLDER_NAME,detailsStream);

        # write out the details
        filer = open(DETAILS_FILE,'w');
        filer.write(detailsStream.flush());
        filer.flush();
        filer.close();
        
