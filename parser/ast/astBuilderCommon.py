#!/usr/bin/python

import os;
import sys;

from parser.ast.typeCheck.typeCheckUtil import setErrorEncountered



from astLabels import *;
from astNode import AstNode;
from lexer.waldoLex import ONCREATE_TOKEN;
from parserUtil import errPrint;

#Program text that we are parsing.  Set in getParser function.  Allows
#us to output surrounding lines when reporting an error.
ProgramText = None;
ERROR_NUM_LINES_EITHER_SIDE = 4;

#note: otherwise, starts at first rule.  
start = 'RootExpression';
#need to have something named lexer for parser to chew into
lexer = None;

def p_NameSection(p):
    'NameSection : Identifier'
    p[0] = p[1];
    p[0].setNote(AST_PROT_OBJ_NAME);


def p_EndpointAliasSection(p):
    'EndpointAliasSection : ENDPOINT Identifier SEMI_COLON ENDPOINT Identifier SEMI_COLON';
    p[0] = AstNode(AST_ENDPOINT_ALIAS_SECTION,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[2], p[5]]);

    

def p_TraceSection(p):
    '''
    TraceSection : TRACES CURLY_LEFT TraceBodySection CURLY_RIGHT
                 | TRACES CURLY_LEFT CURLY_RIGHT
                 ''';
    
    #note: this is an intermediate production, and will get skipped.
    p[0] = AstNode(AST_TRACE_SECTION,p.lineno(1),p.lexpos(1));

    if len(p) == 4:
        pass;
        # # throw error if no code in traces body section.
        # p[0].value = p[1]; # WaldoParseException requires a value field.
        # errMsg = '\nERROR: you must enter code into the "' + p[1] + '" ';
        # errMsg += 'section before you can compile.\n';
        # raise WaldoParseException(p[0],errMsg);

    else:
        # getting TraceBodySection's children removes it as an intermediate node.
        p[0].addChildren(p[3].getChildren());


def p_Garbage(p):
    '''
    Garbage : SINGLE_LINE_COMMENT
            | NEWLINE
            | TAB
            | MULTI_LINE_COMMENT_BEGIN            
            | MULTI_LINE_COMMENT_END
            | SPACE
            | ALL_ELSE
    '''
    # note that this rule should never actually be matched.  It's just
    # included to avoid ply warnings caused by not having a rule to
    # match these tokens.
    err_msg = '\nBehram error: Should never actually attempt to '
    err_msg += 'parse rules for any of these tokens.  Just have '
    err_msg += 'a parsing rule here to avoid ply warnings.\n'
    print err_msg
    assert(False)
    

def p_TraceItem(p):
    'TraceItem : Identifier DOT Identifier'
    #Each TraceItem is connected by arrows in Trace section
    # TraceItem -> TraceItem -> TraceItem;
    p[0] = AstNode(AST_TRACE_ITEM,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);

def p_TraceLine(p):
    '''TraceLine : TraceItem  SEND_ARROW TraceLine
                 | TraceItem  '''

    p[0] = AstNode(AST_TRACE_LINE,p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        #have additional parts of trace body to grab.
        p[0].addChildren(p[3].getChildren());


def p_Jump(p):
    '''
    Jump : JUMP Identifier DOT Identifier
         | FINISH LEFT_PAREN RIGHT_PAREN
    '''

    if len(p) == 4:
        p[0] = AstNode(AST_JUMP_COMPLETE,p.lineno(1),p.lexpos(1));
    else:
        p[0] = AstNode(AST_JUMP,p.lineno(1),p.lexpos(1));
        p[0].addChildren([p[2],p[4]]);
        

def p_SharedSection(p):
    '''SharedSection : SHARED CURLY_LEFT SharedBodySection CURLY_RIGHT
                     | SHARED CURLY_LEFT CURLY_RIGHT''';

    p[0] = AstNode(AST_SHARED_SECTION,p.lineno(1),p.lexpos(1));
    if len(p) == 5:
        p[0].addChildren(p[3].getChildren());

            
def p_SharedBodySection(p):
    '''SharedBodySection : AnnotatedDeclaration SEMI_COLON SharedBodySection
                         | AnnotatedDeclaration SEMI_COLON'''
    p[0] = AstNode(AST_SHARED_BODY_SECTION, p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());

        
def p_AnnotatedDeclaration(p):
    '''AnnotatedDeclaration : Identifier CONTROLS Type Identifier 
                            | Identifier CONTROLS Type Identifier EQUALS TerminalReturnable
                            | NOTHING_TYPE CONTROLS Type Identifier
                            | NOTHING_TYPE CONTROLS Type Identifier EQUALS TerminalReturnable
                            | Declaration
                            '''

    if (p[1] == TYPE_NOTHING):
        # create an Identifier with controls as nothing
        p[1] = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[1]);

    p[0] = AstNode(AST_ANNOTATED_DECLARATION,p[1].lineNo,p[1].linePos);

    if len(p) == 2:
        # means that we do not have any annotation on the variable,
        # ie, change it to Nothing Controls
        declaration_node = p[1]
        declared_type_node = declaration_node.children[0]
        declared_name_node = declaration_node.children[1]

        # create an Identifier with controls as nothing
        nothing_controller_identifier_node = AstNode(
            AST_IDENTIFIER,declaration_node.lineNo,
            declaration_node.linePos,TYPE_NOTHING)

        p[0].addChildren(
            [nothing_controller_identifier_node,declared_type_node,
             declared_name_node])

        if len(declaration_node.children) == 3:
            # means that there's some initializer that we need to add
            initialization_node = declaration_node.children[2]
            p[0].addChild(initialization_node)
        
        return
    

    p[0].addChildren([p[1],p[3],p[4]]);
    
    if (len(p) == 7):
        #have an initialization statement to perform
        p[0].addChild(p[6]);

