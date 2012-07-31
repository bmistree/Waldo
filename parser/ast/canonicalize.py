#!/usr/bin/python

# Pre-type checking processing on ast to make it easier to type check.
#
#    * Rule is that any argument passed into message sequence ends
#      up in global section of message sequence.  Copy argument names
#      from message send sequence into sequence global names
#

from astNode import *;
from astLabels import *;

def preprocess(astNode,progText):
    '''
    @param {AstNode} astNode --- Root of ast.
    
    Runs through all the sequences provided and copies the
    declarations for the arguments passed into sendMessage function
    into shared arguments for sequence.

    All changes to astNode happen through reference.
    '''
    sequencesSection = astNode.children[6];
    endPt1Section = astNode.children[4];
    endPt2Section = astNode.children[5];
    sharedSection = astNode.children[3];
    tracesSection = astNode.children[2];

    for sequence in sequencesSection.children:
        copyPassedInToSeqShared(sequence);


def copyPassedInToSeqShared(seqNode):
    seqGlobs = seqNode.children[1];
    
    seqFunctions = seqNode.children[2];
    msgSendFunction = seqFunctions.children[1];
    msgSendArgs = msgSendFunction.children[2];
    for funcDeclArg in msgSendArgs.children:
        newGlob = AstNode(AST_DECLARATION,funcDeclArg.lineNo,funcDeclArg.linePos);
        newGlob.addChildren(funcDeclArg.getChildren());
        seqGlobs.addChild(newGlob);

        
