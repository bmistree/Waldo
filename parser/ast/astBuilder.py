#!/usr/bin/python

import sys;
sys.path.append('../../lexer/')
from waldoLex import tokens;
from waldoLex import constructLexer;
from astLabels import *;
from astNode import AstNode;
from astNode import setErrorEncountered;
from astNode import getErrorEncountered as astGetErrorEncountered;
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



#note: otherwise, starts at first rule.  
start = 'RootExpression';
#need to have something named lexer for parser to chew into
lexer = constructLexer();


def p_RootExpression(p):
    'RootExpression : NameSection EndpointAliasSection TraceSection SharedSection EndpointSection EndpointSection';
    p[0] = AstNode(AST_ROOT,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[2],p[3],p[4],p[5],p[6]]);
    

def p_NameSection(p):
    'NameSection : Identifier'
    p[0] = p[1];
    p[0].setNote(AST_PROT_OBJ_NAME);

def p_EndpointAliasSection(p):
    'EndpointAliasSection : ENDPOINT Identifier SEMI_COLON ENDPOINT Identifier SEMI_COLON';
    p[0] = AstNode(AST_ENDPOINT_ALIAS_SECTION,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2], p[5]]);

def p_TraceSection(p):
    'TraceSection : TRACES CURLY_LEFT TraceBodySection CURLY_RIGHT';
    #note: this is an intermediate production, and will get skipped.
    p[0] = AstNode(AST_TRACE_SECTION,p.lineno(1),p.lexpos(1));
    
    #getting TraceBodySection's children removes it as an intermediate node.
    p[0].addChildren(p[3].getChildren());


def p_TraceItem(p):
    'TraceItem : Identifier DOT Identifier'
    #Each TraceItem is connected by arrows in Trace section
    # TraceItem -> TraceItem -> TraceItem;
    p[0] = AstNode(AST_TRACE_ITEM,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);

def p_TraceBodySection(p):
    '''TraceBodySection : TraceLine SEMI_COLON TraceBodySection
                        | TraceLine SEMI_COLON''';
    #note: currently, cannot have empty trace body section.
    p[0] = AstNode(AST_TRACE_BODY_SECTION,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if(len(p) == 4):
        #flattens all TraceLines into siblings
        p[0].addChildren(p[3].getChildren());
    

def p_TraceLine(p):
    '''TraceLine : TraceItem  SEND_ARROW TraceLine
                 | TraceItem  '''

    p[0] = AstNode(AST_TRACE_LINE,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        #have additional parts of trace body to grab.
        p[0].addChildren(p[3].getChildren());

def p_SharedSection(p):
    '''SharedSection : SHARED CURLY_LEFT SharedBodySection CURLY_RIGHT
                     | SHARED CURLY_LEFT CURLY_RIGHT''';

    p[0] = AstNode(AST_SHARED_SECTION,p.lineno(1),p.lexpos(1));
    if (len(p) == 5):
        if (not isEmptyNode(p[3])):
            p[0].addChildren(p[3].getChildren());
        else:
            p[0].addChild(p[3]);

            
def p_SharedBodySection(p):
    '''SharedBodySection : AnnotatedDeclaration SEMI_COLON SharedBodySection
                         | AnnotatedDeclaration SEMI_COLON'''
    p[0] = AstNode(AST_SHARED_BODY_SECTION, p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());

        
        
def p_AnnotatedDeclaration(p):
    '''AnnotatedDeclaration : Identifier CONTROLS Type Identifier 
                            | Identifier CONTROLS Type Identifier EQUALS TerminalReturnable'''
    p[0] = AstNode(AST_ANNOTATED_DECLARATION,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3],p[4]]);
    
    if (len(p) == 7):
        #have an initialization statement to perform
        p[0].addChild(p[6]);

def p_Type(p):
    '''Type : NUMBER_TYPE
            | STRING_TYPE
            | LIST_TYPE
            | BOOL_TYPE
            | NOTHING_TYPE
            | SENDS
            | RECEIVES
            '''

    p[0] = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),p[1]);




def p_TerminalReturnable(p):
    '''
    TerminalReturnable : OperatableOn
                       | NonOperatableOn
    '''
    p[0] = p[1];

    
def p_NonOperatableOn(p):
    '''
    NonOperatableOn : MessageLiteral
                    | PrintCall
    '''
    #cannot use operators between PrintCall and message literal (they
    #are not operatable on).  Everything in OperatableOn we can put
    #operators between (except for == ).  Gets rid of reduce/reduce
    #conflict from having a minus sign after a message literal to
    #separate into terminal returnable, nonoperatableon, and
    #operatableon.
    p[0] = p[1];
    
    
                      
    
