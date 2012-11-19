#!/usr/bin/python

import sys;
import os;


from lexer.waldoLex import tokens;
from lexer.waldoLex import ONCREATE_TOKEN;
from lexer.waldoLex import constructLexer;
from astLabels import *;
from astNode import AstNode;


from typeCheck.typeCheckUtil import getErrorEncountered as astGetErrorEncountered;
from typeCheck.typeCheckUtil import resetErrorEncountered as astResetErrorEncountered;
from typeCheck.typeCheckUtil import setErrorEncountered;

import ply.yacc as yacc;
from parserUtil import errPrint;
from parserUtil import setOutputErrorsTo;


from astBuilderCommon import * 

# Overall Structure:
# NameSection
# EndpointAliasSection
# TraceSection
# Struct section (optional)
# SharedSection (optional)
# Message sequence section
# EndpointSection
# EndpointSection ... not necessary if have symmetric names....


def p_RootExpression(p):
    '''
    RootExpression : NameSection EndpointAliasSection TraceSection StructSharedSection MessageSequenceSection EndpointSection EndpointSection
                   | NameSection EndpointAliasSection TraceSection StructSharedSection EndpointSection EndpointSection
                   
    '''
    
    p[0] = AstNode(AST_ROOT,p[1].lineNo,p[1].linePos);

    name_section = p[1]
    endpoint_alias_section = p[2]
    trace_section = p[3]
    struct_shared_section = p[4]

    struct_section = struct_shared_section.children[0]
    shared_section = struct_shared_section.children[1]
    
    
    p[0].addChildren(
        [name_section,endpoint_alias_section,trace_section,shared_section]);

    msg_seq_section = AstNode(AST_MESSAGE_SEQUENCE_SECTION,p[4].lineNo,p[4].linePos);
    endpoint_section_1 = p[5]
    endpoint_section_2 = p[6]
    
    if len(p) == 8:
        msg_seq_section = p[5]
        endpoint_section_1 = p[6]
        endpoint_section_2 = p[7]
    

    p[0].addChildren([
            endpoint_section_1,endpoint_section_2,
            msg_seq_section,struct_section]);   


def p_MessageSequenceSection(p):
    '''MessageSequenceSection : MessageSequence MessageSequenceSection
                              | MessageSequence
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
            


def p_MessageSequence(p):
    '''
    MessageSequence : SEQUENCE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT MessageSequenceGlobalSection MessageSequenceFunctions CURLY_RIGHT
    MessageSequence : SEQUENCE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT MessageSequenceFunctions CURLY_RIGHT
    '''
    # syntax:
    #    Sequence <some name> (<some arguments>)
    #    {
    #        <some sequence globals> (optional)
    #        <some sequence functions>
    #    }

    # children produced:
    #   Identifier: <some name>
    #   FunctionDeclArgList: <some arguments>
    #   SEQUENCE GLOBALS: <some sequence globals>
    #   MessageSequenceFunctions: <some sequence functions>

    # note that canonicalize moves FunctionDeclArgList from child of
    # AST_MESSAGE_SEQUENCE to child of the first message send
    # function.
    
    p[0] = AstNode(AST_MESSAGE_SEQUENCE,p[2].lineNo,p[2].linePos);
    seq_args = p[4]
    seq_name = p[2]
    p[0].addChildren([seq_name,seq_args])

    
    # default to empty message sequence globals section if not defined
    seq_globs = AstNode(AST_MESSAGE_SEQUENCE_GLOBALS,p[2].lineNo,p[2].linePos);
    seq_functions = p[7]
    if len(p) == 10:
        seq_globs = p[7]
        seq_functions= p[8];

    p[0].addChildren([seq_globs,seq_functions]);

    
def p_MessageSequenceGlobalSection(p):
    '''MessageSequenceGlobalSection : Declaration SEMI_COLON MessageSequenceGlobalSection
                                    | Declaration SEMI_COLON '''
    p[0] = AstNode(AST_MESSAGE_SEQUENCE_GLOBALS,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());

        
def p_MessageSequenceFunctions(p):
    '''
    MessageSequenceFunctions : MessageSendSequenceFunction MessageReceiveSequenceFunctions
    '''
    
    p[0] = AstNode(AST_MESSAGE_SEQUENCE_FUNCTIONS,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    p[0].addChildren(p[2].getChildren());

    
def p_MessageSendSequenceFunction(p):
    '''
    MessageSendSequenceFunction : Identifier DOT Identifier CURLY_LEFT CURLY_RIGHT
                                | Identifier DOT Identifier CURLY_LEFT FunctionBody CURLY_RIGHT
    '''
    # Syntax
    #    <endpoint name>.<function name>
    #    {
    #        <function body> (optional)
    #    }

    # Children produced
    #    Identifier: <endpoint name>
    #    Identifier: <function name>
    #    FunctionBody: <function body>

    # note: canonicalize inserts a FunctionDeclArgList as a child for
    # this between function name and endpoint body
    
    p[0] = AstNode(AST_MESSAGE_SEND_SEQUENCE_FUNCTION,p[1].lineNo,p[1].linePos);
    endpoint_name = p[1]
    func_name = p[3]
    
    # imposter function body in case this was a noop.
    func_body = AstNode(AST_FUNCTION_BODY,p[1].lineNo,p[1].linePos)
    if len(p) == 7:
        func_body = p[5]

    p[0].addChildren([endpoint_name,func_name,func_body])

        
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
                                   | OnCompleteFunction
                                   
    '''

    if len(p) == 2:
        # means it was an on complete function.  just use that directly
        p[0] = p[1];
        return;
    
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
                             | ForStatement
                             | WhileStatement
                             | PlusEqual SEMI_COLON
                             | MinusEqual SEMI_COLON
                             | DivideEqual SEMI_COLON
                             | MultiplyEqual SEMI_COLON                             
                             | ReturnableExpression SEMI_COLON
                             | ReturnStatement SEMI_COLON
    '''
    p[0] = AstNode(AST_FUNCTION_BODY_STATEMENT,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);

    
def p_NonOperatableOn(p):
    '''
    NonOperatableOn : PrintCall
                    | RefreshCall
                    | Jump
                    | ExtAssign
                    | ExtCopy
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

