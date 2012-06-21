#!/usr/bin/python

# Takes a version 2 ast and turns it into a version 1 ast for type
# checking and emitting.

from astNode import *;

INCOMING_MESSAGE_NAME = 'Number'; # overloading incoming message with
                                  # something that we know will never
                                  # be used because it's a reserved
                                  # word.

OUTGOING_MESSAGE_NAME = 'Text';   # overloading outgoing message with
                                  # something that we know will never
                                  # be used because it's a reserved
                                  # word.

  
def v2ToV1Ast(astNode,progText):
    '''
    @param {AstNode} astNode --- Root of the version 2 ast.
    
    Biggest difference between each ast is that the version 2 ast has
    a separate section for each sequence of messages.  Version 1
    instead places the functions within the endpoint sections
    themselves.  Need to take the version 2 ast and create separate
    send and receive message functions for each.  Importantly, need to
    construct message sends in such a way that all sequence global
    information is transmitted and re-referenced appropriately using
    messaging functions.

    All changes to astNode happen through reference.
    '''
    sequencesSection = astNode.children[6];
    endPt1Section = astNode.children[4];
    endPt2Section = astNode.children[5];
    sharedSection = astNode.children[3];
    tracesSection = astNode.children[2];

    v2TypeCheck(sequencesSection,tracesSection,sharedSection,endPt1Section,endPt2Section,progText);
    
    for sequence in sequencesSection.children:
        updateWithMsgSequence(sequence,endPt1Section,endPt2Section,progText);
        
    del astNode.children[6];


def v2TypeCheck(sequencesSection,tracesSection,sharedSection,endPt1Section,endPt2Section,progText):
    '''
    Performs four types of v2-specific type checking, throwing errors if needed:
    
      1: Checks that sequence global variable names do not interfere with
         endpoint globals or shared variables.
      
      2: Checks that labels for traces do not interfere with endpoints.

      3: Checks that each trace line has a sequence section.

      4: Checks that no sequence section exists that does not have a trace line.
    '''
    
    # build a dict of sequence global variable names
    seqGlobNamesDict =  {};


    filledInSequenceNames = {};
    for sequence in sequencesSection.children:
        sequenceName = sequence.children[0].value;
        filledInSequenceNames[sequenceName] = sequence;
        seqGlobSection = sequence.children[1];
        for seqGlobNode in seqGlobSection.children:
            name = seqGlobNode.children[1].value;
            seqGlobNamesDict[name] = seqGlobNode;

            
    # check through the endpoint globals
    for sharedItemNode in sharedSection.children:
        #sharedItemNode is of type annotatedDeclaration
        name = sharedItemNode.children[2].value;
        
        if name in seqGlobNamesDict:
            # means that there is a naming conflict between sequence
            # global and full-file global: throw error
            conflictNode = seqGlobNamesDict[name];
            
            errMsg = '\nError.  You declared "' + name + '" to be ';
            errMsg += 'a globally shared variable, but then re-declared ';
            errMsg += 'it to be shared during a message sequence.  Either ';
            errMsg += 're-name or delete one.\n';
            errorFunction(errMsg,[conflictNode,sharedItemNode],[conflictNode.lineNo,sharedItemNode.lineNo],progText);      

    # check through the endpoint globals.
    v2TypeCheckEndPtGlobs(seqGlobNamesDict,endPt1Section,progText);
    v2TypeCheckEndPtGlobs(seqGlobNamesDict,endPt2Section,progText);

    endPt1Name = endPt1Section.children[0].value;
    endPt2Name = endPt2Section.children[0].value;
    
    # check that labels for traces do not interfere with endpoints
    traceLineNames = {};
    for traceLineNode in tracesSection.children:
        traceLineName = traceLineNode.children[0].value;
        traceLineNames[traceLineName] = traceLineNode;
        conflictNode = None;
        if (traceLineName == endPt1Name):
            conflictNode = endPt1Section;
        elif(traceLineName == endPt2Name):
            conflictNode = endPt2Section;

        if (conflictNode != None):
            # means that one of the trace lines has the same name as
            # an endpoint.  emit error.
            errMsg = '\nError.  You declared both a trace line and an ';
            errMsg += 'endpoint to have the same name: "' + traceLineName + '".  ';
            errMsg += 'Either re-name or delete one.\n';
            errorFunction(errMsg,[conflictNode,traceLineNode],[conflictNode.lineNo,traceLineNode.lineNo],progText);


    ######CHECK that each trace line has a sequence section
    for traceName in traceLineNames.keys():
        if not (traceName in filledInSequenceNames):
            # specified a trace without specifying its sequence.
            errMsg = '\nError.  You specified a trace with name "' +traceName + '" ';
            errMsg += 'without filling in its associated sequence.\n';
            traceNode = traceLineNames[traceName];
            errorFunction(errMsg,[traceNode],[traceNode.lineNo],progText);
            
    ######CHECK that each sequence section has a matching trace line
    for sequenceName in filledInSequenceNames.keys():
        if not (sequenceName in traceLineNames):
            # specified a sequence without specifying its trace line
            errMsg = '\nError.  You specified a message sequence block "' +sequenceName + '" ';
            errMsg += 'without filling in its associated trace line.\n';
            sequenceBlockNode = filledInSequenceNames[sequenceName];
            errorFunction(errMsg,[sequenceBlockNode],[sequenceBlockNode.lineNo],progText);
            
            
    # if got to this point, then no error.


            

