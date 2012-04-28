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

        '''
        takes a variable name and returns what the variable should
        actually be named in the program text.
        '''
        self.mappings = {};
        

        
    def addShared(self,sharedName,sharedVal):
        self.checkUsageError('addShared');

        sharedName = self.addVarOrFuncNameToMap(sharedName);
        sharedVar = Variable (sharedName,sharedVal);
        self.ept1.sharedVariables.append(sharedVar);
        self.ept2.sharedVariables.append(sharedVar);

    
        
    def addVarOrFuncNameToMap(self,varName,root=True):
        '''
        self.mappings maps the name of the variable that the scripter
        used in Waldo source text to an internal name that does not
        conflict with any python keyword (eg, 'if', 'not', 'self', etc.)

        This function inserts the variable into this map, and returns
        with what name a variable with this name should take..
        '''
        self.checkUsageError('addVarOrFuncNameToMap');
        if (isPythonReserved(varName) or self.isAlreadyUsed(varName)):
            newName = self.addVarOrFuncNameToMap('_' + varName,False);
            if (root):
                self.mappings[varName] = newName;
            
            return newName;

        return varName;

    def isAlreadyUsed(self,varName):
        '''
        @returns True if another variable or function in the program
        already uses the name varName.  False otherwise.

        We know if another variable in the program is using the name
        varName if one of the values in the self.mappings dict is the
        same as varName.
        '''
        #FIXME: Inefficient

        for s in self.mappings.keys():
            if (self.mappings[s] == varName):
                return True;

        return False;
        
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

#From http://pentangle.net/python/handbook/node52.html
#I also personally added self.
PYTHON_RESERVED_WORD_DICT = {
    'self': True,
    'and':True,
    'assert':True,
    'break':True,
    'class':True,
    'continue':True,
    'def':True,
    'del':True,
    'elif':True,
    'else':True,
    'except':True,
    'exec':True,
    'finally':True,
    'for':True,
    'from':True,
    'global':True,
    'if':True,
    'import':True,
    'in':True,
    'is':True,
    'lambda':True,
    'not':True,
    'or':True,
    'pass':True,
    'print':True,
    'raise':True,
    'return':True,
    'try':True,
    'while':True,
    'Data':True,
    'Float':True,
    'Int':True,
    'Numeric':True,
    'Oxphys':True,
    'array': True,
    'close':True,
    'float':True,
    'int':True,
    'input':True,
    'open':True,
    'range':True,
    'type':True,
    'write':True,
    'zeros':True,
    'acos':True,
    'asin':True,
    'atan':True,
    'cos':True,
    'e':True,
    'exp':True,
    'fabs':True,
    'floor':True,
    'log':True,
    'log10':True,
    'pi':True,
    'sin':True,
    'sqrt':True,
    'tan':True
    }

def isPythonReserved(varName):
    '''
    @returns True if varName is a reserved word in python.  False
    otherwise.
    '''
    print('\nTesting: ' + varName + '\n');
    returner = varName in PYTHON_RESERVED_WORD_DICT;
    print(returner);
    print('\n\n');
    return returner;
    
    
        
class Endpoint():
    def __init__(self,name):
        self.name = name;

        #decided to make these arrays instead of dicts, because in
        #certain instances, order of declaration matters.  (for
        #instance, shared variables.)
        self.publicMethods = [];
        self.internalMethods = [];
        
        self.msgReceiverMethods = [];
        self.msgSendMethods = [];

        #list of Variable objects
        self.sharedVariables = [];
        self.endpointVariables = [];

    def varName(self,potentialName):
        '''
        @param {String} potentialName -- Waldo name of variable being
        used.

        @returns {String} either self.potentialName or potentialName,
        depending on whether the variable that is being assigned/used
        is a method of the endpoint's class or if it's not,
        respectively.
        '''
        #tradeoff of making the shared/endpoint/methods containers
        #arrays is that I actually have to iterate over full array to
        #check if potentialName exists in them.

        if (potentialName in self.mappings):
            potentialName = self.mappings[potentialName];
        
        for s in self.publicMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.internalMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.internalMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.msgReceiverMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;
            
        for s in self.msgSendMethods:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        #list of strings of variables
        for s in self.sharedVariables:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        for s in self.endpointVariables:
            if (s.name == potentialName):
                return 'self.' + potentialName;

        return potentialName;

        
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
