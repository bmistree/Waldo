#!/usr/bin/python

import sys,os
import os

deps_path = os.path.join(
    os.path.dirname(__file__),'..')
sys.path.append(deps_path)


from lexer.waldoLex import tokens;
from lexer.waldoLex import ONCREATE_TOKEN;
from lexer.waldoLex import constructLexer;
from astLabels import *;
from astNode import AstNode;


from typeCheck.typeCheckUtil import getErrorEncountered as astGetErrorEncountered;
from typeCheck.typeCheckUtil import resetErrorEncountered as astResetErrorEncountered;
from typeCheck.typeCheckUtil import setErrorEncountered;


import deps.ply.ply.yacc as yacc

from parserUtil import errPrint;
from parserUtil import setOutputErrorsTo;


from astBuilderCommon import * 



def p_RootExpression(p):
    '''
    RootExpression : NameSection EndpointAliasSection TraceStructSharedSection MessageSequenceSection EndpointDefinitionSection
                   | NameSection EndpointAliasSection TraceStructSharedSection EndpointDefinitionSection
    '''

    p[0] = AstNode(AST_ROOT,p[1].lineNo,p[1].linePos);

    name_section = p[1]
    endpoint_alias_section = p[2]
    trace_struct_shared_section = p[3]

    trace_section = trace_struct_shared_section.children[0]
    struct_section = trace_struct_shared_section.children[1]
    shared_section = trace_struct_shared_section.children[2]
    
    
    p[0].addChildren(
        [name_section,endpoint_alias_section,trace_section,shared_section]);

    msg_seq_section = AstNode(AST_MESSAGE_SEQUENCE_SECTION,p[4].lineNo,p[4].linePos);
    endpoint_definition_section = p[4]
    
    if len(p) == 6:
        msg_seq_section = p[4]
        endpoint_definition_section = p[5]

    p[0].addChildren([
            endpoint_definition_section,msg_seq_section,struct_section])

    # ends up producing
    #   name_section
    #   endpoint_alias_section
    #   trace_section
    #   shared section
    #   endpoint definition section
    #     (containing one endpoint or two endpoints)
    #   msg seq section
    #   struct section

    # Canonicalize however turns it into
    #   name_section
    #   endpoint_alias_section
    #   trace_section
    #   shared section
    #   endpoint1 section
    #   endpoint2 section
    #   msg seq section
    #   struct section

def p_EndpointDefinitionSection(p):
    '''
    EndpointDefinitionSection : EndpointDefinitionSection EndpointSection
                              | EndpointSection
    '''
    p[0] = AstNode(AST_ENDPOINT_DEFINITION_SECTION,p[1].lineNo,p[1].linePos)

    # order of first and second section does not matter

    if len(p) == 3:
        end_def_sec_node = p[1]
        second_section = p[2]
        p[0].addChildren(end_def_sec_node.getChildren())
        p[0].addChild(second_section)
    else:
        first_section = p[1]
        p[0].addChild(first_section)

    if len(p[0].children) > 2:
        err_msg = 'Parse error.  Can have at most 2 endpoints per connection.'
        raise WaldoParseException(p[0],err_msg)


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
    MessageSequence : SEQUENCE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN MessageSequenceReturns CURLY_LEFT MessageSequenceGlobalSection MessageSequenceFunctions CURLY_RIGHT
    MessageSequence : SEQUENCE Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN MessageSequenceReturns CURLY_LEFT MessageSequenceFunctions CURLY_RIGHT
    '''
    # syntax:
    #    Sequence <some name> (<some arguments>) returns Text msg, TrueFalse succeeded (returns optional)
    #    {
    #        <some sequence globals> (optional)
    #        <some sequence functions>
    #    }

    # children produced:
    #   Identifier: <some name>
    #   FunctionDeclArgList: <some arguments>
    #   SEQUENCE GLOBALS: <some sequence globals>
    #   MessageSequenceFunctions: <some sequence functions>
    #   return statements
    
    # note that canonicalize moves FunctionDeclArgList from child of
    # AST_MESSAGE_SEQUENCE to child of the first message send
    # function.
    
    p[0] = AstNode(AST_MESSAGE_SEQUENCE,p[2].lineNo,p[2].linePos);
    seq_args = p[4]
    seq_name = p[2]
    seq_returns = p[6]
    p[0].addChildren([seq_name,seq_args])

    
    # default to empty message sequence globals section if not defined
    seq_globs = AstNode(AST_MESSAGE_SEQUENCE_GLOBALS,p[2].lineNo,p[2].linePos);
    seq_functions = p[8]
    if len(p) == 11:
        seq_globs = p[8]
        seq_functions= p[9];

    p[0].addChildren([seq_globs,seq_functions]);
    p[0].addChildren([seq_returns])


def p_MessageSequenceReturns(p):
    '''
    MessageSequenceReturns : Empty
                           | RETURNS FunctionDeclArgList
    '''
    if len(p) == 2:
        # means that we are empty, create an empty function decl
        # arglist and use it for child
        p[0] = AstNode(AST_FUNCTION_DECL_ARGLIST,p[1].lineNo,p[1].linePos)
    else:
        p[0] = p[2]
        


    
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

    # note, note: canonicalize also inserts a functiondeclarglist with
    # return types at the end
    
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
    '''
    TraceBodySection : Identifier COLON TraceLine SEMI_COLON TraceBodySection
                     | Identifier COLON TraceLine SEMI_COLON
    '''

    # produces many children.  Each child has format:
    #   Identifier (name of trace line/message sequence)
    #   Message sequence block name
    #   Message sequence block name
    #   ...
    
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
                             | BreakStatement SEMI_COLON
                             | ContinueStatement SEMI_COLON
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




def getParser(suppress_warnings,programText=None,outputErrsTo=sys.stderr):
    global lexer;
    lexer = constructLexer();

    global ProgramText;
    
    if suppress_warnings:
        returner = yacc.yacc(errorlog=yacc.NullLogger())
    else:
        returner = yacc.yacc()
        
    ProgramText = programText;

    setOutputErrorsTo(outputErrsTo);
    
    return returner;


def getErrorEncountered():
    return astGetErrorEncountered();

def resetErrorEncountered():
    return astResetErrorEncountered();

