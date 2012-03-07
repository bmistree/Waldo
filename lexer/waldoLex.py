#!/usr/bin/python

from ply import lex

tokens = (
    #high-level structure
    "ENDPOINT",
    "TRACES",
    "SHARED",

    #functions
    "FUNCTION",
    "MSG_SEND",
    "MSG_RECEIVE",
    "PUBLIC",

    #messsage notation
    "SEND_ARROW",
    
    #comments
    "SINGLE_LINE_COMMENT",
    "MULTI_LINE_COMMENT_BEGIN",
    "MULTI_LINE_COMMENT_END",
    "EQUALS",

    #boolean logic
    "IF",
    "ELSE",
    "ELSE_IF",
    "BOOL_EQUALS",
    "NOT",
    "TRUE",
    "FALSE",
    
    #data types
    "MAP",
    "INT",
    "STRING",
    "LIST",
    "BOOL",

    #whitespace
    "SPACE",
    "TAB",
    "NEWLINE",
    
    #other
    "READABLE",
    "SEMI_COLON",    
    "COMMA",


    #brackets/braces
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "LEFT_BRACKET",
    "RIGHT_BRACKET",
    "CURLY_LEFT",
    "CURLY_RIGHT",

    
    "NUMBER",
    "IDENTIFIER",
    
    #Strings and quotes
    "MULTI_LINE_STRING",
    "SINGLE_LINE_STRING",
    
    "ALL_ELSE",
    )
'''
Still to add:
  begin verbatim
  end verbatim
  for
  switch
  case
'''

SkipTokenType = "SPACE";

class LexStateMachine():
    def __init__ (self):
        self.inMultiLineComment  = False;
        self.inSingleLineComment = False;
        self.inMultiLineString   = False;
        self.inSingleLineString  = False;
        self.fullString = '';
        
        self.numEndpointsSeen    =     0;
        
    def addToken(self,toke):
        tokeType = toke.type;
        returner = toke;

        #determine whether to skip token
        if (self.inMultiLineString):
            if (tokeType != "MULTI_LINE_STRING"):
                #we're still in the multi-line string
                self.fullString += str(toke.value);
                returner.type = SkipTokenType;
        elif(self.inSingleLineString):
            if (tokeType != "SINGLE_LINE_STRING"):
                #we're still in the single-line string
                self.fullString += str(toke.value);
                returner.type = SkipTokenType;
        elif (self.inMultiLineComment):
            returner.type = SkipTokenType;
        elif(self.inSingleLineComment):
            returner.type = SkipTokenType;
        elif(tokeType == "SPACE"):
            returner.type = SkipTokenType;
        elif(tokeType == "TAB"):
            returner.type = SkipTokenType;
        elif(tokeType == "NEWLINE"):
            returner.type = SkipTokenType;
        elif (tokeType == 'ALL_ELSE'):
            if ((self.inMultiLineComment) or (self.inSingleLineComment)):
                returner.type = SkipTokenType;
            else:
                errMsg = 'Should not have gotten an ';
                errMsg += 'all else when not in comment';
                errMsg += '\n' + repr(toke.value) + '\n';
                raise TypeError(generateTypeError(errMsg, toke));
            

        #adjust state machine
        if (self.inMultiLineString):
            #check close multi-line string
            if (tokeType == "MULTI_LINE_STRING"):
                #preserver token type of string on end.
                self.inMultiLineString = False;
                returner.value = self.fullString;
                self.fullString = '';

        elif (self.inSingleLineString):
            #check close multi-line string
            if (tokeType == "SINGLE_LINE_STRING"):
                #preserver token type of string on end.
                self.inSingleLineString = False;
                returner.value = self.fullString;
                self.fullString = '';
        elif (self.inMultiLineComment):
            if (tokeType == "MULTI_LINE_COMMENT_END"):
                self.inMultiLineComment = False;
        elif(self.inSingleLineComment):
            if (tokeType == "NEWLINE"):
                self.inSingleLineComment = False;
        elif(tokeType == "MULTI_LINE_COMMENT_BEGIN"):
            self.inMultiLineComment = True;
        elif(tokeType == "SINGLE_LINE_COMMENT"):
            self.inSingleLineComment = True;
        elif(tokeType == "MULTI_LINE_STRING"):
            self.inMultiLineString = True;
            returner.type = SkipTokenType;
        elif(tokeType == "SINGLE_LINE_STRING"):
            self.inSingleLineString = True;
            returner.type = SkipTokenType;
        else:
            if (tokeType == "MULTI_LINE_COMMENT_END"):
                errMsg = "Cannot lex.  multi-line comment ";
                errMsg = "end occurred before multi-line begin."
                raise TypeError(generateTypeError(errMsg,toke));
                
        return returner;