def p_OperatableOn(p):
    '''OperatableOn : Number
                    | BracketStatement    
                    | Identifier
                    | String
                    | Bool
                    | FunctionCall
                    ''';
    p[0] = p[1];

    
    

def p_PrintCall(p):
    '''
    PrintCall : PRINT LEFT_PAREN ReturnableExpression RIGHT_PAREN
    '''

    
    p[0] = AstNode(AST_PRINT,p.lineno(1),p.lexpos(1));
    p[0].addChild(p[3]);


def p_BracketStatement(p):
    '''
    BracketStatement : Identifier LEFT_BRACKET ReturnableExpression RIGHT_BRACKET
    '''
    
    p[0] = AstNode(AST_BRACKET_STATEMENT,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);
    
    
def p_MessageLiteral(p):
    '''
    MessageLiteral : CURLY_LEFT InternalMessageLiteral CURLY_RIGHT
                   | CURLY_LEFT CURLY_RIGHT
    '''

    if (len(p) == 4):
        p[0] = p[2];
    elif(len(p) == 3):
        p[0]= AstNode(AST_MESSAGE_LITERAL,p.lineno(1),p.lexpos(1));
    else:
        print('\nError in MessageLiteral.  Unexpected length to match\n');
        assert(False);

        
def p_InternalMessageLiteral(p):
    '''InternalMessageLiteral : MessageLiteralElement 
                              | InternalMessageLiteral COMMA MessageLiteralElement
                              '''
    
    p[0]= AstNode(AST_MESSAGE_LITERAL,p[1].lineNo,p[1].linePos);

    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nError in InternalMessageLiteral.  Unexpected length to match\n');
        assert(False);

    

    
def p_MessageLiteralElement(p):
    '''
    MessageLiteralElement : String COLON ReturnableExpression
    '''
    p[0] = AstNode(AST_MESSAGE_LITERAL_ELEMENT, p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);
    


def p_Number(p):
    '''Number : NUMBER
              | MINUS NUMBER'''

    if (len(p) == 2):
        p[0] = AstNode(AST_NUMBER,p.lineno(1),p.lexpos(1),p[1]);
    elif(len(p) == 3):
        p[0] = AstNode(AST_NUMBER,p.lineno(2),p.lexpos(2),'-'+p[2]);
    else:
        errMsg = '\nBehram error when parsing for number.  Incorrect ';
        errMsg += 'num statements when matching.\n';
        print(errMsg);
        assert(False);

        
    p[0].type = TYPE_NUMBER;
    
def p_String(p):
    '''String : MULTI_LINE_STRING
              | SINGLE_LINE_STRING''';

    p[0] = AstNode(AST_STRING,p.lineno(1),p.lexpos(1),p[1]);
    p[0].type = TYPE_STRING;

def p_Bool(p):
    '''Bool : TRUE
            | FALSE'''
    p[0] = AstNode(AST_BOOL,p.lineno(1),p.lexpos(1),p[1]);
    p[0].type = TYPE_BOOL;
    
    
    
def p_Identifier(p):
    'Identifier : IDENTIFIER';
    p[0] = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[1]);


def p_EndpointSection(p):
    '''EndpointSection : Identifier CURLY_LEFT EndpointBodySection CURLY_RIGHT
                       | Identifier CURLY_LEFT CURLY_RIGHT'''
    p[0] = AstNode(AST_ENDPOINT,p[1].lineNo,p[1].linePos);

    p[0].addChild(p[1]);
    if (len(p) == 5):
        p[0].addChild(p[3]);

def p_EndpointBodySection(p):
    '''EndpointBodySection : EndpointGlobalSection EndpointFunctionSection
                           | EndpointFunctionSection
                           '''

    p[0] = AstNode(AST_ENDPOINT_BODY_SECTION,p[1].lineNo,p[1].linePos);
    if (len(p) == 3):
        p[0].addChildren([p[1],p[2]]);
    elif ((len(p) == 2) and (not isEmptyNode(p[1]))):
        p[0].addChild(AstNode(AST_ENDPOINT_GLOBAL_SECTION, p[1].lineNo,p[1].linPos));
        p[0].addChild(p[1]);
    else:
        print('\nError in endpoint body section.  Got an unusual number of arguments.\n');
        assert(False);
    

