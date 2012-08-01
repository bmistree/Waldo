#!/usr/bin/python

import sys;
import os;
curDir = os.path.dirname(__file__);
sys.path.append(os.path.join(curDir,'typeCheck'));

import typeCheck as typeChecker;
import d3.treeDraw as treeDraw;


class AstNode():
    
    def __init__(self,_label,_lineNo=None,_linePos=None,_value=None):
        '''
        Only leaf nodes have values that are not None.
        (Things like Numbers, Strings, Identifiers, etc.)
        '''
        self.label    = _label;
        self.value    = _value;
        self.lineNo   = _lineNo;
        self.linePos  = _linePos;
        self.type     = None;
        self.note     = None;
        self.children = [];

    def setNote(self,note):
        self.note = note;
        
    def addChild(self, childToAdd):
        self.children.append(childToAdd);

    def prependChild(self,childToPrepend):
        self.children.insert(0,childToPrepend);
        
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
            
    def typeCheck(self,progText,typeStack=None,avoidFunctionObjects=False):
        return typeChecker.typeCheck(self,progText,typeStack);

    def toJSON(self,indentLevel=0,drawHigh=False):
        '''
        JSON format:
        {
            "name": "<self.label>",
            "type": "<self.type>",
            "value": <self.value>,
            "drawHigh": drawHigh
            "children": [
                   //recurse
              ]
        }
        '''
        #name print
        returner = indentText('{\n',indentLevel);
        returner += indentText('"name": "',indentLevel+1);
        returner += self.label;
        returner += '"';


        if (self.value != None):
            returner += ',\n';
            returner += indentText('"value": "',indentLevel+1);
            returner += self.value;
            returner += '"'

        
        if (self.type != None):
            returner += ',\n';
            returner += indentText('"type": "',indentLevel+1);
            returner += self.type;
            returner += '"'


        #print drawHigh
        returner += ',\n';
        returner += indentText('"drawHigh": ',indentLevel+1);
        if (drawHigh):
            returner += 'true';
        else:
            returner += 'false';
            
            
        #child print
        if (len(self.children) != 0):
            returner += ',\n';
            returner += indentText('"children": [\n',indentLevel+1);

            for s in range(0,len(self.children)):
                drawHigh = not drawHigh;
                returner += self.children[s].toJSON(indentLevel+1,drawHigh);
                if (s != (len(self.children) -1 )):
                    returner += ',\n';
            returner += ']';

        #close object
        returner += '\n' + indentText('}',indentLevel);
        return returner;

    
    def drawPretty(self,filename,pathToD3='d3',width=5000,height=3000):
        '''
        For now, an ugly way of generating a pretty view 
        '''

        #default args did not work how I anticipated.
        if (pathToD3 == None):
            pathToD3 = 'd3';
        if(width == None):
            width = 5000;
        if(height==None):
            height = 3000;
            
        treeDraw.prettyDrawTree(filename=filename,data=self.toJSON(),pathToD3=pathToD3,width=width,height=height);


def indentText(text,numIndents):
    returner = '';
    for s in range(0,numIndents):
        returner += '\t'
    returner += text;
    return returner;


