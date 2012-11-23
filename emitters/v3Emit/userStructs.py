#!/usr/bin/env python

import emitUtils 


def emit_user_structs(ast_root_node):
    '''
    Runs through all user-defined structs and outputs classes, which
    can be used to hold and write values
    
    @returns a string to be added to the emitted file
    '''

    struct_node = ast_root_node.children[7]

    returner = '\n'
    for single_struct_node in struct_node.children:
        returner += emit_single_struct(single_struct_node)

    returner += '\n'
    return returner


def emit_single_struct(single_struct_node):
    '''
    @param {AstNode} single_struct_node ---

    @returns {String} --- The class created from the single struct
    '''

    struct_name_node = single_struct_node.children[0]
    struct_name = struct_name_node.value
    struct_body_node = single_struct_node.children[1]
    
    class_header = 'class %s(object):\n' % struct_name

    init_header = 'def __init__(self):\n'
    
    
    init_body = ''
    for decl_node in struct_body_node.children:
        # decl_type_node = decl_node.children[0]
        identifier_node = decl_node.children[1]
        identifier_name = identifier_node.value
        
        init_body += 'self.%s = ' % identifier_name
        init_body += emitUtils.getDefaultValueFromDeclNode(decl_node)
        init_body += '\n\n'

    init_function = init_header + emitUtils.indentString(init_body,1)

    to_return = class_header + emitUtils.indentString(init_function,1)
    return '\n' + to_return + '\n'