def p_EndpointGlobalSection(p):
    '''EndpointGlobalSection : Declaration SEMI_COLON EndpointGlobalSection
                             | Declaration SEMI_COLON'''
    p[0] = AstNode(AST_ENDPOINT_GLOBAL_SECTION, p[1].lineNo,p[1].linePos);
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
                               |  OnCreateFunction EndpointFunctionSection
                               |  OnCreateFunction 
                               '''
    
    p[0] = AstNode(AST_ENDPOINT_FUNCTION_SECTION,p[1].lineNo,p[1].linePos);
    
    p[0].addChild(p[1]);
        
    if (len(p) == 3):
        p[0].addChildren(p[2].getChildren());


def p_TypedSendsStatement(p):
    '''
    TypedSendsStatement : CURLY_LEFT CURLY_RIGHT
                        | CURLY_LEFT TypedMessageSendsLines CURLY_RIGHT
    '''

    p[0] = AstNode(AST_TYPED_SENDS_STATEMENT, p.lineno(1),p.lexpos(1));

    if (len(p) == 4):
        p[0].addChildren(p[2].getChildren());

def p_TypedMessageSendsLines(p):
    '''
    TypedMessageSendsLines : TypedMessageSendsLine
                           | TypedMessageSendsLines COMMA TypedMessageSendsLine
    '''

    #This p[0] ends up getting skipped because of ordering of p_TypedSendsStatement
    p[0] = AstNode(AST_TYPED_SENDS_STATEMENT,p[1].lineNo,p[1].linePos);
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        print('\nError in TypedMessageSendsLines.  Unexpected length to match\n');
        assert(False);

        

def p_TypedMessageSendsLine(p):
    '''
    TypedMessageSendsLine : Type Identifier  
    '''
    p[0] = AstNode(AST_TYPED_SENDS_LINE,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[2]]);

    
    
def p_MsgReceiveFunction(p):
    '''MsgReceiveFunction : MSG_RECEIVE Identifier RECEIVES Identifier COLON TypedSendsStatement SENDS COLON TypedSendsStatement CURLY_LEFT FunctionBody CURLY_RIGHT
                          | MSG_RECEIVE Identifier RECEIVES Identifier COLON TypedSendsStatement SENDS COLON TypedSendsStatement CURLY_LEFT CURLY_RIGHT
                          ''';
    
    p[0] = AstNode(AST_MSG_RECEIVE_FUNCTION, p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[4],p[6],p[9]]);
    if (len(p) == 13):
        p[0].addChild(p[11]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));



        
def p_MsgSendFunction(p):
    '''MsgSendFunction : MSG_SEND Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN SENDS TypedSendsStatement CURLY_LEFT FunctionBody CURLY_RIGHT
                       | MSG_SEND Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN SENDS TypedSendsStatement CURLY_LEFT  CURLY_RIGHT'''


    p[0] = AstNode(AST_MSG_SEND_FUNCTION, p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[4]]);
    if (len(p) == 11):
        p[0].addChild(p[9]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));

    #add the send statement on to the end.
    p[0].addChild(p[7]);
    
def p_Function(p):
    '''Function : FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS Type CURLY_LEFT FunctionBody CURLY_RIGHT
                | FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS Type CURLY_LEFT  CURLY_RIGHT'''
    p[0] = AstNode(AST_FUNCTION, p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[7],p[4]]);
    if (len(p) == 11):
        p[0].addChild(p[9]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));


    
        
def p_PublicFunction(p):
    '''PublicFunction : PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS Type CURLY_LEFT FunctionBody CURLY_RIGHT
                      | PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS Type CURLY_LEFT  CURLY_RIGHT'''
    
    p[0] = AstNode(AST_PUBLIC_FUNCTION, p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[3],p[8],p[5]]);
    if (len(p) == 12):
        p[0].addChild(p[10]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));

        

def p_FunctionBody(p):
    '''FunctionBody : FunctionBody FunctionBodyStatement
                    | FunctionBodyStatement'''
    p[0] = AstNode(AST_FUNCTION_BODY, p[1].lineNo,p[1].linePos);
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
                             | SendStatement SEMI_COLON
                             | AssignmentStatement SEMI_COLON
                             | ConditionStatement
                             | ReturnableExpression SEMI_COLON
                             | ReturnStatement SEMI_COLON
    '''
    p[0] = AstNode(AST_FUNCTION_BODY_STATEMENT,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);

