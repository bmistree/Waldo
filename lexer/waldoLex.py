#!/usr/bin/python

from ply import lex

ONCREATE_TOKEN =  "OnCreate";


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
    "RETURNS",
    "SENDS",
    "RECEIVES",
    
    #messsage notation
    "SEND_ARROW",
    
    #comments
    "SINGLE_LINE_COMMENT",
    "MULTI_LINE_COMMENT_BEGIN",
    "MULTI_LINE_COMMENT_END",

    
    "SEND_OPERATOR",
    "RETURN_OPERATOR",
    "TO_OPERATOR",
    "EQUALS",

    "ONCREATE",
    
    #boolean logic
    "IF",
    "ELSE_IF",
    "ELSE",
    "BOOL_EQUALS",
    "BOOL_NOT_EQUALS",
    "NOT",
    
    "GREATER_THAN_EQ",
    "GREATER_THAN",
    "LESS_THAN_EQ",
    "LESS_THAN",

    
    "BOOL_TYPE",
    
    "TRUE",
    "FALSE",
    
    #data types
    "NUMBER_TYPE",
    "STRING_TYPE",
    "NOTHING_TYPE",

    
    #whitespace
    "SPACE",
    "TAB",
    "NEWLINE",
    
    #other
    "CONTROLS",
    "SEMI_COLON",    
    "COMMA",
    "COLON",
    

    #boolean operators
    "AND",
    "OR",

    #math operators
    "PLUS",
    "MINUS",
    "DIVIDE",
    "MULTIPLY",

    "PRINT",
    
    #brackets/braces
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "LEFT_BRACKET",
    "RIGHT_BRACKET",
    "CURLY_LEFT",
    "CURLY_RIGHT",

    "DOT",
    
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

def generateTokenErrMessage(toke):
    '''
    @returns {String} -- An error message based on the
    token value seen when get into ALL_ELSE.

    For common errors, eg using _ to start an identifier, will provide
    additional information.
    '''

    tVal = repr(toke.value);
    errMsg = 'Error lexing input.  ';
    errMsg += '\n' + tVal + '\n';

    tVal = toke.value;
    additional = None;
    if (tVal == None):
        return errMsg,additional;
    
    if (tVal == '!'):
        additional = 'Maybe you should try using the keyword "Not" instead.  ';
        additional += 'Or use "!=" for "not equals".\n';
    elif (tVal == '&'):
        additional = 'Maybe you should try using the keyword "And" instead ';
        additional += 'if you are performing a logical operation.  There is ';
        additional += 'no way to take the bitwise-and in Waldo.\n'
    elif (tVal == '|'):
        additional = 'Maybe you should try using the keyword "Or" instead ';
        additional += 'if you are performing a logical operation.  There is ';
        additional += 'no way to take the bitwise-or in Waldo.\n'
    elif (tVal == '#'):
        additional = 'If you were trying to write a comment, comments in ';
        additional += 'Waldo are written with // or /* */'
    elif (tVal == '_'):
        additional = 'If you were trying to begin a variable name with "_", ';
        additional += 'This is not allowed.';
    elif(tVal == '%'):
        additional = 'There is no modulo operator in Waldo yet';

    return errMsg, additional;

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
        elif(tokeType == "MULTI_LINE_COMMENT_BEGIN"):
            returner.type = SkipTokenType;
        elif(tokeType == "SINGLE_LINE_COMMENT"):
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
                errMsg,additionalMsg= generateTokenErrMessage(toke);
                # errMsg = 'Should not have gotten an ';
                # errMsg += 'all else when not in comment';
                # errMsg += '\n' + repr(toke.value) + '\n';
                raise WaldoLexException(generateTypeError(errMsg, toke,additionalMsg));
            

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
                raise WaldoLexException(generateTypeError(errMsg,toke));


        if (returner.type == SkipTokenType):
            return None;
        return returner;

mStateMachine = LexStateMachine();    
    
def generateTypeError(errMsg, token,additionalMsg=None):

    errBody = errMsg + ' at line number ' + str(token.lexer.lineno);

    if (additionalMsg != None):
        errBody += '\n' + additionalMsg;
    
    return errBody;

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
    'MessageSend';
    return mStateMachine.addToken(t);

