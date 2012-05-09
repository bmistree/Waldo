#!/usr/bin/python

import emitHelper;


class Function(object):
    def __init__(self,name,astNode,protObj,declArgListIndex):
        '''
        @param {String} name -- Should already be guaranteed not to
        collide with python variable and other global vars.
        
        @param {Int} declArgListIndex -- Each function astNode
        (public, msgReceive, ...) has many children.  declArgListIndex is
        the index of astNode.children that contains declArgList appears.
        '''
        self.name = name;
        self.astNode = astNode;
        self.protObj = protObj;
        self.endpoint = self.protObj.currentEndpoint;
        self.declArgListIndex = declArgListIndex;
        
    def emit():
        errMsg = '\nBehram error: pure virtual method emit of Function ';
        errMsg += 'called.\n';
        assert(False);

    def pythonizeName(self):
        return self.name;
        
    def createMethodHeader(self):
        #already know that self.name does not conflict with python
        #because was checked before constructed.
        methodHeader = 'def %s(self' % self.pythonizeName();
        
        #fill in arguments
        
        # FIXME: lkjs;
        # argument names may conflict with python keywords.  should
        # fix eventually.
        declArgsList = self.astNode.children[self.declArgListIndex];
        for s in declArgsList.children:
            #each s is a declArg
            if (len(s.children) == 0):
                continue;

            argName = s.children[1].value;
            methodHeader += ', ' + argName;
        
        methodHeader += '):\n';
        return methodHeader;


class InternalFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 2;        
        super(InternalFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);
    def emit(self):
        
        self.endpoint.currentlyEmittingFunction = self;
        
        methodHeader = self.createMethodHeader();

        funcBodyNode = self.astNode.children[3];
        
        methodBody = '''
if (self.whichEnv == COMMITTED_CONTEXT):
''';
        inCommittedBody = emitHelper.runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint,emitHelper.COMMITTED_PREFIX);

        methodBody += emitHelper.indentString(inCommittedBody, 1);

        methodBody += '''
elif (self.whichEnv == INTERMEDIATE_CONTEXT):
''';
        
        inIntermediateBody = emitHelper.runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint,emitHelper.INTERMEDIATE_PREFIX);
        methodBody += emitHelper.indentString(inIntermediateBody, 1);

        
        methodBody += '''
else:
''';
        elseBody = r"""
errMsg = '\nBehram error: do not know which context to execute internal function in.  Aborting.\n';
print(errMsg);
assert(False);
""";

        methodBody += emitHelper.indentString(elseBody, 1);
        

        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        self.endpoint.currentlyEmittingFunction = None;
        return returnString;


class PublicFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 2;
        super(PublicFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);

    def emit(self):
        self.endpoint.currentlyEmittingFunction = self;
        methodHeader = self.createMethodHeader();        

        funcBodyNode = self.astNode.children[3];
        
        methodBody = '''
self.whichEnv = COMMITTED_CONTEXT;
'''
        methodBody += emitHelper.runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint,emitHelper.COMMITTED_PREFIX);
        
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        self.endpoint.currentlyEmittingFunction = None;
        return returnString;

