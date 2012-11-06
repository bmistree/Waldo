#!/usr/bin/env python

import emitUtils;
import os; 
import sys;

# so can get ast labels
from parser.ast.astLabels import * 


def specifyOnCompleteDict(astRootNode):
    endpointNames = emitUtils.getEndpointNames(astRootNode);
    onCompleteDictValues = {};
    
    for endpointName in endpointNames:
        wrappedOnCompletes = _getOnCompleteSequenceNames(endpointName,astRootNode);

        for wrapped in wrappedOnCompletes:
            endpointName = wrapped.endpointName;
            onCompleteSequenceName = wrapped.sequenceName;

            # note, if change this, must also change name of function
            # in _emitOnComplete method in emitEndpoints.py
            onCompleteFuncName = wrapped.onCompleteNode.sliceAnnotationName;
        
            
            onCompleteKey = "_onCompleteKeyGenerator('" + endpointName + "',";
            onCompleteKey += "'" + onCompleteSequenceName + "')";
            onCompleteValue = onCompleteFuncName;
            
            onCompleteDictValues[onCompleteKey] = onCompleteValue;

    returner = '';
    returner += """
def _onCompleteKeyGenerator(endpointName,sequenceName):
    '''
    For each sequence, we want to be able to lookup its oncomplete
    handler in _OnCompleteDict.  This is indexed by "_EndpointName
    sequenceName".  This function generates that key.

    @param {String} endpointName
    @param {String} sequenceName 
    '''
    return '_' + endpointName + '   ' + sequenceName;


# Maps all message sequence on complete keys to functions that can be
# used to execute them.  a key is generated using the helper
# _onCompleteKeyGenerator functions.  Each function takes in the same
# three default values as a regular internal function (call type,
# active event, and context)
""";
    returner += emitUtils.createDictLiteralAssignment(
        '_OnCompleteDict',onCompleteDictValues);
                                                     
    
    returner += '\n';
    return returner;
    


class _OnCompleteWrapper(object):
    def __init__(self,endpointName,sequenceName,onCompleteNode):
        self.endpointName = endpointName;
        self.sequenceName = sequenceName;
        self.onCompleteNode = onCompleteNode;


def _getOnCompleteSequenceNames(endpointName,astRootNode):

    returner = [];
    
    msgSeqSectionNode = astRootNode.children[6];

    for msgSeqNode in msgSeqSectionNode.children:
        msgSeqNameNode = msgSeqNode.children[0];
        msgSeqName = msgSeqNameNode.value;
        

        seqFuncsNode = msgSeqNode.children[2];

        for msgSeqFuncNode in seqFuncsNode.children:
            endpointIdNode = msgSeqFuncNode.children[0];

            if endpointIdNode.value != endpointName:
                continue;

            if msgSeqFuncNode.label == AST_ONCOMPLETE_FUNCTION:
                returner.append(
                    _OnCompleteWrapper(endpointName,msgSeqName,msgSeqFuncNode));
                
    return returner;


