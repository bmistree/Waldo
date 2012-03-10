#!/usr/bin/python

import sys;
sys.path.append('../../lexer/')
from waldoLex import tokens;
from waldoLex import constructLexer;

from astNode import AstNode;
import ply.yacc as yacc;

#Program text that we are parsing.  Set in getParser function.  Allows
#us to output surrounding lines when reporting an error.
ProgramText = None;
ERROR_NUM_LINES_EITHER_SIDE = 4;

# Overall Structure:
# NameSection
# EndpointAliasSection
# TraceSection
# SharedSection
# EndpointSection
# EndpointSection ... not necessary if have symmetric names....


#AST_TOKENS
AST_ROOT = 'ROOT';
AST_PROT_OBJ_NAME = 'PROT_OBJ_NAME';
AST_ENDPOINT_ALIAS_SECTION = 'ALIAS_SECTION';
#traces
AST_TRACE_SECTION = 'TRACE_SECTION';
AST_TRACE_BODY_SECTION = 'TRACE_BODY_SECTION';   #INTERMEDIATE
AST_TRACE_ITEM = 'TRACE_ITEM';
AST_TRACE_LINE = 'TRACE_LINE';

#shared
AST_SHARED_SECTION = 'SHARED_SECTION';
AST_SHARED_BODY_SECTION = 'SHARED_BODY_SECTION'; #INTERMEDIATE
AST_ANNOTATED_DECLARATION = 'ANNOTATED_DECLARATION';

#endpoint
AST_ENDPOINT = 'ENDPOINT';
AST_ENDPOINT_BODY_SECTION = 'ENDPOINT_BODY_SECTION';
AST_ENDPOINT_GLOBAL_SECTION = 'ENDPOINT_GLOBAL_SECTION';
AST_ENDPOINT_FUNCTION_SECTION = 'ENDPOINT_FUNCTION_SECTION';


#functions
##function types
AST_PUBLIC_FUNCTION = 'PUBLIC_FUNCTION';
AST_FUNCTION = 'FUNCTION';
AST_MSG_SEND_FUNCTION = 'MSG_SEND_FUNCTION';
AST_MSG_RECEIVE_FUNCTION = 'MSG_RECEIVE_FUNCTION';


##function helpers
AST_FUNCTION_BODY = 'FUNCTION_BODY'; #provides new scope
AST_FUNCTION_DECL_ARGLIST = 'FUNCTION_DECL_ARGLIST';
AST_FUNCTION_DECL_ARG = 'FUNCTION_DECL_ARG';
AST_FUNCTION_ARGLIST = 'FUNCTION_ARGLIST';
AST_FUNCTION_BODY_STATEMENT = 'FUNCTION_BODY_STATEMENT';

##conditional expressions
AST_CONDITION_STATEMENT = 'CONDITION_STATEMENT';
AST_IF_STATEMENT = 'IF_STATEMENT';
AST_ELSE_IF_STATEMENTS = 'ELSE_IF_STATEMENTS';
AST_ELSE_IF_STATEMENT = 'ELSE_IF_STATEMENT';
AST_ELSE_STATEMENT = 'ELSE_STATEMENT';
AST_SINGLE_OR_MULTILINE_CURLIED_BLOCK = 'SINGLE_OR_MULTILINE_BLOCK';
AST_BOOLEAN_CONDITION = 'BOOLEAN_CONDITION';
AST_NOT_EXPRESSION = 'NOT_EXPRESSION';



##boolean expressions
AST_AND = 'AND';
AST_OR  = 'OR';
AST_BOOL_EQUALS = '==';
AST_BOOL_NOT_EQUALS = '!=';


AST_NON_BOOLEAN_STATEMENT = 'NON_BOOLEAN_STATEMENT';
AST_RETURNABLE_EXPRESSION = 'RETURNABLE_EXPRESSION';
AST_INTERNAL_RETURNABLE_EXPRESSION = 'INTERNAL_RETURNABLE_EXPRESSION';
AST_ASSIGNMENT_STATEMENT = 'ASSIGNMENT_STATEMENT';
AST_DECLARATION = 'DECLARATION';
AST_STRING = 'STRING_LITERAL';
AST_NUMBER = 'NUMBER_LITERAL';
AST_BOOL = 'BOOL_LITERAL';
AST_TYPE = 'TYPE';
AST_IDENTIFIER = 'IDENTIFIER';
AST_EMPTY = 'EMPTY';