class MsgFunction(Function):
    def __init__ (self,name,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 1;
        self.sendsTo = None;
        
        super(MsgFunction,self).__init__(name,None,protObj,functionArgDeclIndex);

        
    def setSendsTo(self,sendsTo):
        '''
        Each message function should know the function on the other
        endpoint it is sending to.  This allows it to specify which
        handler on the receiver should fire in the message.
        '''
        self.sendsTo = sendsTo;


    def setAstNode(self,astNode):
        '''
        Message functions are created when running through the traces
        section of the code (so that it's easy to determine which msg
        function sends a msg to which other msg function).  At that
        point, we do not have the ast node corresponding to the actual
        message function.  Therefore, we have to allow ourselves to
        set it separately and later.
        '''
        self.astNode = astNode;

        # FIXME: super-hack.
        # lkjs
        self.endpoint = self.protObj.currentEndpoint;


    def caseBasedDispatch(self,first,indentLevel):
        '''
        Each message should be structured to include the name of the
        function on the other endpoint that should handle it.  The
        code that handles the message labeling itself is a large
        if-elif-else statement found in the _sendMsg function of the
        emitted code (and populated in the @see
        emitGeneralSendMessageUtility function of class Endpoint in
        emitEndpoint.py).  In general, it should end up looking
        something like:

        dispatchTo = None;
        if (funcNameFrom == '_msgRecvTwo'):
            dispatchTo = '_msgRecvThree';
        elif(funcNameFrom == '_msgRecvFour'):
            dispatchTo = STREAM_TAIL_SENTINEL;
        else:
            errMsg = '\nBehram Error.  Provided an invalid ';
            errMsg += 'funcNameFrom argument in Pong.\n';
            print(errMsg);
            assert(False);
            
        Each if/elif statement itself is composed by a separate
        MsgFunction in this method.
        '''

        ifElifOperator = 'elif';
        if (first):
            ifElifOperator = 'if';

        ifHead = ifElifOperator + " (funcNameFrom == '" + self.pythonizeName() + "'):\n";

        ifBody = "dispatchTo  = ";

        if (self.sendsTo == None):
            # means that this was the last message receive in a trace
            # line: we should set dispacthTo equal to the sentinnel
            # value representing this case.
            ifBody += 'STREAM_TAIL_SENTINEL;\n';
        else:
            ifBody += "'" + self.sendsTo.pythonizeName() + "';\n";

            
        indentedHead = emitHelper.indentString(ifHead,indentLevel);
        indentedBody = emitHelper.indentString(ifBody,indentLevel+1);

        return indentedHead + indentedBody;
        
        
class MsgSendFunction(MsgFunction):
    def __init__(self,name,protObj):
        super(MsgSendFunction,self).__init__(name,protObj);

    def pythonizeName(self):
        '''
        Using a convention of changing a msg send function's name from
        <FuncName> to _msgSend<FuncName>
        '''
        return '_msgSend' + self.name;

        
    def emit(self):
        self.endpoint.currentlyEmittingFunction = self;

        methodHeader = self.createMethodHeader();
        
        funcBodyNode = self.astNode.children[2];


        methodBodyTop = r"""
# means that we are already processing a trace stream.
# schedule this for another time
if (self.amInTrace):
""";

        ifBody = """
queueElementName = '%s';
queueElementArgs = []; # no args beyond self were passed into the send function.
queueElement = _MessageSendQueueElement(queueElementName,queueElementArgs);

self.msgSendQueue.append(queueElement);
return;
""" % self.pythonizeName();

        methodBodyTop += emitHelper.indentString(ifBody,1);

        methodBodyTop += """
# blocks further send messages from executing
self.amInTrace = True;

#stores intermediate send function
self.outstandingSend = _MessageSendQueueElement('%s',[]);

#sets environment for further calls
self.whichEnv = INTERMEDIATE_CONTEXT;


# actually write the user-specified "guts" of the function.
""" % self.pythonizeName();

        

        methodBodyBottom = emitHelper.runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint,emitHelper.INTERMEDIATE_PREFIX);

        methodBody = methodBodyTop + methodBodyBottom;
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        self.endpoint.currentlyEmittingFunction = None;        
        return returnString;


        
class MsgReceiveFunction(MsgFunction):
    def __init__(self,name,protObj):
        super(MsgReceiveFunction,self).__init__(name,protObj);

    def pythonizeName(self):
        '''
        Using a convention of changing a msg send function's name from
        <FuncName> to _msgRecv<FuncName>
        '''
        return '_msgRecv' + self.name;

        
    def emit(self):
        self.endpoint.currentlyEmittingFunction = self;

        methodHeader = self.createMethodHeader();
        methodBody = '''
self.whichEnv = INTERMEDIATE_CONTEXT;
'''
        if (len(self.astNode.children) == 4):
            # means that msg receive had no body.
            pass;
        else:
            funcBodyNode = self.astNode.children[4];
            methodBody += emitHelper.runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint,emitHelper.INTERMEDIATE_PREFIX);
        
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        self.endpoint.currentlyEmittingFunction = None;        
        return returnString;


    def createMethodHeader(self):
        # had to override so that would correctly fill in input
        # arg. (does not take an arglist like the other functions.)
        
        #already know that self.name does not conflict with python
        #because was checked before constructed.
        methodHeader = 'def %s(self,' % self.pythonizeName();
        
        #fill in arguments
        
        # FIXME: lkjs;
        # argument names may conflict with python keywords.  should
        # fix eventually.
        methodHeader += self.astNode.children[1].value;
        
        methodHeader += '):\n';
        return methodHeader;