def p_StructSharedSection(p):
    '''
    StructSharedSection : StructSection SharedSection
                        | StructSection
                        | SharedSection
                        | Empty
    '''

    p[0] = AstNode(AST_STRUCT_SHARED_SECTION,p.lineno(1),p.lexpos(1))
    if len(p) == 3:
        p[0].addChildren([p[1],p[2]])
    elif len(p) == 2:

        blank_struct = AstNode(AST_STRUCT_SECTION,p.lineno(1),p.lexpos(1))
        blank_shared = AstNode(AST_SHARED_SECTION,p.lineno(1),p.lexpos(1))
        
        if isEmptyNode(p[1]):
            # means that we have to fill in two blank
            p[0].addChildren([blank_struct,blank_shared])
        elif p[1].label == AST_STRUCT_SECTION:
            p[0].addChildren([p[1],blank_shared])
        elif p[1].label == AST_SHARED_SECTION:
            p[0].addChildren([blank_struct,p[1]])
        else:
            err_msg = '\nBehram error.  Unexpected label.\n'
            print(err_msg)
            assert(False)
    else:
        err_msg = '\nBehram error.  More parts to struct '
        err_msg += 'shared than expected.\n'
        print (err_msg)
        assert(False)

        
def p_StructSection(p):
    '''
    StructSection : Struct
                  | StructSection Struct
    '''
    
    p[0] = AstNode(AST_STRUCT_SECTION,p[1].lineNo,p[1].linePos)
    if len(p) == 3:
        p[0].addChildren(p[1].getChildren())
        p[0].addChild(p[2])
    elif len(p) == 2:
        p[0].addChild(p[1])
    else:
        errPrint('\nError in StructSection.  Unexpected length to match.\n')
    
def p_Struct (p):
    '''
    Struct : STRUCT Identifier CURLY_LEFT StructBody CURLY_RIGHT
    '''
    p[0] = AstNode(AST_STRUCT_DECLARATION,p.lineno(1),p.lexpos(1))
    struct_name = p[2]
    struct_body = p[4]
    p[0].addChildren([struct_name,struct_body])

    
def p_StructBody(p):
    '''
    StructBody : StructBody Declaration SEMI_COLON
               | Declaration SEMI_COLON
    '''
    p[0] = AstNode(AST_STRUCT_BODY, p.lineno(1),p.lexpos(1))

    if len(p) == 4:
        struct_body_node = p[1]
        decl_node = p[2]
        p[0].addChildren(struct_body_node.getChildren())
    elif len(p) == 3:
        decl_node = p[1]
    else:
        err_msg = '\nBehram error.  Unexpected length in Struct Body.\n'
        print (err_msg)
        assert(False)

    p[0].addChild(decl_node)
    

def p_Type(p):
    '''
    Type : NUMBER_TYPE
         | STRING_TYPE
         | BOOL_TYPE
         | NOTHING_TYPE
         | FunctionType
         | ListType
         | MapType
         | StructType

         | ENDPOINT 
         
         | EXTERNAL NUMBER_TYPE
         | EXTERNAL STRING_TYPE
         | EXTERNAL BOOL_TYPE
         | EXTERNAL ListType
         | EXTERNAL MapType
         '''

    p[0] = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1));    
    if len(p) == 2:
        typeIndex = 1;
    else:
        typeIndex = 2;

    if isinstance(p[typeIndex],basestring):
        p[0].value = p[typeIndex];
    else:
        # means that has function, list type, or struct type
        p[0] = p[typeIndex];

    if len(p) == 3:
        p[0].external = True;

