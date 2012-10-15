#!/usr/bin/env python

import sys;
import os;

from emitUtils import EmitContext

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;

# so can get slicer code
sys.path.append(os.path.join(curDir,'..','..','slice')); # so can get at slicer
from slicer import slicer;
from typeStack import TypeStack;

from uniformHeader import uniformHeader;
from eventDependencies import specifyDependencies;
from emitEndpoints import emitEndpoints;
from onCompleteDict import specifyOnCompleteDict;

def astEmit(astRootNode,emitContext=None):
    '''
    @pararm {AstNode} astRootNode --- The root node of the ast that
    was generated from the source text after it has been type checked,
    but before it has been sliced.

    @param {EmitContext object} emitContext --- @see class EmitContext
    in emitUtils.py
    
    @returns {String or None} ---- String if succeeded, none if
    failed.
    '''

    if emitContext == None:
        emitContext = EmitContext(False)
    
    ####### slice the ast
    fdepArray = slicer(astRootNode);

    fdepDict = {};
    # conver the array of function dependencies to a dict
    for fdep in fdepArray:
        fdepDict[fdep.funcName] = fdep;

        
    ###### start emitting code

    # all Waldo files start the same way, regardless of contents
    returner = uniformHeader();

    # create the _PROTOTYPE_EVENTS_DICT based on the dependencies that
    # the slicer created
    returner += specifyDependencies(fdepDict);

    # now actually emit each endpoint object (including user-defined
    # functions specified in program source text).
    returner += emitEndpoints(astRootNode,fdepDict,emitContext);

    # now emit the oncomplete dict
    returner += specifyOnCompleteDict(astRootNode);
    
    return returner;

