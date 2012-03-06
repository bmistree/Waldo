

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
    "CURLY_RIGHT"

    #number
    "NUMBER",
    "VARIABLE",
    
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

        self.numEndpointsSeen    =     0;
        
    def addToken(self,toke):
        tokeType = toke.type;
        returner = toke;

        #determine whether to skip token
        if (self.inMultiLineComment):
            returner.type = SkipTokenType;
        elif(self.inSingleLineComment):
            returner.type = SkipTokenType;
        elif(tokeType == "SPACE"):
            returner.type = SkipTokenType;
        elif(tokeType == "TAB"):
            returner.type = SkipTokenType;
        elif(tokeType == "NEWLINE"):
            returner.type = SkipTokenType;

        #adjust state machine
        if (self.inMultiLineComment):
            if (toke.type == "MULTI_LINE_COMMENT_END"):
                self.inMultiLineComment = False;
        elif(self.inSingleLineComment):
            if (toke.type == "NEWLINE"):
                self.inSingleLineComment = False;
        else:
            if (toke.type == "MULTI_LINE_COMMENT_END"):
                errMsg = "Cannot lex.  multi-line comment ";
                errMsg = "end occurred before multi-line begin."
                raise TypeError(generateTypeError(errMsg));
                
        return returner;

mStateMachine = LexStateMachine();    
    
def generateTypeError(errMsg):
    return errMsg;

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
    'function';
    return mStateMachine.addToken(t);

def t_MSG_SEND(t):
    'msg_send';
    return mStateMachine.addToken(t);

def t_MSG_RECEIVE(t):
    'msg_receive';
    return mStateMachine.addToken(t);

def t_PUBLIC(t):
    'public';
    return mStateMachine.addToken(t);

def t_SENDARROW(t):
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
    'if'
    return mStateMachine.addToken(t);

def t_ELSE(t):
    'else'
    return mStateMachine.addToken(t);

def t_ELSE_IF(t):
    'else[ \t\r\f\v]+if'
    return mStateMachine.addToken(t);

def t_BOOL_EQUALS(t):
    '\=\='
    return mStateMachine.addToken(t);

def t_NOT(t):
    'not'
    return mStateMachine.addToken(t);

def t_TRUE(t):
    'true'
    return mStateMachine.addToken(t);

def t_FALSE(t):
    'false'
    return mStateMachine.addToken(t);

def t_MAP(t):
    'map'
    return mStateMachine.addToken(t);

def t_INT(t):
    'int'
    return mStateMachine.addToken(t);

def t_STRING(t):
    'String'
    return mStateMachine.addToken(t);

def t_LIST(t):
    'list'
    return mStateMachine.addToken(t);

def t_BOOL(t):
    #re-name to something more friendly than boolean.
    'Bool'
    return mStateMachine.addToken(t);

def t_SPACE(t):
    '[ ]+'
    return mStateMachine.addToken(t);

def t_NEWLINE(t):
    '[\n]+'
    return mStateMachine.addToken(t);

#ensure that all keywords are capitalized.

def t_READABLE(t):
    'readable'
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
    '\d+(\.\d*)?'
    return mStateMachine.addToken(t);

def t_VARIABLE(t):
    '[a-zA-Z][a-zA-z0-9\_]*';
    return mStateMachine.addToken(t);

def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,));



def constructLexer():
    lex.lex();
    return lex;