def p_StructType(p):
    '''
    StructType : STRUCT Identifier
    '''
    p[0] = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),TYPE_STRUCT)
    p[0].addChild(p[2])

    
# def p_ExtAssignForTuple(p):
#     '''
#     ExtAssignForTuple : EXT_ASSIGN HOLDER TO_OPERATOR OperatableOn
#     '''
#     p[0] = AstNode(AST_EXT_ASSIGN_FOR_TUPLE,p.lineno(1),p.lexpos(1))
#     p[0].addChild(p[4])
    
# def p_ExtCopyForTuple(p):
#     '''
#     ExtCopyForTuple : EXT_COPY HOLDER TO_OPERATOR OperatableOn
#     '''
#     p[0] = AstNode(AST_EXT_COPY_FOR_TUPLE,p.lineno(1),p.lexpos(1))
#     p[0].addChild(p[4])
    


def p_ExtAssign(p):
    '''
    ExtAssign : EXT_ASSIGN ReturnableExpression TO_OPERATOR OperatableOn
    '''
    p[0] = AstNode(AST_EXT_ASSIGN,p.lineno(1),p.lexpos(1))
    p[0].addChildren([p[2],p[4]])

def p_ExtCopy(p):
    '''
    ExtCopy : EXT_COPY ReturnableExpression TO_OPERATOR OperatableOn
    '''
    p[0] = AstNode(AST_EXT_COPY,p.lineno(1),p.lexpos(1))
    p[0].addChildren([p[2],p[4]])

def p_MapType(p):
    '''
    MapType : MAP LEFT_PAREN FROM COLON Type COMMA TO_OPERATOR COLON Type RIGHT_PAREN
    '''
    p[0] = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),TYPE_MAP);
    # children are key and value of map, respectively
    p[0].addChildren([p[5],p[9]]);

    
def p_ListType(p):
    '''
    ListType : LIST LEFT_PAREN ELEMENT COLON Type RIGHT_PAREN
    '''
    p[0] = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),TYPE_LIST);
    # defines the type of the list
    p[0].addChild(p[5]);

        
def p_FunctionType(p):
    '''
    FunctionType : FUNCTION LEFT_PAREN IN COLON FunctionTypeList SEMI_COLON RETURNS COLON FunctionTypeList RIGHT_PAREN
    FunctionType : FUNCTION LEFT_PAREN RETURNS COLON FunctionTypeList RIGHT_PAREN
    '''
    
    p[0] = AstNode(AST_TYPE, p.lineno(1),p.lexpos(1),TYPE_FUNCTION);

    inToAdd = AstNode(AST_EMPTY,p.lineno(1),p.lexpos(1));
    returnsToAdd = p[5];
    if (len(p) == 11):
        inToAdd = p[5];
        returnsToAdd = p[9];
        
    p[0].addChildren([inToAdd, returnsToAdd]);


def p_FunctionTypeList(p):
    '''
    FunctionTypeList : Type
                     | FunctionTypeList COMMA Type
    '''
    p[0] = AstNode(AST_FUNCTION_TYPE_LIST,p[1].lineNo,p[1].linePos);
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        p[0].addChild(p[1]);
    else:
        errPrint('\nError in TypeList.  Unexpected length to match\n');
        assert(False);


    
def p_TerminalReturnable(p):
    '''
    TerminalReturnable : OperatableOn
                       | NonOperatableOn
    '''
    p[0] = p[1];

def p_LenStatement(p):
    '''
    LenStatement : LEN LEFT_PAREN ReturnableExpression RIGHT_PAREN
    '''
    p[0] = AstNode(AST_LEN,p.lineno(1),p.lexpos(1));
    p[0].addChild(p[3]);

def p_RangeStatement(p):
    '''
    RangeStatement : RANGE LEFT_PAREN ReturnableExpression COMMA ReturnableExpression RIGHT_PAREN
                   | RANGE LEFT_PAREN ReturnableExpression COMMA ReturnableExpression COMMA ReturnableExpression RIGHT_PAREN
    '''

    p[0] = AstNode(AST_RANGE,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[3],p[5]]);
    if len(p) == 7:
        # first line: choose to increment by 1:
        toAdd = AstNode(AST_NUMBER,p.lineno(6),p.lexpos(6),'1');
    else:
        # second line: increment by specified amount
        toAdd = p[7];
    p[0].addChild(toAdd);

def p_KeysStatement(p):
    '''
    KeysStatement : KEYS LEFT_PAREN ReturnableExpression RIGHT_PAREN
    '''
    p[0] = AstNode(AST_KEYS,p.lineno(1),p.lexpos(1));
    p[0].addChild(p[3]);

    
    
