#!/usr/bin/env python

import sys, os

import waldo.parser.ast.typeCheck.typeCheck as typeChecker
import d3.treeDraw as treeDraw


class AstNode():

    # quite a hack.  the emitter occasionally needs to create nodes on
    # the fly, with annotation values that do not conflict with any
    # other annotation values.  Can use these to handle this
    NULL_ANNOTATION_NAME = ''
    NULL_ANNOTATION_TYPE_HUMAN_READABLE = ''
    
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
        self.external = None;
        self.note     = None;
        self.children = [];

        # All identifiers get a slice annotation (note that other
        # nodes, such as literals, do not).  The slice annotation
        # provides a name for an identifier.  So if you use the same
        # identifier multiple times in a function, each of those
        # identifier's nodes will have the same slice annotation name.
        # (Of course, if you use the same identifier name to name
        # different pieces of data [eg. each endpoint has a global
        # variable with the same name], then the astnodes for each
        # will have different sliceAnnotationName-s.
        self.sliceAnnotationName = None;
        # @see TypeStack.IDENTIFIER_TYPE_*.  The slice annotation type
        # tells us whether this node is a shared/endpoint
        # global/function argument/ etc.
        self.sliceAnnotationType = None;
        # The TypeStack.IDENTIFIER_TYPE_*-s are all integers, which
        # makes it harder for a human to reason about when debugging.
        # This is the human-readable string that corresponds to each
        # slice annotation, and must match sliceAnnotationType.  For
        # instance, if self.sliceAnnotationType is
        # TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT, then the
        # self.sliceAnnotationTypeHumanReadable should be "function
        # argument"
        self.sliceAnnotationTypeHumanReadable = None; 

    def setSliceAnnotation(
        self,annotateName,annotateType,annotateTypeHumanReadable):
        '''
        @see documentation for self.sliceAnnotationName and
        sliceAnnotationType above.

        Should only be called from slicer code.
        '''
        self.sliceAnnotationName = annotateName;
        self.sliceAnnotationType = annotateType;
        self.sliceAnnotationTypeHumanReadable = annotateTypeHumanReadable;

    def _debugErrorIfHaveNoAnnotation(self,calledFrom):
        if self.sliceAnnotationName == None:
            errMsg = '\nBehram error: requesting the annotation of ';
            errMsg += 'an astNode that does not have one.  The ';
            errMsg += 'requester is ' + calledFrom + '.\n';
            print(errMsg);
            assert(False);

            
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
            "sliceAnnotationName": "<self.sliceAnnotationName>",
            "sliceAnnotationType": "<self.sliceAnnotationTypeHumanReadable>",
            "drawHigh": drawHigh,
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


        if self.value != None:
            returner += ',\n';
            returner += indentText('"value": "',indentLevel+1);
            if isinstance (self.value,basestring):
                returner += escapeQuotes(self.value);
            else:
                returner += self.value;
            returner += '"';

        if self.type != None:
            returner += ',\n';
            returner += indentText('"type": "',indentLevel+1);
            returner += escapeQuotes(self.type);
            returner += '"';

        if self.sliceAnnotationName != None:
            returner += ',\n';
            returner += indentText('"sliceAnnotationName": "',indentLevel+1);
            returner += self.sliceAnnotationName;
            returner += '"';

        if self.sliceAnnotationTypeHumanReadable != None:
            returner += ',\n';
            returner += indentText('"sliceAnnotationType": "',indentLevel+1);
            returner += self.sliceAnnotationTypeHumanReadable;
            returner += '"';
        
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


def escapeQuotes(text):
    return text.replace('"','\\"');
