from parser.ast.astLabels import *
import parser.ast.typeCheck as TypeCheck

class EmitContext(object):
    def __init__(self):

        # These are relevant when we are emitting code for message
        # sequences.  Essentially, the semantics of jump statements is
        # that after we jump, we do not continue to execute code below
        # the jump (ie, we do not return to the point of call).  To
        # allow for these semantics, immediately after a jump, we must
        # return out of the emitted sequence function.  In the case
        # where we are in an emitted message send sequence function,
        # we don't just want to return, we also want to return the
        # relevant return parameters.  As a result, we pass around a
        # section of code corresponding to the return statement that
        # we should use immediately after a jump.
        self.in_message_send = False
        self.in_message_receive = False
        self.message_seq_return_txt = ''


def get_endpoint_names(ast_root):
    '''
    @return {2-tuple} --- Each element contains a string representing
    one of the endpoint names.
    '''
    alias_section = ast_root.children[1]
    end_name1 = alias_section.children[0].value
    end_name2 = alias_section.children[1].value
    return (end_name1,end_name2)
    

def library_transform(name):
    '''
    @param {String} name

    In this iteration of Waldo emitter, many of the libraries, etc.,
    that Waldo uses are in separate libraries.  To access these
    uniformly, prepending a module name.
    '''
    # FIXME: Actually need to ensure that libraries are structures
    # such that _waldo_libs exists and has correct __init__.py file.
    return '_waldo_libs.' + name


def emit_assert(err_msg):
    print '\n\nEmit error: ' + err_msg + '\n\n'
    assert(False)

def emit_warn(warn_msg):
    print '\n\nEmit warn: ' + warn_msg + '\n\n'
    
def indent_str(string,amt_to_indent=1):
    '''
    @param {String} string -- Each line in this string we will insert
    indentAmount number of tabs before and return the new, resulting
    string.
    
    @param {int} amt_to_indent

    @returns {String}
    '''
    split_on_newline = string.split('\n')
    indented_string = ''

    indenter = '';
    for s in range(0,amt_to_indent):
        indenter += '    ';

    for s in range(0,len(split_on_newline)):
        if len(split_on_newline[s]) != 0:
            indented_string += indenter + split_on_newline[s]
        if s != len(split_on_newline) -1:
            indented_string += '\n'

    return indented_string


def is_message_sequence_node(node):
    return ((node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION) or
            (node.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION))

def get_var_name_from_annotated_decl(annotated_decl_node):
    '''
    @param {AstNode object} annotated_decl_node
    
    @returns {String}
    '''
    #### DEBUG
    if annotated_decl_node.label != AST_ANNOTATED_DECLARATION:
        emit_assert(
            'Expected annotated declaration in ' +
            'get_var_name_from_annotated_decl.')
    #### END DEBUG

    name_node = annotated_decl_node.children[2]
    #### DEBUG    
    if name_node.sliceAnnotationName == None:
        emit_assert(
            'Variable has not been annotated by slicer')
    #### END DEBUG
        
    return name_node.sliceAnnotationName

def get_var_initializer_from_annotated_decl(annotated_decl_node):
    '''
    @param {AstNode object} annotated_decl_node
    
    @returns {AstNode or None} --- If the variable has an initializer,
    then returns the ast node used for initializing the declaration.
    '''
    if len(annotated_decl_node.children) != 4:
        return None
    return annotated_decl_node.children[3]


def get_var_type_dict_from_annotated_decl(annotated_decl_node):
    '''
    @param {AstNode object} annotated_decl_node
    
    @returns {Type Dict} --- Returns variable's type dict.
    '''
    #### DEBUG
    if annotated_decl_node.label != AST_ANNOTATED_DECLARATION:
        emit_assert(
            'Expected annotated declaration in ' +
            'get_var_type_dict_from_annotated_decl.')
    #### END DEBUG
        
    type_node = annotated_decl_node.children[1]
    return type_node.type
    

def get_var_initializer_from_decl(decl_node):
    '''
    @param {AstNode object} decl_node
    
    @returns {AstNode or None} --- If the variable has an initializer,
    then returns the ast node used for initializing the declaration.
    '''
    if len(decl_node.children) != 3:
        return None
    return decl_node.children[2]


