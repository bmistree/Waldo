#!/usr/bin/python

import sys;
import json;

OutputErrsTo = sys.stderr;


def setOutputErrorsTo(toOutputTo):
    global OutputErrsTo;
    OutputErrsTo = toOutputTo;

def errPrint(toPrint):
    '''
    @param{String} toPrint
    Outputs toPrint on stderr
    '''
    global OutputErrsTo;
    print >> OutputErrsTo , toPrint;


