from parser.ast.astLabels import *
from slice.typeStack import TypeStack
import emit_utils

def emit_statement(
    statement_node,endpoint_name,ast_root,fdep_dict,emit_ctx):
    '''
    @returns {String}
    '''
    statement_txt = ''
    if statement_node.label == AST_IDENTIFIER:
        # FIXME: not handling dot statements for user structs here
        statement_txt = _emit_identifier(statement_node)

    elif statement_node.label == AST_FUNCTION_BODY_STATEMENT:
        for child_node in statement_node.children:
            statement_txt += emit_statement(
                child_node,endpoint_name,ast_root,fdep_dict,
                emit_ctx)
    
    else:
        emit_utils.emit_warn(
            'Unknown label in emit statement ' + statement_node.label)

    return statement_txt



def _emit_identifier(identifier_node):
    '''
    @param {AstNode} identifier_node --- corresponds to node labeled
    AST_IDENTIFIER
    '''
    #### DEBUG
    if identifier_node.label != AST_IDENTIFIER:
        emit_utils.emit_assert(
            'statemnt_node must be an identifier')
    #### END DEBUG
        
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
    elif idAnnotationType in [TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,
                              TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT]:
        identifier_txt = '_context.sequence_local_store.get_var_if_exists("%s")' %(
            id_annotation_name)
    #### DEBUG
    else:
        emit_utils.emit_assert(
            'Unknown annotation on identifier')
    #### END DEBUG
    return identifier_txt
