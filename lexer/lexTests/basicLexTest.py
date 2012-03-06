#!/usr/bin/python
import sys;
sys.path.append('../');

import waldoLex;


def runBasic():
    print('\n\n');
    lexer = waldoLex.constructLexer();
    
    lexer.input("CH32 COOH")
    for tok in iter(lexer.token, None):
        print repr(tok.type), repr(tok.value)
    print('\n\n');
        

if __name__== '__main__':
    runBasic();