#note: otherwise, starts at first rule.  
start = 'RootExpression';
#need to have something named lexer for parser to chew into
lexer = constructLexer();


def p_RootExpression(p):
    'RootExpression : NameSection EndpointAliasSection TraceSection SharedSection EndpointSection';
    p[0] = AstNode(AST_ROOT,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1],p[2],p[3],p[4],p[5]]);
    

def p_NameSection(p):
    'NameSection : Identifier'
    p[0] = AstNode(AST_PROT_OBJ_NAME,p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);

def p_EndpointAliasSection(p):
    'EndpointAliasSection : ENDPOINT Identifier SEMI_COLON ENDPOINT Identifier SEMI_COLON';
    p[0] = AstNode(AST_ENDPOINT_ALIAS_SECTION,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[2], p[5]]);

def p_TraceSection(p):
    'TraceSection : TRACES CURLY_LEFT TraceBodySection CURLY_RIGHT';
    #note: this is an intermediate production, and will get skipped.
    p[0] = AstNode(AST_TRACE_SECTION,p.lineno(0),p.lexpos(0));
    
    #getting TraceBodySection's children removes it as an intermediate node.
    p[0].addChildren(p[3].getChildren());


def p_TraceItem(p):
    'TraceItem : Identifier DOT Identifier'
    #Each TraceItem is connected by arrows in Trace section
    # TraceItem -> TraceItem -> TraceItem;
    p[0] = AstNode(AST_TRACE_ITEM,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[1],p[3]]);

def p_TraceBodySection(p):
    '''TraceBodySection : TraceLine SEMI_COLON TraceBodySection
                        | TraceLine SEMI_COLON''';
    #note: currently, cannot have empty trace body section.
    p[0] = AstNode(AST_TRACE_BODY_SECTION,p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);
    if(len(p) == 4):
        #flattens all TraceLines into siblings
        p[0].addChildren(p[3].getChildren());
    

def p_TraceLine(p):
    '''TraceLine : TraceItem  SEND_ARROW TraceLine
                 | TraceItem  '''

    p[0] = AstNode(AST_TRACE_LINE,p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);
    if (len(p) == 4):
        #have additional parts of trace body to grab.
        p[0].addChildren(p[3].getChildren());

def p_SharedSection(p):
    '''SharedSection : SHARED CURLY_LEFT SharedBodySection CURLY_RIGHT
                     | SHARED CURLY_LEFT CURLY_RIGHT''';

    p[0] = AstNode(AST_SHARED_SECTION,p.lineno(0),p.lexpos(0));
    if (not isEmptyNode(p[3])):
        p[0].addChildren(p[3].getChildren());
    else:
        p[0].addChild(p[3]);

def p_SharedBodySection(p):
    '''SharedBodySection : AnnotatedDeclaration SEMI_COLON SharedBodySection
                         | AnnotatedDeclaration SEMI_COLON'''
    p[0] = AstNode(AST_SHARED_BODY_SECTION, p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());

        
        
def p_AnnotatedDeclaration(p):
    '''AnnotatedDeclaration : Identifier CONTROLS Type Identifier 
                            | Identifier CONTROLS Type Identifier EQUALS Initializer'''
    p[0] = AstNode(AST_ANNOTATED_DECLARATION,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[1],p[3],p[4]]);
    
    if (len(p) == 7):
        #have an initialization statement to perform
        p[0].addChild(p[6]);

def p_Type(p):
    '''Type : NUMBER_TYPE
            | STRING_TYPE
            | LIST_TYPE
            | BOOL_TYPE'''
    p[0] = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),p[1]);


def p_Initializer(p):
    '''Initializer : Number
                   | Identifier
                   | String
                   | Bool
                   | FunctionCall
                   ''';
    p[0] = p[1];

    

def p_Number(p):
    '''Number : NUMBER '''
    p[0] = AstNode(AST_NUMBER,p.lineno(1),p.lexpos(1),p[1]);

    
