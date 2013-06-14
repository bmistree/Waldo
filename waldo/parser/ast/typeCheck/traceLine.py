#!/usr/bin/python



import sys;
import os;
from waldo.parser.ast.parserUtil import errPrint
from waldo.parser.ast.astLabels import AST_MESSAGE_SEND_SEQUENCE_FUNCTION, AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION


def endpointFuncNameToString(endpointName, funcName):
    return endpointName + '.' + funcName;

def traceItemToString(traceItem):
    endpointName = traceItem.children[0].value;
    funcName = traceItem.children[1].value;
    return endpointFuncNameToString(endpointName,funcName);
    
    

class TypeCheckError():
    def __init__(self,nodes,errMsg):
        '''
        @param {array of AstNodes} nodes -- Each AstNode involved as
        part of error
        '''
        self.nodes = nodes;
        self.lineNos = [];
        for s in nodes:
            self.lineNos.append(s.lineNo);
            
        self.errMsg = errMsg;

        
class TraceLineManager():
    '''
    Stores data for each trace line.  Does some basic error checking
    
    '''
    def __init__ (self,typeStack):
        self.traceLines = dict();
        self.typeStack = typeStack;
        self.traceSectionAstNode = None;

    def setAstTraceSectionNode(self,traceSectionAstNode):
        self.traceSectionAstNode =  traceSectionAstNode;
    
        
    def addTraceLine(self,traceLineAst):
        '''
        @returns None if addition is successful.
                 TypeCheckError object if unsuccessful.
        '''
        
        # start at 2nd child because first child is the name of the
        # sequence of messages.
        msgStarter = traceItemToString(traceLineAst.children[1]);

        index = self.traceLines.get(msgStarter, None);
        if (index != None):
            tLineAst = self.traceLines[msgStarter].traceLineAst;
            errMsg = '\nError: already have a trace line ';
            errMsg += 'that starts with "' + msgStarter + '" function.\n';
            return TypeCheckError([traceLineAst, tLineAst],errMsg);
        
        # check to ensure that within trace line, have not repeated
        # the same function
        # skip first index because that's the name of the trace.
        for traceItemNodeIndex in range(1,len(traceLineAst.children)):
            traceItemNode = traceLineAst.children[traceItemNodeIndex];
            tItemNodeStr = traceItemToString(traceItemNode);

            # # check to ensure none of this trace line's own elements
            # # recycle message receive functions
            for otherNodeIndex in range(traceItemNodeIndex + 1, len(traceLineAst.children)):
                otherNode = traceLineAst.children[otherNodeIndex];

                oNodeStr = traceItemToString(otherNode);
                if tItemNodeStr == oNodeStr:
                    errMsg = '\nError: cannot reuse the same function with name "';
                    errMsg += tItemNodeStr + '" within same trace line.\n';
                    nodes = [traceItemNode,otherNode];
                    return TypeCheckError(nodes,errMsg);

            # check to ensure no other trace line's elements recycle
            # message receive functions.
            for tLineKey in self.traceLines.keys():
                tLine = self.traceLines[tLineKey];

                usesSameNode = tLine.usesSameTraceItem(traceItemNode);
                if usesSameNode != None:
                    errMsg = '\nError: cannot reuse the same function with name "';
                    errMsg += tItemNodeStr + '" between trace lines.  Each item ';
                    errMsg += 'in a message trace must be unique.\n';
                    nodes = [traceItemNode,usesSameNode];
                    return TypeCheckError(nodes,errMsg);

        
        self.traceLines[msgStarter] = TraceLine(traceLineAst);
        return None;


    def checkRepeatedSequenceLine(self):
        '''
        @returns TraceError or None
           TraceError if any of the sequences share the same names
           None if none of the trace lines shares the same name.
        '''
        existsDict = {};
        for tLineKey in self.traceLines.keys():
            tLine = self.traceLines[tLineKey];
            tLineAst = tLine.traceLineAst;
            seqName = tLineAst.children[0].value;
            if existsDict.get(seqName,None) != None:
                errMsg = 'You named two message sequences the same thing: "';
                errMsg += seqName + '."  You must have unique names for ';
                errMsg += 'message sequences.';
                nodes = [tLineAst,existsDict[seqName]];
                return TypeCheckError(nodes,errMsg);
            
            existsDict[seqName] = tLineAst;
            
        return None;

    
    def checkTraceItemInputOutput(self):
        '''
        run through all trace lines to see if the message outputs
        match the message inputs.

        @return {None or TypeCheckError} -- None if inputs and outputs
        agree.  TypeCheckError if they do not.
        '''

        for s in self.traceLines:
            traceError = self.traceLines[s].checkTraceItemInputOutput();
            if (traceError != None):
                return traceError;

        return None;


    def addMsgSendFunction(self,msgSendFuncAstNode, endpointName):
        '''
        @param{AstNode} msgSendFuncAstNode --- Type label should be 
        AST_MESSAGE_SEND_SEQUENCE_FUNCTION

        @param{String} endpointName

        Returns a TypeCheckError object if the function is not used in
        a trace.  (ie, no entry in self.traceLines corresponding to
        the string-ified function.)

        Also, returns a TypeCheckError if it appears that msg send function was
        used as a message receive function in a trace.

        Otherwise, returns None.
        
        Right now, doing an extremely inefficient job of actually
        checking through traces for errors.
        
        @returns {None or TypeCheckError} -- Returns TypeCheckError if
        any non-first part of the trace line uses the msgSend
        function.  Returns None to indicate no error.
        
        '''
        if msgSendFuncAstNode.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
            errMsg = '\nBehram error.  Should only receive an ast_message_send sequence ';
            errMsg += ' in addMsgSendFunction of traceLine.py.\n';
            print(errMsg);
            assert(False);
        
        expectedEndpointName = msgSendFuncAstNode.children[0].value;
        if expectedEndpointName != endpointName:
            errMsg = '\nError: declaring a msg send function named "';
            errMsg += funcName + '."  Using an incorrect endpoint name ';
            errMsg += 'of "' + expectedEndpointName + '."\n';
            nodes = [msgSendFuncAstNode,self.traceSectionAstNode];
            return TypeCheckError(nodes,errMsg);


        funcName = msgSendFuncAstNode.children[1].value;
        index = endpointFuncNameToString(endpointName,funcName);

        if (self.traceLines.get(index,None) == None):
            errMsg = '\nError: declaring a msg send function named "';
            errMsg += funcName + '" in ' + endpointName;
            errMsg += ' that is not specified in any message sequence.\n';
            nodes = [msgSendFuncAstNode,self.traceSectionAstNode];
            return TypeCheckError(nodes,errMsg);


        for s in self.traceLines.keys():
            '''
            run through all trace lines to see if they are using this
            msgSend function in some way that they shouldn't.
            '''
            traceError = self.traceLines[s].checkMsgSendFunction(
                msgSendFuncAstNode,endpointName);
            if (traceError != None):
                return traceError;

        return None;

    
    def addMsgRecvFunction(self,msgRecvFuncAstNode,endpointName):
        '''
        @param {AstNode} msgRecvFuncAstNode --- AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION

        @param {String} endpointName
        
        @returns {None or TypeCheckError} --

        TypeCheckError if msg receive function is not being used by
        any trace or if msg receive function is being used to begin a
        trace line.

        Otherwise, returns None.
        
        '''
        if msgRecvFuncAstNode.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
            errMsg = '\nBehram error.  Should only receive an ast_message_receive sequence ';
            errMsg += ' in addMsgRecvFunction of traceLine.py.\n';
            print(errMsg);
            assert(False);

        expectedEndpointName = msgRecvFuncAstNode.children[0].value;
        if expectedEndpointName != endpointName:
            errMsg = '\nError: declaring a msg receive function named "';
            errMsg += funcName + '."  Using an incorrect endpoint name ';
            errMsg += 'of "' + expectedEndpointName + '."\n';
            nodes = [msgRecvFuncAstNode,self.traceSectionAstNode];
            return TypeCheckError(nodes,errMsg);


        funcName = msgRecvFuncAstNode.children[1].value;
        index = endpointFuncNameToString(endpointName,funcName);

        tLine = self.traceLines.get(index,None);
        if (tLine != None):
            errMsg = '\nError: you are starting a trace line with ';
            errMsg += '"' + funcName + '", which is declared to be ';
            errMsg += 'a message receive function.  The first element ';
            errMsg += 'in a trace line should be a message send function.  ';
            errMsg += 'The difference is that a message send does not require ';
            errMsg += 'an incoming message, whereas a message receive function does.  ';
            errMsg += 'You should either change "' + funcName + '" to be a message send ';
            errMsg += 'function, or select a message send function to use.\n';
            
            nodes = [msgRecvFuncAstNode,tLine.traceLineAst];
            return TypeCheckError(nodes,errMsg);

        
        used = False;
        for s in self.traceLines.keys():
            '''
            checks to ensure that msgRecvFunction is actually used in trace section.
            '''
            usedOnLine = self.traceLines[s].checkMsgRecvFunction(msgRecvFuncAstNode,endpointName);
            used = usedOnLine or used;


        if (not used):
            #means that we never used this msgRecv function.
            errMsg = '\nError: message receive function named "';
            errMsg += funcName + '" in endpoint named "' + endpointName + '" ';
            errMsg += 'was not used in any message sequence.\n';
            nodes = [msgRecvFuncAstNode,self.traceSectionAstNode];
            return TypeCheckError(nodes,errMsg);
        
        return None;


    def checkUndefinedMsgSendOrReceive(self):
        '''
        @return{None or TypeCheckError} -- None if no error,
        TypeCheckError otherwise.
        '''
        for s in self.traceLines.keys():
            undefinedError = self.traceLines[s].errorOnUndefined();
            if (undefinedError != None):
                return undefinedError;
            
        return None;