mStateMachine = LexStateMachine();    
    
def generateTypeError(errMsg, token):
    return errMsg + ' at line number ' + str(token.lexer.lineno);

'''
Rule definitions
'''

#high-level structure
def t_ENDPOINT(t):
    'Endpoint';
    return mStateMachine.addToken(t);

def t_TRACES(t):
    'Traces';
    return mStateMachine.addToken(t);

def t_SHARED(t):
    'Shared';
    return mStateMachine.addToken(t);

def t_FUNCTION(t):
    'Function';
    return mStateMachine.addToken(t);

def t_MSG_SEND(t):
    'Msg_send';
    return mStateMachine.addToken(t);

def t_MSG_RECEIVE(t):
    'Msg_receive';
    return mStateMachine.addToken(t);

def t_PUBLIC(t):
    'Public';
    return mStateMachine.addToken(t);

def t_SEND_ARROW(t):
    '-\>'
    return mStateMachine.addToken(t);

def t_SINGLE_LINE_COMMENT(t):
    '\/\/'
    return mStateMachine.addToken(t);

def t_MULTI_LINE_COMMENT_BEGIN(t):
    '\/\*'
    return mStateMachine.addToken(t);


def t_MULTI_LINE_COMMENT_END(t):
    '\*\/'
    return mStateMachine.addToken(t);

def t_EQUALS(t):
    '\='
    return mStateMachine.addToken(t);

def t_IF(t):
    'If'
    return mStateMachine.addToken(t);

def t_ELSE(t):
    'Else'
    return mStateMachine.addToken(t);

def t_ELSE_IF(t):
    r'Else[ \t\r\f\v]+if'
    return mStateMachine.addToken(t);

def t_BOOL_EQUALS(t):
    '\=\='
    return mStateMachine.addToken(t);

def t_NOT(t):
    'Not'
    return mStateMachine.addToken(t);

def t_TRUE(t):
    'True'
    return mStateMachine.addToken(t);

def t_FALSE(t):
    'False'
    return mStateMachine.addToken(t);

def t_MAP(t):
    'Map'
    return mStateMachine.addToken(t);

def t_INT(t):
    'Int'
    return mStateMachine.addToken(t);

def t_STRING(t):
    'String'
    return mStateMachine.addToken(t);

def t_LIST(t):
    'List'
    return mStateMachine.addToken(t);

def t_BOOL(t):
    #re-name to something more friendly than boolean.
    'Bool'
    return mStateMachine.addToken(t);

def t_SPACE(t):
    '[ ]+'
    return mStateMachine.addToken(t);

def t_NEWLINE(t):
    r"[\n]"
    t.lexer.lineno += len(t.value);
    t.value = r"\n";
    return mStateMachine.addToken(t);

#ensure that all keywords are capitalized.

def t_READABLE(t):
    'Readable'
    return mStateMachine.addToken(t);

def t_LEFT_PAREN(t):
    '\('
    return mStateMachine.addToken(t);

def t_RIGHT_PAREN(t):
    '\)'
    return mStateMachine.addToken(t);

def t_COMMA(t):
    '\,'
    return mStateMachine.addToken(t);

def t_LEFT_BRACKET(t):
    '\['
    return mStateMachine.addToken(t);

def t_RIGHT_BRACKET(t):
    '\]'
    return mStateMachine.addToken(t);

def t_SEMI_COLON(t):
    '\;'
    return mStateMachine.addToken(t);


def t_CURLY_LEFT(t):
    '\{';
    return mStateMachine.addToken(t);

def t_CURLY_RIGHT(t):
    '\}';
    return mStateMachine.addToken(t);


def t_NUMBER(t):
    '[\-]?\d+(\.\d*)?'
    return mStateMachine.addToken(t);

def t_IDENTIFIER(t):
    '[a-zA-Z][a-zA-z0-9\_]*';
    return mStateMachine.addToken(t);

def t_MULTI_LINE_STRING(t):
    r'[\"]'
    return mStateMachine.addToken(t);

def t_SINGLE_LINE_STRING(t):
    r'[\']'
    return mStateMachine.addToken(t);


def t_ALL_ELSE(t):
    '.'
    return mStateMachine.addToken(t);

def t_error(t):
    raise TypeError("Unknown text '%s'  at line number '%s'" % (t.value,t.lexer.lineno));



def constructLexer():
    mStateMachine = LexStateMachine();
    lex.lex();
    return lex;
