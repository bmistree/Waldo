#!/usr/bin/env python

from astNode import *
from astLabels import *
import astBuilder
import pickle

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

        * A user calls a sequence's name to begin the sequence.
          However, the emitter, slicer, and type checker expect that
          the user is actually calling the name of the first sequence
          block of each method.

          This method changes the mapping between the two.  It
          re-names the first sequence block with the sequence name.

        * To handle symmetric nodes:
        
             1) Check if the alias section is symmetric.  If it is
                then check that only have one endpoint in
                EndpointDefinitionSection.

             2) Make a deep copy of the endpoint definition section
                and replace its identifier with the identifier of the
                symmetric node.

             3) Re-write root, splitting endpoint_section node into
                two nodes, one for each section.

             4) Update message sequences to make symmetric copies for
                other value.

             5) Update peered data annotated with who controls it
                (FIXME: have not implemented this part).

    
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

    # first star above
    rename_sequences(astNode)
    # second star    
    handle_symmetric(astNode)
    # third star    
    move_sequence_function_args(astNode)
    # fourth star    
    move_sequence_function_return_types(astNode)

    
    
def rename_sequences(ast_root_node):
    '''
    A user calls a sequence's name to begin the sequence.  However,
    the emitter, slicer, and type checker expect that the user is
    actually calling the name of the first sequence block of each
    method.

    This method changes the mapping between the two.  It re-names the
    first sequence block with the sequence name.
    '''

    # First, iterate through sequences section, which declares all
    # sequences
    msg_sequence_dec_node = ast_root_node.children[2]
    
    # lefthand side is the original function, and the right hand side
    # is the name of the sequence
    for sequence_line in msg_sequence_dec_node.children:
        # get the name of the sequence line
        seq_name_node = sequence_line.children[0]
        seq_name = seq_name_node.value
        
        # get all the declared sequence blocks
        seq_send_node = sequence_line.children[1]
        send_name_node = seq_send_node.children[1]
        
        # exchange the sequence name with the send name
        send_name_node.value = seq_name

        
    # Second, iterate through actual sequence block definitions
    msg_sequences_node = ast_root_node.children[5]
    # debug
    if msg_sequences_node.label != AST_MESSAGE_SEQUENCE_SECTION:
        err_msg = '\nIncorrect label on message sequences node.\n'
        print msg_sequences_node.label
        import pdb
        pdb.set_trace()
        print err_msg
        assert (False)
    # end debug

    for sequence_node in msg_sequences_node.children:
        sequence_name_node = sequence_node.children[0]
        sequence_block_nodes = sequence_node.children[3]
        sequence_send_block_node = sequence_block_nodes.children[0]
        sequence_send_name_node = sequence_send_block_node.children[1]

        # exchange sequence name with sequence send
        sequence_send_name_node.value = sequence_name_node.value
        
    