class TraceLine ():
    '''
    Representation of trace line ( Server.one -> Client.two ->
    Server.three).  Whenever encounter a definition of either a
    message send or message receive function, should call
    checkMsgSendFunction or checkMsgRecvFunction.  Those will note
    that a function being used in the trace actually was defined
    in one of the endpoint sections.

    After running through definitions in both endpoints, calling
    errorOnUndeclared prints an error if any of the msgSend or
    msgReceive functions used in the trace ine weren't defined in an
    endpoint section.
    
    '''
    
    def __init__(self,traceLineAst):
        self.traceLineAst = traceLineAst;
        
        #elements of stringifiedTraceItems are strings produced from
        #calling traceItemToString on each traceItem from the trace
        #line.
        
        #The list is sorted so that first message sent is in index 0,
        #next message sent is in index 1, etc.
        self.stringifiedTraceItems = [];

        #contains a zero if nothing has called checkMsgSendFunction or
        #checkMsgReceiveFunction for a function with the stringified
        #name.  Contains a 1 otherwise.  Allows us to check whether
        #the item has been declared in a trace, but never actually
        #defined below.
        self.definedUndefinedList = [];

        self.sequenceName = traceLineAst.children[0].value;

        firstChild = True;
        for traceItem in traceLineAst.children:
            if firstChild:
                firstChild = False;
                continue;

            toAppend = traceItemToString(traceItem);
            self.stringifiedTraceItems.append(toAppend);
            self.definedUndefinedList.append(0);


        # keeps a list of all the ast nodes of the message sending and
        # receiving functions.  (not the trace line ast nodes, but the
        # actual AST_MSG_SEND_FUNCTION and AST_MSG_RECEIVE_FUNCTION.
        # This list should be maintained in sorted order (ie, index 0
        # should be the msg send statement, index 1 should be the
        # receive statement that gets input from the 0 statement,
        # etc.).  It is used to ensure that the messages declared as
        # the output of one function agrees with the type of message
        # expected by the input function.
        self.usedNodes = [0] * len(self.stringifiedTraceItems);


    def usesSameTraceItem(self,traceItemNode):
        '''
        Checks if this trace line uses the same trace item within its
        sequence of messages.  If it does, then returns the node
        associated with the conflicting trace item.  If it does not,
        return None.
        '''
        toStringOther = traceItemToString(traceItemNode);
        
        # skip the first child because that is just the name of the
        # trace line.
        firstChild = True;
        for traceItemLocal in self.traceLineAst.children:
            if firstChild:
                firstChild = False;
                continue;

            toStringLocal = traceItemToString(traceItemLocal);

            if toStringLocal == toStringOther:
                return traceItemLocal;
        
        return None;

        
        
    def checkTraceItemInputOutput(self):
        '''
        Runs through self.usedNodes to ensure that the message that
        one function sends agrees with the message its recipient
        anticipated.

        @returns {None or TypeCheckError} -- None if all the inputs
        and outputs match.  TypeCheckError if they do not.
        '''
        for s in self.usedNodes:
            if (s == 0):
                # means that we had an undefined item in the trace
                # line, and we cannot check input/output.  Should
                # abort further check.

                # returning None because something else should catch
                # this error (@see errorOnUndefined).
                return None;

        msgSendNode = self.usedNodes[0];
        outgoingFuncName = msgSendNode.children[0].value;
        typedOutgoingMsgNode = msgSendNode.children[3];
        for s in range(1,len(self.usedNodes)):
            msgRecvNode = self.usedNodes[s];
            typedIncomingMsgNode = msgRecvNode.children[2];
            incomingFuncName = msgRecvNode.children[0].value;

            disagreeError = self.incomingOutgoingDisagree(typedIncomingMsgNode,typedOutgoingMsgNode,incomingFuncName,outgoingFuncName);
            if (disagreeError != None):
                return disagreeError;

            # get outgoing to compare to incoming for next
            outgoingFuncName = incomingFuncName;
            typedOutgoingMsgNode = msgRecvNode.children[3];

        return None;
            
            
    def incomingOutgoingDisagree(self,typedIncomingMsgNode,typedOutgoingMsgNode,incomingFuncName,outgoingFuncName):
        '''
        @param {astNode with label typed_sends_statement}
        typedIncomingMsgNode,typedOutgoingMsgNode
        
        @param {String} incomingFuncName,outgoingFuncName -- the names
        of the msgSend/receive functions that have entry and exit
        messages of typedIncomingMsgNode and typedOutgoingMsgNode,
        respectively.  These are used for error reporting.
        
        @returns None or TypeCheckError -- None if every field of
        typedIncomingMsgNode appears in every field of
        typedOutgoingMsgNode (and the types agree) and every field of
        typedOutgoingMsgNode appears in every field of
        typedIncomingMsgNode.  Otherwise, returns TypeCheckError.
        '''
        # every field of typedIncomingMsgNode should be in every field

        # check that every field that's in incoming is also in
        # outgoing (and that they have matching types)
        for incomingLine in typedIncomingMsgNode.children:
            incomingTypeName = incomingLine.children[0].value;
            incomingFieldName = incomingLine.children[1].value;

            found = False;
            for outgoingLine in typedOutgoingMsgNode.children:
                outgoingTypeName = outgoingLine.children[0].value;
                outgoingFieldName = outgoingLine.children[1].value;

                if (incomingFieldName == outgoingFieldName):
                    if (outgoingTypeName != incomingTypeName):
                        errMsg = '\nMismatched type error.  ';
                        errMsg += 'The message produced by "' + outgoingFuncName + '"  ';
                        errMsg += 'has an element named "' + outgoingFieldName + '" with ';
                        errMsg += 'type "' + outgoingTypeName + '".  '
                        errMsg += 'The message that "' + incomingFuncName + '" takes in ';
                        errMsg += 'also has a field with that name, but has a different type: "';
                        errMsg += incomingTypeName + '".  Please change either the message sender ';
                        errMsg += 'or receiver so that "' + outgoingFieldName + '" has the same type.\n';

                        nodes = [outgoingLine, incomingLine];
                        
                        return TypeCheckError(nodes,errMsg);
                    else:
                        found = True;
                        break;
                    
            if (not found):
                # means that incoming expected a field that was not
                # present in outgoing.
                errMsg = '\nMissing input error.  ';
                errMsg += 'The message read by "' + incomingFuncName + '" ';
                errMsg += 'expects a message that has a field named "' + incomingFieldName +'".  ';
                errMsg += '"' + outgoingFuncName + '" did not provide it.\n';
                nodes = [incomingLine,typedOutgoingMsgNode];
                return TypeCheckError(nodes,errMsg);

            
        # check that every field that's in outgoing is also in
        # incoming.  Do not need to check for matching types, because
        # did that above.
        for outgoingLine in typedOutgoingMsgNode.children:
            outgoingFieldName = outgoingLine.children[1].value;

            found = False;
            for incomingLine in typedIncomingMsgNode.children:
                incomingFieldName = incomingLine.children[1].value;

                if (outgoingFieldName == incomingFieldName):
                    found = True;
                    break;

            if (not found):
                errMsg = '\nExtra output error.  ';
                errMsg += 'The message sent by "' + outgoingFuncName + '" ';
                errMsg += 'contains an extra field, "' + outgoingFieldName + '", ';
                errMsg += 'that the message receiving function, "' + incomingFuncName + '" ';
                errMsg += 'did not expect\n';

                nodes = [outgoingLine,typedIncomingMsgNode];
                return TypeCheckError(nodes,errMsg);

        return None;
        
    def checkMsgSendFunction(self,msgSendFuncAstNode,endpointName):
        '''
        @returns {None or TypeCheckError} -- Returns TypeCheckError if
        any non-first part of the trace line uses the msgSend
        function.  Returns None to indicate no error.
        '''
        funcName = msgSendFuncAstNode.children[1].value;

        if (len(self.stringifiedTraceItems) == 0):
            errMsg = '\nBehram error: you should never have a case where ';
            errMsg += 'self.stringifiedTraceItems is empty.\n';
            errPrint(errMsg);
            assert(False);

        stringifiedFuncName = endpointFuncNameToString(endpointName,funcName);
            
        if (self.stringifiedTraceItems[0] == stringifiedFuncName):
            self.definedUndefinedList[0] += 1;
            self.usedNodes[0] = msgSendFuncAstNode;


        #start at 1 so that skip over msgSendFunction that initiates trace.
        for s in range(1,len(self.stringifiedTraceItems)):
            if (self.stringifiedTraceItems[s] == stringifiedFuncName):
                errMsg = '\nMessage send error: You are using a message send ';
                errMsg += 'function named "' + funcName + '", in the middle ';
                errMsg += 'of a sequence of messages.  You cannot use a message ';
                errMsg += 'send function in the middle of a sequence of messages.  '
                errMsg += 'This is because message send functions do not take any ';
                errMsg += 'input messages.  ';
                errMsg += 'You should use a message receive function instead or ';
                errMsg += 'change "' + funcName + '" to a message receive function.\n';

                nodes = [self.traceLineAst,msgSendFuncAstNode];
                return TypeCheckError(nodes,errMsg);

            
        return None;

    

    def checkMsgRecvFunction(self,msgRecvFuncAstNode,endpointName):
        '''
        Returns true if the msgRecv function is used in this trace,
        false otherwise.
        '''
        funcName = msgRecvFuncAstNode.children[1].value;

        stringifiedFuncName = endpointFuncNameToString(endpointName,funcName);
        
        returner = False;
        for s in range(1,len(self.stringifiedTraceItems)):
            if (self.stringifiedTraceItems[s] == stringifiedFuncName):
                self.definedUndefinedList[s] += 1;
                # puts trace node into usedNodes so can iterate over
                # usedNodes later to check if message sending and
                # receiving signatures match.
                self.usedNodes[s] = msgRecvFuncAstNode;
                returner = True;
                #note: do not return here because may have repeats of
                #message receptions.

        return returner;


    def errorOnUndefined(self):
        '''
        Runs through all items in trace and checks if any of them are
        being used, but have not been defined later in function (ie,
        have a zero value in definedUndefinedList).

        THIS IS A TEMPORARY FUNCTION AND SHOULD EVENTUALLY BE SWAPPED
        OUT.

        @return{None or TypeCheckError} -- None if no error,
        TypeCheckError otherwise.
        '''
        for s in range(0,len(self.definedUndefinedList)):
            if (self.definedUndefinedList[s] == 0):
                errMsg = '\nError: using a function named ';
                errMsg += '"' + self.stringifiedTraceItems[s] + '" in ';
                errMsg += 'message sequences, but never actually defined it.\n';
                return TypeCheckError([self.traceLineAst],errMsg);

        # nothing was undefined: there is no error.
        return None;
