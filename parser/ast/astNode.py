#!/usr/bin/python

import sys;
sys.path.append('d3');
import treeDraw;
from astLabels import *;
from astTypeCheckStack import TypeCheckContextStack;

def indentText(text,numIndents):
    returner = '';
    for s in range(0,numIndents):
        returner += '\t'
    returner += text;
    return returner;

def isEmptyAstNode(node):
    return (node.type == "EMPTY");

        
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

            

    def typeCheck(self,progText,typeStack=None):
        #based on types of children, check my type.  Also, pass up
        #line numbers.
        
        if ((self.label != AST_ROOT) and (typeStack == None)):
            print('\nError.  Must have typeStack unless root node\n');
            assert(False);
        elif(self.label == AST_ROOT):
            typeStack = TypeCheckContextStack();

            
        if ((self.label == AST_ROOT) or
            (self.label == AST_SHARED_SECTION) or
            (self.label == AST_ENDPOINT_GLOBAL_SECTION) or
            (self.label == AST_ENDPOINT_FUNCTION_SECTION)):
            #each of these create new contexts.  don't forget to
            #remove several of them at the bottom of the function.
            #note: do not have ast_function_body here because need to
            #create a new context before get into function body so
            #that we can catch arguments passed into the function.
            
            typeStack.pushContext();


        if(self.label == AST_ROOT):
            #top of program

            #getting protocol object name
            typeStack.protObjName = self.children[0].value;

            #handling alias section
            aliasSection = self.children[1];

            #endpoint 1
            typeStack.endpoint1 = aliasSection.children[0].value; 
            typeStack.endpoint1LineNo = aliasSection.children[0].lineNo;

            #endpoint 2
            typeStack.endpoint2 = aliasSection.children[1].value; 
            typeStack.endpoint2LineNo = aliasSection.children[1].lineNo;
            
            if (typeStack.endpoint1 == typeStack.endpoint2):
                errorFunction('Cannot use same names for endpoints',[typeStack.endpoint1,typeStack.endpoint2],[typeStack.endpoint1LineNo,typeStack.endpoint2LineNo],progText);

            #get into shared section
            #note: shared section should leave its context on the stack.
            self.children[3].typeCheck(progText,typeStack);

            #check one endpoint
            self.children[4].typeCheck(progText,typeStack);

            print('\nWarning, still need to add other endpoint to parser for checking\n');
            
            #go back and type check trace items.  see notes in
            #corresponding elif.
            self.children[2].typeCheck(progText,typeStack);
                

        elif(self.label == AST_TRACE_SECTION):
            '''
            need to check that first part of all TraceItems correspond
            to an Endpoint.
            need to check that alternate between Endpoints
            need to check that no two traces begin with same TraceItem
            need to check to ensure all functions referenced match
            with msg_send and msg_receive (probably can't do that part
            at this point.  Maybe later).
            '''
            print('\nTo do: still must type check trace section\n');

        elif(self.label == AST_SHARED_SECTION):
            #each child will be an annotated declaration.
            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif(self.label == AST_ANNOTATED_DECLARATION):
            # the type of this identifier
            #reset my type to it.
            self.type = self.children[1].value;
            currentLineNo = self.children[1].lineNo;
            if (len(self.children) == 4):
                #have an initializer too.
                self.children[3].typeCheck(progText,typeStack);
                assignType = self.children[3].type;
                if (assignType != self.type):
                    if (assignType == None):
                        assignType = '<None>';
                    errorString = 'Assigned type [' + assignType + '] does not ';
                    errorString += 'match declared type [' + self.type + '].';
                    errorFunction(errorString,[self],[currentLineNo],progText);

            #actually store the new type
            identifierName = self.children[2].value;
            existsAlready = typeStack.getIdentifierElement(identifierName);
            if (existsAlready != None):
                errorFunction('Already have an identifier named ' + identifierName,[self],[currentLineNo, existsAlready.lineNo],progText);
            else:
                if (typeStack.getFuncIdentifierType(identifierName)):
                    errText = 'Already have a function named ' + identifierName;
                    errText += '.  Therefore, cannot name an identifier with this name.';
                    errorFunction(errText,[self,existsAlready.astNode],[currentLineNo,existsAlready.lineNo],progText);

                    
                typeStack.addIdentifier(identifierName,self.type,self,currentLineNo);
            
        elif(self.label == AST_NUMBER):
            self.type = TYPE_NUMBER;
        elif(self.label == AST_STRING):
            self.type = TYPE_STRING;
        elif(self.label == AST_BOOL):
            self.type = TYPE_BOOL;
        elif(self.label == AST_FUNCTION_CALL):
            print('\nNeed to finish type checking for AST_FUNCTION_CALL\n');

        elif (self.label == AST_TYPE):
            self.type = self.value;

            
        elif(self.label == AST_ENDPOINT):
            #check if endpoint name matches previous endpoint name
            endName = self.children[0].value;
            currentLineNo = self.children[0].lineNo;
            if (not typeStack.isEndpoint(endName)):
                errMsg = 'Endpoint named ' + endName + ' was not defined at top of file ';
                errMsg = ' are you sure your endpoints match?';
                errorFunction(errMsg,[self],[currentLineNo,typeStack.endpoint1LineNo,typeStack.endpoint2LineNo],progText);

            #check endpoint body section
            self.children[1].typeCheck(progText,typeStack);


        elif(self.label == AST_ENDPOINT_BODY_SECTION):
            #typecheck global section
            self.children[0].typeCheck(progText,typeStack);
            #check function section.
            self.children[1].typeCheck(progText,typeStack);

            #note: perform extra pop for stack that endpoint global
            #section put on.
            typeStack.popContext();

        elif(self.label == AST_ENDPOINT_GLOBAL_SECTION):

            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif(self.label == AST_DECLARATION):
            declaredType = self.children[0].value;
            name = self.children[1].value;
            currentLineNo = self.children[0].lineNo;
            if (len(self.children) == 3):
                self.children[2].typeCheck(progText,typeStack);
                rhsType = self.children[2].type;
                if (rhsType != declaredType):
                    errMsg = 'Type mismatch for variable named "' + name + '".';
                    errMsg += '  Declared with type [' + declaredType + '], but ';
                    errMsg += 'assigned to type [' + rhsType + '].';
                    errorFunction(errMsg,[self],[currentLineNo],progText);

                    
            #check if already have a function or variable with the
            #targetted name.
            prevId = typeStack.getIdentifierElement(name);
            prevFunc = typeStack.getFuncIdentifierType(name);
            if ((prevId != None) or (prevFunc != None)):
                nodes =[self];
                lineNos = [currentLineNo];
                if (prevId != None):
                    nodes.append(prevId.astNode);
                    lineNos.append(prevId.lineNum);
                if (prevFunc != None):
                    nodes.append(prevFunc.element.astNode);
                    lineNos.append(prevId.element.lineNum);

                errMsg = 'Error trying to name a variable "' + name;
                errMsg += '".  Already have a function or variable with ';
                errMsg += 'the same name.'
                errorFunction(errMsg,nodes,lineNos,progText);
                    
                    
            typeStack.addIdentifier(name,declaredType,self,currentLineNo);
            self.type = declaredType;

        elif(self.label == AST_IDENTIFIER):
            name = self.value;
            typer = typeStack.getIdentifierType(name);
            if (typer == None):
                errMsg = 'Cannot infer type of ' + name + '.  Are you sure it is valid?';
                errorFunction(errMsg,[self],[self.lineNo],progText);
                self.type = 'Undefined';
            else:
                self.type = typer;
                
            
        elif(self.label == AST_ENDPOINT_FUNCTION_SECTION):
            # this just type checks the headers of each function.
            # Have to insert the header of each function
            for s in self.children:
                s.functionDeclarationTypeCheck(progText,typeStack);

            # now we type check the bodies of each function
            for s in self.children:
                s.typeCheck(progText,typeStack);
                

        elif ((self.label == AST_PUBLIC_FUNCTION) or
              (self.label == AST_FUNCTION) or
              (self.label == AST_MSG_SEND_FUNCTION) or
              (self.label == AST_MSG_RECEIVE_FUNCTION)):
            '''
            begins type check for body of the function, this code
            pushes arguments into context and then calls recursive
            type check on function body itself.
            '''

            ## create a new type context to insert intermediate data
            ## in.  context is popped at the end of the elif statement.
            typeStack.pushContext();
            funcName = self.children[0].value;            

            stackFunc = typeStack.getFuncIdentifierType(funcName);
            
            #set my line number to be the line number of when the
            #function type was declared.
            self.lineNo = self.children[0].lineNo;
            
            if (stackFunc == None):
                errMsg = 'Behram error: should have inserted function ';
                errMsg += 'with name "' + funcName + '" into type stack ';
                errMsg += 'before type checking function body.'
                print('\n\n');
                print(errMsg);
                print('\n\n');
                assert(False);

            #when we are checking function body, any return statement
            #that we hit should return something of the type specfied
            #by the return type here.
            typeStack.setShouldReturn(stackFunc.getReturnType());


            #insert passed in arguments into context;
            
            if ((self.label == AST_PUBLIC_FUNCTION) or (self.label == AST_FUNCTION)):
                funcDeclArgListIndex = 2;
                funcBodyIndex = 3;
            elif ((self.label == AST_MSG_SEND_FUNCTION) or (self.label == AST_MSG_RECEIVE_FUNCTION)):
                funcDeclArgListIndex = 1;
                funcBodyIndex = 2;
            else:
                errMsg = '\nBehram error: invalid function ';
                errMsg += 'type when type checking functions\n';
                print(errMsg);
                

            #add all arguments passed in in function declaration to
            #current context.
            self.children[funcDeclArgListIndex].typeCheck(progText,typeStack);
            

            # type check the actual function body
            self.children[funcBodyIndex].typeCheck(progText,typeStack);
            
            ## remove the created type context
            typeStack.popContext();


        elif(self.label == AST_FUNCTION_BODY):
            for s in self.children:
                s.typeCheck(progText,typeStack);

        elif (self.label == AST_FUNCTION_DECL_ARGLIST):
            #iterate through each individual declared argument
            for s in self.children:
                s.typeCheck(progText,typeStack);


        elif (self.label == AST_FUNCTION_DECL_ARG):
            '''
            for declared argument, checks for its collision
            with existing variables and functions, and then inserts
            it into a typestack context.
            '''
            self.lineNo = self.children[0].lineNo;
            argType = self.children[0].value;
            argName = self.children[1].value;

            collisionObj = typeStack.checkCollision(argName,self);

            if (collisionObj != None):
                #FIXME: for this error message, may want to
                #re-phrase with something about scope, so do not
                #take the wrong error message away.
                    
                errMsg = 'Error trying to name an argument "';
                errMsg += argName + '" in your function.  ';
                errMsg += 'You already have a function or variable ';
                errMsg += 'with the same name.';

                errorFunction(errMsg,collisionObj.nodes,collisionObj.lineNos,progText);
            else:
                typeStack.addIdentifier(argName,argType,self,self.lineNo);
                
        else:
            print('\nLabels that still need type checking: ');
            print('\t' + self.label);
                
            
            
        #remove the new context that we had created.  Note: shared
        #section is intentionally missing.  Want to maintain that 
        #context while type-checking the endpoint sections.
        #skip global section too.
        if ((self.label == AST_ROOT) or
            (self.label == AST_ENDPOINT_FUNCTION_SECTION)):
            
            typeStack.popContext();



    def functionDeclarationTypeCheck(self, progText,typeStack):
        '''
        Takes a node of type public function, ast function, message
        send function, or message receive function.  Does not set any
        types itself, but rather loads functions into the typeStack
        itself.
        '''
        if ((self.label != AST_PUBLIC_FUNCTION) and
            (self.label != AST_FUNCTION) and
            (self.label != AST_MSG_SEND_FUNCTION) and
            (self.label != AST_MSG_RECEIVE_FUNCTION)):
            print('\nError, sending an incorrect tag to be loaded into functionDeclarationTypeCheck\n');
            assert(False);

            
        funcName = self.children[0].value;            
        self.lineNo = self.children[0].lineNo;
        

        if ((self.label == AST_PUBLIC_FUNCTION) or (self.label == AST_FUNCTION)):
            #get declared return type (only applicable for functions and public functions)
            self.children[1].typeCheck(progText,typeStack);
            returnType = self.children[1].type;
            argDeclIndex = 2;
        else:
            #msg send and msg receive functions do not have declared
            #return types (for now).  use the return type for each
            returnType = TYPE_MSG_SEND_FUNCTION if (self.label == AST_MSG_SEND_FUNCTION) else TYPE_MSG_RECEIVE_FUNCTION;
            argDeclIndex = 1;



        #get types of function arguments
            
        #add a context to type stack for arg declarations and pop it
        #later so that arg decl arguments do not persist after the
        #type check of arg text.
        typeStack.pushContext();
        self.children[argDeclIndex].typeCheck(progText,typeStack);
        typeStack.popContext();

        args = self.children[argDeclIndex].children;
            
        argTypeList = [];
        for t in args:
            argTypeList.append(t.type);

        collisionObj = typeStack.checkCollision(funcName,self);
        if (collisionObj != None):
            #FIXME: for this error message, may want to
            #re-phrase with something about scope, so do not
            #take the wrong error message away.
            errMsg = 'Error trying to name a function "' + funcName;
            errMsg += '".  Already have a function or variable with ';
            errMsg += 'the same name.'

            errorFunction(errMsg,collisionObj.nodes,collisionObj.lineNos,progText);
        else:
            typeStack.addFuncIdentifier(funcName,returnType,argTypeList,self,self.lineNo);

        

            
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


