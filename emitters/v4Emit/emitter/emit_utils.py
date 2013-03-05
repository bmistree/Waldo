from parser.ast.astLabels import *

class EmitContext(object):
    pass


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
    print ('\n\nEmit error: ' + err_msg + '\n\n')
    assert(False)

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

    name_node = annotated_decl.children[2]
    #### DEBUG    
    if name_node.sliceAnnotationName == None:
        emit_assert(
            'Variable has not been annotated by slicer')
    #### END DEBUG
        
    return name_node.sliceAnnotationName

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
        
    type_node = annotated_decl.children[1]
    return type_node.type
    


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
            'get_var_type_dict_from_annotated_decl.')
    #### END DEBUG
        
    type_node = decl_node.children[0]
    return type_node.type
    