def handle_symmetric(ast_node):
    alias_section_node = ast_node.children[1]
    endpoint_section_node = ast_node.children[4]

    if alias_section_node.label != AST_SYMMETRIC_ALIAS_SECTION:
        if len(endpoint_section_node.children) > 2:
            err_msg = 'For non-symmetric declaration, require '
            err_msg += 'one or two endpoint definitions.'
            endpoint_section_node.value = 'Endpoint'
            raise astBuilder.WaldoParseException(
                endpoint_section_node,err_msg)

        if len(endpoint_section_node.children) == 1:

            if len(alias_section_node.children) != 1:
                err_msg = 'Requested separate endpoints at top of file,'
                err_msg += 'but only defined one at bottom.  Maybe use '
                err_msg += 'Symmetric instead?'
                endpoint_section_node.value = 'Endpoint'
                raise astBuilder.WaldoParseException(
                    endpoint_section_node,err_msg)
                
            
            # means that we must invent another endpoint: give it a
            # name that we know will not conflict with any other
            # Endpoint name.  Can do so by appending an '_' to the
            # beginning of the first endpoint's name
            endpoint_1_definition_node = endpoint_section_node.children[0]
            endpoint_1_name_node = endpoint_1_definition_node.children[0]
            name_defined = endpoint_1_name_node.value
            
            dummy_endpoint_name = '_' + name_defined

            endpoint_identifier_node = AstNode(
                AST_IDENTIFIER,endpoint_1_definition_node.lineNo,
                endpoint_1_definition_node.linePos,dummy_endpoint_name)
            
            bodySecChild = AstNode(
                AST_ENDPOINT_BODY_SECTION,endpoint_1_definition_node.lineNo,
                endpoint_1_definition_node.linePos)
            
            bodyGlobSec = AstNode(
                AST_ENDPOINT_GLOBAL_SECTION,endpoint_1_definition_node.lineNo,
                endpoint_1_definition_node.linePos)
            
            funcGlobSec = AstNode(
                AST_ENDPOINT_FUNCTION_SECTION,endpoint_1_definition_node.lineNo,
                endpoint_1_definition_node.linePos)
            
            bodySecChild.addChildren([bodyGlobSec,funcGlobSec])

            endpoint_2_definition_node = AstNode(
                AST_ENDPOINT,endpoint_1_definition_node.lineNo,
                endpoint_1_definition_node.linePos)

            endpoint_2_definition_node.addChildren([endpoint_identifier_node,bodySecChild])

            alias_section_node.addChild(endpoint_identifier_node)
            
        else:
            if len(alias_section_node.children) != 2:
                err_msg = 'Defined two endpoints in file, but only declared '
                err_msg += 'one at top.'
                endpoint_section_node.value = 'Endpoint'
                raise astBuilder.WaldoParseException(
                    endpoint_section_node,err_msg)

            
            # we were given two endpoints
            endpoint_1_definition_node = endpoint_section_node.children[0]
            endpoint_2_definition_node = endpoint_section_node.children[1]

    else:
        alias_section_node.label = AST_ENDPOINT_ALIAS_SECTION

        name_node_1 = alias_section_node.children[0]
        name_1 = name_node_1.value
        name_node_2 = alias_section_node.children[1]
        name_2 = name_node_2.value
        
        num_endpoint_definitions = len(endpoint_section_node.children)
        if  num_endpoint_definitions != 1:
            err_msg = 'For symmetric declaration, expecting one '
            err_msg += 'endpoint definition.  Received '
            err_msg += str(num_endpoint_definitions) + '.'
            endpoint_section_node.value = name_1 + '|' + name_2
            raise astBuilder.WaldoParseException(
                endpoint_section_node,err_msg)

        defined_endpoint_node = endpoint_section_node.children[0]
        defined_endpoint_name_node = defined_endpoint_node.children[0]
        name_defined = defined_endpoint_name_node.value

        copy_defined_endpoint_node = pickle.loads(
            pickle.dumps(defined_endpoint_node))
        copy_endpoint_name_node = copy_defined_endpoint_node.children[0]

        # change name of copy
        name_copied = name_1
        if name_defined == name_1:
            name_copied = name_2
        copy_endpoint_name_node.value = name_copied

        endpoint_1_definition_node = defined_endpoint_node
        endpoint_2_definition_node = copy_defined_endpoint_node
        

        # for every message sequence in sequences section, produce an
        # alternate sequence, flipping order of
        trace_section_node = ast_node.children[2]
        symmetric_traces = []
        for trace_node in trace_section_node.children:
            # deep copy trace item so that modifications on copies
            # will not affect new items
            copied_trace_node = pickle.loads(pickle.dumps(trace_node))
            symmetric_traces.append(copied_trace_node)

            # change name of trace node
            copied_trace_name_node = copied_trace_node.children[0]
            pre_copied_trace_name = copied_trace_name_node.value
            copied_trace_name = change_msg_seq_name_for_symmetric(
                name_copied,pre_copied_trace_name)
            copied_trace_name_node.value = copied_trace_name
            
            
            # overwrite each of the sequence blocks' first node names,
            # reversing Endpoint names
            for trace_item_node in copied_trace_node.children[1:]:
                endpoint_name_node = trace_item_node.children[0]
                original_endpoint_name = endpoint_name_node.value
                
                new_endpoint_name = name_copied
                if original_endpoint_name == name_copied:
                    new_endpoint_name = name_defined
                endpoint_name_node.value = new_endpoint_name
                
        trace_section_node.addChildren(symmetric_traces)

                
        # for every message sequence, create a new one with the
        # symmetric name + send endpoint messages in different orders
        msg_seq_section_node = ast_node.children[5]
        copied_sequence_nodes = pickle.loads(pickle.dumps(msg_seq_section_node.children))

        for copied_sequence_node in copied_sequence_nodes:
            # copy over the name of the overall sequence
            copied_sequence_name_node = copied_sequence_node.children[0]
            copied_sequence_original_name = copied_sequence_name_node.value

            copied_sequence_name_node.value = change_msg_seq_name_for_symmetric(
                name_copied,copied_sequence_original_name)

            # change endpoint names in each of the sequence steps
            msg_seq_functions_node = copied_sequence_node.children[3]
            for msg_seq_function_node in msg_seq_functions_node.children:
                msg_seq_function_endpoint_name_node = msg_seq_function_node.children[0]

                new_endpoint_name = name_copied
                if msg_seq_function_endpoint_name_node.value == name_copied:
                    new_endpoint_name = name_defined

                msg_seq_function_endpoint_name_node.value = new_endpoint_name

        msg_seq_section_node.addChildren(copied_sequence_nodes)
                
                
        # FIXME: make copies of peered data that only one side controls

    # insert the new endpoint nodes into ast_node...note, displace
    # old endpoint section.
    ast_node.children[4] = endpoint_1_definition_node
    ast_node.children.insert(5,endpoint_2_definition_node )


def change_msg_seq_name_for_symmetric(new_endpoint_name,msg_seq_name):
    '''
    When have a symmetric file, need to create a duplicate message
    sequence for each existing message sequence.  
    '''
    # FIXME: does not actually guarantee that there will be no
    # collision with an existing message sequence.
    return new_endpoint_name + '____' + msg_seq_name
    
            

        
    
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

        msg_send_func_node.children.insert(2,func_args_node)

       
