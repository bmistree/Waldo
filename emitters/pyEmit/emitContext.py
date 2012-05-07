#!/usr/bin/python

'''
Each endpoint has its own context.  This context is used to store the
shared variables and global variables for a single endpoint.  The
endpoint itself keeps track of two copies of each context: "committed"
and "intermediate".

The committed context keeps track of snapshotted variables after 

The intermediate context keeps track of variables that are not 

Intermediate results are not visible to public methods.
'''

import emitHelper;

def emitContextClass(endpoint):
    '''
    @returns {String} corresponding to context class for this endpoint
    (context stores all shared and global variables for this endpoint.
    '''
    
    classHead = """
class %s():
"""  % endpoint.contextClassName;

    #generate body of class
    initMethod = emitInit(endpoint,1);
    copyMethod = emitCopy(endpoint,1);
    generateEnvironmentDataMethod = emitGenerateEnvironmentData(endpoint,1);
    updateEnvironmentDataMethod = emitUpdateEnvironmentData(endpoint,1);

    #piece together body of class
    classBody = '';
    classBody += initMethod + '\n';
    classBody += copyMethod + '\n';
    classBody += generateEnvironmentDataMethod + '\n';
    classBody += updateEnvironmentDataMethod + '\n';

    return classHead + emitHelper.indentString(classBody,1);

    
    

def emitUpdateEnvironmentData(endpoint,indentLevel):

    updateEnvironmentDataHead = '''
def updateEnvironmentData(self,sharedVarDict):
'''

    updateEnvironmentDataBody = """
'''
EXACT
        
@param {dict} sharedVarDict -- Keys of dictionary are names of
global variables.  Values are the actual values of the
associated global variables.
'''

# run through shared variables dictionary and update all
# shared variables held by this context to those provided in
# sharedVarDict.  (A lot of these clumsy eval forms stem from
# wanting to make the code emitter of the compiler as easy to
# write as possible.)
for s in sharedVarDict.keys():
""";
    
    # need to use indent consistent with indents produced by
    # indentString function for valid python.
    forBody = '''

toExecSetSharedStr = 'self.%s = sharedVarDict["%s"];' % (s,s);
obj = compile(toExecSetSharedStr,'','exec');
eval(obj);

''';

    updateEnvironmentDataBody += emitHelper.indentString(forBody,1);

    indentedUpdateEnvironmentHead = emitHelper.indentString(updateEnvironmentDataHead,indentLevel);
    indentedUpdateEnvironmentBody = emitHelper.indentString(updateEnvironmentDataBody,indentLevel+1);

    return indentedUpdateEnvironmentHead + '\n' + indentedUpdateEnvironmentBody;






    
def emitGenerateEnvironmentData(endpoint,indentLevel):

    generateEnvironmentDataHead = '''
def generateEnvironmentData(self):
'''

    generateEnvironmentDataBody = """
'''
NOT EXACT
        
Should take all the shared variables and write them to a
dictionary.  The context of the other endpoint should be able
to take this dictionary and re-constitute the global variables
from it from its updateEnvironmentData function.
'''

returner = {};

"""

    #only want to copy the shared data
    for s in endpoint.sharedVariables:
        usedName = s.getUsedName();
        generateEnvironmentDataBody += 'returner["%s"] = self.%s;\n' % (usedName,usedName);

    generateEnvironmentDataBody += '\nreturn returner;\n';

    indentedGenerateEnvironmentDataHead = emitHelper.indentString(generateEnvironmentDataHead,indentLevel);
    indentedGenerateEnvironmentDataBody = emitHelper.indentString(generateEnvironmentDataBody,indentLevel + 1);

    return indentedGenerateEnvironmentDataHead + '\n' + indentedGenerateEnvironmentDataBody;

    
def emitCopy(endpoint,indentLevel):

    copyHead = '''
def copy(self):
''';

    copyBody = '''
returner = _PingContext(self._myPriority,self._theirPriority);
returner._myPriority = self._myPriority;
returner._theirPriority = self._theirPriority;

        
#note, may need to perform deep copies of these as well.

'''

    #actually specify the data that need to be copied over;
    copyBody += '\n#####shared variables####\n';
    for s in endpoint.sharedVariables:
        copyBody += 'returner.' + s.getUsedName() + '=';
        copyBody += 'self.' + s.getUsedName() + ';\n';

    copyBody += '\n\n#####endpoint global variables####\n';
    for s in endpoint.endpointVariables:
        copyBody += 'returner.' + s.getUsedName() + '=';
        copyBody += 'self.' + s.getUsedName() + ';\n';
    

    copyBody += '''

return returner;
''';

    indentedCopyHead = emitHelper.indentString(copyHead,indentLevel);
    indentedCopyBody = emitHelper.indentString(copyBody,indentLevel + 1);
    returnString = indentedCopyHead + '\n' + indentedCopyBody;
    
    return returnString;


def emitInit(endpoint,indentLevel):
    initHead = """
def __init__(self,_myPriority,_theirPriority):
"""
    initBody = """
# In cases where to sides simultaneously send, indicates which
# side should send first (the one with the greater priority).
self._myPriority = _myPriority;
self._theirPriority = _theirPriority;
""";

    initBody += '### emitting shared variables \n'
    for s in endpoint.sharedVariables:
        initBody += s.emit('self.');
        initBody += '\n';

    initBody += '### emitting endpoint global variables \n'            
    for s in endpoint.endpointVariables:
        initBody += s.emit('self.');
        initBody += '\n';

    indentedInitHead = emitHelper.indentString(initHead,indentLevel);
    indentedInitBody = emitHelper.indentString(initBody,indentLevel+1);
    
    return indentedInitHead + '\n' + indentedInitBody;