ERROR_NUM_LINES_EITHER_SIDE = 4;



def errorFunction(errorString,astNodes,lineNumbers,progText):
    '''
    @param {String} errorString -- Text associated with error.
    @param {Array < AstNode>} astNodes -- Contains all ast nodes associated with the error.
    @param {Array < Int> } lineNumbers -- Contains all line numbers associated with error.
    @param {String} progText -- The source text of the program.
    '''
    
    print('\n\n');
    print('*************************');
    print('Error in type checking:');
    print(errorString);

    print('-------\nAST node labels:');
    for s in astNodes:
        print(s.label)
        
    print('-------\nLine numbers:');
    for s in lineNumbers:
        print(s);

    programTextArray = progText.split('\n');
    print('-------\nProgram text:');
    for errorLine in lineNumbers:
        print('\n\n');
        lowerLineNum = max(0,errorLine - ERROR_NUM_LINES_EITHER_SIDE);
        upperLineNum = min(len(programTextArray),errorLine + ERROR_NUM_LINES_EITHER_SIDE);

        for s in range(lowerLineNum, upperLineNum):
            errorText = '';
            errorText += str(s+1);

            if (s == errorLine -1):
                errorText += '*   ';
            else:
                errorText += '    ';
                    
            errorText += programTextArray[s];
            print(errorText);

        
    print('*************************');
    print('\n\n');