def p_ReturnStatement(p):
    '''
    ReturnStatement : RETURN_OPERATOR ReturnableExpression
                    | RETURN_OPERATOR Empty
    '''
    p[0] = AstNode(AST_RETURN_STATEMENT,p.lineno(1),p.lexpos(1));
    if (isEmptyNode(p[2])):
        # insert type nothing node so can still perform check
        p[0].addChild(AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),TYPE_NOTHING));
    else:
        # insert returnable expression
        p[0].addChild(p[2]);


def p_OnCreateFunction(p):
    '''
    OnCreateFunction : ONCREATE  LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
    '''
    p[0] = AstNode(AST_ONCREATE_FUNCTION,p.lineno(1),p.lexpos(1));
    onCreateName = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[1]);
    p[0].addChildren([onCreateName,p[3],p[6]]);
    

def p_SendStatement(p):
    '''SendStatement : SEND_OPERATOR Identifier TO_OPERATOR Identifier
    '''
    p[0] = AstNode(AST_SEND_STATEMENT,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[4]]);

    
def p_ConditionStatement(p):
    '''ConditionStatement : IfStatement ElseIfStatements ElseStatement'''
    
    p[0] = AstNode(AST_CONDITION_STATEMENT,p[1].lineNo,p[1].linePos);

    p[0].addChildren([p[1],p[2],p[3]]);


def p_IfStatement(p):
    '''IfStatement : IF BooleanCondition SingleLineOrMultilineCurliedBlock '''
    p[0] = AstNode(AST_IF_STATEMENT,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[3]]);

    
def p_ElseIfStatements(p):
    '''ElseIfStatements : Empty
                        | ElseIfStatements ElseIfStatement'''
    
    p[0] = AstNode(AST_ELSE_IF_STATEMENTS,p[1].lineNo,p[1].linePos);
    if (len(p) == 3):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[2]);

def p_ElseIfStatement(p):
    '''ElseIfStatement : ELSE_IF BooleanCondition SingleLineOrMultilineCurliedBlock'''
    p[0] = AstNode(AST_ELSE_IF_STATEMENT,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[3]]);

    
    
def p_ElseStatement(p):
    '''ElseStatement : Empty
                     | ELSE SingleLineOrMultilineCurliedBlock '''

    if (len(p) == 3):
        p[0] = AstNode(AST_ELSE_STATEMENT,p.lineno(0),p.lexpos(0));
        p[0].addChild(p[2]);
    elif(len(p) == 2):
        p[0] = AstNode(AST_ELSE_STATEMENT,p[1].lineNo,p[1].linePos);

    else:
        print('\nIncorrect match count in ElseStatement.\n');
        assert(False);


def p_SingleLineOrMultilineCurliedBlock(p):
    '''SingleLineOrMultilineCurliedBlock :  FunctionBodyStatement
                                         |  CURLY_LEFT FunctionBody CURLY_RIGHT
                                         |  CURLY_LEFT CURLY_RIGHT
    ''';
    

    if (len(p) == 2):
        p[0] = AstNode(AST_FUNCTION_BODY,p[1].lineNo,p[1].linePos);
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
    p[0] = AstNode(AST_BOOLEAN_CONDITION, p.lineno(1),p.lexpos(1));
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
    


def p_AssignmentStatement(p):
    '''AssignmentStatement : Identifier EQUALS ReturnableExpression
                           | BracketStatement EQUALS ReturnableExpression
    '''
    p[0] = AstNode(AST_ASSIGNMENT_STATEMENT,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);

    
    
def p_ReturnableExpression(p):
    '''ReturnableExpression : LEFT_PAREN ReturnableExpression RIGHT_PAREN BinaryOperator ReturnableExpression
                            | ParenthesizedExpression
                            | LEFT_PAREN ReturnableExpression RIGHT_PAREN 
    '''

    if (len(p) == 6):
        p[0] = p[4];
        p[4].addChildren([p[2],p[5]]);
    elif(len(p) == 2):
        p[0] = p[1];
    elif(len(p) == 4):
        p[0] = p[2];
    else:
        print('\nIncorrect number of matches in ReturnableExpression\n');
        assert(False);

def p_BinaryOperator(p):
    '''
    BinaryOperator : PlusMinusOperator
                   | MultDivOperator
                   | BooleanOperator
    '''
    p[0] = p[1];

def p_ParenthesizedExpression(p):
    '''ParenthesizedExpression : NOT ParenthesizedExpression
                               | InternalReturnableExpression
    '''
    if (len(p) == 3):
        p[0] = AstNode(AST_NOT_EXPRESSION, p.lineno(1),p.lexpos(1));
        p[0].addChild(p[2]);
    elif(len(p) == 2):
        p[0] = p[1];
    else:
        print('\nIncorrect matching in ReturnableExpression\n');
        assert(False);

        