def p_String(p):
    '''String : MULTI_LINE_STRING
              | SINGLE_LINE_STRING''';

    p[0] = AstNode(AST_STRING,p.lineno(1),p.lexpos(1),p[1]);
    

def p_Bool(p):
    '''Bool : TRUE
            | FALSE'''
    p[0] = AstNode(AST_BOOL,p.lineno(1),p.lexpos(1),p[1]);
    
    
    
def p_Identifier(p):
    'Identifier : IDENTIFIER';
    p[0] = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[1]);


def p_EndpointSection(p):
    '''EndpointSection : Identifier CURLY_LEFT EndpointBodySection CURLY_RIGHT
                       | Identifier CURLY_LEFT CURLY_RIGHT'''
    p[0] = AstNode(AST_ENDPOINT,p.lineno(0),p.lexpos(0));

    p[0].addChild(p[1]);
    if (len(p) == 5):
        p[0].addChild(p[3]);

def p_EndpointBodySection(p):
    '''EndpointBodySection : EndpointGlobalSection EndpointFunctionSection
                           | EndpointFunctionSection'''

    p[0] = AstNode(AST_ENDPOINT_BODY_SECTION,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1]]);
    if (len(p) == 3):
        p[0].addChild(p[2]);
    # p[0].addChildren([p[1],p[2]]);

def p_EndpointGlobalSection(p):
    '''EndpointGlobalSection : Declaration SEMI_COLON EndpointGlobalSection
                             | Declaration SEMI_COLON'''
    p[0] = AstNode(AST_ENDPOINT_GLOBAL_SECTION, p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());

def p_EndpointFunctionSection(p):
    '''EndpointFunctionSection :  PublicFunction EndpointFunctionSection
                               |  PublicFunction
                               |  Function EndpointFunctionSection
                               |  Function
                               |  MsgSendFunction EndpointFunctionSection
                               |  MsgSendFunction
                               |  MsgReceiveFunction EndpointFunctionSection
                               |  MsgReceiveFunction                               
                               '''
    
    p[0] = AstNode(AST_ENDPOINT_FUNCTION_SECTION,p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);
    if (len(p) == 3):
        p[0].addChildren(p[2].getChildren());


def p_MsgReceiveFunction(p):
    '''MsgReceiveFunction : MSG_RECEIVE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                          | MSG_RECEIVE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT  CURLY_RIGHT'''
    p[0] = AstNode(AST_MSG_RECEIVE_FUNCTION, p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[2],p[4]]);
    if (len(p) == 9):
        p[0].addChild(p[7]);


def p_MsgSendFunction(p):
    '''MsgSendFunction : MSG_SEND Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                       | MSG_SEND Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT  CURLY_RIGHT'''
    p[0] = AstNode(AST_MSG_SEND_FUNCTION, p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[2],p[4]]);
    if (len(p) == 9):
        p[0].addChild(p[7]);

    
def p_Function(p):
    '''Function : FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                | FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT  CURLY_RIGHT'''
    p[0] = AstNode(AST_FUNCTION, p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[2],p[4]]);
    if (len(p) == 9):
        p[0].addChild(p[7]);

    
        
def p_PublicFunction(p):
    '''PublicFunction : PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                      | PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT  CURLY_RIGHT'''
    
    p[0] = AstNode(AST_PUBLIC_FUNCTION, p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[3],p[5]]);
    if (len(p) == 10):
        p[0].addChild(p[8]);

def p_FunctionBody(p):
    '''FunctionBody : FunctionBody FunctionBodyStatement
                    | FunctionBodyStatement'''
    p[0] = AstNode(AST_FUNCTION_BODY, p.lineno(0),p.lexpos(0));
    if (len(p) == 3):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[2]);
    elif (len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nError statement length mismatch in FunctionBody\n');
        assert(False);

        
def p_FunctionBodyStatement(p):
    '''FunctionBodyStatement : Declaration SEMI_COLON
                             | AssignmentStatement SEMI_COLON
                             | ConditionStatement 
    '''
    p[0] = AstNode(AST_FUNCTION_BODY_STATEMENT,p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);

def p_ConditionStatement(p):
    '''ConditionStatement : IfStatement ElseIfStatements ElseStatement'''
    
    p[0] = AstNode(AST_CONDITION_STATEMENT,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1],p[2],p[3]]);


