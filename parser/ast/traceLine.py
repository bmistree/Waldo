#!/usr/bin/python


def endpointFuncNameToString(endpointName, funcName):
    return endpointName + '.' + funcName;

def traceItemToString(traceItem):
    endpointName = traceItem.children[0].value;
    funcName = traceItem.children[1].value;
    return endpointFuncNameToString(endpointName,funcName);
    
    

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
        msgStarter = traceItemToString(traceLineAst.children[0]);
        
        index = self.traceLines.get(msgStarter, None);
        if (index != None):
            errMsg = '\nError: already have a trace line ';
            errMsg += 'that starts with this function.\n';
            print(errMsg);
            assert(False);
            
        self.traceLines[msgStarter] = TraceLine(traceLineAst);
            

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
                errMsg += '"' + self.stringifiedTraceitems[s] + '" in ';
                errMsg += 'a trace, but never actually defined it.\n';
                print(errMsg);
                assert(False);
