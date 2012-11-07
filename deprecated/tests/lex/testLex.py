#!/usr/bin/env python

import sys;
import os;
TEST_FOLDER_NAME = 'examples';
DETAILS_FILE = 'details.txt';

curPath = os.path.dirname(__file__);
lexPath = os.path.join(curPath,'..','..','lexer');
sys.path.append(lexPath);
import basicLexTest;

sys.path.append(os.path.join(curPath,'..','util'));
import testCommon;


def printUsage():
    usageMsg = '\n\n\t./testLex.py goes into examples folder and attempts ';
    usageMsg += 'to lex all of the files with the .wld extension within it.  ';
    usageMsg += 'It then compares the lexed output with the .out version of the ';
    usageMsg += 'file.  Ie, it would lex test1.wld and compare the lex output with ';
    usageMsg += 'test1.wld.out.  If they agree, pass.  If they do not, then fail.\n';
    print(usageMsg);


if __name__ == '__main__':
    if len(sys.argv) != 1:
        printUsage();
    else:
        detailsStream = testCommon.StreamLike();
        testCommon.runTests(basicLexTest.lexText,TEST_FOLDER_NAME,detailsStream);

        # write out the details
        filer = open(DETAILS_FILE,'w');
        filer.write(detailsStream.flush());
        filer.flush();
        filer.close();
