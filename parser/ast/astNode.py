#!/usr/bin/python

def indentText(text,numIndents):
    returner = '';
    for s in range(0,numIndents):
        returner += '\t'
    returner += text;
    return returner;
        
        
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


        
    def toJson(self,indentLevel=0):
        '''
        JSON format:
        {
            "name": "<self.type>: <self.value>",
            "children": [
                   //recurse
              ]
        }
        '''
        #name print
        returner = indentText('{\n',indentLevel);
        returner += indentText('"name": "',indentLevel+1);
        returner += self.type;
        if (self.value != None):
            returner += ':  ' + self.value;
        returner += '"';

        #child print
        if (len(self.children) != 0):
            returner += ',\n';
            returner += indentText('"children": [\n',indentLevel+1);

            for s in range(0,len(self.children)):
                returner += self.children[s].toJson(indentLevel+1);
                if (s != (len(self.children) -1 )):
                    returner += ',\n';
            returner += ']';

        #close object
        returner += '\n' + indentText('}',indentLevel);
        return returner;
        