def p_IfStatement(p):
    '''IfStatement : IF BooleanCondition SingleLineOrMultilineCurliedBlock '''
    p[0] = AstNode(AST_IF_STATEMENT,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[2],p[3]]);

    
def p_ElseIfStatements(p):
    '''ElseIfStatements : Empty
                        | ElseIfStatements ElseIfStatement'''
    
    p[0] = AstNode(AST_ELSE_IF_STATEMENTS,p.lineno(0),p.lexpos(0));
    if (len(p) == 3):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[2]);

def p_ElseIfStatement(p):
    '''ElseIfStatement : ELSE_IF BooleanCondition SingleLineOrMultilineCurliedBlock'''
    p[0] = AstNode(AST_ELSE_IF_STATEMENT,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[2],p[3]]);

    
    
def p_ElseStatement(p):
    '''ElseStatement : Empty
                     | ELSE SingleLineOrMultilineCurliedBlock '''
    p[0] = AstNode(AST_ELSE_STATEMENT,p.lineno(0),p.lexpos(0));
    if (len(p) == 3):
        p[0].addChild(p[2]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nIncorrect match count in ElseStatement.\n');
        assert(False);


def p_SingleLineOrMultilineCurliedBlock(p):
    '''SingleLineOrMultilineCurliedBlock :  FunctionBodyStatement
                                         |  CURLY_LEFT FunctionBody CURLY_RIGHT
                                         |  CURLY_LEFT CURLY_RIGHT
    ''';
    

    if (len(p) == 2):
        p[0] = AstNode(AST_FUNCTION_BODY,p.lineno(0),p.lexpos(0));
        p[0].addChild(p[1]);        
    elif(len(p) == 4):
        p[0] = p[2];
    elif(len(p) == 3):
        p[0] = AstNode(AST_EMPTY);
    else:
        print('\nIncorrect match vector in SingleLineOrMultilineCurliedBlock\n');
        assert(False);

    
def p_BooleanCondition(p):
    '''BooleanCondition : LEFT_PAREN ReturnableExpression RIGHT_PAREN'''
    p[0] = AstNode(AST_BOOLEAN_CONDITION, p.lineno(0),p.lexpos(0));
    p[0].addChild(p[2]);

        
def p_BooleanOperator(p):
    '''BooleanOperator : AND
                       | OR
                       | BOOL_EQUALS
                       | BOOL_NOT_EQUALS 
                       '''

    if (p[1] == 'And'):
        p[0] = AstNode(AST_AND,p.lineno(1),p.lexpos(1));
    elif(p[1] == 'Or'):
        p[0] = AstNode(AST_OR,p.lineno(1),p.lexpos(1));
    elif(p[1] == '=='):
        p[0] = AstNode(AST_BOOL_EQUALS,p.lineno(1),p.lexpos(1));
    elif(p[1] == '!='):
        p[0] = AstNode(AST_BOOL_NOT_EQUALS,p.lineno(1),p.lexpos(1));        
    else:
        print('\nIncorrect boolean operator: ' + p[1] + '\n');
        assert(False);
    

    
def emptyElseIf():
    return AstNode(AST_ELSE_IF_STATEMENT,0,0);

def emptyElse():
    return AstNode(AST_ELSE_STATEMENT,0,0);

def isElseIfStatement(p):
    return p.type == AST_ELSE_IF_STATEMENT;

def p_AssignmentStatement(p):
    '''AssignmentStatement : Identifier EQUALS ReturnableExpression
    '''
    p[0] = AstNode(AST_ASSIGNMENT_STATEMENT,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1],p[3]]);

def p_ReturnableExpression(p):
    '''ReturnableExpression : NOT ReturnableExpression
                            | InternalReturnableExpression
    '''
    if (len(p) == 3):
        p[0] = AstNode(AST_NOT_EXPRESSION, p.lineno(0),p.lexpos(0));
        p[0].addChild(p[2]);
    elif(len(p) == 2):
        p[0] = p[1];
    else:
        print('\nIncorrect matching in ReturnableExpression\n');
        assert(False);
        
        