def v2TypeCheckEndPtGlobs(seqGlobNamesDict,endPtSec,progText):
    '''
    @param {dict<String,AstNode>} seqGlobNamesDict --- Keys are the
    names of the declared functions, values are the Declaration
    AstNodes in the sequences section that are associated with the
    sequences-global variable.

    @param {AstNode} endPtSec --- Endpoint section to check through to
    see if its global variables interfere with the sequence's global
    variables.

    Runs through the endpoint, checking to ensure that the endpoint's
    global variables do not collide with the sequence's globals.
    '''
    if (len(endPtSec.children) != 2):
        return;
    if (len(endPtSec.children[1].children) == 0):
        return;
        
    endPtGlobs = endPtSec.children[1].children[0];
    endPtName = endPtSec.children[0].value;

    for globNode in endPtGlobs.children:
        # globNode is a Declaration
        name = globNode.children[1].value;
        if name in seqGlobNamesDict:
            conflictNode = seqGlobNamesDict[name];
            
            errMsg = '\nError.  You declared "' + name + '" to be ';
            errMsg += 'a variable for your endpoint named "' + endPtName;
            errMsg += '", but then re-declared ';
            errMsg += 'it to be shared during a message sequence.  Either ';
            errMsg += 're-name or delete one.\n';
            errorFunction(errMsg,[conflictNode,globNode],[conflictNode.lineNo,globNode.lineNo],progText);      
    
                                     
