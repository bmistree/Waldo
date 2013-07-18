import emit_utils 
import waldo.parser.ast.typeCheck as TypeCheck
from waldo.parser.ast.astLabels import *
import waldo.lib.util as lib_util
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

    Will produce something like the following:
    
def SingleSide(_waldo_classes,_host_uuid,_conn_obj):

    class _SingleSide (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj):

        ...

    return _SingleSide(_waldo_classes,_host_uuid,_conn_obj)


    The reason that we wrap the class in a function instead of just
    directly providing the class is so that we do not have to
    statically link the generated file to any library.  Can take in an
    argument that dynamically tells us how to make the Endpoint
    inherit from the hidden Waldo _Endpoint.
    '''
    endpoint_factory_func = (
        'def %s (_waldo_classes,_host_uuid,_conn_obj,*args):\n' %
        endpoint_name)
    
    endpoint_header = 'class _%s (_waldo_classes["Endpoint"]):\n' % (
        endpoint_name)

    endpoint_body = emit_endpoint_body(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    endpoint_class = endpoint_header + emit_utils.indent_str(endpoint_body)

    
    endpoint_factory_func += emit_utils.indent_str(endpoint_class)
    endpoint_factory_func += emit_utils.indent_str(
        'return _%s(_waldo_classes,_host_uuid,_conn_obj,*args)\n' % endpoint_name)
        
    return endpoint_factory_func
    

def emit_endpoint_body(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    For params and return, @see emit_single_endpoint
    '''

    # emit __init__
    endpoint_body_text = emit_endpoint_init(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    endpoint_body_text += '\n\n'

    # emit oncreate method
    endpoint_body_text += '### OnCreate method\n'
    endpoint_body_text += emit_endpoint_oncreate_method_def(
        endpoint_name,ast_root,fdep_dict,emit_ctx)

    
    # emit public and private method
    endpoint_body_text += '### USER DEFINED METHODS ###\n'
    endpoint_body_text += emit_endpoint_publics_privates(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    # emit sequence blocks
    endpoint_body_text += '### USER DEFINED SEQUENCE BLOCKS ###\n'
    endpoint_body_text += emit_endpoint_message_sequence_blocks(
        endpoint_name,ast_root,fdep_dict,emit_ctx)

    return endpoint_body_text
    

def emit_endpoint_init(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    For params and return, @see emit_single_endpoint
    '''
    oncreate_argument_string = ''
    oncreate_node = get_oncreate_node(endpoint_name,ast_root)
    if oncreate_node != None:
        oncreate_arg_names = get_method_arg_names(oncreate_node)
        oncreate_argument_string = reduce (
            lambda x, y : x + ',' + y,
            oncreate_arg_names,'')

    init_header = (
        'def __init__(self,_waldo_classes,_host_uuid,_conn_obj%s):\n' % oncreate_argument_string)

    # create endpoint and peered variable store
    
    # should initialize variable store before entering into _Endpoint
    # super class initializer: super class initializer registers the
    # _Endpoint with connection object.  
    endpoint_global_and_peered_variable_store_load_txt = (
        emit_endpoint_global_and_peered_variable_store(
            endpoint_name,'_host_uuid',ast_root,fdep_dict,emit_ctx))

    # actually initialize super class
    init_body = '''
# a little ugly in that need to pre-initialize _host_uuid, because
# code used for initializing variable store may rely on it.  (Eg., if
# initializing nested lists.)
self._waldo_classes = _waldo_classes
self._host_uuid = _host_uuid
self._global_var_store = %s(_host_uuid)
%s
%s.__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)

''' % (emit_utils.library_transform('VariableStore'),
       endpoint_global_and_peered_variable_store_load_txt,
       emit_utils.library_transform('Endpoint'))


    # emit call to oncreate method
    init_body += emit_oncreate_call(endpoint_name,ast_root)

    return init_header + emit_utils.indent_str(init_body)


def emit_oncreate_call(endpoint_name,ast_root):
    '''
    Inside of each endpoint's initializer, we may need to emit a call
    to an onCreate initializer method.  Below emits the text that
    actually calls the initializer method.
    
    @returns {String}
    '''
    oncreate_node = get_oncreate_node(endpoint_name,ast_root)
    
    if oncreate_node != None:
        oncreate_arglist = get_method_arg_names(oncreate_node)
        comma_sep_arg_names = reduce (
            lambda x, y : x + ',' + y,
            oncreate_arglist,'')

        # run the initializer
        oncreate_call_txt = '''
while True:  # FIXME: currently using infinite retry 
    _root_event = self._act_event_map.create_root_event()
    _ctx = %s(
        self._global_var_store,
        # not using sequence local store
        %s(self._host_uuid))

    # call internal function... note True as last param tells internal
    # version of function that it needs to de-waldo-ify all return
    # arguments (while inside transaction) so that this method may
    # return them....if it were false, might just get back refrences
    # to Waldo variables, and de-waldo-ifying them outside of the
    # transaction might return over-written/inconsistent values.
    try:
        _to_return = self.%s(_root_event,_ctx %s,[])
    except %s:
        pass

    # try committing root event
    _root_event.request_commit()
    _commit_resp = _root_event.event_complete_queue.get()
    if isinstance(_commit_resp,%s):
        # means it isn't a backout message: we're done

        # local endpoint's initialization has succeeded, tell other side that
        # we're done initializing.
        self._this_side_ready()

        return _to_return

    ''' % (emit_utils.library_transform('ExecutingEventContext'),
           emit_utils.library_transform('VariableStore'),
           lib_util.internal_oncreate_func_call_name('onCreate'),
           comma_sep_arg_names,
           emit_utils.library_transform('BackoutException'),
           emit_utils.library_transform('CompleteRootCallResult'))

    else:
        oncreate_call_txt = '\n'

    # local endpoint's initialization has succeeded, tell other side
    # that we're done initializing.  note: we don't hit this section
    # of code if we actually had an oncreate node, so it's okay that
    # we list self._this_side_ready() twice: only one of them will
    # ever be called.
    oncreate_call_txt += '''
# local endpoint's initialization has succeeded, tell other side that
# we're done initializing.
self._this_side_ready()
'''
    return oncreate_call_txt


def emit_endpoint_global_and_peered_variable_store(
    endpoint_name,host_uuid_var_name,ast_root,fdep_dict,emit_ctx):
    '''
    For params, @see emit_single_endpoint

    Returns a string that initializes the global variable store
    contained in self._global_var_store.
    '''
    
    endpoint_global_decl_nodes = get_endpoint_global_decl_nodes(
        endpoint_name,ast_root)
    peered_decl_nodes = get_peered_decl_nodes(ast_root)

    var_store_loading_text = '_active_event = None'
    var_store_loading_text += '''
_context = %s(
    self._global_var_store,
    # not using sequence local store
    %s(_host_uuid))
''' % (
        emit_utils.library_transform('ExecutingEventContext'),
        emit_utils.library_transform('VariableStore'))

    var_store_loading_text += create_wvariables_array(
        host_uuid_var_name,endpoint_global_decl_nodes,False,
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    var_store_loading_text += create_wvariables_array(
        host_uuid_var_name,peered_decl_nodes,True,
        endpoint_name,ast_root,fdep_dict,emit_ctx)

    return var_store_loading_text


def emit_endpoint_oncreate_method_def(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    If the node exists, then emit code for it, otherwise, pass
    '''
    oncreate_node = get_oncreate_node(endpoint_name,ast_root)
    if oncreate_node != None:
        # actually define the oncreate node
        oncreate_method_txt = emit_private_method_interface(
            oncreate_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
            lib_util.internal_oncreate_func_call_name)
    else:
        oncreate_method_txt = '\n# no oncreate defined to emit method for \n'
        
    return oncreate_method_txt


def create_wvariables_array(
    host_uuid_var_name,decl_node_array,peered,
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {String} host_uuid_var_name --- The name of the variable
    that contains the host uuid.

    @param {Array} decl_node_array --- Each element of the array is an
    AST_DECLARATION node or an AST_ANNOTATED_DECLARATION node.

    @param {bool} peered --- True if new variable is supposed to be
    peered, False otherwise.
    '''
    wvar_load_text = ''
    
    for decl_node in decl_node_array:

        if TypeCheck.templateUtil.is_struct(decl_node.type):
            var_declaration,var_name = emit_statement.struct_rhs_declaration(
                decl_node,host_uuid_var_name,peered,
                endpoint_name,ast_root,fdep_dict,emit_ctx,True)
        else:
            var_declaration,var_name = emit_statement.non_struct_rhs_declaration(
                decl_node,host_uuid_var_name,peered,
                endpoint_name,ast_root,fdep_dict,emit_ctx,True)

        wvar_load_text += '''
self._global_var_store.add_var(
    '%s',%s)
''' % (var_name,var_declaration)

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
    method_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
    name_mangler=lib_util.endpoint_call_func_name,prefix=None):
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

    @param {Function} name_mangler --- Takes in a string and
    returns a string.  The compiler uses different internal names for
    functions than appear in the Waldo source text.  This is so that
    users are less likely to accidentally call into unsafe functions.
    This function should translate the name of the function from the
    source to an internal function.

    @param {String or None} prefix --- If we are emitting a message
    send function, there are some initialization operations that it
    must do.  Instead of copying the function arguments, we use the
    string provided in prefix.
    
    Also can be called to emit a message send or message receive
    function.
    '''

    name_node_index = 0
    if emit_utils.is_message_sequence_node(method_node):
        name_node_index = 1
    
    method_name_node = method_node.children[name_node_index]
    src_method_name = method_name_node.value
    internal_method_name = name_mangler(src_method_name)

    # When returning, check if it was a call from an outside-Waldo
    # function into this function... if it was (ie,
    # _returning_to_public_ext_array is not None), then we must
    # de-waldo-ify the return values before returning.  The values of
    # _returning_to_public_ext_array correspond to which return values
    # should be returned as externals (ie, we do not de-waldo-ify
    # them).
    method_arg_names = ['_returning_to_public_ext_array=None']
    if method_node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        # will fill in the default value of None in reduce
        method_arg_names = ['_returning_to_public_ext_array']
    if method_node.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        # message receives take no arguments
        method_arg_names = get_method_arg_names(method_node) + method_arg_names

    if method_node.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        comma_sep_arg_names = reduce (
            lambda x, y : x + ',' + y,
            method_arg_names,'')
    else:
        # provide default values for all argument sequence local data.
        # That way, jumps are easier (we do not have to match # of
        # arguments when jumping).
        comma_sep_arg_names = reduce (
            lambda x, y : x + ',' + y + '=None',
            method_arg_names,'')
        
    private_header = '''
def %s(self,_active_event,_context%s):
''' % (internal_method_name, comma_sep_arg_names)

    # actually emit body of function
    private_body = '\n'

    if method_node.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        if prefix == None:
            private_body = convert_args_to_waldo(method_node)
        else:
            # we are in a message send function: this means that
            # instead of copying in args, we must test if we've
            # already been initialized (to handle jumps properly).
            # Similarly, we must initialize other sequence global
            # data.
            private_body = prefix
            
    method_body_node = get_method_body_node_from_method_node(method_node)
    emitted_something = False
    for statement_node in method_body_node.children:
        emitted_something = True
        private_body += emit_statement.emit_statement(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        private_body += '\n'
        
    if private_body.strip() == '':
        # in case of empty functions
        private_body += 'pass\n'
    
    return private_header + emit_utils.indent_str(private_body)
        

def convert_args_to_waldo(method_node,sequence_local=False):
    '''
    In many cases, am not passing WaldoObjects to arguments being
    called.  (Examples: when a programmer uses a non-reference type
    that is not external.)  Currently, the compiler's invariant
    however is that all variables should be Waldo objects.  As a
    result, for each argument passed in, we check if it is a Waldo
    object.  If it is not, we turn it into one, (depending on the type
    it has).

    Additionally, method caller always passes in the reference to a
    Waldo object when the method is called with a variable.  For example,

    a = 5;
    some_method(a);

    Actually passes the reference to a into the called function.  This
    is fine if a is a reference type (list, map, user struct, function
    object) or the signature of some_method takes in an external.
    However, it is not okay for non-external value types.  These
    should be passed by value.  For each non-external value type, tell
    turn_into_waldo_var to force a copy of the variable.


    @param {bool} sequence_local --- If sequence_local is True, that
    means that the data must be copied into a peered vriable,
    regardless of whether or not they are a reference type.
    
    '''
    arg_node_index = get_arg_index_from_func_node_label(method_node.label)
    func_decl_arglist_node = method_node.children[arg_node_index]
    converted_args_string = ''

    # need to emit two sections of code, decide which to run based on
    # whether this was an endpoint call or not.  The reason that we
    # make this distinction is that non-external maps, lists, and user
    # structs passed across endpoint call boundaries are copied,
    # rather than used by reference.  (Across non-endpoint method call
    # boundaries, they're used by reference.)

    converted_args_string = 'if _context.check_and_set_from_endpoint_call_false():\n'
    converted_args_string += emit_utils.indent_str(
        convert_args_helper(func_decl_arglist_node,sequence_local,True) +
        '\npass\n')
    
    converted_args_string += '\nelse:\n'
    converted_args_string += emit_utils.indent_str(
        convert_args_helper(func_decl_arglist_node,sequence_local,False) +
        '\npass\n')

    converted_args_string += '\n'
    return converted_args_string



def convert_args_helper (func_decl_arglist_node,sequence_local,is_endpoint_call):
    '''
    @see convert_args_to_waldo
    '''
    converted_args_string = ''
    
    for func_decl_arg_node in func_decl_arglist_node.children:
        arg_name_node = func_decl_arg_node.children[1]
        var_type_dict = func_decl_arg_node.children[0].type
        # the name of the argument as it appears in the Waldo source
        # text
        arg_name = arg_name_node.value
        # the unique, name of the argument, annotated by the slice-ing
        # code.
        arg_unique_name = arg_name_node.sliceAnnotationName

        
        if not sequence_local:
            force_copy = 'True'

            multi_threaded= 'False'
            
            if TypeCheck.templateUtil.is_external(func_decl_arg_node.type):
                force_copy = 'False'
                multi_threaded = 'True'
            
            if ((not is_endpoint_call) and
                emit_utils.is_reference_type(func_decl_arg_node)):
                # we force copy maps, lists, and user structs only if
                # it's an endpoint call and they're not external.  
                force_copy = 'False'

            if TypeCheck.templateUtil.is_basic_function_type(func_decl_arg_node.type):
                # functions copied in must have their external args
                # arrays set.  these should be passed into the context
                # method that transforms a function into a waldo variable.
                ext_args_array_txt = emit_statement.emit_external_args_list_from_func_obj_type_dict(
                    func_decl_arg_node.type)

                converted_args_string += (
                    arg_name + ' = ' +
                    '_context.func_turn_into_waldo_var(' + arg_name +
                    ',%s,_active_event,self._host_uuid,False,%s,%s)\n' %
                    (force_copy,ext_args_array_txt,multi_threaded))

            else:
                converted_args_string += (
                    arg_name + ' = ' +
                    '_context.turn_into_waldo_var_if_was_var(' + arg_name +
                    ',%s,_active_event,self._host_uuid,False,%s)\n' % (force_copy,multi_threaded))

        else:

            if arg_unique_name == None:
                emit_utils.emit_assert(
                    'When converting sequence local args, arg name has no ' +
                    'unique name.')

            # FIXME: assume that there's a mechanism preventing
            # copying functions in user structs.  Longer-term answer
            # may be to remove function fields from user structs???
            # Rely on endpoint calls for foreign functions???
                
            # returns a peered version of passed in data
            convert_call_txt = (
                '_context.convert_for_seq_local(' + arg_name + ',' +
                '_active_event,self._host_uuid)\n' )

            # actually adds the created peered variable above to the
            # variable store.
            converted_args_string +='''
_context.sequence_local_store.add_var(
    "%s", %s)
''' % ( arg_unique_name , convert_call_txt)

    return converted_args_string

    

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

    # wait until ready initialization for node has completed before
    # continuing
    public_body = '''
# ensure that both sides have completed their onCreate calls
# before continuing
self._block_ready()
'''
    
    #### Deep copy non-external args
    # non_ext_arg_names is an array of strings
    non_ext_arg_names = get_non_external_arg_names_from_func_node(
        public_method_node)
                
    # do not need to copy arguments in: each function call does so on
    # its own.

    # Each element in this list is an index for a return parameter
    # that should be de-waldo-ified before returning.  We pass this
    # argument to the internal function that the internal function
    # knows which returns need to be de-waldo-ified before being
    # returned and which do not.
    list_return_external_positions = (
        get_external_return_positions_from_func_node(public_method_node))

    #### create a root event + ctx for event, call internal, and reurn
    internal_method_name = lib_util.endpoint_call_func_name(method_name)
    public_body += '''
while True:  # FIXME: currently using infinite retry 
    _root_event = self._act_event_map.create_root_event()
    _ctx = %s(
        self._global_var_store,
        # not using sequence local store
        %s(self._host_uuid))

    # call internal function... note True as last param tells internal
    # version of function that it needs to de-waldo-ify all return
    # arguments (while inside transaction) so that this method may
    # return them....if it were false, might just get back refrences
    # to Waldo variables, and de-waldo-ifying them outside of the
    # transaction might return over-written/inconsistent values.
    try:
        _to_return = self.%s(_root_event,_ctx %s,%s)
    except %s:
        pass

    # try committing root event
    _root_event.request_commit()
    _commit_resp = _root_event.event_complete_queue.get()
    if isinstance(_commit_resp,%s):
        # means it isn't a backout message: we're done
        return _to_return
    elif isinstance(_commit_resp,%s):
        raise %s()

''' % (emit_utils.library_transform('ExecutingEventContext'),
       emit_utils.library_transform('VariableStore'),
       internal_method_name,
       comma_sep_arg_names,
       str(list_return_external_positions),
       emit_utils.library_transform('BackoutException'),
       emit_utils.library_transform('CompleteRootCallResult'),
       emit_utils.library_transform('StopRootCallResult'),
       emit_utils.library_transform('StoppedException')
       )

    return public_header + emit_utils.indent_str(public_body)


def emit_endpoint_message_sequence_blocks(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    Emits all of the message sequence blocks for endpoint with name
    endpoint_name
    '''
    emitted_txt = '\n### User-defined message send blocks ###\n'
    emitted_txt += emit_endpoint_message_send_blocks(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    emitted_txt += '\n### User-defined message receive blocks ###\n'
    emitted_txt += emit_endpoint_message_receive_blocks(
        endpoint_name,ast_root,fdep_dict,emit_ctx)
    emitted_txt += '\n'
    return emitted_txt


def emit_endpoint_message_receive_blocks(
    endpoint_name,ast_root,fdep_dict,emit_ctx):

    message_receive_block_node_array = get_message_receive_block_nodes(
        endpoint_name,ast_root)

    receive_block_node_txt = ''
    for (message_receive_node, next_to_call_node, _) in message_receive_block_node_array:
        receive_block_node_txt += emit_message_receive(
            message_receive_node,next_to_call_node,
            endpoint_name,ast_root,fdep_dict,emit_ctx)

    return receive_block_node_txt
    

def emit_endpoint_message_send_blocks(
    endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    A message_send function must return at the end the specified
    sequence local parameters.
    
    @see emit_endpoint_message_sequence_blocks
    '''
    message_send_block_node_array = get_message_send_block_nodes(
        endpoint_name,ast_root)
    
    send_block_node_txt = ''
    for (message_send_node, next_to_call_node, seq_globals_node) in message_send_block_node_array:
        send_block_node_txt += emit_message_send(
            message_send_node,next_to_call_node,seq_globals_node,
            endpoint_name, ast_root,fdep_dict,emit_ctx)

    return send_block_node_txt


def emit_message_send(
    message_send_node,next_to_call_node,seq_globals_node,
    endpoint_name,ast_root, fdep_dict,emit_ctx):
    '''
    @param {AstNode} seq_globals_node --- Has label
    AST_MESSAGE_SEQUENCE_GLOBALS....In message send, we initialize the
    values of all sequence global variables.  Use this to do that.
    '''

    method_arg_names = get_method_arg_names(message_send_node)
    seq_local_init_prefix = '''
_first_msg = False
if not _context.set_msg_send_initialized_bit_true():
    # we must load all arguments into sequence local data and perform
    # initialization on sequence local data....start by loading
    # arguments into sequence local data
    # below tells the message send that it must serialize and
    # send all sequence local data.
    _first_msg = True
'''
    seq_local_init_prefix += emit_utils.indent_str(
        convert_args_to_waldo(message_send_node,True))
    # now emit the sequence global initializations and declarations
    # (this will also emit for the return nodes).
    seq_local_init_prefix += emit_utils.indent_str(emit_statement.emit_statement(
            seq_globals_node,endpoint_name,ast_root,fdep_dict,emit_ctx))    
    seq_local_init_prefix += emit_utils.indent_str('\npass\n')
    seq_local_init_prefix += '\n'

    
    # when message send ends, it must grab the sequence local data
    # requested to return.  To control for jumps, any time we jump, we
    # take whatever text is in emit_ctx's message_seq_return_txt and
    # insert it.  (For a message send function, this will return
    # sequence local data.  For a message receive function, this will
    # just be a return.)  This way, can insure that do not continue
    # executing after jump.
    return_var_name_nodes = get_message_send_return_var_names(
        message_send_node)

    msg_send_return_txt = '\nreturn '
    for counter in range(0,len(return_var_name_nodes)):
        var_name_node = return_var_name_nodes[counter]
        msg_send_return_txt += (
            '_context.sequence_local_store.get_var_if_exists("%s")' %
            var_name_node)
        if counter != (len(return_var_name_nodes) -1):
            msg_send_return_txt += ','
            

        
    emit_ctx.in_message_send = True
    emit_ctx.message_seq_return_txt = msg_send_return_txt

    # a message send function should look the same as a private
    # internal method (if we name it a little
    # differently...name_mangler arg takes care of this; and we
    # keep track of the return statement to issue on jump calls)
    msg_send_txt = emit_private_method_interface(
        message_send_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
        lib_util.partner_endpoint_msg_call_func_name,seq_local_init_prefix)

    # issue call for what to call next
    msg_send_txt += '\n'
    msg_send_txt += emit_utils.indent_str(
        emit_message_node_what_to_call_next(next_to_call_node,emit_ctx))

    # takes care of fall-through return (ie, message send has
    # completed)
    msg_send_txt += emit_utils.indent_str(msg_send_return_txt)
    msg_send_txt += '\n'
    emit_ctx.in_message_send = False
    emit_ctx.message_seq_return_txt = ''
    return msg_send_txt


def emit_message_receive(
    message_receive_node,next_to_call_node,endpoint_name,ast_root,
    fdep_dict,emit_ctx):
    '''
    @param {AstNode or None} next_to_call_node --- If AstNode, then
    has label AST_MESSAGE_RECEIVE_FUNCTION.  If None, means that this
    is the last message receive node in sequence and should tell other
    side to issue a block call with target None.
    '''

    msg_recv_node_name_node = message_receive_node.children[1]
    msg_recv_name = msg_recv_node_name_node.value
    
    emit_ctx.in_message_receive = True
    emit_ctx.message_seq_return_txt = '\nreturn '

    msg_receive_txt = emit_private_method_interface(
        message_receive_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
        lib_util.partner_endpoint_msg_call_func_name)
    msg_receive_txt += '\n'
    
    emit_ctx.in_message_receive = False
    emit_ctx.message_seq_return_txt = ''

    ## Ends by telling the opposite side what to do next
    next_to_call_txt = 'None'
    if next_to_call_node != None:
        # the name of the next sequence block to execute, as it
        # appears in the source Waldo text, ie, before mangling.
        next_sequence_block_src_name = next_to_call_node.children[1].value
        
        next_to_call_txt = '"' + lib_util.partner_endpoint_msg_call_func_name(
            next_sequence_block_src_name) + '"'
        

        
    # note that we must wait on receiving a response from the other
    # side before we can continue on, or the original sender may
    # return too early. We should not wait on the last message that we
    # send however, because, we do not expect any response to it.
    # (Ie, if next_to_call_txt == 'None', then do not wait.)
    next_sequence_txt = '''

_threadsafe_queue = %s.Queue()
_active_event.issue_partner_sequence_block_call(
    _context,%s,_threadsafe_queue,False)
# must wait on the result of the call before returning

if %s != None:
    # means that we have another sequence item to execute next

    _queue_elem = _threadsafe_queue.get()


''' % (emit_utils.library_transform('Queue'),
       next_to_call_txt,
       next_to_call_txt)



    next_sequence_txt += '''

    if isinstance(_queue_elem,%s):
        # back everything out: 
        raise %s()

    _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

    # apply changes to sequence variables.  Note: that
    # the system has already applied deltas for global data.
    _context.sequence_local_store.incorporate_deltas(
        _active_event,_queue_elem.sequence_local_var_store_deltas)

    # send more messages
    _to_exec_next = _queue_elem.to_exec_next_name_msg_field
    if _to_exec_next != None:
        # means that we do not have any additional functions to exec
        _to_exec = getattr(self,_to_exec_next)
        _to_exec(_active_event,_context)

''' % (emit_utils.library_transform('BackoutBeforeReceiveMessageResult'),
       emit_utils.library_transform('BackoutException'))


    msg_receive_txt += emit_utils.indent_str(next_sequence_txt)
    return msg_receive_txt


def emit_message_node_what_to_call_next(next_to_call_node,emit_ctx):
    '''
    @param {AstNode or None} next_to_call_node --- A message receive
    node or None.  At the end of a message send or message receive
    function, execution should "fall through" to the following message
    receive block.  This function emits the code that handles this
    logic.  Ie, it requests active event to issue a request to execute
    a message sequence block.  (Note: if next_to_call_node is None,
    then that means that we were at the end of a sequence and do not
    have any other blocks to execute: return empty string.
    '''

    if next_to_call_node == None:
        return ''

    # FIXME: seems to reproduce a lot of work already done in
    # emit_message_receive.
    
    next_message_name_node = next_to_call_node.children[1]
    next_message_name = next_message_name_node.value

    issue_call_is_first_txt = 'False'
    if emit_ctx.in_message_send:
        # allows us to determine if this is the first message in a
        # sequence block that is being sent.  If it is, then we need
        # to force sequence local data to be synchronized.  If it's
        # not, we only need to synchronize modified sequence local data.
        issue_call_is_first_txt = '_first_msg'

    
    return  '''
_threadsafe_queue = %s.Queue()
_active_event.issue_partner_sequence_block_call(
    _context,'%s',_threadsafe_queue, '%s')
_queue_elem = _threadsafe_queue.get()

if isinstance(_queue_elem,%s):
    raise %s()

_context.set_to_reply_with(_queue_elem.reply_with_msg_field)

# apply changes to sequence variables.  (There shouldn't
# be any, but it's worth getting in practice.)  Note: that
# the system has already applied deltas for global data.
_context.sequence_local_store.incorporate_deltas(
    _active_event,_queue_elem.sequence_local_var_store_deltas)

# send more messages
_to_exec_next = _queue_elem.to_exec_next_name_msg_field
if _to_exec_next != None:
    # means that we do not have any additional functions to exec
    _to_exec = getattr(self,_to_exec_next)
    _to_exec(_active_event,_context)
else:
    # end of sequence: reset to_reply_with_uuid in context.  we do
    # this so that if we go on to execute another message sequence
    # following this one, then the message sequence will be viewed as
    # a new message sequence, rather than the continuation of a
    # previous one.
    _context.reset_to_reply_with()

''' % (emit_utils.library_transform('Queue'),
       next_message_name, # the name of the message receive func to
                          # exec on other side in plain text
       issue_call_is_first_txt,
       emit_utils.library_transform('BackoutBeforeReceiveMessageResult'),
       emit_utils.library_transform('BackoutException'),
       )

                                   
def get_message_send_return_var_names(message_send_node):
    '''
    @returns {Array} --- Returns an array of strings, each is the
    sequence local name of a sequence local data item that gets
    returned.
    '''
    return_name_array = []

    return_decl_arg_list_node = message_send_node.children[4]
    for return_decl_node in return_decl_arg_list_node.children:
        return_var_name_node = return_decl_node.children[1]
        return_var_name = return_var_name_node.value

        return_name_array.append(
            return_var_name_node.sliceAnnotationName)

    return return_name_array


def get_message_send_block_nodes(endpoint_name,ast_root):
    '''
    @returns {Array of 3-tuples} --- @see _get_endpoint_sequnece_nodes
    '''
    return _get_endpoint_sequence_nodes(
        endpoint_name,ast_root,AST_MESSAGE_SEND_SEQUENCE_FUNCTION)

def get_message_receive_block_nodes(endpoint_name,ast_root):
    '''
    @returns {Array of 3-tuples} --- @see _get_endpoint_sequnece_nodes
    '''
    return _get_endpoint_sequence_nodes(
        endpoint_name,ast_root,AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION)


def _get_endpoint_sequence_nodes(
    endpoint_name,ast_root,label_to_filter_for):
    '''
    @param {AstLabel (string)} label_to_filter_for --- Either
    AST_MESSAGE_SEND_SEQUENCE_FUNCTION or
    AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION.  Used to select whether to
    return send blocks or receive blocks.
    
    @returns {Array of 3-tuples} --- Each element of the array has the
    form (a,b,c),

       a: A message sequence node that on the endpoint with name
          endpoint_name.

       b: The message sequence node that a "falls through" into.  Will
          be on opposite endpoint of a.  Can also be None if a was end
          of sequence.

       c: The sequence globals node associated with the entire message
          sequence.  (Note: this is only really useful for message
          send blocks....message receive blocks will likely ignore it.)
    '''
    endpoint_seq_node_array = []
    msg_seq_section_node = ast_root.children[6]

    for msg_seq_node in msg_seq_section_node.children:
        msg_seq_name_node = msg_seq_node.children[0]
        msg_seq_name = msg_seq_name_node.value
        
        seq_globals_node = msg_seq_node.children[1]
        seq_funcs_node = msg_seq_node.children[2]

        for counter in range(0, len(seq_funcs_node.children)):
            msg_func_node = seq_funcs_node.children[counter]
            
            if msg_func_node.label != label_to_filter_for:
                continue
            
            endpoint_id_node = msg_func_node.children[0]

            if endpoint_id_node.value == endpoint_name:
                # means that this function is one of this endpoint's
                # functions
                
                next_to_get_called_node = None
                if counter + 1 < len(seq_funcs_node.children):
                    next_to_get_called_node = seq_funcs_node.children[counter + 1]

                endpoint_seq_node_array.append(
                    (msg_func_node,next_to_get_called_node,seq_globals_node))
          
    return endpoint_seq_node_array


def get_oncreate_node(endpoint_name,ast_root):
    '''
    @param {String} endpoint_name

    @param {AstNode} ast_root

    @returns {AstNode or None} --- Either returns the AstNode
    associated with the endpoint named endpoint_name, or returns None.
    '''
    oncreate_node_list = _get_endpoint_method_nodes(
        endpoint_name,ast_root,AST_ONCREATE_FUNCTION)

    # there can only be one onCreate node, so must unwrap it.
    if len(oncreate_node_list) == 0:
        return None

    return oncreate_node_list[0]

    

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
    either be AST_PUBLIC_FUNCTION, AST_PRIVATE_FUNCTION, or
    AST_ONCREATE, depending on whether we want to return an array of
    public or private nodes.

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
        if not TypeCheck.templateUtil.is_external(func_decl_arg_node.type):
            name_node = func_decl_arg_node.children[1]
            returner.append(name_node.value)

    return returner


def get_external_return_positions_from_func_node(func_node):
    '''
    @returns {list} --- Each element is an integer corresponding to
    the index in the return tuple of a return value that is external

    public function () returns Num, External Num, Num {}

    We would return [1].
    '''
    return_type_node_index = get_return_type_index_from_func_node_label(
        func_node.label)
    return_type_node = func_node.children[return_type_node_index]

    external_return_indices = []
    
    for return_counter in range(0,len(return_type_node.children)):
        return_node = return_type_node.children[return_counter]
        if TypeCheck.templateUtil.is_external(return_node.type):
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
            'Unknown label getting return type for.')
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
            'get_arg_index_from_func_node_label.')
    #### END DEBUG
    return arg_node_index
