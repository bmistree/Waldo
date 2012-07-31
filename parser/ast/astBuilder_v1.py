#!/usr/bin/python

import sys;
import os;

lexerPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..','lexer');
sys.path.insert(0, lexerPath);

typeCheckErrorUtilPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                      'typeCheck');
sys.path.append(typeCheckErrorUtilPath);

from waldoLex import tokens;
from waldoLex import constructLexer;
from astLabels import *;
from astNode import AstNode;
from typeCheckUtil import getErrorEncountered as astGetErrorEncountered;
from typeCheckUtil import resetErrorEncountered as astResetErrorEncountered;
import ply.yacc as yacc;
from parserUtil import errPrint;
from parserUtil import setOutputErrorsTo;

from astBuilderCommon import * 


# Overall Structure:
# NameSection
# EndpointAliasSection
# TraceSection
# SharedSection
# EndpointSection
# EndpointSection ... not necessary if have symmetric names....


def p_RootExpression(p):
    'RootExpression : NameSection EndpointAliasSection TraceSection SharedSection EndpointSection EndpointSection';
    p[0] = AstNode(AST_ROOT,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[2],p[3],p[4],p[5],p[6]]);
    

def p_TraceBodySection(p):
    '''TraceBodySection : TraceLine SEMI_COLON TraceBodySection
                        | TraceLine SEMI_COLON''';
    #note: currently, cannot have empty trace body section.
    p[0] = AstNode(AST_TRACE_BODY_SECTION,p[1].lineNo,p[1].linePos);
    
    # to make ast consistent with other tree inserting blank name for
    # trace line.
    p[1].prependChild(AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),''));
    
    p[0].addChild(p[1]);
    if(len(p) == 4):
        #flattens all TraceLines into siblings
        p[0].addChildren(p[3].getChildren());
    

    
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
        errPrint('\nError in MessageLiteral.  Unexpected length to match\n');
        assert(False);

        
def p_InternalMessageLiteral(p):
    '''InternalMessageLiteral : MessageLiteralElement 
                              | InternalMessageLiteral COMMA MessageLiteralElement
                              '''
    
    p[0] = AstNode(AST_MESSAGE_LITERAL,p[1].lineNo,p[1].linePos);

    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        errPrint('\nError in InternalMessageLiteral.  Unexpected length to match\n');
        assert(False);

    
def p_MessageLiteralElement(p):
    '''
    MessageLiteralElement : String COLON ReturnableExpression
    '''
    p[0] = AstNode(AST_MESSAGE_LITERAL_ELEMENT, p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);
    


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
        errPrint('\nError in TypedMessageSendsLines.  Unexpected length to match\n');
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

                          | MSG_RECEIVE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RECEIVES Identifier COLON TypedSendsStatement SENDS COLON TypedSendsStatement CURLY_LEFT FunctionBody CURLY_RIGHT
                          | MSG_RECEIVE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RECEIVES Identifier COLON TypedSendsStatement SENDS COLON TypedSendsStatement CURLY_LEFT CURLY_RIGHT
                          ''';

    p[0] = AstNode(AST_MSG_RECEIVE_FUNCTION, p.lineno(1),p.lexpos(1));
    
    # last two lines should be caught and presented as errors: message
    # receive functions should not take arguments.
    if (len(p) == 16) or (len(p) == 15):
        errMsg = '\nError specifying a ' + p[1] + ' function named "';
        errMsg += p[2].value + '".  ' + p[1] + ' functions should not take ';
        errMsg += 'arguments.  Therefore, it should not have parentheses.  ';
        errMsg += 'Instead, use the IncomingMessage and OutgoingMessage syntax.\n';
        p[0].value = p[2].value;
        raise WaldoParseException(p[0],errMsg);

    p[0].addChildren([p[2],p[4],p[6],p[9]]);
    if (len(p) == 13):
        p[0].addChild(p[11]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));

        
def p_MsgSendFunction(p):
    '''MsgSendFunction : MSG_SEND Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN SENDS COLON TypedSendsStatement CURLY_LEFT FunctionBody CURLY_RIGHT
                       | MSG_SEND Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN SENDS COLON TypedSendsStatement CURLY_LEFT  CURLY_RIGHT'''


    p[0] = AstNode(AST_MSG_SEND_FUNCTION, p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[4]]);
    if (len(p) == 12):
        p[0].addChild(p[10]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));

    #add the send statement on to the end.
    p[0].addChild(p[8]);
    

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

    
def p_SendStatement(p):
    '''SendStatement : SEND_OPERATOR Identifier TO_OPERATOR Identifier
    '''
    p[0] = AstNode(AST_SEND_STATEMENT,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2],p[4]]);


def getParser(programText=None,outputErrsTo=sys.stderr):
    global lexer;
    lexer = constructLexer();

    global ProgramText;
    returner = yacc.yacc();
    ProgramText = programText;

    setOutputErrorsTo(outputErrsTo);
    
    return returner;


def getErrorEncountered():
    return astGetErrorEncountered();

def resetErrorEncountered():
    return astResetErrorEncountered();