def p_NonBracketOperatableOn(p):
    '''
    NonBracketOperatableOn : Number
                           | Identifier
                           | String
                           | Bool
                           | List
                           | Map
                           | FunctionCall
                           | ToTextCall
                           | KeysStatement
                           | LenStatement
                           | RangeStatement
                           | DotStatement
                           | Garbage
                           | Self
                           '''

    # FIXME: got rid of ExtAssignForTuple and ExtCopyForTuple for the
    # time being.
    
    # '''NonBracketOperatableOn : Number
    #                           | Identifier
    #                           | String
    #                           | Bool
    #                           | List
    #                           | Map
    #                           | FunctionCall
    #                           | ToTextCall
    #                           | KeysStatement
    #                           | LenStatement
    #                           | RangeStatement
    #                           | DotStatement
    #                           | ExtAssignForTuple
    #                           | ExtCopyForTuple
    #                           | Garbage
    #                           '''
    
    # note that ExtAssignForTuple and ExtCopyForTuple can only be
    # operatable on as the lhs of an assignment statement from a
    # function call.
    
    p[0] = p[1];



def p_PlusEqual(p):
    '''
    PlusEqual : OperatableOn PLUS_EQUAL ReturnableExpression
    '''
    to_assign_to = p[1]
    to_assign_with = p[3]
    
    p[0] = AstNode(
        AST_ASSIGNMENT_STATEMENT,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to = AstNode(
        AST_OPERATABLE_ON_COMMA_LIST,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to.addChild(to_assign_to)

    p[0].addChild(list_to_assign_to);
    plusNode = AstNode(AST_PLUS,p[1].lineNo,p[1].linePos);
    plusNode.addChildren([to_assign_to,to_assign_with]);
    p[0].addChild(plusNode);

    
def p_MinusEqual(p):
    '''
    MinusEqual : OperatableOn MINUS_EQUAL ReturnableExpression
    '''
    to_assign_to = p[1]
    to_assign_with = p[3]
    

    p[0] = AstNode(
        AST_ASSIGNMENT_STATEMENT,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to = AstNode(
        AST_OPERATABLE_ON_COMMA_LIST,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to.addChild(to_assign_to)

    p[0].addChild(list_to_assign_to);
    minusNode = AstNode(AST_MINUS,p[1].lineNo,p[1].linePos);
    minusNode.addChildren([to_assign_to,to_assign_with]);
    p[0].addChild(minusNode);
    
def p_MultiplyEqual(p):
    '''
    MultiplyEqual : OperatableOn MULTIPLY_EQUAL ReturnableExpression
    '''
    to_assign_to = p[1]
    to_assign_with = p[3]
    
    p[0] = AstNode(
        AST_ASSIGNMENT_STATEMENT,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to = AstNode(
        AST_OPERATABLE_ON_COMMA_LIST,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to.addChild(to_assign_to)

    p[0].addChild(list_to_assign_to);
    multiplyNode = AstNode(AST_MULTIPLY,p[1].lineNo,p[1].linePos);
    multiplyNode.addChildren([to_assign_to,to_assign_with]);
    p[0].addChild(multiplyNode);

    
def p_DivideEqual(p):
    '''
    DivideEqual : OperatableOn DIVIDE_EQUAL ReturnableExpression
    '''
    to_assign_to = p[1]
    to_assign_with = p[3]
    

    p[0] = AstNode(
        AST_ASSIGNMENT_STATEMENT,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to = AstNode(
        AST_OPERATABLE_ON_COMMA_LIST,to_assign_to.lineNo,to_assign_to.linePos)
    list_to_assign_to.addChild(to_assign_to)

    p[0].addChild(list_to_assign_to);
    divideNode = AstNode(AST_DIVIDE,p[1].lineNo,p[1].linePos);
    divideNode.addChildren([to_assign_to,to_assign_with]);
    p[0].addChild(divideNode);

    
def p_OperatableOn(p):
    '''
    OperatableOn : NonBracketOperatableOn
                 | OperatableOn LEFT_BRACKET ReturnableExpression RIGHT_BRACKET
    '''
    if len(p) == 2:
        p[0] = p[1];
    else:
        # add in bracket statement.  left child is what indexing into; right child is index.
        p[0] = AstNode(AST_BRACKET_STATEMENT,p[1].lineNo,p[1].linePos);
        p[0].addChildren([p[1],p[3]]);


def p_PrintCall(p):
    '''
    PrintCall : PRINT LEFT_PAREN ReturnableExpression RIGHT_PAREN
    '''
    p[0] = AstNode(AST_PRINT,p.lineno(1),p.lexpos(1));
    p[0].addChild(p[3]);


def p_RefreshCall(p):
    '''
    RefreshCall : REFRESH LEFT_PAREN RIGHT_PAREN
    '''
    p[0] = AstNode(AST_REFRESH,p.lineno(1),p.lexpos(1));

    
def p_ToTextCall(p):
    '''
    ToTextCall : TOTEXT LEFT_PAREN ReturnableExpression RIGHT_PAREN
    '''
    p[0] = AstNode(AST_TOTEXT_FUNCTION,p.lineno(1),p.lexpos(1));
    p[0].addChild(p[3]);

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
        errPrint(errMsg);
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
    
def p_List(p):
    '''
    List : LEFT_BRACKET ListLiteralItemList RIGHT_BRACKET
    '''
    p[0] = AstNode(AST_LIST,p.lineno(1),p.lexpos(1));
    newKids = p[2].getChildren();
    newKids.reverse();
    p[0].addChildren(newKids);

def p_ListLiteralItemList(p):
    '''ListLiteralItemList : ReturnableExpression 
                           | ReturnableExpression COMMA ListLiteralItemList 
                           | Empty'''

    # this will produce a reversed list.  ensure to re-reverse when
    # use in list.
    p[0] = AstNode(AST_LIST_INTERMEDIATE,p[1].lineNo,p[1].linePos);
    if (len(p) == 4):
        # second line
        p[0].addChildren(p[3].getChildren());
        p[0].addChild(p[1]);
    elif(len(p) == 2):
        if (not isEmptyNode(p[1])):
            # first line
            p[0].addChild(p[1]);
    else:
        errPrint('\nError in ListLiteralItemList.  Unexpected length to match\n');
        assert(False);

    
def p_Map(p):
    '''
    Map : CURLY_LEFT MapLiteralItemList CURLY_RIGHT
    '''
    p[0] = AstNode(AST_MAP,p.lineno(1),p.lexpos(1));
    # ensures that map literal will be parsed in left-to-right order.
    # doubt that this will be defined behavior, but for the time being,
    # keep it that way.
    newKids = p[2].getChildren();
    newKids.reverse();
    p[0].addChildren(newKids);


def p_MapLiteralItemList(p):
    '''
    MapLiteralItemList : MapLiteralItem
                       | MapLiteralItem COMMA MapLiteralItemList
                       | Empty
    '''
    p[0] = AstNode(AST_MAP_INTERMEDIATE,p[1].lineNo,p[1].linePos);
    if (len(p) == 2) and (p[1].label == AST_MAP_ITEM):
        # first line
        p[0].addChild(p[1]);
    elif len(p) == 4:
        # second line
        p[0] = p[3];
        p[0].addChild(p[1]);
    else:
        # last line: it's just empty
        pass;


    
def p_MapLiteralItem(p):
    '''
    MapLiteralItem : ReturnableExpression COLON ReturnableExpression
    '''
    p[0] = AstNode(AST_MAP_ITEM,p.lineno(1),p.lexpos(1));
    p[0].addChildren([p[1],p[3]]);    
 
        
def p_Identifier(p):
    'Identifier : IDENTIFIER';
    p[0] = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[1]);

def p_Self(p):
    'Self : SELF'
    p[0] = AstNode(AST_SELF,p.lineno(1),p.lexpos(1))

def p_EndpointSection(p):
    '''EndpointSection : Identifier CURLY_LEFT EndpointBodySection CURLY_RIGHT
                       | Identifier CURLY_LEFT CURLY_RIGHT'''
    p[0] = AstNode(AST_ENDPOINT,p[1].lineNo,p[1].linePos);

    p[0].addChild(p[1]);
    if (len(p) == 5):
        p[0].addChild(p[3]);
    elif len(p) == 4:
        # means that we had nothing defined in the endpoint create
        # empty versions so that type checking gets what it expects.
        bodySecChild = AstNode(AST_ENDPOINT_BODY_SECTION,p[1].lineNo,p[1].linePos);
        bodyGlobSec = AstNode(AST_ENDPOINT_GLOBAL_SECTION,p[1].lineNo,p[1].linePos);
        funcGlobSec = AstNode(AST_ENDPOINT_FUNCTION_SECTION,p[1].lineNo,p[1].linePos);
        bodySecChild.addChildren([bodyGlobSec,funcGlobSec]);
        p[0].addChild(bodySecChild);


def p_EndpointBodySection(p):
    '''EndpointBodySection : EndpointGlobalSection EndpointFunctionSection
                           | EndpointFunctionSection
                           | EndpointGlobalSection
                           '''

    p[0] = AstNode(AST_ENDPOINT_BODY_SECTION,p[1].lineNo,p[1].linePos);
    if (len(p) == 3):
        p[0].addChildren([p[1],p[2]]);
    elif len(p) == 2:
        # check that had no globals, but had a function:
        if p[1].label == AST_ENDPOINT_FUNCTION_SECTION:
            # means that we had no globals.  add them
            p[0].addChild(AstNode(AST_ENDPOINT_GLOBAL_SECTION, p[1].lineNo,p[1].linePos));
            p[0].addChild(p[1]);
        else:
            # menas that there were globals, but no functions.  add
            # empty functions.
            p[0].addChild(p[1]);
            p[0].addChild(AstNode(AST_ENDPOINT_FUNCTION_SECTION,p[1].lineNo,p[1].linePos));
    else:
        errPrint('\nError in endpoint body section.  Got an unusual number of arguments.\n');
        assert(False);
    

def p_EndpointGlobalSection(p):
    '''EndpointGlobalSection : Declaration SEMI_COLON EndpointGlobalSection
                             | Declaration SEMI_COLON'''
    p[0] = AstNode(AST_ENDPOINT_GLOBAL_SECTION, p[1].lineNo,p[1].linePos);
    p[0].addChild(p[1]);
    if (len(p) == 4):
        p[0].addChildren(p[3].getChildren());


def p_Function(p):
    '''Function : PRIVATE FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS FunctionTypeList CURLY_LEFT FunctionBody CURLY_RIGHT
                | PRIVATE FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS FunctionTypeList CURLY_LEFT  CURLY_RIGHT
                | PRIVATE FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                | PRIVATE FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT  CURLY_RIGHT
                '''                 
    p[0] = AstNode(AST_PRIVATE_FUNCTION, p.lineno(1),p.lexpos(1));

    # if no returns type was declared, then insert it for user so that it returns nothing
    returnsTypeNode = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),TYPE_NOTHING);
    if (len(p) == 12) or (len(p) == 11):
        # handles cases where returns type was declared
        returnsTypeNode = p[8];

    
    p[0].addChildren([p[3],returnsTypeNode,p[5]]);

    if (len(p) == 12):
        # return type and function body
        p[0].addChild(p[10]);
    elif(len(p) == 10):
        # no return type and function body
        p[0].addChild(p[8]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));

    
def p_PublicFunction(p):
    '''
    PublicFunction : PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS FunctionTypeList CURLY_LEFT FunctionBody CURLY_RIGHT
                   | PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN RETURNS FunctionTypeList CURLY_LEFT  CURLY_RIGHT
                   | PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                   | PUBLIC FUNCTION Identifier LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT CURLY_RIGHT
                   '''
    
    p[0] = AstNode(AST_PUBLIC_FUNCTION, p.lineno(1),p.lexpos(1));

    # if no returns type was declared, then insert it for user so that it returns nothing
    returnsTypeNode = AstNode(AST_TYPE,p.lineno(1),p.lexpos(1),TYPE_NOTHING);
    if (len(p) == 12) or (len(p) == 11):
        # handles cases where returns type was declared
        returnsTypeNode = p[8];
        
    p[0].addChildren([p[3],returnsTypeNode,p[5]]);
    if (len(p) == 12):
        # return type and function body
        p[0].addChild(p[10]);
    elif len(p) == 10:
        # no return type and function body
        p[0].addChild(p[8]);
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
        errPrint('\nError statement length mismatch in FunctionBody\n');
        assert(False);


def p_BreakStatement(p):
    '''
    BreakStatement : BREAK
    '''
    p[0] = AstNode(AST_BREAK,p.lineno(1),p.lexpos(1))

def p_ContinueStatement(p):
    '''
    ContinueStatement : CONTINUE
    '''
    p[0] = AstNode(AST_CONTINUE,p.lineno(1),p.lexpos(1))

    
    
def p_ReturnStatement(p):
    '''
    ReturnStatement : RETURN_OPERATOR FunctionArgList
    '''
    p[0] = AstNode(AST_RETURN_STATEMENT,p.lineno(1),p.lexpos(1));
    p[0].addChild(p[2])

    
def p_OnCreateFunction(p):
    '''
    OnCreateFunction : ONCREATE  LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT FunctionBody CURLY_RIGHT
                     | ONCREATE  LEFT_PAREN FunctionDeclArgList RIGHT_PAREN CURLY_LEFT CURLY_RIGHT
    '''
    p[0] = AstNode(AST_ONCREATE_FUNCTION,p.lineno(1),p.lexpos(1));
    onCreateName = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[1]);
    p[0].addChildren([onCreateName,p[3]]);
    if (len(p) == 8):
        p[0].addChild(p[6]);
    else:
        #means that we had no function body, insert an impostor
        #function body node.
        p[0].addChild(AstNode(AST_FUNCTION_BODY, p.lineno(1),p.lexpos(1)));

        
def p_OnCompleteFunction(p):
    '''
    OnCompleteFunction : Identifier DOT ONCOMPLETE CURLY_LEFT FunctionBody CURLY_RIGHT
                       | Identifier DOT ONCOMPLETE CURLY_LEFT CURLY_RIGHT
    '''
    p[0] = AstNode(AST_ONCOMPLETE_FUNCTION,p.lineno(2),p.lexpos(2));
    onCompleteName = AstNode(AST_IDENTIFIER,p.lineno(1),p.lexpos(1),p[3]);
    p[0].addChildren([p[1], onCompleteName]); # contains the endpoint that of this function

    functionBodyToAdd = p[5];
    if len(p) == 6:
        # means that have empty function body, should add dummy instead
        functionBodyToAdd = AstNode(AST_FUNCTION_BODY,p.lineno(2),p.lexpos(2));
    p[0].addChild(functionBodyToAdd);


def p_WhileStatement(p):
    '''
    WhileStatement : WHILE LEFT_PAREN ReturnableExpression RIGHT_PAREN SingleLineOrMultilineCurliedBlock
    '''
    p[0] = AstNode(AST_WHILE_STATEMENT,p.lineno(1),p.lexpos(1))
    bool_cond = p[3]
    body = p[5]
    p[0].addChildren([bool_cond,body])
    
    
def p_ForStatement (p):
    '''
    ForStatement : FOR LEFT_PAREN Identifier IN ReturnableExpression RIGHT_PAREN SingleLineOrMultilineCurliedBlock
                 | FOR LEFT_PAREN Type Identifier IN ReturnableExpression RIGHT_PAREN SingleLineOrMultilineCurliedBlock    
    '''
    
    p[0] = AstNode(AST_FOR_STATEMENT,p.lineno(1),p.lexpos(1));
    if len(p) == 8:
        # means that not defining a new variable
        p[0].addChildren([ p[3], p[5], p[7] ] );
    elif len(p) == 9:
        # defining a new variable
        p[0].addChildren([ p[3], p[4], p[6], p[8] ]);
    else:
        errMsg = '\nBehram error: incorrect number of tokens when ';
        errMsg += 'parsing for statement.\n';
        print(errMsg);
        assert(False);

        
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
        errPrint('\nIncorrect match count in ElseStatement.\n');
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
        errPrint('\nIncorrect match vector in SingleLineOrMultilineCurliedBlock\n');
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
                       | GREATER_THAN
                       | GREATER_THAN_EQ
                       | LESS_THAN
                       | LESS_THAN_EQ
                       '''

    if (p[1] == 'and'):
        p[0] = AstNode(AST_AND,p.lineno(1),p.lexpos(1));
    elif(p[1] == 'or'):
        p[0] = AstNode(AST_OR,p.lineno(1),p.lexpos(1));
    elif(p[1] == '=='):
        p[0] = AstNode(AST_BOOL_EQUALS,p.lineno(1),p.lexpos(1));
    elif(p[1] == '!='):
        p[0] = AstNode(AST_BOOL_NOT_EQUALS,p.lineno(1),p.lexpos(1));
    elif(p[1] == '>'):
        p[0] = AstNode(AST_GREATER_THAN,p.lineno(1),p.lexpos(1));
    elif(p[1] == '>='):
        p[0] = AstNode(AST_GREATER_THAN_EQ,p.lineno(1),p.lexpos(1));
    elif(p[1] == '<'):
        p[0] = AstNode(AST_LESS_THAN,p.lineno(1),p.lexpos(1));
    elif(p[1] == '<='):
        p[0] = AstNode(AST_LESS_THAN_EQ,p.lineno(1),p.lexpos(1));        
    else:
        errPrint('\nIncorrect boolean operator: ' + p[1] + '\n');
        assert(False);


def p_DotStatement(p):
    '''
    DotStatement : OperatableOn DOT Identifier
    '''
    p[0] = AstNode(AST_DOT_STATEMENT,p.lineno(2),p.lexpos(2))
    p[0].addChildren([p[1],p[3]])

    
def p_AssignmentStatement(p):
    '''
    AssignmentStatement : OperatableOnCommaList EQUALS ReturnableExpression
    '''
    operatable_on_list = p[1]
    if len(operatable_on_list.children) == 0:
        err_msg = 'Error in assignment statement.  Must assign '
        err_msg += 'to something.'
        raise WaldoParseException(
            operatable_on_list,err_msg);
    
    p[0] = AstNode(AST_ASSIGNMENT_STATEMENT,p[1].lineNo,p[1].linePos);
    p[0].addChildren([p[1],p[3]]);

    
def p_OperatableOnCommaList(p):
    '''
    OperatableOnCommaList : OperatableOn
                          | OperatableOnCommaList COMMA OperatableOn
                          | Empty
    '''

    p[0] = AstNode(AST_OPERATABLE_ON_COMMA_LIST,p[1].lineNo,p[1].linePos);
    if (len(p) == 4):
        p[0].addChildren(p[1].getChildren());
        p[0].addChild(p[3]);
    elif(len(p) == 2):
        if (not isEmptyNode(p[1])):
            p[0].addChild(p[1]);
    else:
        errPrint('\nError in OperatableOnCommaList.  Unexpected length to match\n');
        assert(False);


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
        errPrint('\nIncorrect number of matches in ReturnableExpression\n');
        assert(False);

def p_BinaryOperator(p):
    '''
    BinaryOperator : PlusMinusOperator
                   | MultDivOperator
                   | BooleanOperator
    '''
    p[0] = p[1];

def p_ParenthesizedExpression(p):
    '''ParenthesizedExpression : NOT ReturnableExpression
                               | InExpression
    '''
    
    if (len(p) == 3):
        p[0] = AstNode(AST_NOT_EXPRESSION, p.lineno(1),p.lexpos(1));
        p[0].addChild(p[2]);
    elif(len(p) == 2):
        p[0] = p[1];
    else:
        errPrint('\nIncorrect matching in ReturnableExpression\n');
        assert(False);


def p_InExpression(p):
    '''
    InExpression : BooleanStatement IN InExpression
                 | BooleanStatement
    '''
    if len(p) == 4:
        p[0] = AstNode(AST_IN_STATEMENT, p[1].lineNo,p[1].linePos);
        p[0].addChildren([ p[1], p[3] ]);
    else:
        p[0] = p[1];


def p_BooleanStatement(p):
    '''BooleanStatement : NonBooleanStatement BooleanOperator BooleanStatement
                        | NonBooleanStatement'''

    #skip over internal_returnable_expression label
    if (len(p) == 2):
        p[0] = p[1];
    elif (len(p) == 4):
        p[0] = p[2];
        p[0].addChild(p[1]);
        p[0].addChild(p[3]);
    else:
        errPrint('\nIn BooleanStatement, incorrect number of matches\n');
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
        errPrint('\nIncorrect number of matches in NonBooleanStatement\n');
        assert(False);
        
    
def p_PlusMinusOperator(p):
    '''PlusMinusOperator : PLUS
                         | MINUS'''

    if (p[1] == '+'):
        p[0] = AstNode(AST_PLUS, p.lineno(1),p.lexpos(1));
    elif(p[1] == '-'):
        p[0] = AstNode(AST_MINUS, p.lineno(1),p.lexpos(1));
    else:
        errPrint('\nIncorrect number of matches in PlusMinusOperator\n');
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
        errPrint('\nIncorrect number of matches in MultDivStatement\n');
        assert(False);

        
def p_MultDivOperator(p):
    '''MultDivOperator : MULTIPLY
                       | DIVIDE'''

    if (p[1] == '*'):
        p[0] = AstNode(AST_MULTIPLY, p.lineno(1),p.lexpos(1));
    elif(p[1] == '/'):
        p[0] = AstNode(AST_DIVIDE, p.lineno(1),p.lexpos(1));
    else:
        errPrint('\nIncorrect number of matches in MultDivOperator\n');
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
        errPrint('\nError in FunctionDeclArgList.  Unexpected length to match\n');
        assert(False);


def p_FunctionCall(p):
    '''
    FunctionCall : OperatableOn LEFT_PAREN FunctionArgList RIGHT_PAREN
    '''
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
        errPrint('\nError in FunctionArgList.  Unexpected length to match\n');
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


def p_error(p):
    raise WaldoParseException(p);



class WaldoParseException(Exception):

   def __init__(self, p, msg=None):

       if (msg != None):
           # means that we raised the error ourselves, not lexpy.  Do
           # some basic translation to ensure that our astnode methods
           # line up with those that are passed through in ply.
           p.lineno = p.lineNo;
           p.lexpos = p.linePos;
           
       
       setErrorEncountered();
       self.value = '';
       if (p == None):
           self.value += '\nError: end of file and missing some structure\n';
       elif p.value == ONCREATE_TOKEN:
           errMsg = '\nError: OnCreate is a reserved word that  ';
           errMsg += 'cannot be called directly from other functions.\n';
           self.value += errMsg;
       else:
        
           if msg != None:
               self.value += msg;

        
           self.value += '\nSyntax error on "' + p.value + '".\n';
           self.value += 'Near line number: ' + str(p.lineno);
           self.value += '\n';

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

               errorText += '\nThe actual error may be one or two lines ';
               errorText += 'above or below this point.  \nCommon errors ';
               errorText += 'include forgetting a semi-colon or not capitalizing ';
               errorText += 'a \nkeyword operator (for instance "return 3;" instead ';
               errorText += 'of \n"Return 3;".\n';

               self.value += errorText;


   def __str__(self):
       return repr(self.value);
    
