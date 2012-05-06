#!/usr/bin/python

#From http://pentangle.net/python/handbook/node52.html
#I also personally added self.
PYTHON_RESERVED_WORD_DICT = {
    'self': True,
    'and':True,
    'assert':True,
    'break':True,
    'class':True,
    'continue':True,
    'def':True,
    'del':True,
    'elif':True,
    'else':True,
    'except':True,
    'exec':True,
    'finally':True,
    'for':True,
    'from':True,
    'global':True,
    'if':True,
    'import':True,
    'in':True,
    'is':True,
    'lambda':True,
    'not':True,
    'or':True,
    'pass':True,
    'print':True,
    'raise':True,
    'return':True,
    'try':True,
    'while':True,
    'Data':True,
    'Float':True,
    'Int':True,
    'Numeric':True,
    'Oxphys':True,
    'array': True,
    'close':True,
    'float':True,
    'int':True,
    'input':True,
    'open':True,
    'range':True,
    'type':True,
    'write':True,
    'zeros':True,
    'acos':True,
    'asin':True,
    'atan':True,
    'cos':True,
    'e':True,
    'exp':True,
    'fabs':True,
    'floor':True,
    'log':True,
    'log10':True,
    'pi':True,
    'sin':True,
    'sqrt':True,
    'tan':True
    }

def isPythonReserved(varName):
    '''
    @returns True if varName is a reserved word in python.  False
    otherwise.
    '''
    returner = varName in PYTHON_RESERVED_WORD_DICT;
    return returner;
    