def p_InternalReturnableExpression(p):    
    '''InternalReturnableExpression : NonBooleanStatement BooleanOperator InternalReturnableExpression
                                    | NonBooleanStatement'''

    #skip over internal_returnable_expression label
    if (len(p) == 2):
        p[0] = p[1];
    elif (len(p) == 4):
        p[0] = p[2];
        p[0].addChild(p[1]);
        p[0].addChild(p[3]);
    else:
        print('\nIn InternalReturnableExpression, incorrect number of matches\n');
        assert(False);
    
    
def p_NonBooleanStatement(p):
    '''NonBooleanStatement : MultDivStatement PlusMinusOperator NonBooleanStatement
                           | MultDivStatement
                           | NonOperatableOn
                           '''

    if(len(p) == 4):
        p[0] = p[2];
        p[0].addChildren([p[1],p[3]]);
    elif(len(p) == 2):
        p[0] = p[1];
    else:
        print('\nIncorrect number of matches in NonBooleanStatement\n');
        assert(False);
        
    
def p_PlusMinusOperator(p):
    '''PlusMinusOperator : PLUS
                         | MINUS'''

    if (p[1] == '+'):
        p[0] = AstNode(AST_PLUS, p.lineno(1),p.lexpos(1));
    elif(p[1] == '-'):
        p[0] = AstNode(AST_MINUS, p.lineno(1),p.lexpos(1));
    else:
        print('\nIncorrect number of matches in PlusMinusOperator\n');
        assert(False);


def p_MultDivStatement(p):
    '''MultDivStatement : OperatableOn MultDivOperator MultDivStatement
                        | OperatableOn'''

    if(len(p) == 4):
        p[0] = p[2];
        p[0].addChildren([p[1],p[3]]);
    elif(len(p) == 2):
        p[0] = p[1];
    else:
        print('\nIncorrect number of matches in MultDivStatement\n');
        assert(False);

        
def p_MultDivOperator(p):
    '''MultDivOperator : MULTIPLY
                       | DIVIDE'''

    if (p[1] == '*'):
        p[0] = AstNode(AST_MULTIPLY, p.lineno(1),p.lexpos(1));
    elif(p[1] == '/'):
        p[0] = AstNode(AST_DIVIDE, p.lineno(1),p.lexpos(1));
    else:
        print('\nIncorrect number of matches in MultDivOperator\n');
        assert(False);
    
    
def p_FunctionDeclArgList(p):
    '''FunctionDeclArgList : FunctionDeclArg 
                           | FunctionDeclArgList COMMA FunctionDeclArg
                           | Empty'''

    p[0] = AstNode(AST_FUNCTION_DECL_ARGLIST,p[1].lineNo,p[1].linePos);
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        if (not isEmptyNode(p[1])):
            p[0].addChild(p[1]);
    else:
        print('\nError in FunctionDeclArgList.  Unexpected length to match\n');
        assert(False);


def p_FunctionCall(p):
    '''FunctionCall : Identifier LEFT_PAREN FunctionArgList RIGHT_PAREN'''
    p[0] = AstNode(AST_FUNCTION_CALL,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);

    
def p_FunctionArgList(p):
    '''FunctionArgList : ReturnableExpression 
                       | FunctionArgList COMMA ReturnableExpression 
                       | Empty'''
    
    p[0] = AstNode(AST_FUNCTION_ARGLIST,p[1].lineNo,p[1].linePos);
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
                
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        if (not isEmptyNode(p[1])):
            p[0].addChild(p[1]);
    else:
        print('\nError in FunctionArgList.  Unexpected length to match\n');
        assert(False);
        


        
def p_FunctionDeclArg(p):
    '''FunctionDeclArg : Type Identifier'''
    p[0] = AstNode(AST_FUNCTION_DECL_ARG,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[2]]);
    

def p_Declaration(p):
    '''Declaration : Type Identifier
                   | Type Identifier EQUALS ReturnableExpression'''
    p[0] = AstNode(AST_DECLARATION,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[2]]);
    if (len(p) == 5):
        p[0].addChild(p[4]);

def p_Empty(p):
    '''Empty : '''
    p[0] = AstNode(AST_EMPTY);

    
def p_error(p):

    setErrorEncountered();
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
    return (nodeToCheck.label == AST_EMPTY);


def getParser(programText=None):
    global ProgramText;
    returner = yacc.yacc();
    ProgramText = programText;
    return returner;


def getErrorEncountered():
    return astGetErrorEncountered();