def updateWithMsgSequence(sequence,endPt1Section,endPt2Section,progText):
    '''
    @param{AstNode} sequence --- A node of type AST_MESSAGE_SEQUENCE
    @param{AstNode} endPt1Section --- A node of type AST_ENDPOINT
    @param{AstNode} endPt2Section --- A node of type AST_ENDPOINT

    Takes sequence node, creates message send and message receive
    nodes out of it, and then appends those nodes to the relevant
    parts of the endpoint ast nodes.

    Also, inserts send statement at end of each of the created message
    functions.  Also ensures that sequence global variables are
    referenced through message functions.
    '''
    seqGlobalsNode = sequence.children[1];
    seqFunctionsNode = sequence.children[2];

    endPt1Name = endPt1Section.children[0].value;
    endPt2Name = endPt2Section.children[0].value;
    
    firstFuncNode = True;
    for funcNode in seqFunctionsNode.children:
        # each funcNode is a single function in the message
        # send-receive pipeline.
        
        endPtName = funcNode.children[0].value;
        funcNameNode = funcNode.children[1];
        
        # get the relevant endpoint to add to
        if (endPtName == endPt1Name):
            endPtToAddTo = endPt1Section;
            otherEndPtName = endPt2Name;
        elif(endPtName == endPt2Name):
            endPtToAddTo = endPt2Section;
            otherEndPtName = endPt1Name;
        else:
            errMsg = '\nSyntax error: should match given endpoint names\n';
            # lkjs: make into real error message.
            errMsg = '\nInvalid endpoint name prefixing message sequence ';
            errMsg += 'function with name "' + funcNameNode.value + '".  ';
            errMsg += 'Found name "' + endPtName + '".  Should be either ';
            errMsg += '"'+endPt1Name+'" or "' + endPt2Name + '".\n';
            errorFunction(errMsg,[funcNameNode],[funcNameNode.lineNo],progText);


            
        # should just need to add the created function as an
        # additional child of endPtFuncSection.
        if (len(endPtToAddTo.children) == 1):
            # add a body section for functions and globals
            bodySectionNode = AstNode(AST_ENDPOINT_BODY_SECTION,endPtToAddTo.lineNo,endPtToAddTo.linePos);

            endGlobals = AstNode(AST_ENDPOINT_GLOBAL_SECTION,endPtToAddTo.lineNo,endPtToAddTo.linePos);
            endFunctions = AstNode(AST_ENDPOINT_FUNCTION_SECTION,endPtToAddTo.lineNo,endPtToAddTo.linePos);
            
            bodySectionNode.addChild(endGlobals);
            bodySectionNode.addChild(endFunctions);
            endPtToAddTo.addChild(bodySectionNode);
            
            
        endPtFuncSection = endPtToAddTo.children[1].children[1];
        toAddNode = None;
        
            
        if firstFuncNode:
            firstFuncNode = False;

            toAddNode = AstNode(AST_MSG_SEND_FUNCTION,funcNode.lineNo,funcNode.linePos);
            # add the name of the function
            toAddNode.addChild(funcNameNode);

            # add the function decl arglist
            funcDeclArgListNode = funcNode.children[2];
            toAddNode.addChild(funcDeclArgListNode);

            # add the function body
            funcBodyNode = funcNode.children[3];
            toAddNode.addChild(funcBodyNode);

            initializationVec = [];

            
            # craft my own send statement
            typedSendsStatementNode = AstNode(AST_TYPED_SENDS_STATEMENT,funcNode.lineNo,funcNode.linePos);


            # Also, need to declare an incoming message-like object at
            # the top of the send function.  This is because the
            # sequence globals are sent in hidden messages between
            # endpoints.  Message receive statements reference the
            # sequence global variables through their incoming
            # messages.  However, the message send function has no
            # incoming message.  Therefore, we create an outgoing
            # message at the top of the function that defines and
            # initializes all the global sequence variables.
            outgoingMessageNode = AstNode(AST_MESSAGE_LITERAL,funcNode.lineNo,funcNode.linePos);
            
            for seqParamNode in seqGlobalsNode.children:
                typeNode = seqParamNode.children[0];
                identifierNode = seqParamNode.children[1];

                sendsLineNode = AstNode(AST_TYPED_SENDS_LINE,typeNode.lineNo,typeNode.linePos);
                sendsLineNode.addChildren([typeNode,identifierNode]);

                typedSendsStatementNode.addChild(sendsLineNode);

                # to ensure that all sequence globals are initialized
                # at beginning of message send function:
                msgLiteralElemNode = AstNode(AST_MESSAGE_LITERAL_ELEMENT,typeNode.lineNo,typeNode.linePos);
                strLiteralNode = AstNode(AST_STRING,typeNode.lineNo,typeNode.linePos,identifierNode.value);
                if (len(seqParamNode.children) == 3):
                    # means that we have an initializer
                    valueNode = seqParamNode.children[2];
                else:
                    if (typeNode.value == TYPE_BOOL):
                        valueNode = AstNode(AST_BOOL,typeNode.lineNo,typeNode.linePos,'False');
                    elif(typeNode.value == TYPE_STRING):
                        valueNode = AstNode(AST_STRING,typeNode.lineNo,typeNode.linePos,'');
                    elif (typeNode.value == TYPE_NUMBER):
                        valueNode = AstNode(AST_NUMBER,typeNode.lineNo,typeNode.linePos,'0');
                    else:
                        print('\nUnknown type: ' + typeNode.value + '\n');
                        assert(False);
                

                msgLiteralElemNode.addChildren([strLiteralNode,valueNode]);
                outgoingMessageNode.addChild(msgLiteralElemNode);


            # create a declaration for outgoingmessagenode that is
            # used to initialize message sequence globals.
            outMsgDec = AstNode(AST_DECLARATION, funcNode.lineNo,funcNode.linePos);
            msgLitType = AstNode(AST_TYPE,funcNode.lineNo,funcNode.linePos,TYPE_OUTGOING_MESSAGE);
            msgLitName = AstNode(AST_IDENTIFIER,funcNode.lineNo,funcNode.linePos,INCOMING_MESSAGE_NAME);
            
            outMsgDec.addChildren([msgLitType,msgLitName,outgoingMessageNode]);
            funcBodyNode.prependChild(outMsgDec);
            toAddNode.addChild(typedSendsStatementNode);
        else:
            # message receive function
            toAddNode = AstNode(AST_MSG_RECEIVE_FUNCTION,funcNode.lineNo,funcNode.linePos);
            # add the name of the function
            toAddNode.addChild(funcNameNode);

            # creating a fictitious incoming message identifier
            inMsgNode = AstNode(AST_IDENTIFIER, funcNode.lineNo,funcNode.linePos,INCOMING_MESSAGE_NAME);
            toAddNode.addChild(inMsgNode);

            # now creating a node that defines the elements of the message function
            typedReceiveNode = AstNode(AST_TYPED_SENDS_STATEMENT,funcNode.lineNo,funcNode.linePos);

            for seqParamNode in seqGlobalsNode.children:
                typeNode = seqParamNode.children[0];
                identifierNode = seqParamNode.children[1];

                sendsLineNode = AstNode(AST_TYPED_SENDS_LINE,typeNode.lineNo,typeNode.linePos);
                sendsLineNode.addChildren([typeNode,identifierNode]);

                typedReceiveNode.addChild(sendsLineNode);
            

            # actually add typed receive node
            toAddNode.addChild(typedReceiveNode);            

            # because sends node and receive node are identical,
            # re-use typedReceiveNode
            toAddNode.addChild(typedReceiveNode);            

            # actually add function body
            funcBodyNode = funcNode.children[2];
            toAddNode.addChild(funcBodyNode);

        # each function should have a final sendsStatement to ensure
        # that all globals are updated.
        addSendStatement(funcBodyNode,seqGlobalsNode,otherEndPtName);

        updateVariableNames(toAddNode,seqGlobalsNode);
        # Should add the last node
        endPtFuncSection.addChild(toAddNode);


