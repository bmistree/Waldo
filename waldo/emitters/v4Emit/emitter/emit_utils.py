from waldo.parser.ast.astLabels import *
import waldo.parser.ast.typeCheck as TypeCheck

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
    return 'self._waldo_classes["' + name + '"]'


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
        caller_node = node.children[0]
        if TypeCheck.templateUtil.is_endpoint_function_type(caller_node.type):
            return True
        
    return False


def get_var_type_txt_from_type_dict(var_type_dict,multithreaded=True):
    '''
    @param {dict} var_type_dict --- Gotten from an AstNode's .type
    field.

    @param {bool} multithreaded --- True if the variable we are
    creating may be accessed by multiple threads.  False otherwise.
    
    @returns {2-tuple} (a,b)

        a{String} --- The translated name of the constructor for the
        variable.

        b{bool} --- True if constructing a function object variable.
        False otherwise. 
    '''
    is_func = False
    

    if multithreaded:
        if TypeCheck.templateUtil.is_number(var_type_dict):
            if TypeCheck.templateUtil.is_external(var_type_dict):
                variable_type_str = library_transform('WaldoExtNumVariable')
            else:
                variable_type_str = library_transform('WaldoNumVariable')
        elif TypeCheck.templateUtil.is_true_false(var_type_dict):
            if TypeCheck.templateUtil.is_external(var_type_dict):
                variable_type_str = library_transform('WaldoExtTrueFalseVariable')
            else:
                variable_type_str = library_transform('WaldoTrueFalseVariable')
        elif TypeCheck.templateUtil.is_text(var_type_dict):
            if TypeCheck.templateUtil.is_external(var_type_dict):
                variable_type_str = library_transform('WaldoExtTextVariable')
            else:
                variable_type_str = library_transform('WaldoTextVariable')

        elif TypeCheck.templateUtil.is_basic_function_type(var_type_dict):
            is_func = True

            if TypeCheck.templateUtil.is_external(var_type_dict):
                emit_assert(
                    'Have not yet begun emitting for external function objects')
            else:
                variable_type_str = library_transform('WaldoFunctionVariable')

        elif TypeCheck.templateUtil.isListType(var_type_dict):
            variable_type_str = library_transform('WaldoListVariable')
        elif TypeCheck.templateUtil.isMapType(var_type_dict):
            variable_type_str = library_transform('WaldoMapVariable')
        elif TypeCheck.templateUtil.is_endpoint(var_type_dict):
            variable_type_str = library_transform('WaldoEndpointVariable')

        #### DEBUG
        else:
            emit_assert(
                'Unknown type in create_wvariables_array')
        #### END DEBUG
    else:
        # single multithreaded

        # FIXME: still using multithreaded ext num, ext text, ext tf, func
        
        if TypeCheck.templateUtil.is_number(var_type_dict):
            if TypeCheck.templateUtil.is_external(var_type_dict):

                variable_type_str = library_transform('WaldoExtNumVariable')
            else:
                variable_type_str = library_transform('WaldoSingleThreadNumVariable')
        elif TypeCheck.templateUtil.is_true_false(var_type_dict):
            if TypeCheck.templateUtil.is_external(var_type_dict):
                variable_type_str = library_transform('WaldoExtTrueFalseVariable')
            else:
                variable_type_str = library_transform('WaldoSingleThreadTrueFalseVariable')
        elif TypeCheck.templateUtil.is_text(var_type_dict):
            if TypeCheck.templateUtil.is_external(var_type_dict):
                variable_type_str = library_transform('WaldoExtTextVariable')
            else:
                variable_type_str = library_transform('WaldoSingleThreadTextVariable')

        elif TypeCheck.templateUtil.is_basic_function_type(var_type_dict):
            is_func = True

            if TypeCheck.templateUtil.is_external(var_type_dict):
                emit_assert(
                    'Have not yet begun emitting for external function objects')
            else:
                variable_type_str = library_transform('WaldoFunctionVariable')

        elif TypeCheck.templateUtil.isListType(var_type_dict):
            variable_type_str = library_transform('WaldoSingleThreadListVariable')
        elif TypeCheck.templateUtil.isMapType(var_type_dict):
            variable_type_str = library_transform('WaldoSingleThreadMapVariable')
        elif TypeCheck.templateUtil.is_endpoint(var_type_dict):
            variable_type_str = library_transform('WaldoSingleThreadEndpointVariable')

        #### DEBUG
        else:
            emit_assert(
                'Unknown type in create_wvariables_array')
        #### END DEBUG
            
    return variable_type_str,is_func
        
def is_method_call(node):
    return node.label == AST_FUNCTION_CALL

def is_reference_type_type_dict(type_dict):
    return ((TypeCheck.templateUtil.isListType(type_dict)) or 
            (TypeCheck.templateUtil.isMapType(type_dict)) or
            (TypeCheck.templateUtil.is_struct(type_dict)))


def emit_value_type_default(type_dict):
    '''
    @param {type dict} type_dict --- Must be a value type (not even an
    external value type)

    @returns {String} --- That can be used to initialize the value type.
    Number: '0', Text: '""', TrueFalse: 'False'
    '''

    #### DEBUG
    if (TypeCheck.templateUtil.is_external(type_dict) or
        is_reference_type_type_dict(type_dict)):
        emit_assert(
            'Incorrect type passed into default value type')
    #### END DEBUG
    if TypeCheck.templateUtil.is_number(type_dict):
        return '0'
    elif TypeCheck.templateUtil.is_true_false(type_dict):
        return 'False'
    elif TypeCheck.templateUtil.is_text(type_dict):
        return '""'


    #### DEBUG
    emit_assert('Unknown type requested default of ' + str(type_dict))
    #### END DEBUG
    

    
def is_reference_type(node):
    # FIXME: need to unwrap the possibility of the nodes' being
    # function call returns.
    return is_reference_type_type_dict(node.type)
    
def is_func_obj_call(
    method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    It's a function object call through process of elimination
    '''
    
    if is_endpoint_method_call(method_call_node):
        return False
    
    if is_msg_seq_begin_call(method_call_node,endpoint_name,fdep_dict):
        return False

    lhs_node = method_call_node.children[0]
    if lhs_node.label == AST_IDENTIFIER:
        func_name = lhs_node.value
        fdep = find_function_dep_from_fdep_dict(func_name,endpoint_name,fdep_dict)
        if fdep != None:
            # the name of the function being called is either a
            # message sequence function or a public/private method
            # name.  Means that the call isn't on a function object,
            # but rather on a method.  
            return False

    if is_method_call(method_call_node):
        # can't be anything else
        return True
    
    return False


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
        # could not find any method names on this endpoint matching
        # method name.  This could happen if we're executing a call on
        # a function object.
        return False

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
