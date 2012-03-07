#!/usr/bin/python


class AstNode():

    
    def __init__(self,_type,_value=None):
        '''
        Only leaf nodes have values that are not None.
        (Things like Numbers, Strings, Identifiers, etc.)
        '''
        self.type = _type;
        self.value = _value;
        self.children = [];

        
    def addChild(self, childToAdd):
        self.children.append(childToAdd);

        
    def addChildren(self, childrenToAdd):
        for s in childrenToAdd:
            self.children.append(s);
        
    def getChildren(self):
        return self.children;

    def printAst(self):
        print('\n\nGot into printAst\n\n');