def p_InternalReturnableExpression(p):    
    '''InternalReturnableExpression : NonBooleanStatement BooleanOperator InternalReturnableExpression
                                    | NonBooleanStatement'''
    
    p[0] = AstNode(AST_INTERNAL_RETURNABLE_EXPRESSION,p.lineno(0),p.lexpos(0));
    if (len(p) == 4):
        p[0].addChild(p[2]);
        p[2].addChild(p[1]);
        p[2].addChildren(p[3].getChildren());
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nIn InternalReturnableExpression, incorrect number of matches\n');
        assert(False);
    
    
def p_NonBooleanStatement(p):
    '''NonBooleanStatement : Initializer '''
    p[0] = AstNode(AST_NON_BOOLEAN_STATEMENT,p.lineno(0),p.lexpos(0));
    p[0].addChild(p[1]);

    
def p_FunctionDeclArgList(p):
    '''FunctionDeclArgList : FunctionDeclArg 
                           | FunctionDeclArgList COMMA FunctionDeclArg
                           | Empty'''

    p[0] = AstNode(AST_FUNCTION_DECL_ARGLIST,p.lineno(0),p.lexpos(0));
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nError in FunctionDeclArgList.  Unexpected length to match\n');
        assert(False);


def p_FunctionCall(p):
    '''FunctionCall : Identifier LEFT_PAREN FunctionArgList RIGHT_PAREN'''
    p[0] = AstNode(AST_FUNCTION_CALL,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1],p[3]]);

    
def p_FunctionArgList(p):
    '''FunctionArgList : ReturnableExpression 
                       | FunctionDeclArgList COMMA ReturnableExpression 
                       | Empty'''
    
    p[0] = AstNode(AST_FUNCTION_ARGLIST,p.lineno(0),p.lexpos(0));
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nError in FunctionArgList.  Unexpected length to match\n');
        assert(False);
        


        
def p_FunctionDeclArg(p):
    '''FunctionDeclArg : Type Identifier'''
    p[0] = AstNode(AST_FUNCTION_DECL_ARG,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1],p[2]]);
    
    
def p_Declaration(p):
    '''Declaration : Type Identifier
                   | Type Identifier EQUALS Initializer'''
    p[0] = AstNode(AST_DECLARATION,p.lineno(0),p.lexpos(0));
    p[0].addChildren([p[1],p[2]]);
    if (len(p) == 5):
        p[0].addChild(p[4]);

def p_Empty(p):
    '''Empty : '''
    p[0] = AstNode(AST_EMPTY);

    
def p_error(p):

    if (p == None):
        print('\nError: end of file and missing some structure\n');
    else:
        print('\nSyntax error on "' + p.value + '"');
        print('Line number: ' + str(p.lineno));
        print('\n');

        if (ProgramText != None):
            #have program text, can actually print out the error.
            programTextArray = ProgramText.split('\n');
            errorLine = p.lineno;
            errorCol  = findErrorCol(ProgramText,p);
            errorText = '';
            lowerLineNum = max(0,errorLine - ERROR_NUM_LINES_EITHER_SIDE);
            upperLineNum = min(len(programTextArray),errorLine + ERROR_NUM_LINES_EITHER_SIDE);
            for s in range(lowerLineNum, upperLineNum):
                preamble = str(s+1);

                if (s == errorLine -1):
                    preamble += '*   ';
                else:
                    preamble += '    ';
                    
                errorText += preamble;
                errorText += programTextArray[s];
                errorText += '\n';
                
                if (s == errorLine -1):
                    #want to highlight the column that the error occurred.
                    lexPosLine = '';
                    for t in range(0,len(preamble) + errorCol - 1):
                        lexPosLine += ' ';
                    lexPosLine += '^\n';
                    errorText += lexPosLine;

            print(errorText);


def findErrorCol(progText,p):
    '''
    @param {string} progText -- Text of program that we're trying to
    parse.
    
    @param {production token} p
    '''
    lastNewline = progText.rfind('\n',0,p.lexpos);
    if lastNewline < 0:
	lastNewline = 0;
    returner = (p.lexpos - lastNewline);
    return returner;

def isEmptyNode(nodeToCheck):
    return (nodeToCheck.type == AST_EMPTY);


def getParser(programText=None):
    global ProgramText;
    returner = yacc.yacc();
    ProgramText = programText;
    return returner;

