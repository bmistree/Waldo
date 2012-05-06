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

    def createMethodHeader(self):
        #already know that self.name does not conflict with python
        #because was checked before constructed.
        methodHeader = 'def %s(self' % self.name;

        
        #fill in arguments
        declArgsList = self.astNode.children[self.declArgListIndex];
        for s in declArgsList.children:
            #each s is a declArg
            if (len(s.children) == 0):
                continue;


            argName = s.children[1].value;
            argName = self.endpoint.varName(argName);
            methodHeader += ', ' + argName;
        
        methodHeader += '):\n';
        return methodHeader;


class InternalFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 2;        
        super(InternalFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);
    def emit(self):
        print('\nBehram error: in InternalFunction, need to finish emit method\n');
        methodHeader = self.createMethodHeader();
        methodBody = 'pass';
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        return returnString;


class PublicFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 2;
        super(PublicFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);

    def emit(self):
        print('\nBehram error: in PublicFunction, need to finish emit method\n');
        methodHeader = self.createMethodHeader();        

        methodBody = 'pass;';
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        return returnString;

        
class MsgSendFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 1;
        super(MsgSendFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);
        
        
    def emit(self):
        print('\nBehram error: in MsgSendFunction, need to finish emit method\n');

        methodHeader = self.createMethodHeader();
        
        funcBodyNode = self.astNode.children[2];
        methodBody = emitHelper.runFunctionBodyInternalEmit(funcBodyNode,self.protObj,self.endpoint);
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        return returnString;


        
class MsgReceiveFunction(Function):
    def __init__(self,name,astNode,protObj):
        #see astBuilder or the graphical ast:
        functionArgDeclIndex = 1;
        super(MsgReceiveFunction,self).__init__(name,astNode,protObj,functionArgDeclIndex);


    def emit(self):
        print('\nBehram error: in MsgReceiveFunction, need to finish emit method\n');
        methodHeader = self.createMethodHeader();                
        methodBody = 'pass;';
        
        returnString = emitHelper.indentString(methodHeader,1);
        returnString += emitHelper.indentString(methodBody,2);
        return returnString;