def addSendStatement(funcBodyNode,seqGlobalsNode,otherEndPtName):
    '''
    At the end of every message function, we need to add a sends
    statement to ensure message gets sent to other side.
    '''
    # create an declaration node in which we assign an outgoing
    # message.  Then actually send the outgoing message.

    #####DECLARATION
    
    # left-hand side of declaration
    outMsgTypeNode = AstNode(AST_TYPE,funcBodyNode.lineNo,funcBodyNode.linePos,TYPE_OUTGOING_MESSAGE);
    outMsgIdNode = AstNode(AST_IDENTIFIER,funcBodyNode.lineNo,funcBodyNode.linePos,OUTGOING_MESSAGE_NAME);

    # right-hand side of declaration
    msgLiteralNode = AstNode(AST_MESSAGE_LITERAL,funcBodyNode.lineNo,funcBodyNode.linePos);
    for globDecNode in seqGlobalsNode.children:
        itemName = globDecNode.children[1].value;
        
        strLiteralNode = AstNode(AST_STRING,funcBodyNode.lineNo,funcBodyNode.linePos,itemName);
        idNode = AstNode(AST_IDENTIFIER,funcBodyNode.lineNo,funcBodyNode.linePos,itemName);

        msgLitElem = AstNode(AST_MESSAGE_LITERAL_ELEMENT,strLiteralNode,idNode);
        msgLitElem.addChildren([strLiteralNode,idNode]);
        msgLiteralNode.addChild(msgLitElem);

    decNode = AstNode(AST_DECLARATION,funcBodyNode.lineNo,funcBodyNode.linePos);
    decNode.addChildren([outMsgTypeNode,outMsgIdNode,msgLiteralNode]);

    funcBodyNode.addChild(decNode);

    #######SEND STATEMENT 
    endPtIdNode = AstNode(AST_IDENTIFIER,funcBodyNode.lineNo,funcBodyNode.linePos,otherEndPtName);
    sendNode = AstNode(AST_SEND_STATEMENT,funcBodyNode.lineNo,funcBodyNode.linePos);

    sendNode.addChildren([outMsgIdNode,endPtIdNode]);
    funcBodyNode.addChild(sendNode);


    
def updateVariableNames(toAddNode,seqGlobalsNode):
    '''
    @param{AstNode} toAddNode --- The message receive or message send
    function that we are adding to and endpoint.  Need to go through
    its body to ensure that any identifiers referenced that are
    message sequence globals are exchanged with a typed message.

    @param{AstNode} seqGlobalsNode --- The
    AST_MESSAGE_SEQUENCE_GLOBALS node.
    '''

    funcBodyNodeIndex = 2; # for message sends
    if (toAddNode.label == AST_MSG_RECEIVE_FUNCTION):
        funcBodyNodeIndex = 4; # for message receives
        
    funcBodyNode = toAddNode.children[funcBodyNodeIndex];

    # build dict of identifiers to look for and what to replace them
    # with from globals node

    checkDict = {};
    for globItemNode in seqGlobalsNode.children:
        name = globItemNode.children[1].value;
        checkDict[name] = replacementName(name);
    
    replaceAndRecurse(funcBodyNode,checkDict);


def replaceAndRecurse(node,checkDict):
    # there shouldn't be any cycles in ast, so we should be okay with
    # basic recursion.

    for index in range(0,len(node.children)):
        child = node.children[index];
        if (child.label == AST_IDENTIFIER):
            if (child.value in checkDict):
                bracketNode = AstNode(AST_BRACKET_STATEMENT,child.lineNo,child.linePos);
                name,indexName = checkDict[child.value];
                msgNode = AstNode(AST_IDENTIFIER,child.lineNo,child.linePos,name);
                strNode = AstNode(AST_STRING,child.lineNo,child.linePos,indexName);
                bracketNode.addChildren([msgNode,strNode]);
                node.children[index] = bracketNode;
                
        replaceAndRecurse(node.children[index],checkDict);



def replacementName(originalName):
    '''
    @param {String} originalName ---
    Takes in 'something'
    Returns INCOMING_MESSAGE_NAME["something"]
    '''
    return (INCOMING_MESSAGE_NAME, originalName);
