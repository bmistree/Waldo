import os,sys


from waldo.deps.ply.ply import lex

ONCREATE_TOKEN =  "onCreate";
ONCOMPLETE_TOKEN = 'onComplete';
IDENTIFIER_TOKEN = "IDENTIFIER";
reserved = {
    'Endpoint' : 'ENDPOINT',
    'Sequences': 'TRACES',
    'Peered': 'SHARED',
    'Function': 'FUNCTION',
    'List': 'LIST',
    'Map': 'MAP',
    'from': 'FROM',
    'element': 'ELEMENT',
    'Public': 'PUBLIC',
    'Private': 'PRIVATE',
    'Sequence': 'SEQUENCE',
    'returns': 'RETURNS',
    'in': 'IN',
    'toText': 'TOTEXT',
    ONCREATE_TOKEN: 'ONCREATE',
    ONCOMPLETE_TOKEN: 'ONCOMPLETE',
    'return': 'RETURN_OPERATOR',
    'to': 'TO_OPERATOR',
    'print': 'PRINT',
    'signal': 'SIGNAL',
    'if': 'IF',
    'elseIf': 'ELSE_IF',
    'else': 'ELSE',
    'Nothing': 'NOTHING_TYPE',
    'not': 'NOT',
    'TrueFalse': 'BOOL_TYPE',
    'True': 'TRUE',
    'False': 'FALSE',
    'Number': 'NUMBER_TYPE',
    'Text': 'STRING_TYPE',
    'controls': 'CONTROLS',
    'and': 'AND',
    'or': 'OR',
    'while': 'WHILE',
    'for': 'FOR',
    'range': 'RANGE',
    'keys': 'KEYS',
    'len': 'LEN',
    'External': 'EXTERNAL',
    'finish': 'FINISH',
    'refresh': 'REFRESH',
    'Jump': 'JUMP',
    'extAssign':'EXT_ASSIGN',
    'extCopy':'EXT_COPY',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'Struct': 'STRUCT',
    'self': 'SELF',
    'Symmetric': 'SYMMETRIC',
    };


tokens = [
    #messsage notation
    "SEND_ARROW",
    
    #comments
    "SINGLE_LINE_COMMENT",
    "MULTI_LINE_COMMENT_BEGIN",
    "MULTI_LINE_COMMENT_END",

    "EQUALS",
    "BOOL_EQUALS",
    "BOOL_NOT_EQUALS",
    
    "GREATER_THAN_EQ",
    "GREATER_THAN",
    "LESS_THAN_EQ",
    "LESS_THAN",
    
    #whitespace
    "SPACE",
    "TAB",
    "NEWLINE",
    
    #other
    "SEMI_COLON",    
    "COMMA",
    "COLON",

    # operator=
    "PLUS_EQUAL",
    "MINUS_EQUAL",
    "DIVIDE_EQUAL",
    "MULTIPLY_EQUAL",
    
    #math operators
    "PLUS",
    "MINUS",
    "DIVIDE",
    "MULTIPLY",
    
    #brackets/braces
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "LEFT_BRACKET",
    "RIGHT_BRACKET",
    "CURLY_LEFT",
    "CURLY_RIGHT",
    
    "DOT",
    
    "NUMBER",
    IDENTIFIER_TOKEN,
    'HOLDER',
    
    #Strings and quotes
    "MULTI_LINE_STRING",
    "SINGLE_LINE_STRING",
    
    "ALL_ELSE",
    ] + list(reserved.values());




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



def t_SPACE(t):
    '[ \t]+'
    return mStateMachine.addToken(t);

def t_NEWLINE(t):
    r"[\r]?[\n]"
    t.lexer.lineno += len(t.value);
    t.value = r"\n";
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

def t_DIVIDE_EQUAL(t):
    '\/='
    return mStateMachine.addToken(t);

def t_MINUS_EQUAL(t):
    '-='
    return mStateMachine.addToken(t);

def t_PLUS_EQUAL(t):
    '\+='
    return mStateMachine.addToken(t);

def t_MULTIPLY_EQUAL(t):
    '\*='
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
    return mStateMachine.addToken(t);

def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z_0-9_]*';
    t.type = reserved.get(t.value,IDENTIFIER_TOKEN);    # Check for reserved words
    return mStateMachine.addToken(t);

def t_HOLDER(t):
    r'_'
    return mStateMachine.addToken(t)

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
