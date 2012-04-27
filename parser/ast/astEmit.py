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

    else:
        print('\nIn emitter.  Not sure what to do with label ');
        print(astNode.label);
        print('\n\n');

        

class ProtocolObject():
    def __init__(self, name):
        self.name = name;
        self.ept1 = None;
        self.ept2 = None;

        

class Endpoint():
    def __init__(self,name):
        self.name = name;
        self.publicMethods = [];
        self.internalMethods = [];
        
        self.msgReceiverMethods = [];
        self.msgSendMethods = [];

        self.sharedVariables = [];

        self.endpointVariables = [];
