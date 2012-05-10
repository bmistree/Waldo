#!/usr/bin/python


def endpointFuncNameToString(endpointName, funcName):
    return endpointName + '.' + funcName;

def traceItemToString(traceItem):
    endpointName = traceItem.children[0].value;
    funcName = traceItem.children[1].value;
    return endpointFuncNameToString(endpointName,funcName);
    
    

class TraceLineError():
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
                 TraceLineError object if unsuccessful.
        '''
        msgStarter = traceItemToString(traceLineAst.children[0]);
        
        index = self.traceLines.get(msgStarter, None);
        if (index != None):
            tLineAst = self.traceLines[msgStrarter];
            errMsg = '\nError: already have a trace line ';
            errMsg += 'that starts with "' + msgStarter + '" function.\n';
            return TraceLineError([traceLineAst, tLineAst],errMsg);
            
        self.traceLines[msgStarter] = TraceLine(traceLineAst);
        return None;
        
    def checkTraceItemInputOutput(self):
        # run through all trace lines to see if the message outputs
        # match the message inputs.
        for s in self.traceLines:
            self.traceLines[s].checkTraceItemInputOutput();

        
    def addMsgSendFunction(self,msgSendFuncAstNode, endpointName):
        '''
        Throws an error, if the function is not used in a trace.  (ie,
        no entry in self.traceLines corresponding to the string-ified
        function.)

        Also, throws an error if it appears that msg send function was
        used as a message receive function in a trace.

        Right now, doing an extremely inefficient job of actually
        checking through traces for errors.
        '''
        funcName = msgSendFuncAstNode.children[0].value;
        index = endpointFuncNameToString(endpointName,funcName);
        if (self.traceLines.get(index,None) == None):
            errMsg = '\nError: declaring a msgSend function ';
            errMsg += 'that is not used\n';
            print(errMsg);
            assert(False);

        for s in self.traceLines.keys():
            '''
            run through all trace lines to see if they are using this
            msgSend function in some way that they shouldn't.
            '''
            self.traceLines[s].checkMsgSendFunction(msgSendFuncAstNode,endpointName);


    def addMsgRecvFunction(self,msgRecvFuncAstNode,endpointName):
        '''
        Throws an error if msg receive function is not being used by
        any trace.  Similarly, throws an error if msg receive function
        is being used to begin a trace line.
        '''
        funcName = msgRecvFuncAstNode.children[0].value;
        index = endpointFuncNameToString(endpointName,funcName);

        if (self.traceLines.get(index,None) != None):
            errMsg = '\nError: you cannot start a trace line ';
            errMsg += 'with a message receive function.\n';
            print(errMsg);
            assert(False);

        
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
            errMsg += 'was not used in any trace.\n';
            print(errMsg);
            assert(False);


    def checkUndefinedMsgSendOrReceive(self):
        for s in self.traceLines.keys():
            self.traceLines[s].errorOnUndefined();



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
        
        for traceItem in traceLineAst.children:
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


    def checkTraceItemInputOutput(self):
        '''
        Runs through self.usedNodes to ensure that the message that
        one function sends agrees with the message its recipient
        anticipated.

        @throws error if there's a mismatch
        '''

        for s in self.usedNodes:
            if (s == 0):
                # means that we had an undefined item in the trace
                # line, and we cannot check input/output.  Should
                # abort further check.
                return;

        msgSendNode = self.usedNodes[0];
        typedOutgoingMsgNode = msgSendNode.children[3];
        for s in range(1,len(self.usedNodes)):
            msgRecvNode = self.usedNodes[s];
            typedIncomingMsgNode = msgRecvNode.children[2];

            disagree = self.incomingOutgoingDisagree(typedIncomingMsgNode,typedOutgoingMsgNode);
            if (disagree != None):
                errMsg = '\nOutput of one does not equal the input of another\n';
                print('\n\n');
                print(errMsg);
                print('\n\n');
                assert(False);

            # get outgoing to compare to incoming for next
            typedOutgoingMsgNode = msgRecvNode.children[3];

            
    def incomingOutgoingDisagree(self,typedIncomingMsgNode,typedOutgoingMsgNode):
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
                        errMsg = '\nError.  Mismatched types when checking ';
                        errMsg += 'incoming and outgoing.\n';
                        print(errMsg);
                        assert(False);
                    else:
                        found = True;
                        break;
                    
            if (not found):
                # means that incoming expected a field that was not
                # present in outgoing.
                errMsg = '\nError.  Incoming expected a field that ';
                errMsg += 'outgoing did not provide.\n';
                print(errMsg);
                assert(False);

                
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
                errMsg = '\nError.  Outgoing provides a field that ';
                errMsg += 'incoming did not expect.\n';
                print(errMsg);
                assert(False);
            
                

        
    def checkMsgSendFunction(self,msgSendFuncAstNode,endpointName):
        '''
        Throws an error if any non-first part of the trace line uses
        the msgSend function
        '''
        funcName = msgSendFuncAstNode.children[0].value;


        if (len(self.stringifiedTraceItems) == 0):
            errMsg = '\nBehram error: you should never have a case where ';
            errMsg += 'self.stringifiedTraceItems is empty.\n';
            print(errMsg);
            assert(False);

        stringifiedFuncName = endpointFuncNameToString(endpointName,funcName);
            
        if (self.stringifiedTraceItems[0] == stringifiedFuncName):
            self.definedUndefinedList[0] += 1;
            self.usedNodes[0] = msgSendFuncAstNode;

        #start at 1 so that skip over msgSendFunction that initiates trace.
        for s in range(1,len(self.stringifiedTraceItems)):
            if (self.stringifiedTraceItems[s] == stringifiedFuncName):
                errMsg = '\nError: with "' + stringifiedFuncName + '".  ';
                errMsg += 'cannot use it as msg receive function in trace.\n';
                print(errMsg);
                assert(False);


    def checkMsgRecvFunction(self,msgRecvFuncAstNode,endpointName):
        '''
        Returns true if the msgRecv function is used in this trace,
        false otherwise.
        '''
        funcName = msgRecvFuncAstNode.children[0].value;

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
        OUT EVENTUALLY.
        '''
        for s in range(0,len(self.definedUndefinedList)):
            if (self.definedUndefinedList[s] == 0):
                errMsg = '\nError: using a function named ';
                errMsg += '"' + self.stringifiedTraceItems[s] + '" in ';
                errMsg += 'a trace, but never actually defined it.\n';
                print(errMsg);
                assert(False);
