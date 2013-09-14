import emit_utils

from waldo.parser.ast.astLabels import *

# so can get slicer code
from waldo.slice.slicer import slicer
from waldo.slice.typeStack import TypeStack

import uniform_header 
import emit_endpoints 


def astEmit(astRootNode):
    return ast_emit(astRootNode)

def ast_emit(ast_root_node):
    '''
    @pararm {AstNode} ast_root_node --- The root node of the ast that
    was generated from the source text after it has been type checked,
    but before it has been sliced.

    @param {EmitContext object} emit_context --- @see class EmitContext
    in emitUtils.py
    
    @returns {String or None} ---- String if succeeded, none if
    failed.
    '''
    waldo_name = ast_root_node.children[0].value
    
    emit_ctx = emit_utils.EmitContext()
    
    ####### slice the ast
    fdep_array = slicer(ast_root_node)

    fdep_dict = {};
    # convert the array of function dependencies to a dict
    for fdep in fdep_array:
        fdep_dict[fdep.funcName] = fdep

        
    ###### start emitting code

    # all Waldo files start the same way, regardless of contents
    returner = uniform_header.uniform_header()

    # now, encapsulate both emitted endpoints in a wrapping class
    returner += '''
public class %s
{

''' % waldo_name

    
    # now actually emit each endpoint object (including user-defined
    # functions specified in program source text).
    returner += emit_utils.indent_str(
        emit_endpoints.emit_endpoints(ast_root_node,fdep_dict,emit_ctx))

    returner += '\n\n}\n'
    
    return returner

