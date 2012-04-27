#!/usr/bin/python
from astLabels import *;


def runEmitter(astNode,protObj=None):

    
    if (astNode.label == AST_ROOT):
        #getting protocol

        #proto obj nmae
        protObjName = astNode.children[0].value;
        protObj = ProtocolObject(protObjName);

        #handling alias section
        aliasSection = astNode.children[1];
        
        #endpoint name
        ept1Name = aliasSection.children[0].value; 
        ept2Name = aliasSection.children[1].value;

        protObj.ept1 = Endpoint(ept1Name);
        protObj.ept2 = Endpoint(ept2Name);

        #run emitter over shared section
        sharedSection = astNode.children[3];
        runEmitter(sharedSection,protObj);

        #run emitter over one endpoint
        ept1 = astNode.children[4];
        runEmitter(ept1,protObj);

        #run emitter over other endpoint
        ept2 = astNode.children[5];
        runEmitter(ept2,protObj);

        #now actually emit
        protObj.emit();

        
    elif(astNode.label == AST_SHARED_SECTION):
        #add the shared values to each endpoints class
        for s in astNode.children:
            #only annotated declarations are in children
            runEmitter(s,protObj);

    elif (astNode.label == AST_ANNOTATED_DECLARATION):
        varName = astNode.children[2].value;
        varVal = None;
        if (len(astNode.children) == 4):
            #FIXME: Not handling initializers for annotated declarations correctly.
            #lkjs;
            errMsg = '\n\nNot handling initializers for annotated declarations correctly.\n\n';
            print(errMsg);

        protObj.addShared(varName,varVal);

        
    else:
        print('\nIn emitter.  Not sure what to do with label ');
        print(astNode.label);
        print('\n\n');

        

class ProtocolObject():
    def __init__(self, name):
        self.name = name;
        self.ept1 = None;
        self.ept2 = None;

    def addShared(self,sharedName,sharedVal):
        self.checkUsageError('addShared');

        sharedVar = Variable (sharedName,sharedVal);
        self.ept1.sharedVariables.append(sharedVar);
        self.ept2.sharedVariables.append(sharedVar);

    def checkUsageError(self,whichFunc):
        '''
        For sanity-checking/debugging.
        '''
        if ((self.ept1 == None) or (self.ept2 == None)):
            errMsg = '\n\nBehram error: should have set ';
            errMsg += 'both endpoints before calling ';
            errMsg += whichFunc + '.\n\n';
            print(errMsg);
            assert(False);
        
    def emit(self):
        self.checkUsageError('emit');
        returnString = '';
        returnString += '\n\n\n';
        returnString += self.ept1.emit();
        returnString += '\n\n\n';
        returnString += self.ept2.emit();
        returnString += '\n\n\n';
        
        print(returnString);
        
        
        
class Endpoint():
    def __init__(self,name):
        self.name = name;
        self.publicMethods = [];
        self.internalMethods = [];
        
        self.msgReceiverMethods = [];
        self.msgSendMethods = [];

        #list of strings of variables
        self.sharedVariables = [];

        self.endpointVariables = [];

    def emit(self):
        '''
        @returns {String} class for this endpoint
        '''
        returnString = '';
        returnString += self.emitClassHeader();
        returnString += '\n\n';
        returnString += self.emitClassInit();
        returnString += '\n\n';
        return returnString;
        
    def emitClassHeader(self):
        returnString = '''
class %s:
''' % self.name;

        return returnString;

    
    def emitClassInit(self):
        
        initHeaderString = '''
def __init__(self):
'''
        initBodyString = '';
        initBodyString += '\n#shared variables section\n'
        for s in self.sharedVariables:
            initBodyString += s.emit() + '\n';

        initBodyString += '\n#endpoint global variables section\n'
        for s in self.endpointVariables:
            initBodyString += s.emit() + '\n';
        
        returnString = indentString(initHeaderString,1);
        returnString += indentString(initBodyString,2);
        return returnString;


def indentString(string,indentAmount):
    '''
    @param {String} string -- Each line in this string we will insert
    indentAmount number of tabs before and return the new, resulting
    string.
    
    @param {Int} indentAmount 

    @returns {String}
    '''
    splitOnNewLine = string.split('\n');
    returnString = '';

    indenter = '';
    for s in range(0,indentAmount):
        indenter += '    ';
    
    for s in splitOnNewLine:
        returnString += indenter + s + '\n';

    return returnString;
    
class Variable():
    def __init__(self,name,val=None):
        self.name = name;
        self.val = None;

    def emit(self):
        print('\n\nThis is self.name: ');
        print(self.name);
        print('\n\n');
        returnString = self.name;
        returnString += ' = ';
        
        if (self.val == None):
            returnString += 'None';
        else:
            returnString += self.val;
        returnString += ';';
        
        return returnString;