def t_MSG_RECEIVE(t):
    'MessageReceive';
    return mStateMachine.addToken(t);

def t_PUBLIC(t):
    'Public';
    return mStateMachine.addToken(t);

def t_RETURNS(t):
    "Returns";
    return mStateMachine.addToken(t);

def t_SENDS(t):
    "OutgoingMessage";
    return mStateMachine.addToken(t);

def t_RECEIVES(t):
    "IncomingMessage";
    return mStateMachine.addToken(t);

def t_ONCREATE(t):
    "OnCreate";
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

def t_BOOL_EQUALS(t):
    '\=\='
    return mStateMachine.addToken(t);

def t_BOOL_NOT_EQUALS(t):
    "\!\="
    return mStateMachine.addToken(t);


def t_LESS_THAN_EQ(t):
    "\<\="
    return mStateMachine.addToken(t);

def t_LESS_THAN(t):
    "\<"
    return mStateMachine.addToken(t);


def t_GREATER_THAN_EQ(t):
    "\>\="
    return mStateMachine.addToken(t);

def t_GREATER_THAN(t):
    "\>"
    return mStateMachine.addToken(t);


def t_EQUALS(t):
    '\='
    return mStateMachine.addToken(t);

def t_SEND_OPERATOR(t):
    'Send'
    return mStateMachine.addToken(t);

def t_RETURN_OPERATOR(t):
    'Return'
    return mStateMachine.addToken(t);


def t_TO_OPERATOR(t):
    'To'
    return mStateMachine.addToken(t);

def t_PRINT(t):
    'Print'
    return mStateMachine.addToken(t);

def t_IF(t):
    'If'
    return mStateMachine.addToken(t);

def t_ELSE_IF(t):
    r'ElseIf'
    return mStateMachine.addToken(t);


def t_ELSE(t):
    'Else'
    return mStateMachine.addToken(t);

def t_NOTHING_TYPE(t):
    "Nothing"
    return mStateMachine.addToken(t);


def t_NOT(t):
    'Not'
    return mStateMachine.addToken(t);


def t_BOOL_TYPE(t):
    #re-name to something more friendly than boolean.
    'TrueFalse'
    return mStateMachine.addToken(t);


def t_TRUE(t):
    'True'
    return mStateMachine.addToken(t);

def t_FALSE(t):
    'False'
    return mStateMachine.addToken(t);


def t_NUMBER_TYPE(t):
    'Number'
    return mStateMachine.addToken(t);

def t_STRING_TYPE(t):
    'Text'
    return mStateMachine.addToken(t);



def t_SPACE(t):
    '[ ]+'
    return mStateMachine.addToken(t);

def t_NEWLINE(t):
    r"[\r]?[\n]"
    t.lexer.lineno += len(t.value);
    t.value = r"\n";
    return mStateMachine.addToken(t);

#ensure that all keywords are capitalized.

def t_CONTROLS(t):
    'Controls'
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

def t_COLON(t):
    '\:'
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

def t_AND(t):
    'And';
    return mStateMachine.addToken(t);

def t_OR(t):
    'Or';
    return mStateMachine.addToken(t);


def t_DIVIDE(t):
    '\/';
    return mStateMachine.addToken(t);

def t_MULTIPLY(t):
    '\*';
    return mStateMachine.addToken(t);


def t_PLUS(t):
    '\+';
    return mStateMachine.addToken(t);

def t_MINUS(t):
    '\-';
    return mStateMachine.addToken(t);
    

def t_DOT(t):
    '[.]';
    return mStateMachine.addToken(t);
    
def t_NUMBER(t):
    '\d+(\.\d*)?'
    # '[\-]?\d+(\.\d*)?'
    return mStateMachine.addToken(t);

def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z_0-9_]*'
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
    raise WaldoLexException("Unknown text '%s'  at line number '%s'" % (t.value,t.lexer.lineno));


class WaldoLexException(Exception):

   def __init__(self, errMsg):
       self.value = errMsg;

   def __str__(self):
       return repr(self.value)
    
    






def constructLexer():
    mStateMachine = LexStateMachine();
    lex.lex();
    return lex;
