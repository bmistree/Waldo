#!/usr/bin/env python

import sys;
import os;
import emitUtils;

curDir = os.path.dirname(__file__);

# so can get ast labels
sys.path.append(os.path.join(curDir,'..','..','parser','ast'));
from astLabels import *;

sys.path.append(os.path.join(curDir,'..','..','slice','typeStack'));
from typeStack import TypeStack;


def emit(astNode,fdepDict):
    returner = '';


    if astNode.label == AST_ANNOTATED_DECLARATION:
        # it's a shared variable
        #   shared{ Nothing controls someNum = 0;}
        #   self._committedContext.shareds['1__someNum'];
        identifierNode = astNode.children[2];
        returner += emit(identifierNode,fdepDict);
        
        if len(astNode.children) == 4:
            # means have initialization information
            returner += ' = ';
            returner += emit(astNode.children[3],fdepDict);

    elif astNode.label == AST_IDENTIFIER:
        astNode._debugErrorIfHaveNoAnnotation(
            'mainEmit.emit: identifier');

        idAnnotationName = astNode.sliceAnnotationName;
        idAnnotationType = astNode.sliceAnnotationType;

        if idAnnotationType == TypeStack.IDENTIFIER_TYPE_LOCAL:
            returner += identifierNode.value + ' ';
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL:
            returner += "self._committedContext.endGlobals['";
            returner += idAnnotationName + "'] ";
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL:
            returner += "self._committedContext.seqGlobals['";
            returner += idAnnotationName + "'] ";
        elif idAnnotationType == TypeStack.IDENTIFIER_TYPE_SHARED:
            returner += "self._committedContext.shareds['";
            returner += idAnnotationName + "'] ";            
        else:
            errMsg = '\nBehram error: incorrect annotation type for ';
            errMsg += 'declared variable in emit of mainEmit.\n';
            print(errMsg);
            assert(False);        

    elif astNode.label == AST_DECLARATION:
        # could either be a shared or local variable.  use annotation
        # to determine.
        identifierNode = astNode.children[1];
        returner += emit(identifierNode,fdepDict);
        if len(astNode.children) == 3:
            # includes initialization information
            initializationNode = astNode.children[2];
            returner += ' = ';
            returner += emit(initializationNode,fdepDict);

    elif astNode.label == AST_BOOL:
        returner +=  astNode.value + ' ';
        
    elif astNode.label == AST_STRING:
        returner += "'"  + astNode.value + "' ";
        
    elif astNode.label == AST_NUMBER:
        returner += astNode.value + ' ';
        
    else:
        errMsg = '\nBehram error: emitting for unknown label: ';
        errMsg += astNode.label + '\n';
        print(errMsg);
    


    return returner;
