import emit_utils 
import parser.ast.typeCheck as TypeCheck
from parser.ast.astLabels import *

def emit_endpoints(ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode object} ast_root --- The root of the ast.

    @param {dict} fdep_dict --- Keys are strings (names of functions),
    values are FunctionDeps objects.  (@see slice.functionDeps)

    @param {EmitContext object} emit_ctx --- Ancillary state
    information (eg., are we in a message sequence?) to help with
    emitting.

    @returns{String} --- What should be emitted to Waldo file.
    '''
    emitted_endpoints_text = ''

    endpoint_names = emit_utils.get_endpoint_names(ast_root)
    
    emitted_endpoints_text += emit_single_endpoint(
        endpoint_names[0],ast_root,fdep_dict,emit_ctx)
    
    emitted_endpoints_text += emit_single_endpoint(
        endpoint_names[1],ast_root,fdep_dict,emit_ctx)

    return emitted_endpoints_text
    

def emit_single_endpoint(endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {String} endpoint_name --- The name of the endpoint we are
    currently emitting.

    For all other params + return, @see emit_endpoints
    '''
    endpoint_header = 'class %s (%s):\n' % (
        endpoint_name,emit_utils.library_transform('_Endpoint'))

    endpoint_body = emit_endpoint_body(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    return endpoint_header + emit_utils.indent_str(endpoint_body)
    

def emit_endpoint_body(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    For params and return, @see emit_single_endpoint
    '''

    # emit __init__
    endpoint_body_text = emit_endpoint_init(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    endpoint_body_text += '\n'

    # emit public and private functions
    endpoint_body_text += '### USER DEFINED FUNCTIONS ###\n'

    # FIXME: fill this section in
    
    # emit sequence blocks
    endpoint_body_text += '### USER DEFINED SEQUENCE BLOCKS ###\n'
    
    # FIXME: fill this section in
    
    return endpoint_body_text
    

def emit_endpoint_init(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    For params and return, @see emit_single_endpoint
    '''

    # FIXME: for now, not taking in any onCreate arguments and not
    # calling onCreate.

    init_header = 'def __init__(self,_host_uuid,_conn_obj):\n'

    # create endpoint and peered variable store
    init_body,glob_var_store_name = emit_endpoint_global_and_peered_variable_store(
        endpoint_name,'_host_uuid',ast_root,fdep_dict,emit_ctx)

    # actually initialize super class
    init_body += '''
%s.__init__(self,_host_uuid,conn_obj,%s)
''' % (emit_utils.library_transform('_Endpoint'), glob_var_store_name)
    
    # FIXME: this is where would actually make call to onCreate
    
    return init_header + emit_utils.indent_str(init_body)


def emit_endpoint_global_and_peered_variable_store(
    endpoint_name,host_uuid_var_name,ast_root,fdep_dict,emit_ctx):
    '''
    For params, @see emit_single_endpoint

    Returns a string that initializes the global variable store with
    data for an endpoint + a string for the name of the glob var store
    temporary variable.
    '''

    glob_var_store_tmp_name = '_glob_var_store'
    
    endpoint_global_decl_nodes = get_endpoint_global_decl_nodes(
        endpoint_name,ast_root)
    peered_decl_nodes = get_peered_decl_nodes(ast_root)

    var_store_loading_text = create_wvariables_array(
        glob_var_store_tmp_name,host_uuid_var_name,
        endpoint_global_decl_nodes,False)
    var_store_loading_text += create_wvariables_array(
        glob_var_store_tmp_name,host_uuid_var_name,
        peered_decl_nodes,True)

    return var_store_loading_text, glob_var_store_tmp_name


def create_wvariables_array(
    var_store_name,host_uuid_var_name,decl_node_array,peered):
    '''
    @param {String} var_store_name --- The name of the variable that
    contains the variable store that we are writing to.  (Eg.,
    _glob_var_store if in __init__ of subclassed endpoint, or
    self._global_var_store if in method of subclassed endpoint.)

    @param {String} host_uuid_var_name --- The name of the variable
    that contains the host uuid.

    @param {Array} decl_node_array --- Each element of the array is an
    AST_DECLARATION node or an AST_ANNOTATED_DECLARATION node.

    @param {bool} peered --- True if new variable is supposed to be
    peered, False otherwise.
    '''

    # FIXME: for now, skipping initializers.
    wvar_load_text = ''

    peered_str = 'True' if peered else 'False'
    
    for decl_node in decl_node_array:

        # check if annotated declaration or just declaration

        if decl_node.label == AST_ANNOTATED_DECLARATION:
            var_name = emit_utils.get_var_name_from_annotated_decl(decl_node)
            var_type = emit_utils.get_var_type_dict_from_annotated_decl(decl_node)
        elif decl_node.label == AST_DECLARATION:
            var_name = emit_utils.get_var_name_from_decl(decl_node)
            var_type = emit_utils.get_var_type_dict_from_decl(decl_node)            
        #### DEBUG
        else:
            emit_utils.emit_assert(
                'In create_wvariables_array, trying to create a ' +
                'var that is not a declaration.')
        #### END DEBUG

        # FIXME: still need to add entries for function, endpoint, and
        # user struct types.
            
        if TypeCheck.templateUtil.is_number(var_type):
            variable_type_str = emit_utils.library_transform('WaldoNumVariable')
        elif TypeCheck.templateUtil.is_true_false(var_type):
            variable_type_str = emit_utils.library_transform('WaldoTrueFalseVariable')
        elif TypeCheck.templateUtil.is_text(var_type):
            variable_type_str = emit_utils.library_transform('WaldoTextVariable')
        elif TypeCheck.templateUtil.is_text(var_type):
            variable_type_str = emit_utils.library_transform('WaldoTextVariable')
        elif TypeCheck.templateUtil.isListType(var_type):
            variable_type_str = emit_utils.library_transform('WaldoListVariable')
        elif TypeCheck.templateUtil.isMapType(var_type):
            variable_type_str = emit_utils.library_transform('WaldoMapVariable')
        #### DEBUG
        else:
            emit_utils.emit_assert(
                'Unknown type in create_wvariables_array')
        #### END DEBUG
            
        wvar_load_text += '''
%s.add_var(
    '%s',
    %s(  # the type of waldo variable to create
        '%s', # variable's name
        %s, # host uuid var name
        %s  # if peered, True, otherwise, False
        # FIXME: no initializer
    ))
''' % (var_store_name, var_name,variable_type_str,
       var_name,host_uuid_var_name,peered_str)
        

    return wvar_load_text


def get_peered_decl_nodes(ast_root):
    '''
    @param {AstNode} ast_root

    @returns {Array} --- Returns an array of
    AST_ANNOTATED_DECLARATION_NODES for each peered node.
    data.
    '''
    peered_section_node = ast_root.children[3]
    annotated_decl_node_array = []
    for annotated_decl_node in peered_section_node.children:
        annotated_decl_node_array.append(annotated_decl_node)
        
    return annotated_decl_node_array
    

def get_endpoint_global_decl_nodes(endpoint_name,ast_root):
    '''
    @param {String} endpoint_name
    @param {AstNode} ast_root
    
    @returns {Array} --- Returns an array of AST_DECLARATION_NODES for
    each endpoint-global piece of data.
    '''

    endpoint_sec_node = get_endpoint_section_node(endpoint_name,ast_root)
    endpoint_body_sec_node = endpoint_sec_node.children[1]
    endpoint_global_sec_node = endpoint_body_sec_node.children[0]

    decl_node_array = []
    for decl_node in endpoint_global_sec_node.children:
        decl_node_array.append(decl_node)
    return decl_node_array
    
    
def get_endpoint_section_node(endpoint_name,ast_root):
    end1_sec_node = ast_root.children[4]
    end2_sec_node = ast_root.children[5]

    end1_name_node = end1_sec_node.children[0]
    end1_name = end1_name_node.value

    if end1_name == endpoint_name:
        return end1_sec_node

    return end2_sec_node