def get_var_name_from_decl(decl_node):
    '''
    @param {AstNode object} decl_node
    
    @returns {String}
    '''
    #### DEBUG
    if decl_node.label != AST_DECLARATION:
        emit_assert(
            'Expected declaration in ' +
            'get_var_name_from_decl.')
    #### END DEBUG

    name_node = decl_node.children[1]
    #### DEBUG    
    if name_node.sliceAnnotationName == None:
        emit_assert(
            'Variable has not been annotated by slicer')
    #### END DEBUG
        
    return name_node.sliceAnnotationName

def get_var_type_dict_from_decl(decl_node):
    '''
    @param {AstNode object} decl_node
    
    @returns {Type Dict} --- Returns variable's type dict.
    '''
    #### DEBUG
    if decl_node.label != AST_DECLARATION:
        emit_assert(
            'Expected annotated declaration in ' +
            'get_var_type_dict_from_decl.')
    #### END DEBUG
        
    type_node = decl_node.children[0]
    return type_node.type


def get_method_call_arg_list_node(method_call_node):
    return method_call_node.children[1]

def is_endpoint_method_call(node):
    if is_method_call(node):
        name_node = node.children[0]
        # FIXME: currently, the only way to test if it's a function call
        # on an endpoint object is if the func name is a dot statement
        if name_node.label == AST_DOT_STATEMENT:
            return True
        
    return False


def get_var_type_txt_from_type_dict(var_type_dict,var_id_node):
    '''
    @param {dict} var_type_dict --- Gotten from an AstNode's .type
    field.

    @param {AstNode} var_id_node --- The identifier node associated
    with var_type_dict.  Essentially, just want to be able to check
    whether node is external to determine what type of variable to
    create from it.
    '''
    # FIXME: still need to add entries for function, endpoint, and
    # user struct types.
    if TypeCheck.templateUtil.is_number(var_type_dict):
        if var_id_node.external != None:
            variable_type_str = library_transform('WaldoExtNumVariable')
        else:
            variable_type_str = library_transform('WaldoNumVariable')
    elif TypeCheck.templateUtil.is_true_false(var_type_dict):
        if var_id_node.external != None:
            variable_type_str = library_transform('WaldoExtTrueFalseVariable')
        else:
            variable_type_str = library_transform('WaldoTrueFalseVariable')
    elif TypeCheck.templateUtil.is_text(var_type_dict):
        if var_id_node.external != None:
            variable_type_str = library_transform('WaldoExtTextVariable')
        else:
            variable_type_str = library_transform('WaldoTextVariable')
    elif TypeCheck.templateUtil.isListType(var_type_dict):        
        variable_type_str = library_transform('WaldoListVariable')
    elif TypeCheck.templateUtil.isMapType(var_type_dict):
        variable_type_str = library_transform('WaldoMapVariable')
    #### DEBUG
    else:
        emit_assert(
            'Unknown type in create_wvariables_array')
    #### END DEBUG

    return variable_type_str
        

def is_method_call(node):
    return node.label == AST_FUNCTION_CALL


def is_reference_type(node):
    # FIXME: should also add reference types for user structs as well
    # as functions

    # FIXME: need to unwrap the possibility of the nodes' being
    # function call returns.
    return ((TypeCheck.templateUtil.isListType(node.type)) or 
            (TypeCheck.templateUtil.isMapType(node.type)))

def is_msg_seq_begin_call(node,endpoint_name,fdep_dict):
    '''
    @returns{Bool} --- True if this function is a message send, false
    otherwise
    '''
    if not is_method_call(node):
        return False

    name_node = node.children[0]
    if name_node.label != AST_IDENTIFIER:
        return False

    method_name = name_node.value

    fdep = find_function_dep_from_fdep_dict(method_name,endpoint_name,fdep_dict)
    if fdep == None:
        emit_assert(
            'Unable to find function in fdep_dict when checking ' +
            'if it is a message send.')

    # check if the node is labeled as a message sequence node.
    return fdep.funcNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION;


def find_function_dep_from_fdep_dict(func_name,endpoint_name,fdep_dict):
    '''
    @param {String} func_name --- The name of the function as declared
    in the source.

    @param {String} endpoint_name --- The name of the endpoint that
    the function is associated with.
    
    @returns {FunctionDep object or None} --- Returns None if cannot find.
    '''
    for fdep_key in fdep_dict.keys():
        fdep = fdep_dict[fdep_key]

        if ((fdep.endpointName == endpoint_name) and
            (fdep.srcFuncName == func_name)):
            return fdep

    return None
