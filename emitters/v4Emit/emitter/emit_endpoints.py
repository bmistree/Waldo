import emit_utils 
import parser.ast.typeCheck as TypeCheck
from parser.ast.astLabels import *
import emitters.v4Emit.lib.util as lib_util
import emit_statement

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
    endpoint_body_text += '\n\n'

    # emit public and private functions
    endpoint_body_text += '### USER DEFINED METHODS ###\n'
    endpoint_body_text += emit_endpoint_publics_privates(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    
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
''' % (emit_utils.library_transform('Endpoint'), glob_var_store_name)
    
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


def emit_endpoint_publics_privates(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    Returns a string containing the definitions of all the public and
    private methods for endpoint named endpoint_name.
    '''
    endpoint_public_method_nodes = get_endpoint_public_method_nodes(
        endpoint_name,ast_root)
    endpoint_private_method_nodes = get_endpoint_private_method_nodes(
        endpoint_name,ast_root)

    method_defs = ''
    for public_method_node in endpoint_public_method_nodes:
        method_defs += emit_public_method_interface(
            public_method_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        method_defs += '\n'

        method_defs += emit_private_method_interface(
            public_method_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        method_defs += '\n'

    for private_method_node in endpoint_private_method_nodes:
        method_defs += emit_private_method_interface(
            private_method_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        method_defs += '\n'        
    
    return method_defs


def emit_private_method_interface(
    method_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode} method_node --- Either a public method node or a
    private method node.  If it's a public method, then we emit the
    internal method that gets called from the public interface of the
    method.  We emit private versions of public methods for two
    reasons:

       1: The public versions of the methods do some very basic
          bookkeeping (copy args in, check for backout and retry,
          etc.)

       2: When issuing an endpoint call, endpoint call gets issued to
          private part of function, which does most of the work.
    '''
    method_name_node = method_node.children[0]
    src_method_name = method_name_node.value
    internal_method_name = lib_util.endpoint_call_func_name(src_method_name)

    method_arg_names = get_method_arg_names(method_node)
    comma_sep_arg_names = reduce (
        lambda x, y : x + ',' + y,
        method_arg_names,'')
    
    private_header = '''
def %s(self,_active_event,_context%s):
''' % (internal_method_name, comma_sep_arg_names)

    # actually emit body of function
    private_body = ''
    method_body_node = get_method_body_node_from_method_node(method_node)
    emitted_something = False
    for statement_node in method_body_node.children:
        emitted_something = True
        private_body += emit_statement.emit_statement(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        private_body += '\n'
        
    if not emitted_something:
        # in case of empty functions
        private_body += 'pass\n'
    
    return private_header + emit_utils.indent_str(private_body)
        
    
def emit_public_method_interface(
    public_method_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode} public_method_node --- An AstNode with label
    AST_PUBLIC_FUNCTION
    '''
    method_name_node = public_method_node.children[0]
    method_name = method_name_node.value

    method_arg_names = get_method_arg_names(public_method_node)
    # turns the array of argnames above into a single string of csv
    # arg names
    comma_sep_arg_names = reduce (
        lambda x, y : x + ',' + y,
        method_arg_names,'')

    public_header = '''
def %s(self%s):
''' % (method_name, comma_sep_arg_names)


    public_body = ''
    #### Deep copy non-external args
    # non_ext_arg_names is an array of strings
    non_ext_arg_names = get_non_external_arg_names_from_func_node(
        public_method_node)
    for non_ext_arg_name in non_ext_arg_names:
        # translates to: non_extarg = <waldo import
        # path>public_arg_copy_in(non_extarg)
        public_body += '''
%s = %s(%s))
''' % (non_ext_arg_name,
       # FIXME: create a public_arg_copy_in ... essentially, for any 
       emit_utils.library_transform('public_arg_copy_in'),
       non_ext_arg_name)


    # Each element in this list is an index for a return parameter
    # that should be de-waldo-ified before returning.
    list_return_non_external_positions = (
        get_non_external_return_positions_from_func_node(public_method_node))

    #### create a root event + ctx for event, call internal, and reurn
    internal_method_name = lib_util.endpoint_call_func_name(method_name)
    public_body += '''
while True:  # FIXME: currently using infinite retry 
    _root_event = self._act_event_map.create_root_event()
    _ctx = %s(
        self._global_var_store,
        # not using sequence local store
        %s(self._host_uuid))

    # call internal function
    self.%s(_root_event,_ctx %s)
    # try committing root event
    _root_event.request_commit()
    _commit_resp = _root_event.event_complete_queue.get()
    if isinstance(_commit_resp,%s):
        # means it isn't a backout message: we're done
        break

# _list_non_external_returns contains the numeric indices of all
# items in _commit_resp.to_return tuple that should be returned as
# an external
_list_non_external_returns = %s
if isinstance(_commit_resp.to_return,tuple):
    _to_return = list(_commit_resp.to_return)
    for _i in _list_non_external_returns:
        _to_return[_i] = %s(_to_return[_i]) # de_waldoify_for_return
else:
    # we are returning a single value...check if even that single
    # value was not supposed to be an external
    _to_return = _commit_resp.to_return
    if len(_list_non_external_returns) == 0:
        _to_return = %s(_to_return)

return tuple(_to_return)
''' % (emit_utils.library_transform('ExecutingEventContext'),
       emit_utils.library_transform('VariableStore'),
       internal_method_name,
       comma_sep_arg_names,
       emit_utils.library_transform('CompleteRootCallResult'),
       str(list_return_non_external_positions),
       emit_utils.library_transform('de_waldoify_for_return'),
       emit_utils.library_transform('de_waldoify_for_return'))

    return public_header + emit_utils.indent_str(public_body)
    
    
def get_method_arg_names(method_node):
    '''
    @param {AstNode} method_node --- Either a public method node or a
    private method node
    
    @returns {Array} --- Each element is a string with the name of the
    method's argument.
    '''
    arg_names = []

    arg_node_index = get_arg_index_from_func_node_label(method_node.label)
    
    func_decl_arglist_node = method_node.children[arg_node_index]
    for func_decl_arg_node in func_decl_arglist_node.children:
        arg_name_node = func_decl_arg_node.children[1]
        arg_names.append(arg_name_node.value)
    
    return arg_names
    

def get_method_body_node_from_method_node(method_node):
    '''
    @param {AstNode} method_node --- for private, public, oncreate,
    message receive, and message send functions

    @returns{AstNode} --- The ast node containing the function's body.
    '''
    method_node_index = None;
    if method_node.label == AST_PUBLIC_FUNCTION:
        method_node_index = 3;
    elif method_node.label == AST_PRIVATE_FUNCTION:
        method_node_index = 3;
    elif method_node.label == AST_ONCREATE_FUNCTION:
        method_node_index = 2;
    elif method_node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        method_node_index = 3;
    elif method_node.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        method_node_index = 2;
    elif method_node.label == AST_ONCOMPLETE_FUNCTION:
        method_node_index = 2;
    else:
        errMsg = '\nBehram error: cannot get funcbodynode from ';
        errMsg += 'nodes that are not function nodes.\n';
        print(errMsg);
        assert(False);

    return method_node.children[method_node_index];


def get_endpoint_public_method_nodes(endpoint_name,ast_root):
    '''
    @returns{Array} --- Returns an array containing all the public
    method nodes defined for the endpoint with name endpoint_name
    '''
    return _get_endpoint_method_nodes(
        endpoint_name,ast_root,AST_PUBLIC_FUNCTION)

def get_endpoint_private_method_nodes(endpoint_name,ast_root):
    '''
    @see get_endpoint_public_method_nodes, except for private methods
    '''
    return _get_endpoint_method_nodes(
        endpoint_name,ast_root,AST_PRIVATE_FUNCTION)

def _get_endpoint_method_nodes(endpoint_name,ast_root,label_looking_for):
    '''
    Returns all methods that have label label_looking_for (which will
    either be AST_PUBLIC_FUNCTION or AST_PRIVATE_FUNCTION, depending
    on whether we want to return an array of public or private nodes.

    @see get_endpoint_public_method_nodes
    '''
    endpoint_node = get_endpoint_section_node(endpoint_name,ast_root)
    endpoint_body_node = endpoint_node.children[1]
    endpoint_method_sec_node = endpoint_body_node.children[1]

    methods_array = []
    for endpoint_method_node in endpoint_method_sec_node.children:
        if endpoint_method_node.label == label_looking_for:
            methods_array.append(endpoint_method_node)
            
    return methods_array
    

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

    #### DEBUG
    end2_name_node = end2_sec_node.children[0]
    end2_name = end2_name_node.value
    if end2_name != endpoint_name:
        emit_utils.emit_assert(
            'Cannot find endpoint named ' + endpoint_name)
    #### END DEBUG
    
    return end2_sec_node


def get_non_external_arg_names_from_func_node(func_node):
    '''
    @param {AstNode} func_node --- for private, public, oncreate,
    message receive, and message send functions.

    @returns {Array} --- Each element is a string representing the
    name of a non-external argument that the user passed in.
    '''
    arg_node_index = get_arg_index_from_func_node_label(func_node.label)

    returner = []
    func_decl_arg_list_node = func_node.children[arg_node_index]
    for func_decl_arg_node in func_decl_arg_list_node.children:
        if not func_decl_arg_node.external:
            name_node = func_decl_arg_node.children[1]
            returner.append(name_node.value)

    return returner


def get_non_external_return_positions_from_func_node(func_node):
    '''
    @returns {list} --- Each element is an integer corresponding to
    the index in the return tuple of a return value that isn't external.

    public function () returns Num, External Num, Num {}

    We would return [0,2].
    '''
    return_type_node_index = get_return_type_index_from_func_node_label(
        func_node.label)
    return_type_node = func_node.children[return_type_node_index]

    external_return_indices = []
    
    for return_counter in range(0,len(return_type_node.children)):
        return_node = return_type_node.children[return_counter]
        if not return_node.external:
            external_return_indices.append(return_counter)
    return external_return_indices


def get_return_type_index_from_func_node_label(label):
    return_node_index = None
    if label == AST_PUBLIC_FUNCTION:
        return_node_index = 1
    elif label == AST_PRIVATE_FUNCTION:
        return_node_index = 1
    #### DEBUG
    else:
        emit_utils.emit_assert(
            'Unknown label getting return typ for.')
    #### END DEBUG
        
    return return_node_index
    

def get_arg_index_from_func_node_label(label):
    arg_node_index = None
    if label == AST_PUBLIC_FUNCTION:
        arg_node_index = 2
    elif label == AST_PRIVATE_FUNCTION:
        arg_node_index = 2
    elif label == AST_ONCREATE_FUNCTION:
        arg_node_index = 1
    elif label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        arg_node_index = 2
    #### DEBUG
    else:
        emit_utils.emit_assert(
            'Unrecognized label passed to ' +
            'get_arg_index_from_func_node_label')
    #### END DEBUG
    return arg_node_index
