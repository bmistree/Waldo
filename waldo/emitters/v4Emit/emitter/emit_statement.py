from waldo.parser.ast.astLabels import *
from waldo.slice.typeStack import TypeStack
import emit_utils
import waldo.parser.ast.typeCheck as TypeCheck
import waldo.lib.util as lib_util
from waldo.parser.ast.astNode import AstNode

# Constant Dict representing Waldo's builtin endpoint methods. Maps from
# method names to emitted code.
ENDPOINT_BUILTIN_METHODS = {
  'id' : 'self.id()'            # returns the endpoint's unique id
}

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

    elif statement_node.label == AST_SELF:
        statement_txt = 'self'
    
    elif statement_node.label == AST_ASSIGNMENT_STATEMENT:
        statement_txt = _emit_assignment(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    elif statement_node.label == AST_WHILE_STATEMENT:
        bool_cond_node = statement_node.children[0]
        body_node = statement_node.children[1]

        bool_cond_txt = emit_statement(
            bool_cond_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        
        body_txt = emit_statement(
            body_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        body_txt += '\npass\n'
        
        while_head_txt = (
            'while _context.get_val_if_waldo(%s,_active_event): \n' %
            bool_cond_txt)

        statement_txt = while_head_txt + emit_utils.indent_str(body_txt)

    elif statement_node.label == AST_DOT_STATEMENT:
        pre_dot_node = statement_node.children[0]
        post_dot_node = statement_node.children[1]

        pre_dot_txt = emit_statement(
            pre_dot_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        # rhs node is always an identifier type
        post_dot_name = post_dot_node.value

        statement_txt = (
            pre_dot_txt + '.get_val(_active_event)' +
            ('.get_val_on_key(_active_event,"%s")' % post_dot_name))

    elif statement_node.label == AST_PRINT:
        print_body_node = statement_node.children[0]
        statement_txt = 'print ' + emit_statement(
            print_body_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    elif statement_node.label == AST_EMPTY:
        pass

    elif statement_node.label == AST_CONTINUE:
        statement_txt = 'continue'
    elif statement_node.label == AST_BREAK:
        statement_txt = 'break'

    elif statement_node.label == AST_FOR_STATEMENT:
        statement_txt = emit_for(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    elif statement_node.label == AST_RANGE:
        base_range_node = statement_node.children[0]
        limit_range_node = statement_node.children[1]
        increment_range_node = statement_node.children[2]

        base_range_txt = emit_statement(
            base_range_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        limit_range_txt = emit_statement(
            limit_range_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        increment_range_txt = emit_statement(
            increment_range_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        statement_txt = (
            '%s("garbage",self._host_uuid,False,' % emit_utils.library_transform('WaldoSingleThreadListVariable') +
            'list(range(_context.get_val_if_waldo(%s,_active_event),' % base_range_txt +
            '_context.get_val_if_waldo(%s,_active_event),' % limit_range_txt +
            '_context.get_val_if_waldo(%s,_active_event))))' % increment_range_txt )


    elif statement_node.label == AST_SIGNAL_CALL:
        statement_txt = '_context.signal_call(_active_event,'
        signal_arg_nodes = statement_node.children[0]
                
        for signal_arg_node in signal_arg_nodes.children:
            signal_arg_node_txt = emit_statement(
                signal_arg_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            statement_txt += signal_arg_node_txt + ','
        statement_txt += ')\n'
        
    elif statement_node.label == AST_BOOL:
        statement_txt = statement_node.value + ' '

    elif statement_node.label == AST_TOTEXT_FUNCTION:
        to_call_to_txt_on_node = statement_node.children[0]
        to_call_to_txt_on_txt = emit_statement(
            to_call_to_txt_on_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        statement_txt = '_context.to_text(%s,_active_event)' % to_call_to_txt_on_txt

    elif statement_node.label == AST_NOT_EXPRESSION:
        what_notting_node = statement_node.children[0]
        what_notting_txt = emit_statement(
            what_notting_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        
        statement_txt = (
            '( not ( _context.get_val_if_waldo(%s,_active_event) ))' %
            what_notting_txt)

    elif statement_node.label == AST_LEN:
        what_getting_len_of_node = statement_node.children[0]
        what_getting_len_of_txt = emit_statement(
            what_getting_len_of_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        statement_txt = (
            '_context.handle_len(%s,_active_event)' %
            what_getting_len_of_txt)

    elif statement_node.label == AST_CONDITION_STATEMENT:
        statement_txt = emit_condition_statement(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    elif statement_node.label == AST_BOOLEAN_CONDITION:
        statement_txt = emit_statement(
            statement_node.children[0],endpoint_name,ast_root,
            fdep_dict,emit_ctx)

    elif statement_node.label == AST_FUNCTION_BODY:
        for single_statement_node in statement_node.children:
            statement_txt += emit_statement(
                single_statement_node,endpoint_name,ast_root,
                fdep_dict,emit_ctx)
            statement_txt += '\n'
        
    elif statement_node.label == AST_IN_STATEMENT:
        lhs_node = statement_node.children[0]
        rhs_node = statement_node.children[1]

        rhs_txt = emit_statement(
            rhs_node, endpoint_name, ast_root,fdep_dict,emit_ctx)
        lhs_txt = emit_statement(
            lhs_node, endpoint_name, ast_root,fdep_dict,emit_ctx)
        
        statement_txt = (
            '_context.handle_in_check(%s,%s,_active_event)' %
            (lhs_txt, rhs_txt))
        
    elif is_binary_operator_from_label(statement_node.label):
        # checks for +,-,>, etc.
        
        # FIXME: must be careful to check if both sides are
        # lists... should wrap them in a Waldo list variable.
        lhs_node = statement_node.children[0]
        rhs_node = statement_node.children[1]

        lhs_txt = emit_statement(
            lhs_node, endpoint_name,ast_root,fdep_dict,emit_ctx)
        
        rhs_txt = emit_statement(
            rhs_node, endpoint_name,ast_root,fdep_dict,emit_ctx)

        bin_op_txt = get_binary_operator_from_label(statement_node.label)

        statement_txt = (
            '(_context.get_val_if_waldo(%s,_active_event) %s _context.get_val_if_waldo(%s,_active_event))'
            % (lhs_txt, bin_op_txt, rhs_txt))
        

    elif statement_node.label == AST_APPEND_STATEMENT:
        to_append_to_node = statement_node.children[0]
        what_to_append_node = statement_node.children[1]

        what_to_append_txt = emit_statement(
            what_to_append_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)

        to_append_to_txt = emit_statement(
            to_append_to_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)


        element_type_dict = TypeCheck.templateUtil.getListValueType(
            to_append_to_node.type)

        
        if (not emit_utils.is_reference_type_type_dict(element_type_dict) and
           (not TypeCheck.templateUtil.is_external(element_type_dict))):
            what_to_append_txt = (
                '_context.get_val_if_waldo(%s,_active_event)' %
                what_to_append_txt)
            
        statement_txt = (
            to_append_to_txt +
            ('.get_val(_active_event).append_val(_active_event,%s)'
             %
             what_to_append_txt))

    elif statement_node.label == AST_REMOVE_STATEMENT:
        to_remove_from_node = statement_node.children[0]
        what_to_remove_node = statement_node.children[1]

        what_to_remove_txt = emit_statement(
            what_to_remove_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)

        to_remove_from_txt = emit_statement(
            to_remove_from_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)

        statement_txt = (
            to_remove_from_txt + '.get_val(_active_event).del_key_called(_active_event,' +
            '_context.get_val_if_waldo(%s,_active_event))' %
            what_to_remove_txt)

    elif statement_node.label == AST_INSERT_STATEMENT:
        to_insert_into_node = statement_node.children[0]
        index_to_insert_into_node = statement_node.children[1]
        what_to_insert_node = statement_node.children[2]

        index_to_insert_into_txt = emit_statement(
            index_to_insert_into_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)
        
        to_insert_into_txt = emit_statement(
            to_insert_into_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)


        what_to_insert_txt = emit_statement(
            what_to_insert_node,endpoint_name,ast_root,
            fdep_dict,emit_ctx)
        
        # if list's elements are not reference types or external
        # types, then we should get their internal types before
        # inserting.
        element_type_dict = TypeCheck.templateUtil.getListValueType(
            to_insert_into_node.type)
        if (not emit_utils.is_reference_type_type_dict(element_type_dict) and
            (not TypeCheck.templateUtil.is_external(element_type_dict))):
            what_to_insert_txt = (
                '_context.get_val_if_waldo(%s,_active_event)' %
                what_to_insert_txt)
        
        statement_txt = (
            to_insert_into_txt + '.get_val(_active_event).insert_into(_active_event,' +
            ('_context.get_val_if_waldo(%s,_active_event),' % index_to_insert_into_txt) +
            what_to_insert_txt + ')')

        
    elif statement_node.label == AST_STRING:
        statement_txt += "'"  + statement_node.value + "' "

    elif statement_node.label == AST_EXT_ASSIGN:
        statement_txt = emit_ext_assign(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)


    elif statement_node.label == AST_EXT_COPY:
        # extCopy 3 to a
        # should produce
        # a.get_val(_active_event).write_val(
        #    _active_event,_context.get_val_if_waldo(
        #        3,_active_event))
        # ie, assign the internal value of a to whatever
        # get_val_if_waldo of 3 produces
        
        to_copy_from_node = statement_node.children[0]
        to_copy_from_node_txt = emit_statement(
            to_copy_from_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        to_copy_to_node = statement_node.children[1]
        to_copy_to_node_txt = emit_statement(
            to_copy_to_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        statement_txt = (
            to_copy_to_node_txt + '.get_val(_active_event).' +
            'write_val(_active_event,_context.get_val_if_waldo(' +
            to_copy_from_node_txt + ',_active_event))'
            )

        # FIXME: what about lists/maps of externals?  How do you
        # assign into and copy them?
        # extCopy 3 to a[3] extAssign a[3] to b
        
    elif statement_node.label == AST_NUMBER:
        statement_txt += statement_node.value + ' '

    elif statement_node.label == AST_DECLARATION:
        # These should all be local variables (peered, endpoint
        # global, and sequence global variables don't get emitted
        # here).
        var_name_node = statement_node.children[1]
        var_name_waldo_src = var_name_node.value

        var_type_node = statement_node.children[0]
        
        if TypeCheck.templateUtil.is_struct(var_type_node.type):
            decl_txt,var_name = struct_rhs_declaration(
                statement_node,'self._host_uuid',
                False, # variable is not peered
                endpoint_name,
                ast_root,fdep_dict,emit_ctx,
                # not multithreaded => pass in false
                False)
            
        elif (emit_utils.is_reference_type_type_dict(var_type_node.type) or
              TypeCheck.templateUtil.is_endpoint(var_type_node.type) or
              TypeCheck.templateUtil.is_basic_function_type(var_type_node.type)):
            
            decl_txt,var_name = non_struct_rhs_declaration(
                statement_node,'self._host_uuid',
                False, # variable is not peered
                endpoint_name,
                ast_root,fdep_dict,emit_ctx,
                # not multithreaded => pass in false
                False)
            
        else:
            # value types do not need to be wrapped
            decl_txt = emit_utils.emit_value_type_default(var_type_node.type)
            initializer_node = emit_utils.get_var_initializer_from_decl(statement_node)
            if initializer_node != None:
                decl_txt =(
                    '_context.get_val_if_waldo(%s,_active_event)' %
                    emit_statement(
                        initializer_node, endpoint_name,ast_root,fdep_dict,emit_ctx))
                
        statement_txt = var_name_waldo_src + ' = ' + decl_txt 


        
    elif statement_node.label == AST_RETURN_STATEMENT:
        statement_txt = _emit_return_statement(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

            
    elif statement_node.label == AST_BRACKET_STATEMENT:
        lhs_node = statement_node.children[0]
        rhs_node = statement_node.children[1]

        exterior_bracket_txt = emit_statement(
            lhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        interior_bracket_txt = emit_statement(
            rhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)


        if TypeCheck.templateUtil.is_text(lhs_node.type):
            statement_txt = (
                '%s.get_val(_active_event)[_context.get_val_if_waldo(%s,_active_event)]'
                %  (exterior_bracket_txt, interior_bracket_txt))
        else:
            statement_txt = (
                '%s.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(%s,_active_event))'
                %  (exterior_bracket_txt, interior_bracket_txt))

        
    elif emit_utils.is_method_call(statement_node):
        statement_txt += _emit_method_call(
            statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    elif statement_node.label == AST_MAP:
        variable_type_str = emit_utils.library_transform('WaldoSingleThreadMapVariable')

        map_item_str = ''
        for map_literal_item_node in statement_node.children:
            map_item_str += emit_statement(
                map_literal_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        
        statement_txt = '''%s("garbage_name",
    self._host_uuid,
    False,
    {%s})''' % (variable_type_str, map_item_str)


    elif statement_node.label == AST_MAP_ITEM:
        # individual entry of map literal
        key_node = statement_node.children[0];
        val_node = statement_node.children[1];

        # keys of map can only be value types
        key_txt = '_context.get_val_if_waldo(%s,_active_event)' % emit_statement(
            key_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        val_txt = '_context.get_val_if_waldo(%s,_active_event)' % emit_statement(
            val_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        statement_txt = key_txt + ': ' + val_txt + ',\n'

        # FIXME: in map literal, do not know whether to get_val on
        # values (ie, assign by reference or by value).  Probably will
        # update the language so that only value statements can be put
        # into a map literal.  same with string.


    elif statement_node.label == AST_LIST:
        variable_type_str = emit_utils.library_transform('WaldoSingleThreadListVariable')

        list_item_str = ''
        for list_literal_item_node in statement_node.children:
            list_item_str += emit_statement(
                list_literal_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            list_item_str += ','

        statement_txt = '''%s("garbage_name",
    self._host_uuid,
    False,
    [%s])''' % (variable_type_str, list_item_str)

    elif statement_node.label == AST_MESSAGE_SEQUENCE_GLOBALS:
        for sequence_local_decl_node in statement_node.children:
            name_node = sequence_local_decl_node.children[1]
            waldo_src_name = name_node.value
            unique_name = name_node.sliceAnnotationName

            # we go through a message sequence's non-argument
            # sequence local data variables.  (This includes the
            # return nodes.)  For each, we create and initialize a
            # variable.  

            # FIXME: we are declaring a Waldo variable and then
            # copying that entire varialbe declartion through
            # _context.convert_for_seq_local to be a peered variable.
            # It would be more efficient to just declare the initial
            # variable as peered and use that.
            
            statement_txt += emit_statement(
                sequence_local_decl_node,endpoint_name,ast_root,
                fdep_dict,emit_ctx)            
            statement_txt += '\n'
            statement_txt += (
                '''_context.sequence_local_store.add_var(
    "%s",_context.convert_for_seq_local(%s,_active_event,self._host_uuid))
''' % (unique_name, waldo_src_name))
    else:
        emit_utils.emit_warn(
            'Unknown label in emit statement ' + statement_node.label)
        
    return statement_txt


def _emit_return_statement(
    return_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    Return statements get emitted into the internal versions of public
    and private functions.  Each internal function has an argument,
    _returning_to_public_ext_array (@see
    emit_endpoints.emit_private_method_interface).  If the internal method 
    is not == None, it means that the internal method was directly called by 

    and anything that it returns will be passed directly back to
    non-Waldo code, so we must de-waldoify return values.
    Importantly, we should not de-waldo-ify externals.  Which values
    are externals should be the values in
    _returning_to_public_ext_array.
    
    '''
    # @see emit_statement._emit_second_level_assign.  Each item
    # returned should be the actual Waldo object.
    # emit_statement._emit_second_level_assign can sort out what
    # needs to be copied before being assigned and what needs to
    # maintain its reference (via external)
    ret_list_node = return_node.children[0]

    # create de_waldo_ified text
    de_waldoed_return_txt = _emit_de_waldoed_return(
        return_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    non_de_waldoed_return_txt = _emit_non_de_waldoed_return(
        return_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    # all returend objects are returned as tuples
    return_txt = '''
if _returning_to_public_ext_array != None:
    # must de-waldo-ify objects before passing back
    %s

# otherwise, use regular return mechanism... do not de-waldo-ify
%s
''' % (de_waldoed_return_txt,non_de_waldoed_return_txt)

    return return_txt
    

def _emit_non_de_waldoed_return(
    return_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    
    ret_list_node = return_node.children[0]
    return_txt = 'return _context.flatten_into_single_return_tuple('

    if len(ret_list_node.children) == 0:
        return_txt += 'None'

    for counter in range(0,len(ret_list_node.children)):
        ret_item_node = ret_list_node.children[counter]
        return_txt += emit_statement(
            ret_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        
        if counter != len(ret_list_node.children) -1:        
            return_txt += ','

    return_txt += ')\n'
    return return_txt


def _emit_de_waldoed_return(
    return_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    ret_list_node = return_node.children[0]    
    return_txt = 'return _context.flatten_into_single_return_tuple('

    if len(ret_list_node.children) == 0:
        return_txt += 'None'

    for counter in range(0,len(ret_list_node.children)):
        ret_item_node = ret_list_node.children[counter]

        # the actual emission of the return value
        item_emit = emit_statement(
            ret_item_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        # Example output of below: 
        # a if 1 in _returning_to_public_ext_array else _context.de_waldoify(a)
        #
        # Ie, output the reference to the piece of data if we are
        # supposed to return an external (index is in
        # _returning_to_public_ext_array).  Otherwise, output a
        # de_waldoified version of data.
        ret_item_txt = (
            '%s if %s in _returning_to_public_ext_array else %s' %
            (item_emit, str(counter), '_context.de_waldoify(' + item_emit +
             ',_active_event)'))
        
        return_txt += ret_item_txt
        
        if counter != len(ret_list_node.children) -1:
            return_txt += ','

    return_txt += ')\n'
    return return_txt



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
    elif emit_utils.is_func_obj_call(
        method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
        return emit_func_object_call(
            method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    # standard public/private call
    return _emit_public_private_method_call(
        method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx)


def emit_func_object_call(
    method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode} method_call_node --- 
    '''
    function_obj_node = method_call_node.children[0]

    # Lookup method name in endpoint builtins
    method_call_name = function_obj_node.value
    if ENDPOINT_BUILTIN_METHODS.get(method_call_name) != None:
        return ENDPOINT_BUILTIN_METHODS.get(method_call_name);

    function_obj_txt = emit_statement(
        function_obj_node,endpoint_name,ast_root,fdep_dict,emit_ctx)


    # contains the arguments passed into the function.
    func_call_arg_list_node = emit_utils.get_method_call_arg_list_node(
        method_call_node)

    # emit each argument separately, passing them in as arguments
    func_call_arg_list_txt_list = []
    for arg_node in func_call_arg_list_node.children:
        func_call_txt = emit_statement(
            arg_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        func_call_arg_list_txt_list.append(func_call_txt)

    func_call_arg_string = reduce (
        lambda x, y : x + ',' + y,
        func_call_arg_list_txt_list,'')


    func_call_txt = (
        '_context.call_func_obj(_active_event,%s%s)' %
        (function_obj_txt, func_call_arg_string))

    return func_call_txt
    

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
        # note: at point of function call, do not need to check
        # whether to pass internal vals (ie, get_val on Waldo
        # variable), because the first thing that the callee does is
        # go through all the arguments that it received and copy them
        # if they're non-external value types.
        method_call_txt += arg_txt + ','

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
    method_call_txt = _emit_public_private_method_call(
        msg_seq_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx,
        lib_util.partner_endpoint_msg_call_func_name)
    
    return (
        '(%s if _context.set_msg_send_initialized_bit_false() else None)' %
        method_call_txt)


def _emit_endpoint_method_call(
    endpoint_method_call_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    Calls into context's hide_endpoint_call, which listens for result
    on threadsafe queue after making the call.  If the queue results
    say that we should back out, then raise a BackoutException.
    ExecutingEvent code will catch it and forward the backout on.
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

    emitted_endpoint_name = emit_statement(
        endpoint_name_node, endpoint_name,ast_root,fdep_dict,emit_ctx)

    method_arg_str = ''
    arg_list_node = emit_utils.get_method_call_arg_list_node(
        endpoint_method_call_node)
    for arg_node in arg_list_node.children:
        method_arg_str += emit_statement(
            arg_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        method_arg_str += ','


    call_txt = (
        '_context.hide_endpoint_call(_active_event,_context,' +
        ('_context.get_val_if_waldo(%s,_active_event)' % emitted_endpoint_name) +
         ',"' + method_name + '",' + method_arg_str + ')'
        )

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
        to_assign_txt = emit_statement(
            rhs_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
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
    
    all_assignments_txt = ''
    for counter in range(0,len(comma_list_node.children)):
        lhs_node = comma_list_node.children[counter]

        rhs = '_tmp' + str(counter)

        if lhs_node.label == AST_BRACKET_STATEMENT:
            lhs_outside_node = lhs_node.children[0]
            lhs_inside_node = lhs_node.children[1]
            
            lhs_outside_txt = emit_statement(
                lhs_outside_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            lhs_inside_txt = emit_statement(
                lhs_inside_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
            
            all_assignments_txt += (
                '_context.assign_on_key(' + lhs_outside_txt + ',' +
                lhs_inside_txt + ',' + rhs + ', _active_event)\n')

        elif lhs_node.label == AST_DOT_STATEMENT:
            pre_dot_node = lhs_node.children[0]
            post_dot_node = lhs_node.children[1]
            
            pre_dot_node_txt = emit_statement(
                pre_dot_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

            #### DEBUG
            if post_dot_node.label != AST_IDENTIFIER:
                emit_utils.emit_assert(
                    'Expected identifier as second part of user ' +
                    'struct access.')
            #### END DEBUG
            post_dot_node_name = post_dot_node.value
            
            all_assignments_txt += (
                '_context.assign_on_key(' + pre_dot_node_txt + ',"' +
                post_dot_node_name + '",' + rhs + ', _active_event)\n')

        else:
            lhs_txt = emit_statement(
                lhs_node,endpoint_name, ast_root,fdep_dict,emit_ctx)

            # for variables that point to immediate values (ie, python
            # values), we will not be able to assign them through
            # _context.assign and _context.assign will return False.
            # In that case, we should assign into the variable
            # directly (the body of the if statement).  However, some
            # variables can only be accessed through a function call
            # to the variable store, which would produce code that
            # looks as follows:
            #
            # _context.global_var_store.get_var_if_exists('some_var') = 4
            #
            # The above code is a syntax error in python (can't assign
            # to function call).  And shouldn't be necessary anyways
            # (because the context_assign should have assigned into
            # it).  Avoid emitting that code by trying to evaluate it:
            # if catch syntax error, then know that context.assign
            # will do work anyways and just input pass.  Otherwise,
            # emit it.
            all_assignments_txt += (                
                'if not _context.assign(' + lhs_txt + ',' + rhs + ',_active_event):\n')
            inside_if_txt = lhs_txt + ' = ' + rhs + '\n'
            
            try:
                exec (inside_if_txt)
            except SyntaxError:
                inside_if_txt = 'pass\n'
            except:
                pass
            
            all_assignments_txt += emit_utils.indent_str(inside_if_txt,1)

            
    return all_assignments_txt
                    

def is_binary_operator_from_label(node_label):
    return node_label in get_binary_operator_label_dict()

def get_binary_operator_from_label(node_label):
    bin_op_dict =  get_binary_operator_label_dict()
    operator = bin_op_dict.get(node_label,None);
    if operator == None:
        emit_utils.emit_assert(
            'Requesting binary operator information for non-binary operator.')
    return operator


def get_binary_operator_label_dict():
    '''
    Helper function for _isBinaryOperatorLabel and
    _getBinaryOperatorFromLabel
    '''
    binary_operator_labels = {
        # arithmetic
        AST_PLUS: '+',
        AST_MINUS: '-',
        AST_DIVIDE: '/',
        AST_MULTIPLY: '*',

        # boolean
        AST_AND: 'and',
        AST_OR: 'or',
        
        # comparison
        AST_BOOL_EQUALS: '==',
        AST_BOOL_NOT_EQUALS: '!=',
        AST_GREATER_THAN: '>',
        AST_GREATER_THAN_EQ: '>=',
        AST_LESS_THAN: '<',
        AST_LESS_THAN_EQ: '<='
        }
    return binary_operator_labels



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


def emit_condition_statement(
    condition_statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @param {AstNode} statement_node --- Should be labeled with
    AST_CONDITION_STATEMENT
    '''

    #### DEBUG
    if condition_statement_node.label != AST_CONDITION_STATEMENT:
        emit_utils.emit_assert(
            'Incorrect node type in emit_condition_statement')
    #### END DEBUG

    if_statement_node = condition_statement_node.children[0]
    elif_statement_node = condition_statement_node.children[1]
    else_statement_node = condition_statement_node.children[2]

    
    ## IF statement
    if_cond_node = if_statement_node.children[0]
    if_body_node = if_statement_node.children[1]
    if_cond_txt = emit_statement(
        if_cond_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    if_body_txt = emit_statement(
        if_body_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    if_body_txt += '\npass\n'

    if_txt = 'if _context.get_val_if_waldo(%s,_active_event):\n' % if_cond_txt
    if_txt += emit_utils.indent_str(if_body_txt)
    if_txt += '\n'
    
    ## ELSE IF statement
    elif_txt = ''
    for single_elif_node in elif_statement_node.children:
        elif_cond_node = single_elif_node.children[0]
        elif_body_node = single_elif_node.children[1]

        elif_cond_txt = emit_statement(
            elif_cond_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        elif_body_txt = emit_statement(
            elif_body_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        elif_body_txt += '\npass\n'

        elif_txt += 'elif _context.get_val_if_waldo(%s,_active_event):\n' % elif_cond_txt
        elif_txt += emit_utils.indent_str(elif_body_txt)
        elif_txt += '\n'
    
    ## ELSE statement
    else_txt = ''
    if len(else_statement_node.children) != 0:
        else_txt += 'else:\n'
        else_body_node = else_statement_node.children[0]
        else_body_txt = emit_statement(
            else_body_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        else_body_txt += '\npass\n'
        else_txt += emit_utils.indent_str(else_body_txt)
        else_txt += '\n'

    return if_txt + elif_txt + else_txt

def emit_ext_assign(
    ext_assign_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    
    to_assign_to_node = ext_assign_node.children[1]
    to_assign_from_node = ext_assign_node.children[0]

    to_assign_from_node_txt = emit_statement(
        to_assign_from_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

    # FIXME: what about ext_assign into user struct?
    
    # need to be careful of function call assignment and need to be
    # careful of bracket assignment

    if to_assign_to_node.label == AST_BRACKET_STATEMENT:
        # must write value on key instead of just getting it
        outside_bracket_node = to_assign_to_node.children[0]
        inside_bracket_node = to_assign_to_node.children[1]

        outside_bracket_node_txt = emit_statement(
            outside_bracket_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        
        inside_bracket_node_txt = emit_statement(
            inside_bracket_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
        
        statement_txt = (
            outside_bracket_node_txt + '.get_val(_active_event)'
            '.write_val_on_key(_active_event,_context.get_val_if_waldo(%s,_active_event),%s)' %
            (inside_bracket_node_txt,to_assign_from_node_txt))

    elif emit_utils.is_method_call(to_assign_to_node):

        # emitting function call
        to_assign_to_txt = emit_statement(
            to_assign_to_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        # means that this must be a public/private method call or
        # endpoint call(if it were a message call, then we
        # wouldn't be able to write an external back)
        statement_txt = (
            to_assign_to_txt + '.write_val(_active_event,%s)' %
            to_assign_from_node_txt)
    else:

        # function call assignment
        to_assign_to_node_txt = emit_statement(
            to_assign_to_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        # from extAssign a to b, produces
        # b.write_val(_active_event, a.get_val(_active_event))
        # ie, take the internal val of a and put it in b.
        statement_txt = (
            to_assign_to_node_txt + ('.write_val(_active_event,%s.get_val(_active_event))' %
            to_assign_from_node_txt))

        
    return statement_txt

def struct_rhs_declaration(
    decl_node,host_uuid_var_name,peered,endpoint_name,ast_root,
    fdep_dict,emit_ctx,multithreaded):
    '''
    @param {bool} multithreaded --- True if the variable that we are
    going to create could be accessed by multiple threads (eg., is an
    endpoint variable or peered variable).  False otherwise.
    
    Used to emit the right hand side of a declaration of a struct
    type.  A struct type *must* have an initializer that populates the
    struct's fields with Waldo variables.

    For returns, @see non_struct_rhs_declaration
    
    '''

    if decl_node.label == AST_ANNOTATED_DECLARATION:
        var_name = emit_utils.get_var_name_from_annotated_decl(decl_node)
        var_type = emit_utils.get_var_type_dict_from_annotated_decl(decl_node)
        initializer_node = emit_utils.get_var_initializer_from_annotated_decl(decl_node)        
    else:
        var_name = emit_utils.get_var_name_from_decl(decl_node)
        var_type = emit_utils.get_var_type_dict_from_decl(decl_node)
        initializer_node = emit_utils.get_var_initializer_from_decl(decl_node)


    initializer_str = ''
    if initializer_node != None:
        initializer_str = emit_statement(
            initializer_node, endpoint_name,ast_root,fdep_dict,emit_ctx)

    struct_type_variable_txt = struct_type_emit_declaration(
        var_type,var_name,host_uuid_var_name,peered,endpoint_name,ast_root,
        fdep_dict,emit_ctx, initializer_str,multithreaded)
    
    return struct_type_variable_txt,var_name


def struct_type_emit_declaration(
    var_type,var_name,host_uuid_var_name,peered,endpoint_name,ast_root,
    fdep_dict,emit_ctx, initializer_str,multithreaded):
    '''
    @param {type dict} var_type --- Should be the type dict for a user
    struct.
    
    @param {String} var_name --- The name of the Waldo 

    @param {bool} multithreaded --- True if the variable that we are
    going to create could be accessed by multiple threads (eg., is an
    endpoint variable or peered variable).  False otherwise.
    
    @returns {String} --- The string for a WaldoUserStructVariable
    with initialization vector or with assignment to new value.
    '''
    #### DEBUG
    if not TypeCheck.templateUtil.is_struct(var_type):
        emit_utils.emit_assert(
            'Expected struct type dict for struct rhs declaration')
    #### END DEBUG

    if initializer_str != '':
        return initializer_str
        
    struct_fields_dict = TypeCheck.templateUtil.get_struct_fields_dict(
        var_type)

    init_val_dict_str = '{'
    for field_name in struct_fields_dict:
        field_type_dict = struct_fields_dict [field_name]

        if TypeCheck.templateUtil.is_struct(field_type_dict):
            field_var_decl = struct_type_emit_declaration(
                field_type_dict,field_name,host_uuid_var_name,peered,
                endpoint_name,ast_root,fdep_dict,emit_ctx)
            
        elif (emit_utils.is_reference_type_type_dict(field_type_dict) or
              TypeCheck.templateUtil.is_external(field_type_dict) or
              TypeCheck.templateUtil.is_basic_function_type(field_type_dict) or
              TypeCheck.templateUtil.is_endpoint(field_type_dict)):
            
            field_var_decl = non_struct_type_emit_declaration(
                field_type_dict,field_name,host_uuid_var_name,peered,
                endpoint_name,ast_root,fdep_dict,emit_ctx,'None',multithreaded)
        else:
            # means it is just a value type.  Load its default value
            field_var_decl = emit_utils.emit_value_type_default(field_type_dict)
            

        init_val_dict_str +=  '"' + field_name + '": '
        init_val_dict_str += field_var_decl + ', '

    init_val_dict_str += '}'
            
    peered_str = str(peered)

    waldo_type = emit_utils.library_transform('WaldoUserStructVariable')
    if multithreaded is False:
        waldo_type = emit_utils.library_transform('WaldoSingleThreadUserStructVariable')
    
    struct_waldo_var_txt = (
        waldo_type +
        '("%s",%s,%s,%s)' % (var_name,host_uuid_var_name,peered_str,init_val_dict_str))

    return struct_waldo_var_txt


def non_struct_rhs_declaration(
    decl_node,host_uuid_var_name,peered,endpoint_name,ast_root,
    fdep_dict,emit_ctx,multithreaded):
    '''
    @param {AstNode} decl_node --- Can either be labeled
    AST_ANNOTATED_DECLARATION or AST_DECLARATION.  Should not be the
    declaration of a struct.  Use struct_declaration function for
    that.

    @param {bool} multithreaded --- True if the variable that we are
    going to create could be accessed by multiple threads (eg., is an
    endpoint variable or peered variable).  False otherwise.
    
    @returns {2-tuple} (a,b)
    
       a {String} --- Emitted text for the creation of the Waldo
                      variable declared by decl_node.

       b {String} --- Name of the variable
    '''

    wvar_load_text = ''

    # check if annotated declaration or just declaration
    initializer_node = None
    if decl_node.label == AST_ANNOTATED_DECLARATION:
        id_node = decl_node.children[1]
        var_name = emit_utils.get_var_name_from_annotated_decl(decl_node)
        var_type = emit_utils.get_var_type_dict_from_annotated_decl(decl_node)
        initializer_node = emit_utils.get_var_initializer_from_annotated_decl(decl_node)
    elif decl_node.label == AST_DECLARATION:
        id_node = decl_node.children[0]
        var_name = emit_utils.get_var_name_from_decl(decl_node)
        var_type = emit_utils.get_var_type_dict_from_decl(decl_node)
        initializer_node = emit_utils.get_var_initializer_from_decl(decl_node)
    #### DEBUG
    else:
        emit_utils.emit_assert(
            'In create_wvariables_array, trying to create a ' +
            'var that is not a declaration.')
    #### END DEBUG

    # handle emitting the initialization node.  note, if no
    # initialization of node, then no value is supplied as last
    # arg when creating the variable.  This means that the
    # WaldoVariable will not be supplied an init_val argument and
    # can use its default initialized value.  (This only works for
    # non-struct declarations.  Structs require an initialization
    # argument for all their internal fields.)
    initializer_str = ''
    if initializer_node != None:
        emitted_init = emit_statement(
            initializer_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        # the actual initializer that will be used when creating variable.
        initializer_str = (
            '_context.get_val_if_waldo(%s,_active_event)' %
             emitted_init)

    wvar_load_txt = non_struct_type_emit_declaration(
        var_type,var_name,host_uuid_var_name,peered,
        endpoint_name,ast_root,fdep_dict,emit_ctx,
        initializer_str,multithreaded)
    
    return wvar_load_txt,var_name


def non_struct_type_emit_declaration(
    type_dict,var_name,host_uuid_var_name,peered,
    endpoint_name,ast_root,fdep_dict,emit_ctx,initializer_str,multithreaded):

    peered_str = 'True' if peered else 'False'
    
    variable_type_str,is_func = emit_utils.get_var_type_txt_from_type_dict(
        type_dict,multithreaded)

    wvar_load_text = '''%s(  # the type of waldo variable to create
    '%s', # variable's name
    %s, # host uuid var name
    %s,  # if peered, True, otherwise, False
    %s
)''' % (variable_type_str,var_name,host_uuid_var_name,
       peered_str, initializer_str)

    if is_func:
        ext_args_array_txt = emit_external_args_list_from_func_obj_type_dict(
            type_dict)
        wvar_load_text += '.set_external_args_array(%s)' % ext_args_array_txt
    
    return wvar_load_text

def emit_external_args_list_from_func_obj_type_dict(type_dict):
    '''
    @param {type dict} type_dict --- The type dictionary for a Waldo
    function object.
    
    @returns {String} --- Should be a string representation of a list.
    Each element of the list is a number.  If a number is in this
    list, then that means that the corresponding argument to func_obj
    is external and therefore should not be de_waldo-ified.  If an
    argument does not have its corresponding index in the array, then
    dewaldo-ify it.
    '''
    #### DEBUG
    if not TypeCheck.templateUtil.is_basic_function_type(type_dict):
        emit_util.emit_assert(
            'Expected function object type in ' +
            'emit_external_args_list_from_func_obj_type_dict')
    #### END DEBUG

    arg_type_dict_list = (
        TypeCheck.templateUtil.get_list_of_input_argument_type_dicts_for_func_object(type_dict))

    external_arg_list = []
    for arg_pos in range(0,len(arg_type_dict_list)):
        arg_type_dict = arg_type_dict_list[arg_pos]
        
        if TypeCheck.templateUtil.is_external(arg_type_dict):
            external_arg_list.append(arg_pos)
        
    return str(external_arg_list)



def emit_for(
    for_node,endpoint_name,ast_root,fdep_dict,emit_ctx):

    #### DEBUG
    if for_node.label != AST_FOR_STATEMENT:
        emit_utils.emit_assert(
            'emit_for expects a for node')
    #### END DEBUG

    if len(for_node.children) == 3:
        identifier_type_node_index = None
        identifier_node_index = 0
        to_iterate_node_index = 1
        for_body_node_index = 2

    elif len(for_node.children) == 4:
        identifier_type_node_index = 0

        identifier_node_index = 1
        to_iterate_node_index = 2
        for_body_node_index = 3


    for_txt = ''
    if identifier_type_node_index != None:
        # need to declare index variable before emitting the for loop
        # create a declaration node and then emit_statement
        decl_node = AstNode(AST_DECLARATION)
        decl_node.addChildren(
            [for_node.children[identifier_type_node_index],
             for_node.children[identifier_node_index]])
        
        iterator_decl_txt = emit_statement(
            decl_node,endpoint_name,ast_root,fdep_dict,emit_ctx)

        for_txt += iterator_decl_txt + '\n'
            
    identifier_node = for_node.children[identifier_node_index]
    to_iterate_node = for_node.children[to_iterate_node_index]
    for_body_node = for_node.children[for_body_node_index]

    # FIXME
    # challenge with for loops: we should use Waldo variables as
    # iterators.  Ie, for the statement:
    #     for (Number i in range(0,10))
    # i should be a WaldoNumberVariable.  But the only way to write
    # into a WaldoVariable is to call write_val on it.  Solution is to
    # create an intermediate Python variable that we use as the index.
    # Then, on the first line of the for loop body, we assign into the
    # Waldo variable (using the python variable) using write_val.  Ie,
    # the above would get translated to:
    #     i = WaldoNum(...)
    #     for _i in range(0,10):
    #         i.write_val(_i,_active_event)
    # The problem with this approach, and the reason for this FIXME is
    # that we need to be careful to select the intermediate Python
    # variable carefully to prevent collisions with other variables.
    # For instance, if a user had the following loop:
    #     for (Number context in range(0,10))
    # and we just used _context, we would have a collision.  For now,
    # just hoping to avoid collisions by picking something obscure.
    inter_iter_name = intermediate_python_name_from_identifier(identifier_node)

    to_iterate_txt = emit_statement(
        to_iterate_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    # actually emit text
    for_txt += (
        'for %s in _context.get_for_iter(%s,_active_event):\n' %
        (inter_iter_name,to_iterate_txt))

    iter_id_txt = emit_statement(
        identifier_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    
    for_body_txt = (
        '%s = _context.write_val(%s,%s,_active_event)\n' %
        (iter_id_txt, iter_id_txt, inter_iter_name))
    # for_body_txt += '.write_val(_active_event,%s)\n' % inter_iter_name

    for_body_txt += emit_statement(
        for_body_node,endpoint_name,ast_root,fdep_dict,emit_ctx)
    for_body_txt += '\npass\n'
    
    for_txt += emit_utils.indent_str(for_body_txt)
    return for_txt


def intermediate_python_name_from_identifier(identifier_node):
    '''
    @see FIXME in middle of emit_for.

    @returns {String}
    '''
    waldo_src_name = identifier_node.value
    return '_secret_waldo_for_iter____' + waldo_src_name
