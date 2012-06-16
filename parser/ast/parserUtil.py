#!/usr/bin/python

import sys;
from  astLabels import *;


OutputErrsTo = sys.stderr;

def isFunctionType(typeLabel):
    '''
    Nodes can have many different type labels.  Some are specified by
    strings (mostly nodes with basic types, eg. Number, String, etc.).

    Nodes for user-defined function types do not just have one
    annotation, but rather a json-ized type.  To check if a node's
    label is one of these user-defined function types, we check to
    exclude all of the other types it could be.

    Returns true if it is a user-defined function type, false otherwise.
    
    '''
    if ((typeLabel != TYPE_BOOL) and (typeLabel != TYPE_NUMBER) and
        (typeLabel != TYPE_STRING) and (typeLabel != TYPE_INCOMING_MESSAGE) and
        (typeLabel != TYPE_OUTGOING_MESSAGE) and (typeLabel != TYPE_NOTHING)):
        return True;

    return False;



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


