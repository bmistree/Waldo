#!/usr/bin/python

import sys;
sys.path.append('d3');
import treeDraw

def indentText(text,numIndents):
    returner = '';
    for s in range(0,numIndents):
        returner += '\t'
    returner += text;
    return returner;

def isEmptyAstNode(node):
    return (node.type == "EMPTY");

        
class AstNode():
    
    def __init__(self,_type,_lineNo=None,_linePos=None,_value=None):
        '''
        Only leaf nodes have values that are not None.
        (Things like Numbers, Strings, Identifiers, etc.)
        '''
        self.type = _type;
        self.value = _value;
        self.lineNo = _lineNo;
        self.linePos = _linePos;
        self.children = [];

        
    def addChild(self, childToAdd):
        self.children.append(childToAdd);

        
    def addChildren(self, childrenToAdd):
        for s in childrenToAdd:
            self.children.append(s);
        
    def getChildren(self):
        return self.children;

    def printAst(self,filename=None):
        text = self.toJSON();
        if (filename != None):
            filer = open(filename,'w');
            filer.write(text);
            filer.flush();
            filer.close();
        else:
            print(self.toJSON());


        
    def toJSON(self,indentLevel=0):
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
                returner += self.children[s].toJSON(indentLevel+1);
                if (s != (len(self.children) -1 )):
                    returner += ',\n';
            returner += ']';

        #close object
        returner += '\n' + indentText('}',indentLevel);
        return returner;

    
    def drawPretty(self,filename,pathToD3='d3',width=1000,height=1000):
        '''
        For now, an ugly way of generating a pretty view 
        '''

        #default args did not work how I anticipated.
        if (pathToD3 == None):
            pathToD3 = 'd3';
        if(width == None):
            width = 1000;
        if(height==None):
            height = 1000;
            
        treeDraw.prettyDrawTree(filename=filename,data=self.toJSON(),pathToD3=pathToD3,width=width,height=height);
