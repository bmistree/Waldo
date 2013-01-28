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
          message send sequence function.  (These are the arguments
          that the message sequence function is meant to take.)

        * Run through all definitions of message sequences and move
          the FunctionDeclArgList-s that appear as children meant to
          return values.  Reformats each of these to be regular
          variable declarations in the messsage sequence global
          section.  Remove the functiondeclarglist from the sequence
          node and add it to the sequence send node so that can still
          use it for type checking.
    
    '''
    
    # first star
    move_sequence_function_args(astNode)
    # second star
    move_sequence_function_return_types(astNode)


def move_sequence_function_return_types (ast_node):
    '''
    The last child of a sequence function contains a
    FunctionDeclArgList of nodes.  Each node names a separate, global
    variable that the message sequence returns.  Translate the 
    FunctionDeclArgList so that they appear as
    declared variables in the message sequence global section.
    '''
    msg_sequences_node = ast_node.children[6]
    for msg_seq_node in msg_sequences_node.children:
        # each msg_seq_node contains all code for a single message
        # sequence.

        # should be a function decl arg list
        msg_seq_return_node = msg_seq_node.children[-1]
        del msg_seq_node.children[-1]
        

        # note that using 1 here, while the actual parsing file has it
        # in the 2 index.  This is because in
        # move_sequence_function_args, we are actually deleting the
        # node that had been in index 1
        msg_seq_globs_node = msg_seq_node.children[1]
        #### DEBUG
        if msg_seq_globs_node.label != AST_MESSAGE_SEQUENCE_GLOBALS:
            err_msg = '\nBehram error in canonicalize.  Expecting '
            err_msg += 'a sequence global node.\n'
            print err_msg
            assert(False)
        #### END DEBUG

        msg_seq_funcs_node = msg_seq_node.children[2]
        #### DEBUG
        if msg_seq_funcs_node.label != AST_MESSAGE_SEQUENCE_FUNCTIONS:
            err_msg = '\nBehram error in canonicalize.  Expecting message '
            err_msg += 'sequence functions label.\n'
            print err_msg
            assert (False)
        #### END DEBUG

        msg_send_func_node = msg_seq_funcs_node.children[0]
        #### DEBUG
        if msg_send_func_node.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
            err_msg = '\nBehram error in canonicalize.  Expecting send message '
            err_msg += 'sequence function label.\n'
            print err_msg
            assert (False)
        #### END DEBUG

        msg_send_func_node.addChild(msg_seq_return_node)
        
        
        # translate each element that we are returning to append to
        # global section
        for func_decl_arg_node in msg_seq_return_node.children:
            type_node = func_decl_arg_node.children[0]
            identifier_node = func_decl_arg_node.children[1]

            # translate to decl node that can then be put into
            # children of msg_seq_globs_node
            decl_node = AstNode(
                AST_DECLARATION,type_node.lineNo,type_node.linePos)
            decl_node.addChildren([type_node,identifier_node])

            # add new decl_node at the end of declarations in
            # msg_seq_globs section.
            msg_seq_globs_node.addChild(decl_node)
            

    
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
    
