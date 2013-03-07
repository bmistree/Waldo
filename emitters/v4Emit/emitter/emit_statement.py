from parser.ast.astLabels import *
from slice.typeStack import TypeStack
import emit_utils
import parser.ast.typeCheck as TypeCheck
import emitters.v4Emit.lib.util as lib_util

def emit_statement(
    statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @returns {String}
    '''
    statement_txt = ''
    if statement_node.label == AST_IDENTIFIER:
        statement_txt = _emit_identifier(statement_node)

    elif statement_node.label == AST_FUNCTION_BODY_STATEMENT:
        for child_node in statement_node.children:
            statement_txt += emit_statement(
                child_node,endpoint_name,ast_root,fdep_dict,
                emit_ctx)

    elif statement_node.label == AST_ASSIGNMENT_STATEMENT:
        statement_txt = _emit_assignment(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    elif statement_node.label == AST_BOOL:
        statement_txt =  statement_node.value + ' '
        
    elif statement_node.label == AST_STRING:
        statement_txt += "'"  + statement_node.value + "' "
        
    elif statement_node.label == AST_NUMBER:
        statement_txt += statement_node.value + ' '

    elif statement_node.label == AST_DECLARATION:
        # These should all be local variables (peered, endpoint
        # global, and sequence global variables don't get emitted
        # here).
        
        var_name_node = statement_node.children[1]
        var_name_waldo_src = var_name_node.value
        
        # initialization is optional: declarations may not have any
        # initializers
        var_initializer_txt = ''
        if len(statement_node.children) == 3:
            var_initializer_node = statement_node.children[2]
            var_initializer_txt = (
                '_context.get_val_if_waldo(%s)' %
                emit_statement(
                    var_initializer_node,endpoint_name,ast_root,
                    fdep_dict,emit_ctx))

        # should contain something like WaldoNumVariable,
        # WaldoTextVariable, etc.
        var_type_txt = emit_utils.get_var_type_txt_from_type_dict(
            emit_utils.get_var_type_dict_from_decl(statement_node))

        # the name that the user used for the variable.
        var_name_txt = emit_utils.get_var_name_from_decl(statement_node)

        # Example of what statement_txt should look like:
        
        # op_successful = _waldo_libs.WaldoTrueFalseVariable(  # the type of waldo variable to create
        #     '1__op_successful', # variable's name
        #     _host_uuid, # host uuid var name
        #     False,  # if peered, True, otherwise, False
        #     True
        # ))
        statement_txt = '''%s = %s( # the type of waldo var to create
    '%s', # var name
    self._uuid, # host uuid
    False, # not peered
    %s) # initializer text''' % (
            var_name_waldo_src,
            emit_utils.library_transform(var_type_txt), var_name_txt,
            var_initializer_txt)

            
            
    elif statement_node.label == AST_RETURN_STATEMENT:

        # @see emit_statement._emit_second_level_assign.  Each item
        # returned should be the actual Waldo object.
        # emit_statement._emit_second_level_assign can sort out what
        # needs to be copied before being assigned and what needs to
        # maintain its reference (via external)
        ret_list_node = statement_node.children[0];

        # all returend objects are returned as tuples
        statement_txt = 'return ('

        if len(ret_list_node.children) == 0:
            statement_txt += 'None'

        for ret_item_node in ret_list_node.children:
            statement_txt += emit_statement(
                ret_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            statement_txt += ','

        statement_txt += ')\n'
            
    elif statement_node.label == AST_BRACKET_STATEMENT:
        lhs_node = statement_node.children[0]
        rhs_node = statement_node.children[1]

        exterior_bracket_txt = emit_statement(
            lhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        interior_bracket_txt = emit_statement(
            rhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        statement_txt = (
            '%s.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(%s))'
            %  (exterior_bracket_txt, interior_bracket_txt))

        
    elif emit_utils.is_method_call(statement_node):
        statement_txt += _emit_method_call(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    elif statement_node.label == AST_MAP:
        variable_type_str = emit_utils.library_transform('WaldoMapVariable')

        map_item_str = ''
        for map_literal_item_node in statement_node.children:
            map_item_str += emit_statement(
                map_literal_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        
        statement_txt = '''%s("garbage_name",
    self._uuid,
    False,
    {%s})''' % (variable_type_str, map_item_str)


    elif statement_node.label == AST_MAP_ITEM:
        # individual entry of map literal
        key_node = statement_node.children[0];
        val_node = statement_node.children[1];

        # keys of map can only be value types
        key_txt = '_context.get_val_if_waldo(%s)' % emit_statement(
            key_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        val_txt = '_context.get_val_if_waldo(%s)' % emit_statement(
            val_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        statement_txt = key_txt + ': ' + val_txt + ',\n'

        # FIXME: in map literal, do not know whether to get_val on
        # values (ie, assign by reference or by value).  Probably will
        # update the language so that only value statements can be put
        # into a map literal.  same with string.


    elif statement_node.label == AST_LIST:
        variable_type_str = emit_utils.library_transform('WaldoListVariable')

        list_item_str = ''
        for list_literal_item_node in statement_node.children:
            list_item_str += emit_statement(
                list_literal_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            list_item_str += ','

        statement_txt = '''%s("garbage_name",
    self._uuid,
    False,
    [%s])''' % (variable_type_str, list_item_str)
        
        
    else:
        emit_utils.emit_warn(
            'Unknown label in emit statement ' + statement_node.label)

    return statement_txt



def _emit_method_call(
    method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode} method_call_node
    '''
    if emit_utils.is_endpoint_method_call(method_call_node):
        return _emit_endpoint_method_call(
            method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    elif emit_utils.is_msg_seq_begin_call(method_call_node,endpoint_name,fdep_dict):
        return _emit_msg_seq_begin_call(
            method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    # FIXME: add code for function objects
    
    # standard public/private call
    return _emit_public_private_method_call(
        method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx)


def _emit_public_private_method_call(
    method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
    name_mangler_func=lib_util.endpoint_call_func_name):
    '''
    @param {Function} name_mangler_func --- Takes in a string and
    returns a string.  The compiler uses different internal names for
    functions than appear in the Waldo source text.  This is so that
    users are less likely to accidentally call into unsafe functions.
    This function should translate the name of the function from the
    source to an internal function.
    
    Programmer makes a call to one of the public or private methods
    defined on endpoint from code within Waldo.

    There is a chance that pass through Python literal values (eg, 3,
    'hello') instead of waldo variables.  The first thing that should
    happen in any method we call is that we should wrap these literals
    again as Waldo variables.  @see emit_endpoints.convert_args_to_waldo
    '''
    method_call_name_node = method_call_node.children[0]
    method_call_name = method_call_name_node.value

    method_call_txt = 'self.%s(_active_event,_context,' % name_mangler_func(
        method_call_name)

    method_call_arg_list_node = emit_utils.get_method_call_arg_list_node(
        method_call_node)
    
    for method_call_arg_node in method_call_arg_list_node.children:
        arg_txt = emit_statement(
            method_call_arg_node, endpoint_name,ast_root,fdep_dict,emit_ctx)

        suffix = ','

        # FIXME: incorrect check: actually want to know whether the
        # function *expects* an external, not whether the var itself
        # is external.  Simplest way to fix is in function to copy
        # non-references if they are not supposed to be external.
        if ((not method_call_arg_node.external) and
            (not emit_utils.is_reference_type(method_call_arg_node))):
            method_call_txt += '_context.get_val_if_waldo(' 
            suffix = '),'

        method_call_txt += arg_txt + suffix

    return method_call_txt + ')'


def _emit_msg_seq_begin_call(
    msg_seq_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    Before beginning a message sequence call, we set context's
    sequence initialized bit to False.  Inside of the message send
    function, we check context's sequence initialized bit.  If it is
    False, set it to True, and load all sequence local data into
    variable store.  If it is False, it means that we were asked to
    jump back to the send part of the sequence and that we should
    therefore *not* reinitialize sequence local data.  

    The way that we set the bit low before executing is a little
    ungainly.  Essentially, we want to support assign-like semantics.

    Assume the following Waldo expression

    a = begin_msg()

    By the time we get to this function (_emit_msg_seq_begin_call), we
    have already emitted (approximately)

    a =

    If we just emitted
    
    set_initialized_bit_false()
    begin_msg()

    Then a would be set to the result of set_bit.  Instead, we use the
    ternary operator:

    a = begin_msg() if _context.set_initialized_bit_false() else None

    where we enusre that _context.set_initialized_bit_false always
    returns True

    Otherwise, the message call looks just like a private function.

    NOTE: This assumes the rule that you cannot start one message
    sequence from *within* another message sequence.
    '''
    return ('%s if _context.set_msg_send_initialized_bit_false() else None' %
            _emit_public_private_method_call(
            msg_seq_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
            lib_util.partner_endpoint_msg_call_func_name))


def _emit_endpoint_method_call(
    endpoint_method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    Listens for result on threadsafe queue after making the call.  If
    the queue results say that we should back out, then raise a
    BackoutException.  ExecutingEvent code will catch it and forward
    the backout on.

    Otherwise, ensure that the read queue element is in _queue_elem.
    '''
    name_node = endpoint_method_call_node.children[0]

    #### DEBUG
    if name_node.label != AST_DOT_STATEMENT:
        emit_utils.emit_assert(
            'When emitting endpoint method call got an ' +
            'invalid call node.')
    #### END DEBUG

    endpoint_name_node = name_node.children[0]
    method_name_node = name_node.children[1]
    method_name = method_name_node.value

    method_arg_str = ''
    arg_list_node = emit_utils.get_method_call_arg_list_node(
        endpoint_method_call_node)
    for arg_node in arg_list_node.children:
        method_arg_str += statement_emit(
            arg_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        method_arg_str += ','
    
    call_txt = ('_threadsafe_queue = %s\n' %
                emit_utils.library_transform('Queue.Queue()'))

    emitted_endpoint_name = statement_emit(
        endpoint_name_node, endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    call_txt += ('_active_event.issue_endpoint_object_call(' +
                 emitted_endpoint_name + ',' + method_name + ',' +
                 '_threadsafe_queue,%s)\n' % method_arg_str )

    call_txt += '_queue_elem = _threadsafe_queue.get()\n'

    # FIXME: may also want to check whether the error is just that the
    # endpoint does not actually have a method with that name...
    call_txt += '''
if not isinstance(_queue_elem,%s):
    raise %s()
''' % (emit_utils.library_transform('EndpointCallResult'),
       emit_utils.library_transform('BackoutException'))
    # FIXME: must add BackoutException to list of exceptions.
    return call_txt



def _emit_assignment(
    assignment_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode} assignment_node --- corresponds to node labeled
    AST_ASSIGNMENT_STATEMENT

    The lhs node is a comma list.  The comma list will always have
    only one element whenever the right hand side is not a function
    that is being called.  The comma list may or may not always be a
    single element when issuing a function call.
    
    '''
    #### DEBUG
    if assignment_node.label != AST_ASSIGNMENT_STATEMENT:
        emit_utils.emit_assert(
            'assignment_node must be an identifier')
    #### END DEBUG

    # always assigning to a comma list of variables.
    comma_list_node = assignment_node.children[0]
    rhs_node = assignment_node.children[1]


    #### DEBUG
    if comma_list_node.label != AST_OPERATABLE_ON_COMMA_LIST:
        emit_utils.emit_assert(
            'Should only assign to a comma list')
    #### END DEBUG

    # strategy, assign into intermediate values: _tmp0, _tmp1, _tmp2,
    # etc., for each element in the tuple.  after that, actually,
    # match each to the place they go in Waldo
    intermediate_assign_txt = ''
    for counter in range(0,len(comma_list_node.children)):
        intermediate_assign_txt += '_tmp' + str(counter)
        if counter != len(comma_list_node.children) -1:
            intermediate_assign_txt += ','


    if emit_utils.is_method_call(rhs_node):
        func_call_txt = emit_statement(
            rhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        if emit_utils.is_endpoint_method_call(rhs_node):
            # execute the function call before 
            intermediate_assign_txt = func_call_txt + '\n' + internmediate_assign_txt
            # emitting an endpoint function call stores values in
            # _queue_elem
            # FIXME: it sucks that _queue_elem is hard-coded
            to_assign_txt = '_queue_elem.to_return'
        else:
            to_assign_txt = func_call_txt

    else:
        to_assign_txt = emit_statement(
            rhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    first_level_assign_txt = intermediate_assign_txt + ' = ' + to_assign_txt + '\n'


    # after first level assign, can take each individual element from
    # function list
    return first_level_assign_txt +_emit_second_level_assign(
        comma_list_node,endpoint_name,ast_root,fdep_dict,emit_ctx)


def _emit_second_level_assign(
    comma_list_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    extAssign _ to a, b = func_call()
    
    (extAssign _ a) and b will each be children of comma_list_node

    We are trying to assign all elements of the comma_list_node to
    intermediate variables generated by _emit_assignment.  For each
    node in comma_list_node, we should have a corresponding
    intermediate variable named _tmpX that we want to assign to it
    (where X is the number of the node in the comma
    list....0,1,2,3...)
    '''
    # gets returned at end of function
    all_assignments_txt = ''
    for counter in range(0,len(comma_list_node.children)):
        lhs_node = comma_list_node.children[counter]
        
        ext_assign = False
        if lhs_node.label == AST_EXT_ASSIGN_FOR_TUPLE:
            # notes that we are performing an assignment to an ext and
            # unwraps the extAssign.
            ext_assign = True
            lhs_node = lhs_node.children[0]

        to_assign_txt = '_tmp' + str(counter)
        if not ext_assign:
            to_assign_txt = '_context.get_val_if_waldo(' + to_assign_txt + ')'
            
        if lhs_node.label == AST_BRACKET_STATEMENT:
            # need to actually assign to a particular key, rather than the
            # overall variable.  can't use write_val, must use
            # write_val_on_key instead.
            outside_bracket_node = lhs_node.children[0]
            inside_bracket_node = lhs_node.children[1]

            outside_txt = emit_statement(
                outside_bracket_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            # FIXME: declare method in WaldoExecutingContext for
            # _get_val_if_waldo.  Essentially, in cases where unsure
            # if using a non-waldo number, string, etc. or a waldo
            # variable, and want to use the value type, this gives the
            # value type.
            inside_txt =  '_context._get_val_if_waldo(%s)' % (
                emit_statement(
                    inside_bracket_node,endpoint_name,
                    ast_root,fdep_dict,emit_ctx))
                                    
            to_assign_to_txt = (
                outside_txt +
                '.get_val(_active_event).write_val_on_key(_active_event,' +
                inside_txt + ',' # gives key for map writing into
                                 # still need actual value
                )
            
        else:
            # was not a bracket statement, can just call write_val
            # directly
            to_assign_to_txt = emit_statement(
                lhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

            to_assign_to_txt += '.write_val(_active_event,'
            
        all_assignments_txt += to_assign_to_txt + to_assign_txt + ')\n'
                      
    return all_assignments_txt
    
    
def _emit_identifier(identifier_node):
    '''
    @param {AstNode} identifier_node --- corresponds to node labeled
    AST_IDENTIFIER
    '''
    #### DEBUG
    if identifier_node.label != AST_IDENTIFIER:
        emit_utils.emit_assert(
            'statement_node must be an identifier')
    #### END DEBUG
        
    # FIXME: not handling dot statements for user structs here
        
    identifier_txt = ''
    id_annotation_name = identifier_node.sliceAnnotationName
    id_annotation_type = identifier_node.sliceAnnotationType
    if id_annotation_type in [TypeStack.IDENTIFIER_TYPE_LOCAL,
                              TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT]:
        # means that we can just address the variable directly
        identifier_txt = identifier_node.value

    elif id_annotation_type in [TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL,
                                TypeStack.IDENTIFIER_TYPE_SHARED]:
        # get value from endpoint's global store
        identifier_txt = '_context.global_store.get_var_if_exists("%s")' % (
            id_annotation_name)
    elif id_annotation_type in [TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,
                              TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT]:
        identifier_txt = '_context.sequence_local_store.get_var_if_exists("%s")' %(
            id_annotation_name)
    #### DEBUG
    else:
        emit_utils.emit_assert(
            'Unknown annotation on identifier ' + str(id_annotation_type))
    #### END DEBUG
    return identifier_txt
