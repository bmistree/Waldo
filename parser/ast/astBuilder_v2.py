#!/usr/bin/python

import sys;
import os;

lexerPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..','..','lexer');
sys.path.insert(0, lexerPath);

from waldoLex import tokens;
from waldoLex import ONCREATE_TOKEN;
from waldoLex import constructLexer;
from astLabels import *;
from astNode import AstNode;

typeCheckErrorUtilPath = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                      'typeCheck');
sys.path.append(typeCheckErrorUtilPath);

from typeCheckUtil import getErrorEncountered as astGetErrorEncountered;
from typeCheckUtil import resetErrorEncountered as astResetErrorEncountered;
from typeCheckUtil import setErrorEncountered;

# from astNode import getErrorEncountered as astGetErrorEncountered;
# from astNode import resetErrorEncountered as astResetErrorEncountered;
import ply.yacc as yacc;
from parserUtil import errPrint;
from parserUtil import setOutputErrorsTo;


from astBuilderCommon import * 

# Overall Structure:
# NameSection
# EndpointAliasSection
# TraceSection
# SharedSection
# Message sequence section
# EndpointSection
# EndpointSection ... not necessary if have symmetric names....




def p_RootExpression(p):
    'RootExpression : NameSection EndpointAliasSection TraceSection SharedSection MessageSequenceSection EndpointSection EndpointSection';
    
    p[0] = AstNode(AST_ROOT,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[2],p[3],p[4],p[6],p[7], p[5]]);  # message section gets added to end


def p_MessageSequenceSection(p):
    '''MessageSequenceSection : MessageSequence MessageSequenceSection
                              | MessageSequence
                              | Empty
    '''
    p[0] = AstNode(AST_MESSAGE_SEQUENCE_SECTION,p[1].lineNo,p[1].linePos);
    
    if not isEmptyNode(p[1]):
        p[0].addChild(p[1]);
    
    if (len(p) == 3):
        #flattens all message sequences into siblings
        kids = p[2].getChildren();
        for kid in kids:
            if isEmptyNode(kid):
                continue;
            p[0].addChild(kid);
            
        # p[0].addChildren(p[2].getChildren());


                   
def p_MessageSequence(p):
    '''
    MessageSequence : SEQUENCE Identifier CURLY_LEFT MessageSequenceGlobalSection MessageSequenceFunctions CURLY_RIGHT
    MessageSequence : SEQUENCE Identifier CURLY_LEFT MessageSequenceFunctions CURLY_RIGHT
    '''
    p[0] = AstNode(AST_MESSAGE_SEQUENCE,p[2].lineNo,p[2].linePos);
    # default to empty message sequence globals section if not defined
    globs = AstNode(AST_MESSAGE_SEQUENCE_GLOBALS,p[2].lineNo,p[2].linePos);
    sequenceFunctions = p[4];
    if (len(p) == 7):
        globs = p[4];
        sequenceFunctions = p[5];

    p[0].addChildren([p[2],globs,sequenceFunctions]);
            
def p_MessageSequenceGlobalSection(p):
    '''MessageSequenceGlobalSection : Declaration SEMI_COLON MessageSequenceGlobalSection
                                    | Declaration SEMI_COLON '''
    p[0] = AstNode(AST_MESSAGE_SEQUENCE_GLOBALS,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());

def p_MessageSequenceFunctions(p):
    '''MessageSequenceFunctions : MessageSendSequenceFunction MessageReceiveSequenceFunctions
    '''
    p[0] = AstNode(AST_MESSAGE_SEQUENCE_FUNCTIONS,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    p[0].addChildren(p[2].getChildren());

def p_MessageSendSequenceFunction(p):
    '''
    MessageSendSequenceFunction : Identifier DOT Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT CURLY_RIGHT
                                | Identifier DOT Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
    '''

    p[0] = AstNode(AST_MESSAGE_SEND_SEQUENCE_FUNCTION,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3],p[5]]);
    if (len(p) == 10):
        p[0].addChild(p[8]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p[1].lineNo,p[1].linePos));


        
def p_MessageReceiveSequenceFunctions(p):
    '''
    MessageReceiveSequenceFunctions : MessageReceiveSequenceFunction MessageReceiveSequenceFunctions
                                    | MessageReceiveSequenceFunction
    '''
    # intermediate ast node, will get removed by above parsing layer
    p[0] = AstNode(AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTIONS, p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 3):
        p[0].addChildren(p[2].getChildren());

        
def p_MessageReceiveSequenceFunction(p):
    '''
    MessageReceiveSequenceFunction : Identifier DOT Identifier CURLY_LEFT CURLY_RIGHT
                                   | Identifier DOT Identifier CURLY_LEFT FunctionBody CURLY_RIGHT

                                   | Identifier DOT Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT CURLY_RIGHT
                                   | Identifier DOT Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                                   
    '''
    p[0] = AstNode(AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION,p[1].lineNo,p[1].linePos);

    # specifically parsing for error of putting parens at end of message receive statement
    if (len(p) == 9) or (len(p) == 10):
        funcName = p[1].value + p[2] + p[3].value;
        errMsg = '\nError in MessageSequence on "' + funcName + '".  ';
        errMsg += 'Only the first function can take in arguments.  ';
        errMsg += 'Subsequent functions are automatically called by ';
        errMsg += 'the system.  You should remove the parentheses at the end of ';
        errMsg += 'the function.\n';
        p[0].value = funcName;
        raise WaldoParseException(p[0],errMsg);
    
    p[0].addChildren([p[1],p[3]]);
    if (len(p) == 7):
        p[0].addChild(p[5]);
    else:
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p[1].lineNo,p[1].linePos));


def p_TraceBodySection(p):
    '''TraceBodySection : Identifier COLON TraceLine SEMI_COLON TraceBodySection
                        | Identifier COLON TraceLine SEMI_COLON
                        ''';
    #note: currently, cannot have empty trace body section.
    p[0] = AstNode(AST_TRACE_BODY_SECTION,p[1].lineNo,p[1].linePos);
    p[3].prependChild(p[1]);
    p[0].addChild(p[3]);
    if(len(p) == 6):
        #flattens all TraceLines into siblings
        p[0].addChildren(p[5].getChildren());
    

def p_FunctionBodyStatement(p):
    '''FunctionBodyStatement : Declaration SEMI_COLON
                             | AssignmentStatement SEMI_COLON
                             | ConditionStatement
                             | ReturnableExpression SEMI_COLON
                             | ReturnStatement SEMI_COLON
    '''
    p[0] = AstNode(AST_FUNCTION_BODY_STATEMENT,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);

        
def p_NonOperatableOn(p):
    '''
    NonOperatableOn : PrintCall
    '''
    #cannot use operators between PrintCall and message literal (they
    #are not operatable on).  Everything in OperatableOn we can put
    #operators between (except for == ).  Gets rid of reduce/reduce
    #conflict from having a minus sign after a message literal to
    #separate into terminal returnable, nonoperatableon, and
    #operatableon.
    p[0] = p[1];
    
    
def p_EndpointFunctionSection(p):
    '''EndpointFunctionSection :  PublicFunction EndpointFunctionSection
                               |  PublicFunction
                               |  Function EndpointFunctionSection
                               |  Function
                               |  OnCreateFunction EndpointFunctionSection
                               |  OnCreateFunction 
                               '''
    
    p[0] = AstNode(AST_ENDPOINT_FUNCTION_SECTION,p[1].lineNo,p[1].linePos);
    
    p[0].addChild(p[1]);
        
    if (len(p) == 3):
        p[0].addChildren(p[2].getChildren());




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

