#!/usr/bin/env python


from astNode import *;
from astLabels import *;

def preprocess(astNode,progText):
    '''
    @param {AstNode} astNode --- Root of ast.
    @param {String} progText --- Text of program.
    
    Run through the ast generated from parsing and operate on it so
    that it is ready for type checking, slicing, and emitting.
    (Shouldn't really need the intermediate stage from parsing to type
    checking, but having this makes it easier to prototype fast
    changes to syntax.)

    Big changes:

        * Run through all definitions of message sequences and move
          the FunctionDeclArgList-s that appear as children under each
          to appear instead as children of each sequence's respective
          message send sequence function.

        * Run through all definitions of message sequences and move
          the FunctionDeclArgList-s that appear as children under 
    
    '''
    
    move_sequence_function_args(astNode)

def move_sequence_function_args(ast_node):
    '''
    Run through all definitions of message sequences and move
    the FunctionDeclArgList-s that appear as children under each
    to appear instead as children of each sequence's respective
    message send sequence function.
    '''

    msg_sequences_node = ast_node.children[6]
    # debug
    if msg_sequences_node.label != AST_MESSAGE_SEQUENCE_SECTION:
        err_msg = '\nIncorrect label on message sequences node.\n'
        print err_msg
        assert (False)
    # end debug

        
    for msg_seq_node in msg_sequences_node.children:
        # remove the second child (containing function aguments) from
        # msg_seq_node's children.  

        func_args_node = msg_seq_node.children[1]
        msg_seq_functions_node = msg_seq_node.children[3]

        # debug
        if func_args_node.label != AST_FUNCTION_DECL_ARGLIST:
            print '\nError: require function decl arglist.\n'
            assert(False)
        # end debug
            
        
        # remove func_args_node from msg sequence
        del msg_seq_node.children[1]

        
        # insert it into msg send func node
        msg_send_func_node = msg_seq_functions_node.children[0]

        msg_send_func_node.children.insert(
            2,func_args_node)
    
