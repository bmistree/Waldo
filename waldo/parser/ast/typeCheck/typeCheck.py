#!/usr/bin/env python

import sys, os


from waldo.parser.ast.astLabels import *;
from astTypeCheckStack import TypeCheckContextStack;
from astTypeCheckStack import FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH;
from astTypeCheckStack import FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_ERROR_TYPE_MISMATCH;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_ERROR_NAME_DOES_NOT_EXIST;
from astTypeCheckStack import MESSAGE_TYPE_CHECK_SUCCEED;
from astTypeCheckStack import createFuncMatchObjFromFuncTypeDict
from waldo.parser.ast.parserUtil import errPrint;

from typeCheckUtil import *
from templateUtil import *


def typeCheck(node,progText,typeStack=None,avoidFunctionObjects=False):
    '''
    avoidFunctionObjects {Bool} --- True if should add function
    objects to typestack context, false otherwise.
    '''
    #based on types of children, check my type.  Also, pass up
    #line numbers.


    ####### basic checks and creating new context #########
    if ((node.label != AST_ROOT) and (typeStack == None)):
        errPrint('\nBehram error.  Must have typeStack unless root node\n');
        assert(False);
    elif(node.label == AST_ROOT):
        typeStack = TypeCheckContextStack();
            
    if ((node.label == AST_ROOT) or
        (node.label == AST_SHARED_SECTION) or
        (node.label == AST_ENDPOINT_GLOBAL_SECTION) or
        (node.label == AST_ENDPOINT_FUNCTION_SECTION)):
        #each of these create new contexts.  don't forget to
        #remove several of them at the bottom of the function.
        #note: do not have ast_function_body here because need to
        #create a new context before get into function body so
        #that we can catch arguments passed into the function.
        typeStack.pushContext();


    ###### MASSIVE SWITCH STATEMENT TO TYPECHECK BASED ON NODE #######

    if node.label == AST_ROOT:
        #top of program

        typeStack.setRootNode(node);
        #getting protocol object name
        typeStack.protObjName = node.children[0].value;

        #handling alias section
        aliasSection = node.children[1];

        #endpoint 1 from alias section
        typeStack.endpoint1 = aliasSection.children[0].value; 
        typeStack.endpoint1LineNo = aliasSection.children[0].lineNo;
        typeStack.endpoint1Ast = aliasSection.children[0];

        #endpoint 2 from alias section
        typeStack.endpoint2 = aliasSection.children[1].value; 
        typeStack.endpoint2LineNo = aliasSection.children[1].lineNo;
        typeStack.endpoint2Ast = aliasSection.children[1];             
        
        if typeStack.endpoint1 == typeStack.endpoint2:
            errorFunction('Cannot use same names for endpoints',
                          [typeStack.endpoint1,typeStack.endpoint2],
                          [typeStack.endpoint1LineNo,typeStack.endpoint2LineNo],
                          progText);

        # check the structs section, loading each type into user type
        # dict
        struct_section_node = node.children[7]
        struct_section_node.typeCheck(progText,typeStack,avoidFunctionObjects)


            
        # #Do first level of type chcecking trace items.  see notes in
        # #corresponding elif of AST_TRACE_SECTION
        # corresponds to
        # the node with label AST_TRACE_SECTION: this is the node
        # with the high-level specification for all message sequences.
        sequencesSectionNode = node.children[2];
        sequencesSectionNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        sharedSectionNode = node.children[3];
        endpoint1Node = node.children[4];
        endpoint2Node = node.children[5];

        # msgSequencesNode has label
        # AST_MESSAGE_SEQUENCE_SECTION... ie, it's the node that
        # contains all of the program text for each message sequence.
        # (sequencesSectionNode above in contrast contains just the
        # high-level specification of which parts of a sequence
        # connect to which other parts.)
        msgSequencesNode = node.children[6];
        
        #get into shared section
        #note: shared section should leave its context on the stack so
        #that can access all variables directly from it.
        sharedSectionNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        # checking the globals of all message sequences to ensure that
        # they do not rely on any information besides just the
        # globally shared variables.
        typeCheckMessageSequencesGlobals(msgSequencesNode,progText,typeStack);
        
        #check one endpoint
        endpoint1Node.typeCheck(progText,typeStack,avoidFunctionObjects);
        #check other endpoint
        endpoint2Node.typeCheck(progText,typeStack,avoidFunctionObjects);

        
        # check if there were elements of the message sequences that
        # weren't actually defined in a sequences section.
        traceError = typeStack.checkUndefinedTraceItems();
        if (traceError != None):
            errorFunction(traceError.errMsg,traceError.nodes,
                          traceError.lineNos,progText);

        # now check if have more than one sequence line with the same
        # name
        traceError = typeStack.checkRepeatedSequenceLine();
        if traceError != None:
            errorFunction(traceError.errMsg,traceError.nodes,
                          traceError.lineNos,progText);

    elif node.label == AST_STRUCT_SECTION:
        # for each struct declared, create a type out of it and add
        # that type to the type stack by calling type check on the
        # declared struct.

        for struct_decl_node in node.children:
            struct_decl_node.typeCheck(progText,typeStack,avoidFunctionObjects)

    elif node.label == AST_STRUCT_DECLARATION:

        struct_name_node = node.children[0]
        struct_name = struct_name_node.value
        struct_body = node.children[1]

        # pre-load a dummy version of 
        dummy_struct_type = create_self_struct_type(struct_name)
        err_msg = typeStack.add_struct_type(struct_name,dummy_struct_type)
        if err_msg != None:
            # means that there was some error adding the struct type
            # to type stack.  (Likely, we already declared a struct of
            # that type.)
            errorFunction(err_msg,[node],[node.lineNo],progText)

        # adding a context onto type stack so that the fields that we
        # type check don't get actually added to type stack context
        typeStack.pushContext()

        # each element is a tuple.  the first element is a string ---
        # the name of the field.  the second element is the type dict
        # for that field
        field_tuple_array = []

        for field_decl_node in struct_body.children:
            field_decl_node.typeCheck(progText,typeStack,avoidFunctionObjects)
            field_decl_type_node = field_decl_node.children[0]
            field_identifier_node = field_decl_node.children[1]
            field_name = field_identifier_node.value

            # disallow
            # Struct SomeStruct
            # {
            #     Number num;
            #     Struct SomeStruct other;
            # }
            #
            # This is because will get infinite recursion when laying
            # out the memory for SomeStruct.  Explicitly check that no
            # field has self type.
            # 
            # Note: it's okay if a subfield of it has self type, eg.,
            # have a List(element: Struct SomeStruct).  Because will
            # only assign additional structs when add elements to it.
            if is_self_struct_type(field_decl_node.type):
                err_msg = (
                'Error.  You cannot have a member of a struct have the ' +
                'same type as that struct.  Note that you can have a field ' +
                'that is a List (or Map) with elements (or values) ' +
                'that point to the same struct if nesting is necessary.')
                
                errorFunction(
                    err_msg,[field_decl_node],[field_decl_node.lineNo],progText)

            
            # not calling type check directly on field_decl_node
            # because we do not want to insert it directly into
            field_tuple_array.append(
                (field_name,field_decl_node.type))

        # remove the fields that we just added to the context
        typeStack.popContext()


        node.type = create_struct_type(struct_name,field_tuple_array)
        dummy_err_msg = typeStack.add_struct_type(struct_name,node.type)
        # expected that we should have an err_msg because already have
        # an entry for the struct type in the type dict that we put in
        # before type checking the struct body (so that the struct
        # body could reference the struct type within it). do nothing
        # as a result of the error.


    elif node.label == AST_SIGNAL_CALL:
        signal_args_node = node.children[0]
        func_arglist_node = signal_args_node.children[0]

        # FIXME: add better type checking for signalling
        
        for func_arg_node in func_arglist_node.children:
            un_function_called_arg_node_type = unwrap_function_call_type_checker(
                func_arg_node.type,func_arg_node,
                ('Error in signal: function call assigning to' +
                'returns more than one value.'),
                progText)

            
    elif node.label == AST_EXT_COPY:
        from_node = node.children[0]
        to_node = node.children[1]
        
        from_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        to_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        
        # if to_node.label != AST_IDENTIFIER:
        #     err_msg = 'You are trying to perform an external copy '
        #     err_msg += 'to an invalid element.  You can only copy '
        #     err_msg += 'to an external identifier.'
        #     errorFunction(err_msg,[to_node],[to_node.lineNo],progText)
        #     return


        un_function_called_to_node_type = unwrap_function_call_type_checker(
            to_node.type,to_node,
            ('Error in extAssign: function call assigning to' +
            'returns more than one value.'),
            progText)

        if not is_external(un_function_called_to_node_type):
            err_msg = 'You are trying to extCopy to a non-external.'
            errorFunction(err_msg,[to_node],[to_node.lineNo],progText)
            return
            
        if checkTypeMismatch(
            to_node,to_node.type,from_node.type,typeStack,progText):

            err_msg = 'Error in copying value to external.  External '
            err_msg += 'has type ' + dict_type_to_str(to_node.type)
            err_msg += ', but copied value '
            err_msg += 'has type ' + dict_type_to_str(from_node.type) +'.'

            err_nodes = [to_node,from_node]
            err_line_nos = [x.lineNo for x in err_nodes]
            errorFunction(err_msg,err_nodes,err_line_nos,progText)
            return

    elif node.label == AST_SELF:
        node.type = generate_type_as_dict(TYPE_ENDPOINT, False)
        
    elif ((node.label == AST_BREAK) or
          (node.label == AST_CONTINUE)):
        node.type = generate_type_as_dict(TYPE_NOTHING,False)
        
    elif node.label == AST_WHILE_STATEMENT:
        bool_cond = node.children[0]
        body = node.children[1]

        bool_cond.typeCheck(progText,typeStack,avoidFunctionObjects)

        un_function_called_type = unwrap_function_call_type_checker(
            bool_cond.type,node,
            ('Error in predicate of while loop: function call ' +
            'returns more than one value.'),
            progText)

        if not is_true_false(un_function_called_type):
            err_msg = 'Error in predicate of while loop.  Should have '
            err_msg += 'TrueFalse type.  Instead, has type '
            err_msg += dict_type_to_str( bool_cond.type )
            err_msg += '.'
            err_nodes = [bool_cond]
            err_line_nos = [bool_cond.lineNo]
            errorFunction(err_msg,err_nodes,err_line_nos,progText)
            return
        
        body.typeCheck(progText,typeStack,avoidFunctionObjects)
        

    # FIXME: hae disabled tuple assignment with extAssign and extCopy
    # elif node.label in [AST_EXT_ASSIGN_FOR_TUPLE, AST_EXT_COPY_FOR_TUPLE]:

    #     # used for error message printing
    #     for_tuple_type = 'extAssign'
    #     if node.label == AST_EXT_COPY_FOR_TUPLE:
    #         for_tuple_type = 'extCopy'
        
    #     if not typeStack.in_lhs_assign:
    #         err_msg = 'Error in call "' + for_tuple_type + ' _ to ..."  '
    #         err_msg += 'You can only use a placeholder, "_", '
    #         err_msg += 'when this expression is on the '
    #         err_msg += 'left hand side of an assignment.  Ie, '
    #         err_msg += for_tuple_type
    #         err_msg += ' _ to some_ext = some_func(); is '
    #         err_msg += 'fine.  But ' + for_tuple_type + ' _ to some_ext; '
    #         err_msg += 'by itself is not.'
    #         err_nodes = [node]
    #         err_line_nos = [node.lineNo]
    #         errorFunction(err_msg,err_nodes,err_line_nos)
    #         return

    #     to_node = node.children[0]
    #     to_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        
    #     if not is_external(to_node.type):
    #         err_msg = 'Error in call "' + dict_type_to_str(for_tuple_type)
    #         err_msg += ' _ to ..." '
    #         err_msg += 'What you are assigning to is not an '
    #         err_msg += 'external.  If it is not supposed to be, '
    #         err_msg += 'then, just use the variable instead.'
    #         err_nodes = [node]
    #         err_line_nos = [node.lineNo]
    #         errorFunction(err_msg,err_nodes,err_line_nos)

    #     # need to bubble up type information to ensure that when type
    #     # check assign, can also type check here.
    #     node.type = to_node.type

        
    elif node.label == AST_EXT_ASSIGN:
        from_node = node.children[0]
        to_node = node.children[1]

        from_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        to_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        
        un_function_called_to_node_type = unwrap_function_call_type_checker(
            to_node.type,to_node,
            ('Error in extAssign: function call assigning to' +
            'returns more than one value.'),
            progText)

        un_function_called_from_node_type = unwrap_function_call_type_checker(
            to_node.type,to_node,
            ('Error in extAssign: function call assigning from' +
            'returns more than one value.'),
            progText)

        
        if not is_external(un_function_called_to_node_type):
            err_msg = 'You are trying to assign to a non-external.'
            errorFunction(err_msg,[to_node],[to_node.lineNo],progText)
            return

        if not is_external(un_function_called_from_node_type):
            err_msg = 'Error in external assign.  Must assign from an '
            err_msg += 'external to another external.  What you are trying '
            err_msg += 'to assign from is not external.'
            errorFunction(err_msg,[from_node],[from_node.lineNo],progText)
            return
        
        if checkTypeMismatch(
            to_node,to_node.type,from_node.type,typeStack,progText):

            err_msg = 'Error in assigning value to external.  External '
            err_msg += 'has type ' + dict_type_to_str(to_node.type)
            err_msg += ', but copied value '
            err_msg += 'has type ' + dict_type_to_str(from_node.type) +'.'

            err_nodes = [to_node,from_node]
            err_line_nos = [x.lineNo for x in err_nodes]
            errorFunction(err_msg,err_nodes,err_line_nos,progText)
            return

    elif node.label == AST_REMOVE_STATEMENT:
        to_remove_from_node = node.children[0]
        to_remove_index = node.children[1]

        to_remove_from_node.typeCheck(
            progText,typeStack,avoidFunctionObjects)

        to_remove_index.typeCheck(
            progText,typeStack,avoidFunctionObjects)

        # do not get anything back when remove the element
        node.type = generate_type_as_dict(TYPE_NOTHING,False)


        un_function_called_rm_from_type = unwrap_function_call_type_checker(
            to_remove_from_node.type,node,
            ('Error in specifying what to remove from: function call ' +
            'returns more than one value.'),
            progText)

        un_function_called_rm_ind_type = unwrap_function_call_type_checker(
            to_remove_index.type,node,
            ('Error in specifying which index to remove: function call ' +
            'returns more than one value.'),
            progText)
        

        # most of the type checking is on the indices to ensure that
        # they remove the same type 
        if isMapType(un_function_called_rm_from_type):
            if is_empty_map(un_function_called_rm_from_type):
                err_msg = 'Error in remove statement.  Cannot '
                err_msg += 'call remove directly on an empty map.'
                errorFunction(
                    err_msg,[to_remove_from_node],[to_remove_from_node.lineNo],
                    progText)

            map_index_type = getMapIndexType(un_function_called_rm_from_type)
            if map_index_type != un_function_called_rm_ind_type:
                err_msg = 'Error in remove statement.  Map\'s indices '
                err_msg += 'have type ' + dict_type_to_str(map_index_type) + ', but '
                err_msg += 'you are asking to remove an index that has '
                err_msg += 'type ' + dict_type_to_str(to_remove_index.type) + '.'
                
                errorFunction(
                    err_msg,[to_remove_from_node],[to_remove_from_node.lineNo],
                    progText)
                    
        elif isListType(un_function_called_rm_from_type):

            if not is_number(un_function_called_rm_ind_type):
                err_msg = 'Error in remove statement.  To remove from List'
                err_msg += ', you must pass a Number to '
                err_msg += 'remove.  You passed a ' + dict_type_to_str(to_remove_index.type)
                err_msg += '.'
                errorFunction(
                    err_msg,[to_remove_from_node],[to_remove_from_node.lineNo],
                    progText)

        else:
            err_msg = 'Error in remove statement.  Item '
            err_msg += 'calling remove on must be a Map or '
            err_msg += 'a List.  The inferred '
            err_msg += 'type is instead ' + to_remove_from_node.type
            err_msg += '.'
            
            errorFunction(
                err_msg,[to_remove_from_node],[to_remove_from_node.lineNo],
                progText)
        
        
    elif node.label == AST_FOR_STATEMENT:

        currentLineNo = node.children[0].lineNo;
        
        if len(node.children) == 3:
            identifierNodeIndex = 0;
            toIterateNodeIndex = 1;
            forBodyNodeIndex = 2;
        
        elif len(node.children) == 4:
            identifierTypeNodeIndex = 0;
            identifierNodeIndex = 1;
            toIterateNodeIndex = 2;
            forBodyNodeIndex = 3;

            typeNode = node.children[identifierTypeNodeIndex];
            typeNode.typeCheck(progText,typeStack,avoidFunctionObjects);
            declaredIdType = typeNode.type;
            node.type = generate_type_as_dict(TYPE_NOTHING,False)

            identifierNode = node.children[identifierNodeIndex];
            identifierName = identifierNode.value;
            existsAlready = typeStack.getIdentifierElement(identifierName);
            if (existsAlready != None):
                errorFunction('Already have an identifier named ' + identifierName,
                              [node],[currentLineNo, existsAlready.lineNo],progText);

            else:
                idType = typeStack.getFuncIdentifierType(identifierName);
                if (idType):
                    errText = 'Already have a function named ' + identifierName;
                    errText += '.  Therefore, cannot name an identifier with this name.';
                    errorFunction(errText,
                                  [node,existsAlready.astNode],
                                  [currentLineNo,existsAlready.lineNo],
                                  progText);

            # actually add the variable to type stack
            typeStack.addIdentifier(identifierName,
                                    declaredIdType,
                                    None,identifierNode,currentLineNo);
            

        else:
            errMsg = '\nBehram error: incorrect number of ast tokens ';
            errMsg += 'when type checking for statement.\n';
            print(errMsg);
            assert(False);

        identifierNode = node.children[identifierNodeIndex];
        identifierName = identifierNode.value;
        identifierNode.typeCheck(progText,typeStack,avoidFunctionObjects);
        toIterateNode = node.children[toIterateNodeIndex];
        toIterateNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_called_to_iter_type = unwrap_function_call_type_checker(
            toIterateNode.type,node,
            ('Error in specifying iterator: function call ' +
            'returns more than one value.'),
            progText)

        un_function_called_id_type = unwrap_function_call_type_checker(
            identifierNode.type,node,
            ('Error in specifying what to iterate over: function call ' +
            'returns more than one value.'),
            progText)

        if isMapType(un_function_called_to_iter_type):
            if is_empty_map(un_function_called_to_iter_type):
                pass;
            else:
                indexType = getMapIndexType(un_function_called_to_iter_type);
                
                if checkTypeMismatch(
                    identifierNode,un_function_called_id_type,indexType,typeStack,progText):
                    errMsg = 'Error assigning identifier in for loop.  ';
                    errMsg += identifierName + ' has type '
                    errMsg += dict_type_to_str(identifierNode.type)
                    errMsg += ', but map has keys with type '
                    errMsg += dict_type_to_str(indexType) + '.';
                    errorFunction(errMsg,[identifierNode],[identifierNode.lineNo],progText);

        elif isListType(un_function_called_to_iter_type):
            if is_empty_list(un_function_called_to_iter_type):
                pass;
            else:
                elementValueType = getListValueType(un_function_called_to_iter_type)

                if checkTypeMismatch(
                    identifierNode,un_function_called_id_type,elementValueType,
                    typeStack,progText):
                    errMsg = 'Error assigning identifier in for loop.  ';
                    errMsg += identifierName + ' has type ' 
                    errMsg += dict_type_to_str(identifierNode.type)
                    errMsg += ', but list has elements with type '
                    errMsg += dict_type_to_str(elementValueType) + '.';
                    errorFunction(errMsg,[identifierNode],[identifierNode.lineNo],progText);

        elif un_function_called_to_iter_type == AST_STRING:
            if un_function_called_to_iter_type == AST_STRING:
                pass;
            else:
                errMsg = 'Error assigning identifier in for loop.  ';
                errMsg += identiferName + ' has type '
                errMsg += dict_type_to_str(identifierNode.type)
                errMsg += ', but you are trying to iterate over Text, so it should ';
                errMsg += 'have type text.';
                errorFunction(errMsg,[identifierNode],[identifierNode.lineNo],progText);
        else:
            errMsg = 'Error in for loop in statement.  Right hand side of in statement ';
            errMsg += 'must be a map, list, or Text.  You provided a '
            errMsg += dict_type_to_str(toIterateNode.type)
            errMsg += '.';
            errorFunction(errMsg,[toIterateNode],[toIterateNode.lineNo],progText);
                    
        # no type error in for condition statement
        # now check the body of the for loop
        forBodyNode = node.children[forBodyNodeIndex];
        forBodyNode.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif node.label == AST_INSERT_STATEMENT:
        to_insert_into_node = node.children[0]
        index_to_insert_node = node.children[1]
        what_to_insert_node = node.children[2]

        to_insert_into_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        index_to_insert_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        what_to_insert_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        
        
        un_function_called_to_insert_into_type = unwrap_function_call_type_checker(
            to_insert_into_node.type,node,
            ('Error in insert on what inserting into: function call ' +
            'returns more than one value.'),
            progText)

        un_function_called_index_to_insert_type = unwrap_function_call_type_checker(
            index_to_insert_node.type,node,
            ('Error in insert on index to insert into: function call ' +
            'returns more than one value.'),
            progText)

        un_function_called_what_to_insert_type = unwrap_function_call_type_checker(
            what_to_insert_node.type,node,
            ('Error in insert on what to insert: function call ' +
            'returns more than one value.'),
            progText)

        if not is_number(un_function_called_index_to_insert_type):
            err_msg = 'Error when inserting.  Index inserting into '
            err_msg += 'must be a Number.  Instead, you provided an '
            err_msg += 'index with type '
            err_msg += dict_type_to_str(un_function_called_index_to_insert_type)
            errorFunction(
                err_msg, [index_to_insert_node],[index_to_insert_node.lineNo],
                progText)

        if not isListType(un_function_called_to_insert_into_type):
            errMsg = 'Error insert operation is only supported on lists.  ';
            errMsg += 'You are calling append on '
            errMsg += dict_type_to_str(un_function_called_to_insert_into_type) + '.';
            errorFunction(
                errMsg,[to_insert_into_node],[to_insert_into_node.lineNo],
                progText)
        if is_empty_list(un_function_called_to_insert_into_type):
            if is_wildcard_type(un_function_called_to_insert_into_type):
                # FIXME: cannot determine what to do for the case
                # where we're appending a wild card to an empty list.
                warn_msg = '\nBehram error: for a list, inserted a wildcard.\n'
                print (warn_msg)
            node.type = buildListTypeSignatureFromTypeName(
                un_function_called_to_insert_into_type,False)

        else:
            node.type = un_function_called_to_insert_into_type
            # check that the elements of the list match what we're appending
            listElemType = getListValueType(un_function_called_to_insert_into_type)
            if checkTypeMismatch(
                to_insert_into_node, listElemType,what_to_insert_node.type,
                typeStack, progText):

                errMsg = 'Type mismatch when trying to insert into element.  List ';
                errMsg += 'inserting into has type '
                errMsg += dict_type_to_str(to_insert_into_node.type) + ', and ';
                errMsg += 'therefore you must insert an element with type ';
                errMsg += dict_type_to_str(listElemType) + '.  Instead, '
                errMsg += 'you inserted an element with ';
                errMsg += 'type ' + dict_type_to_str(what_to_insert_node.type) + '.';
                errorFunction(
                    errMsg, [to_insert_into_node],[to_insert_into_node.lineNo],
                    progText)
        

    elif node.label == AST_APPEND_STATEMENT:
        toAppendToNode = node.children[0];
        toAppendNode = node.children[1];

        toAppendToNode.typeCheck(progText,typeStack,avoidFunctionObjects);
        toAppendNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_called_to_ap_to_type = unwrap_function_call_type_checker(
            toAppendToNode.type,node,
            ('Error in append on what appending to side: function call ' +
            'returns more than one value.'),
            progText)

        un_function_called_to_ap_type = unwrap_function_call_type_checker(
            toAppendNode.type,node,
            ('Error in append on what appending: function call ' +
            'returns more than one value.'),
            progText)
        

        if not isListType(un_function_called_to_ap_to_type):
            errMsg = 'Error append operation is only supported on lists.  ';
            errMsg += 'You are calling append on '
            errMsg += dict_type_to_str(toAppendToNode.type) + '.';
            errorFunction(
                errMsg,[toAppendToNode],[toAppendToNode.lineNo],
                progText)
        if is_empty_list(un_function_called_to_ap_to_type):
            if is_wildcard_type(un_function_called_to_ap_to_type):
                # FIXME: cannot determine what to do for the case
                # where we're appending a wild card to an empty list.
                warn_msg = '\nBehram error: for a list, appended a wildcard.\n'
                print (warn_msg)
            node.type = buildListTypeSignatureFromTypeName(un_function_called_to_ap_to_type,False)

        else:
            node.type = un_function_called_to_ap_to_type
            # check that the elements of the list match what we're appending
            listElemType = getListValueType(un_function_called_to_ap_to_type)
            if checkTypeMismatch(
                toAppendToNode,listElemType,toAppendNode.type,
                typeStack,progText):
                errMsg = 'Type mismatch when trying to append element.  List ';
                errMsg += 'appending to has type '
                errMsg += dict_type_to_str(toAppendToNode.type) + ', and ';
                errMsg += 'therefore you must append an element with type ';
                errMsg += dict_type_to_str(listElemType) + '.  Instead, '
                errMsg += 'you appended an element with ';
                errMsg += 'type ' + dict_type_to_str(toAppendNode.type) + '.';
                errorFunction(errMsg, [toAppendToNode],[toAppendToNode.lineNo],
                              progText);
        
    elif node.label == AST_IN_STATEMENT:
        node.type = generate_type_as_dict(TYPE_BOOL,False)
        lhsNode = node.children[0];
        rhsNode = node.children[1];

        lhsNode.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhsNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_called_lhs_type = unwrap_function_call_type_checker(
            lhsNode.type,node,
            ('Error in in statement: function call ' +
            'returns more than one value on left-hand-side.'),
            progText)
        
        un_function_called_rhs_type = unwrap_function_call_type_checker(
            rhsNode.type,node,
            ('Error in in statement: function call ' +
            'returns more than one value on right-hand-side.'),
            progText)

        if is_text(un_function_called_rhs_type):
            if not is_text(un_function_called_lhs_type):
                errMsg = 'Error with in statement.  Right-hand side of in ';
                errMsg += 'statement has type Text, left-hand side should ';
                errMsg += 'also be of type Text.  However, it is actually ';
                errMsg += 'of type ' + dict_type_to_str(lhsNode.type)
                errorFunction(errMsg,[lhsNode],[lhsNode.lineNo],progText);
        elif isMapType(un_function_called_rhs_type):
            if is_empty_map(un_function_called_rhs_type):
                pass;
            else:
                mapIndexType = getMapIndexType(un_function_called_rhs_type)
                if mapIndexType != un_function_called_lhs_type:
                    errMsg = 'Error with in statement.  Right-hand side of ';
                    errMsg += 'statement is a map type with indices ';
                    errMsg += dict_type_to_str(mapIndexType) + '.  The '
                    errMsg += 'left-hand side of the in ';
                    errMsg += 'statement should have same type.  Instead, it ';
                    errMsg += 'has type ' + dict_type_to_str(lhsNode.type) + '.';
                    errorFunction(errMsg, [lhsNode],[lhsNode.lineNo],progText);
        elif isListType(un_function_called_rhs_type):
            if is_empty_list(un_function_called_rhs_type):
                pass;
            else:
                listElementType = getListValueType(un_function_called_rhs_type)
                if listElementType != un_function_called_lhs_type:
                    errMsg = 'Error with in statement.  Right-hand side of ';
                    errMsg += 'statement is a list type with indices ';
                    errMsg += dict_type_to_str(listElementType) + '.  '
                    errMsg += 'The left-hand side of the in ';
                    errMsg += 'statement should have same type.  Instead, it ';
                    errMsg += 'has type ' + dict_type_to_str(lhsNode.type) + '.';
                    errorFunction(errMsg, [lhsNode],[lhsNode.lineNo],progText);
        else:
            errMsg = 'Error with in statement.  Right-hand side of statement ';
            errMsg += 'must have type List, Map, or Text.  Instead, it has type ';
            errMsg += dict_type_to_str(rhsNode.type) + '.';
            errorFunction(errMsg,[lhsNode],[lhsNode.lineNo],progText);
            
    elif (node.label == AST_JUMP_COMPLETE) or (node.label == AST_JUMP):

        node.type = generate_type_as_dict(TYPE_NOTHING,False)
        if ((not typeStack.inSequencesSection) or
            typeStack.inOnComplete):
            errMsg = 'Error.  You can only issue a jump statement ';
            errMsg += 'or finish directly from a message sequence ';
            errMsg += '(and you cannot jump or finish ';
            errMsg += 'from within an oncomplete statement).'
            errorFunction(errMsg,[node],[node.lineNo],progText);

        
        if node.label == AST_JUMP:
            # additionally checking that jumping to a valid point for
            # jumps.
            endpointNameNode = node.children[0];
            endpointName = endpointNameNode.value;
            traceLineNode = node.children[1];
            traceFunctionName = traceLineNode.value;

            if ((endpointName != typeStack.endpoint1) and
                (endpointName != typeStack.endpoint2)):
                errMsg = "Error.  You are not jumping to a valid endpoint ";
                errMsg += 'sequence function.  Did you misspell the endpoint name?';
                errorFunction(errMsg,[endpointNameNode],[endpointNameNode.lineNo],progText);
                
            # ensure that jumps to a valid position
            found = False;
            for nameTuple in typeStack.sequenceSectionNameTuples:
                seqEndpointName = nameTuple[0];
                seqFunctionName = nameTuple[1];

                if ((seqEndpointName == endpointName) and
                    (traceFunctionName == seqFunctionName)):
                    found = True;
            if not found:
                errMsg = 'Error.  You requested jumping to an invalid ';
                errMsg += 'function name.  You asked to jump to function ';
                errMsg += 'with endpoint "' + endpointName + '" and function ';
                errMsg += 'name "' + traceFunctionName + '."  But there is no such ';
                errMsg += 'function in this sequence.\n';
                errorFunction(errMsg,[node],[node.lineNo],progText);
                
    elif node.label == AST_NOT_EXPRESSION:
        childNode = node.children[0];
        childNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_called_child_type = unwrap_function_call_type_checker(
            childNode.type,node,
            ('Error in not statement: function call ' +
            'returns more than one value, so unsure what to "not".'),
            progText)

        node.lineNo = childNode.lineNo;
        if not is_true_false(un_function_called_child_type):
            typeErrorMsg = 'Error in not expession.  You can only ';
            typeErrorMsg += 'apply not to a TrueFalse.';
            astLineNos = [node.lineNo];
            errorFunction(typeErrorMsg,[childNode],astLineNos,progText);

        node.type = generate_type_as_dict(TYPE_BOOL,False)
        
    elif node.label == AST_TRACE_SECTION:
        '''
        All the type rules of an ast trace section are:
          Check:
            1) Trace line alternates between one side and other

            2) All functions in trace line exist

            3) There are no msgSend/msgReceive functions that are not
               in a traceline

            4) Each traceline begins with a msgSend

            5) Middles and ends of each traceline are msgReceives

            6) No two tracelines begin with the same msgSend

            7) Each trace item begins with a valid endpoint name.

         At this level of type checking, we only handle #1 and #7.
         Type checking in rest of body takes care of #3, #4, #5, and  #6.

         After type checking rest of body, then return check #2 by
         calling typeStack.checkUndefinedTraceItems in type check of astRoot.
        '''
        typeStack.setAstTraceSectionNode(node);

        # skip the first child, which is a name for the 
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif node.label == AST_BRACKET_STATEMENT:
        toReadFrom = node.children[0];
        index = node.children[1];
        toReadFrom.typeCheck(progText,typeStack,avoidFunctionObjects);
        index.typeCheck(progText,typeStack,avoidFunctionObjects);

        node.lineNo = index.lineNo;

        un_function_to_read_from_type = unwrap_function_call_type_checker(
            toReadFrom.type,node,
            ('Error in bracket statement: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use to index into bracket.'),
            progText)
        un_function_index_type = unwrap_function_call_type_checker(
            index.type,node,
            ('Error in bracket statement: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for index into bracket.'),
            progText)

        
        if isMapType(un_function_to_read_from_type):
            typeError,statementType,typeErrorMsg,typeErrorNodes = typeCheckMapBracket(
                toReadFrom,index,typeStack,progText)
            
        elif isListType(un_function_to_read_from_type):
            typeError,statementType,typeErrorMsg,typeErrorNodes = typeCheckListBracket(
                toReadFrom,index,typeStack,progText)
            
        elif is_text(un_function_to_read_from_type):
            typeError = False
            if not is_number(un_function_index_type):
                typeError = True
                typeErrorMsg = 'Error when reading a single character from a Text.  You '
                typeErrorMsg += 'must use a number to index into the Text object.'
                typeErrorNodes = [index]

            statementType = un_function_to_read_from_type
        else:
            typeError = True;
            typeErrorMsg = 'You can only index into a map type, list type, or Text type.  ';
            typeErrorMsg += 'Instead, you are trying to index into a [ ';
            typeErrorMsg += dict_type_to_str(toReadFrom.type) + ' ].\n';
            typeErrorNodes = [toReadFrom];

            
        if typeError:
            node.type = generate_type_as_dict(TYPE_NOTHING,False)
            for node in typeErrorNodes:
                astLineNos = [node.lineNo];
                errorFunction(typeErrorMsg,typeErrorNodes,astLineNos,progText);
        else:
            # apply type
            node.type = statementType

    elif node.label == AST_TRACE_LINE:
        #first, checking that each trace item has an endpoint
        #prefix, and second that the prefixes alternate so that
        #messages are being sent between different endpoints.

        #add trace line to traceManager of typeStack so can do
        #type checks after endpoint bodies are type checked.
        traceError = typeStack.addTraceLine(node);
        if traceError != None:
            errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);

        #will hold the name of the last endpoint used in trace line.
        lastEndpoint = None;
        firstChild = True;
        for traceItem in node.children:

            # skip first item, because that is the potential name
            # of the trace line messsage sequence.
            if firstChild:
                firstChild = False;
                continue;


            endpointName = traceItem.children[0].value;
            currentLineNo = traceItem.children[0].lineNo;

            if (node.lineNo == None):
                node.lineNo = currentLineNo;

            funcName = traceItem.children[1].value;

            endpoint1Ast = typeStack.endpoint1Ast;
            endpoint2Ast = typeStack.endpoint2Ast;
            endpoint1Name = typeStack.endpoint1;
            endpoint2Name = typeStack.endpoint2;
            endpoint1LineNo = typeStack.endpoint1LineNo;
            endpoint2LineNo = typeStack.endpoint2LineNo;

            #check that are using declared endpoints.
            if (not typeStack.isEndpoint(endpointName)):
                errMsg = '\nError in sequence declaration.  Each element ';
                errMsg += 'in the message sequence should have the form ';
                errMsg += '<Endpoint Name>.<Function name>.  For <Endpoint Name>, ';
                errMsg += 'you entered "' + endpointName + '".  You should have entered ';
                errMsg += 'either "' + endpoint1Name + '" or "' + endpoint2Name;
                errMsg += '" to agree with your endpoint declarations.\n';

                astErrorNodes = [node,endpoint1Ast,endpoint2Ast];
                astLineNos = [currentLineNo, endpoint1LineNo, endpoint2LineNo];
                errorFunction(errMsg,astErrorNodes,astLineNos,progText);        
                continue;

            #check for alternating between endpoints
            if (lastEndpoint != None):
                if (lastEndpoint == endpointName):
                    #means that we had a repeat between the endpoints
                    errMsg = '\nError in sequence declaration for item ';
                    errMsg += '"' + endpointName + '.' + funcName  +  '".  ';
                    errMsg += 'Messages in a sequence should alternate which side ';
                    errMsg += 'receives them.  Instead of having "' + endpointName + '" ';
                    errMsg += 'receive two messages in a row, you should have "';
                    if (endpointName == endpoint1Name):
                        errMsg += endpoint2Name;
                    else:
                        errMsg += endpoint1Name;

                    errMsg += '" receive a message in between.\n';
                    errorFunction(errMsg,[node],[currentLineNo],progText);        

            lastEndpoint = endpointName;

    elif node.label == AST_LEN:
        argumentNode = node.children[0];
        argumentNode.typeCheck(progText,typeStack,avoidFunctionObjects)
        
        un_function_arg_node_type = unwrap_function_call_type_checker(
            argumentNode.type,node,
            ('Error in len statement: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to call len on.'),
            progText)

        if ((not is_text(un_function_arg_node_type)) and
            (not isListType(un_function_arg_node_type)) and
            (not isMapType(un_function_arg_node_type))):
            errorString = 'Error in calling len.  Can only call len on a ';
            errorString += 'list, map, or Text.  Instead, you passed in a ';
            errorString += dict_type_to_str(argument.type) + '.';
            errorFunction(errorString,[node],[node.lineNo],progText);

        node.type = generate_type_as_dict(TYPE_NUMBER,False)

    elif node.label == AST_KEYS:
        argumentNode = node.children[0];
        argumentNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        # should take on the type of whatever the type of the map/list
        # was supposed to be.  for a list it should always be a list
        # of numbers.  for a map, take on list of map's element types.
        # if map was empty, then just return an empty list.
        if isListType(argumentNode.type):
            node.type = buildListTypeSignatureFromTypeName(
                generate_type_as_dict(TYPE_NUMBER,False),False)

        elif isMapType(argumentNode.type):
            if is_empty_map(argumentNode.type):
                node.type = generate_type_as_dict(EMPTY_LIST_SENTINEL,False)
            else:
                mapIndexType = getMapIndexType(argumentNode.type)
                node.type = buildListTypeSignatureFromTypeName(
                    mapIndexType,False);
        else:
            errorString = 'Error in calling keys.  Can only call keys on a ';
            errorString += 'list or map.  Instead, you passed in a ';
            errorString += argument.type + '.';
            errorFunction(errorString,[node],[node.lineNo],progText);

    elif node.label == AST_RANGE:
        # all children should be numbers
        argNumber = 0;
        for childNode in node.children:
            argNumber += 1;
            childNode.typeCheck(progText,typeStack,avoidFunctionObjects)

            un_function_child_node_type = unwrap_function_call_type_checker(
                childNode.type,node,
                ('Error in range statement: function call ' +
                'returns more than one value.  Cannot determine which ' +
                 'to get range of.'),
                progText)
            
            if not is_number(un_function_child_node_type):
                errorString = 'Error in calling range.  Range requires all ';
                errorString += 'of its arguments to be numbers.  Instead, the #';
                errorString += str(argNumber) + ' argument you passed in to ';
                errorString += 'range was of type ' + dict_type_to_str(childNode.type) + '.';
                errorFunction(
                    errorString,[node,childNode],[node.lineNo,childNode.lineNo],progText);

        # type that assign should be list to numbers
        node.type = buildListTypeSignatureFromTypeName(
            generate_type_as_dict(TYPE_NUMBER,False),False)
            
    elif node.label == AST_PRINT:
        #check to ensure that it's passed a string
        argument = node.children[0];
        argument.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_arg_type = unwrap_function_call_type_checker(
            argument.type,node,
            ('Error in print statement: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to print.'),
            progText)

        if ((not is_text(un_function_arg_type)) and (not is_number(un_function_arg_type)) and
            (not is_true_false(un_function_arg_type))):
            errorString = 'Print requires a Text, TrueFalse, or a Number ';
            errorString += 'to be passed in.  ';
            errorString += 'It seems that you passed in a ';
            errorString += dict_type_to_str(argument.type) + '.';
            errorFunction(errorString,[node],[node.lineNo],progText);

        node.type = generate_type_as_dict(TYPE_NOTHING,False)

    elif node.label == AST_REFRESH:
        node.type = generate_type_as_dict(TYPE_NOTHING,False)
        
    elif(node.label == AST_TOTEXT_FUNCTION):
        # check to ensure that it's passed a Text, TrueFalse, or a
        # Number.  If it is passed anything else, indicate that
        # can't handle it.
        argumentNode = node.children[0];
        argumentNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_arg_node_type = unwrap_function_call_type_checker(
            argumentNode.type,node,
            ('Error in toText: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to call toText on.'),
            progText)

        if ((not is_text(un_function_arg_node_type)) and (not is_number(un_function_arg_node_type)) and
            (not is_true_false(un_function_arg_node_type))):
            errorString = 'ToText requires a Text, TrueFalse, or a Number ';
            errorString += 'to be passed in.  It seems that you passed in a ';
            errorString += dict_type_to_str(argumentNode.type) + '.';
            errorFunction(errorString,[node],[node.lineNo],progText);

        node.type = generate_type_as_dict(TYPE_STRING,False)

    elif(node.label == AST_SHARED_SECTION):
        #each child will be an annotated declaration.
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_ANNOTATED_DECLARATION):
        # the type of this identifier
        #reset my type to it.
        typeNode = node.children[1];
        typeNode.typeCheck(progText,typeStack,avoidFunctionObjects);
        node.type = typeNode.type;

        currentLineNo = node.children[1].lineNo;
        if (len(node.children) == 4):
            #have an initializer too.
            node.children[3].typeCheck(progText,typeStack,avoidFunctionObjects);
            assignType = node.children[3].type;
            if (assignType != node.type):
                if (assignType == None):
                    assignType = '<None>';
                errorString = 'Assigned type [' + assignType + '] does not ';
                errorString += 'match declared type [' + node.type + '].';
                errorFunction(errorString,[node],[currentLineNo],progText);

        #actually store the new type
        identifierName = node.children[2].value;
        existsAlready = typeStack.getIdentifierElement(identifierName);
        if (existsAlready != None):
            errorFunction('Already have an identifier named ' + identifierName,
                          [node],[currentLineNo, existsAlready.lineNo],progText);
        else:
            controlledByNode = node.children[0];
            idType = typeStack.getFuncIdentifierType(identifierName);
            if (idType):
                errText = 'Already have a function named ' + identifierName;
                errText += '.  Therefore, cannot name an identifier with this name.';
                errorFunction(errText,
                              [node,existsAlready.astNode],
                              [currentLineNo,existsAlready.lineNo],
                              progText);

            # check to ensure that specified a valid endpoint to
            # control the shared variable.
            controlledByStr = controlledByNode.value;
            end1Name = typeStack.endpoint1
            if ((controlledByStr != TYPE_NOTHING) and
                (controlledByStr != typeStack.endpoint1) and
                (controlledByStr != typeStack.endpoint2)):
                errText = 'Can only specify an endpoint or Nothing to control ';
                errText += 'a shared variable.  The available endpoint names are '
                errText += typeStack.endpoint1 + ' and ' + typeStack.endpoint2;
                errText += ', but you specified ' + controlledByStr + '.';
                errorFunction(errText,
                              [node],
                              [currentLineNo],
                              progText);


            # actually add the shared variable.
            typeStack.addIdentifier(identifierName,
                                    node.type,
                                    controlledByStr,node,currentLineNo);

            
    elif(node.label == AST_NUMBER):
        node.type = generate_type_as_dict(TYPE_NUMBER,False)
    elif(node.label == AST_STRING):
        node.type = generate_type_as_dict(TYPE_STRING,False)
    elif(node.label == AST_BOOL):
        node.type = generate_type_as_dict(TYPE_BOOL,False)

    elif node.label == AST_DOT_STATEMENT:
        pre_dot_node = node.children[0]
        post_dot_node = node.children[1]

        pre_dot_node.typeCheck(progText,typeStack,avoidFunctionObjects)

        
        # do not type check post_dot_node.  For a.b, b will not be in
        # scope.  only fully-qualified a.b will be.
        # post_dot_node.typeCheck(progText,typeStack,avoidFunctionObjects)

        if post_dot_node.label != AST_IDENTIFIER:
            err_msg = 'For a.b, require that b be an identifier.'
            errorFunction(
                err_msg,[post_dot_node],[post_dot_node.lineNo],progText)

        post_dot_node_name = post_dot_node.value

        un_function_pre_dot_node_type = unwrap_function_call_type_checker(
            pre_dot_node.type,node,
            ('Error in dot statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to get field of.'),
            progText)


        if (isListType(un_function_pre_dot_node_type) or
            isMapType(un_function_pre_dot_node_type) or
            is_text(un_function_pre_dot_node_type)):

            node.type = generate_type_as_dict(TYPE_NOTHING,False)
            
            # Should only get into this part of statement from
            # function call.  if calling append or remove, change
            # these nodes' labels to ast_append, ast_insert, and
            # ast_remove, respectively.  this will serve as a signal
            # to function call type checking code to handle append and
            # remove differently (ie, create an AST_APPEND,
            # AST_REMOVE, and AST_INSERT statement in ast type tree
            # and use existing emitting and slicing code developed for
            # these labels).

            if post_dot_node_name == 'remove':
                node.label = AST_REMOVE_STATEMENT
                node.children = []
                node.addChild(pre_dot_node)
            elif post_dot_node_name == 'append':
                node.label = AST_APPEND_STATEMENT
                node.children = []
                node.addChild(pre_dot_node)
                
            elif post_dot_node_name == 'insert':
                node.label = AST_INSERT_STATEMENT
                node.children = []
                node.addChild(pre_dot_node)
                
            else:
                err_msg = 'Error.  Type '
                err_msg += dict_type_to_str(pre_dot_node.type)
                err_msg += ' only permits the operations "remove" '
                err_msg += 'and "append" to be called on it.  It '
                err_msg += 'does not support "' + post_dot_node_name + '."'
                errorFunction(err_msg,
                              [post_dot_node],
                              [post_dot_node.lineNo],
                              progText)

        elif is_struct(un_function_pre_dot_node_type):
            # from struct type, get the type of the field named by
            # post_dot_node_name

            if is_self_struct_type(un_function_pre_dot_node_type):
                struct_name = get_struct_name_from_struct_type(
                    un_function_pre_dot_node_type)
                struct_type = typeStack.get_struct_type(
                    struct_name,is_external(un_function_pre_dot_node_type))

            else:
                struct_type = un_function_pre_dot_node_type
            
            node.type = get_struct_field_type(
                post_dot_node_name,struct_type)

            # field we are trying to call did not exist
            if node.type == None:
                err_msg = 'Error.  The struct has type '
                err_msg += dict_type_to_str(pre_dot_node.type)
                err_msg += '.  It does not have a field named "'
                err_msg += post_dot_node_name + '" for you to access.'
                errorFunction(
                    err_msg,[pre_dot_node],[pre_dot_node.lineNo],progText)

        elif is_endpoint(un_function_pre_dot_node_type):
            # FIXME: temporarily assigning result of endpoint node
            # function.  Require type checking for endpoint function
            # call

            node.type = build_endpoint_func_type_signature(
                pre_dot_node,progText,typeStack)
            
        else:
            err_msg = 'Error, when calling a.b, a must be a '
            err_msg += 'struct, list, map, or text type.  Instead, you '
            err_msg += 'provided type '
            err_msg += dict_type_to_str(pre_dot_node.type) + '.'
            errorFunction(
                err_msg,[pre_dot_node],[pre_dot_node.lineNo],progText)

        
    elif node.label == AST_FUNCTION_CALL:
        # a function can be called with a couple of patterns:
        # first pattern: func_name(<args>)
        # second pattern: <struct var>.func_name(<args>)
        # unsupported: func_call()() (ie, a function returns a func,
        # which we then call

        func_name_node = node.children[0]
        func_name_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        node.lineNo = func_name_node.lineNo
        # arguments to function
        func_arg_list_node = node.children[1]


        # special-cased handling append and remove statements to
        # preserve as much previous slicing and emitting code as had
        # been written.  essentially, if the function call was to
        # append or remove from a map/list, then when we call
        # typeCheck on func_name_node, the AST_DOT rule will transform
        # the label of func_name_node to be AST_APPEND_STATEMENT or
        # AST_REMOVE_STATEMENT, depending on whether the programmer
        # was trying to append or remove.  Here, in turn, we must form
        # a *new* ast_append_statement or ast_remove statement,
        # passing the argument of the append or remove call and type
        # check the newly generated statement.  The reason for all
        # this convoluted logic is that the dot notation cannot
        # construct the full ast_append_statement or
        # ast_remove_statement itself because it does not have access
        # to the function's arguments that are available here.
        if func_name_node.label in [
            AST_APPEND_STATEMENT,AST_REMOVE_STATEMENT,AST_INSERT_STATEMENT]:
            
            node.label = func_name_node.label
            # clear exsiting children structure.
            node.children = []
            # this adds in the node that is being appended to
            node.addChild(func_name_node.children[0])

            if func_name_node.label in [AST_APPEND_STATEMENT,AST_REMOVE_STATEMENT]:
                if len(func_arg_list_node.children) != 1:
                    which_func = 'append' if node.label == AST_APPEND_STATEMENT else 'remove'

                    err_msg = 'Error when calling ' + which_func + '.  '
                    err_msg += which_func + ' takes 1 argument.  You '
                    err_msg += 'provided ' + str(len(func_arg_list_node.children))
                    err_msg += '.'
                    errorFunction(err_msg, [node],[node.lineNo],progText)

            else:
                if len(func_arg_list_node.children) != 2:
                    err_msg = 'Error when calling insert.  insert' 
                    err_msg += ' takes 2 arguments.  You provided '
                    err_msg += str(len(func_arg_list_node.children)) + '.'
                    errorFunction(err_msg,[node],[node.lineNo],progText)


            # this adds in the node corresponding to the argument of
            # the append statement.  Eg, if we called a.append(1),
            # then here we would be appending the node corresponding
            # to the literal 1.
            node.addChildren(func_arg_list_node.getChildren())

            # need to re-type check to ensure that the append and
            # remove statements are correct (eg. what we're appending
            # to a list has the same type as the elements of the list,
            # etc.
            node.typeCheck(progText,typeStack,avoidFunctionObjects)
        else:

            if not isFunctionType(func_name_node.type):
                err_msg = 'Error in function call attempt.  '
                err_msg += 'Must make function call on a function '
                err_msg += 'type.  Instead, making it on '
                err_msg += dict_type_to_str(func_name_node.type) + '.'
                errorFunction(
                    err_msg,[func_name_node],[func_name_node.lineNo],progText)
            
            # func_name_node.type should contain the function's type
            # signature now.
            func_match_obj = createFuncMatchObjFromFuncTypeDict(
                func_name_node.type,func_name_node)

            # check if this is a text function or a function object
            is_function_object = True
            func_name = ''
            if func_name_node.label == AST_IDENTIFIER:
                func_name = func_name_node.value
                func_id_type = typeStack.getFuncIdentifierType(func_name)
                if func_id_type != None:
                    is_function_object = False

            # rule that can only call passed-in functions in
            # oncomplete section.
            if is_function_object and (not typeStack.inOnComplete):
                # FIXME: should distinguish calling external functions
                # from calling functions on endpoint objects here and
                # re-enable the error below.
                
                # errMsg = '\nError trying to call function object.  ';
                # errMsg += 'Can only call function object in onComplete ';
                # errMsg += 'section.\n';
                # errMsg = '\nWARNING in typeCheck.py.  ' + errMsg
                # print errMsg
                # errorFunction(errMsg,[node],[node.lineNo],progText);
                pass
                

            if func_match_obj.element.astNode.label == AST_ONCREATE_FUNCTION:
                errMsg = '\nError trying to call OnCreate function.  ';
                errMsg += 'You are not allowed to call OnCreate yournode.  ';
                errMsg += 'The Waldo system itself will call the function ';
                errMsg += 'when creating your endpoint.\n';
                errorFunction(errMsg,[node],[node.lineNo],progText);            

            #set my type as that returned by the function
            node.type = func_match_obj.getReturnType();
            
            #####check the argument types passed into the function
            funcArgList = func_arg_list_node.children;
            allArgTypes = [];
            for s in funcArgList:
                s.typeCheck(progText,typeStack,avoidFunctionObjects);
                allArgTypes.append(s.type);

            argError = None            
            if not is_wildcard_type(node.type):
                argError = func_match_obj.argMatchError(allArgTypes,node);

            if argError != None:
                #means that the types of the arguments passed into the
                #function do not match the arguments that the function
                #is declared with.

                argError.checkValid(); # just for debugging

                if argError.errorType == FUNC_CALL_ARG_MATCH_ERROR_NUM_ARGS_MISMATCH:
                    #means that expected a different number of
                    #arguments than what we called it with.
                    # FIXE: unclear if func_name will have relevant value
                    errMsg = '\nError calling function "' + func_name + '".  ';
                    errMsg += func_name + ' requires '
                    errMsg += str(argError.expected)
                    errMsg += ' arguments.  Instead, you provided '
                    errMsg += str(argError.provided)
                    errMsg += '.\n';

                    errorFunction(errMsg,argError.astNodes,argError.lineNos,progText); 

                elif (argError.errorType == FUNC_CALL_ARG_MATCH_ERROR_TYPE_MISMATCH):
                    #means that although we got the correct number of
                    #arguments, we had type mismatches on several of
                    #them.
                    # FIXME: func_name may be useless here
                    errMsg = '\nError calling function "' + func_name + '".  '
                    for s in range (0, len(argError.argNos)):
                        errMsg += '\n\t'
                        errMsg += 'Argument number ' + str(argError.argNos[s]) + ' was expected '
                        errMsg += 'to be of type ' + dict_type_to_str(argError.expected[s])
                        errMsg += ', but is inferrred '
                        errMsg += 'to have type ' + dict_type_to_str(argError.provided[s])

                    errorFunction(errMsg,argError.astNodes,argError.lineNos,progText); 
                else:
                    errMsg = '\nBehram error in AST_FUNCTION_CALL.  Have an error ';
                    errMsg += 'type for a function that is not recognized.\n'
                    errPrint(errMsg);
                    assert(False);


    elif node.label == AST_FUNCTION_TYPE_LIST:
        node.type = []

        for type_node in node.children:
            type_node.typeCheck(progText,typeStack,avoidFunctionObjects)
            node.type.append(type_node.type)
            
    elif (node.label == AST_TYPE):

        if node.value == TYPE_FUNCTION:
            # more compilcated types for functions

            # create a dictionary for the function type.
            # Function (In: Number, TrueFalse; Out: Text)
            # becomes:
            # { Type: 'Function',
            #    In: [
            #          {
            #            Type: "Number"
            #          },
            #          {
            #            Type: "TrueFalse"
            #          }],
            #    Returns: [{ Type: "Text"}]
            # }
            node.type = buildFuncTypeSignature(
                node,progText,typeStack,node.external != None)

        elif node.value == TYPE_LIST:
            # more complicated types for lists
            # create a dictionary for the list type:
            # List (Element: Number)
            # becomes
            # { Type: 'List',
            #   ElementType: { Type: "Number" }}
            #
            node.type = buildListTypeSignature(
                node,progText,typeStack,node.external != None)

        elif node.value == TYPE_MAP:
            # more complicated types for maps
            # create a dictionary for the map type:
            # Map (From: Number, To: Text)
            # becomes
            # { Type: 'Map',
            #   From: { Type: 'Number'},
            #   To: {Type: 'Text'}
            #  }
            typeSignature,errMsg,errNodes = buildMapTypeSignature(
                node,progText,typeStack,node.external != None)

            if errMsg != None:
                # list comprehension!
                errLineNos = [ x.lineNo for x in errNodes];
                errorFunction(errMsg,errNodes, errLineNos, progText);

            node.type = typeSignature
            
        elif node.value == TYPE_STRUCT:
            struct_name = node.children[0].value

            struct_type = typeStack.get_struct_type(
                struct_name,node.external != None)
            if struct_type == None:
                # means that struct with name struct_name has not been
                # already declared by the user
                err_msg = 'Error.  Struct ' + struct_name + ' has not '
                err_msg += 'been declared ahead of time.  Did you misspell "'
                err_msg += struct_name + '" or forget to declare it?'

                errorFunction(err_msg,[node],[node.lineNo],progText)
                
            node.type = struct_type
            
        else:
            # just assign the type directly since it is one of the
            # basic types Text, TrueFalse, or Number.
            external = False
            if node.external != None:
                external = True

            node.type = generate_type_as_dict(
                node.value,external)

    elif (node.label == AST_LIST):
        node.type = generate_type_as_dict(EMPTY_LIST_SENTINEL,False)
        allTypes = [];

        # get all types from element nodes
        for element in node.children:
            element.typeCheck(progText,typeStack,avoidFunctionObjects);
            allTypes.append(element.type);


        # using nested for loop to ensure that all types are
        # tested against one another.  Type testing here is not
        # transitive (ie if a and b do not produce an error and b
        # and c do not produce an error, it does not mean that a
        # and c will not produce an error.  This is because of
        # empty lists: [] will match [Number] and [] will match
        # [TrueFalse], but [Number] will not match [TrueFalse].
        for typeCheckingIndex in range(0,len(allTypes)):

            potentialType = buildListTypeSignatureFromTypeName(
                allTypes[typeCheckingIndex],False);

            node.type = moreSpecificListMapType(node.type,potentialType);

            for subTypeCheckingIndex in range(typeCheckingIndex+1,len(allTypes)):
                # now check that this type agrees with all subsequent types.
                firstType = allTypes[typeCheckingIndex];
                secondType = allTypes[subTypeCheckingIndex];

                if checkTypeMismatch(element,firstType,secondType,typeStack,progText):
                    errMsg = '\nError in list statement.  Different elements in the ';
                    errMsg += 'list have different types.  The ' + str(typeCheckingIndex+1);
                    errMsg += 'th element in the list has type '
                    errMsg += dict_type_to_str(firstType) + '.  The ';
                    errMsg += str(subTypeCheckingIndex + 1) + 'th has type '
                    errMsg += dict_type_to_str(secondType) + '.\n';
                    errorFunction(errMsg,[node], [node.lineNo], progText);


    elif node.label == AST_MAP:
        # type check all children
        node.type = generate_type_as_dict(EMPTY_MAP_SENTINEL,False)
        allIndexTypes = [];
        allValueTypes = [];

        for counterIndex in range(0,len(node.children)):
            item = node.children[counterIndex];
            index = item.children[0];
            value = item.children[1];

            index.typeCheck(progText,typeStack,avoidFunctionObjects);
            value.typeCheck(progText,typeStack,avoidFunctionObjects);

            if not isValueType(index.type):
                errMsg = '\nError in Map.  You can only index a map using ';
                errMsg += 'Number, Text, or TrueFalse.  However, the ' + str(counterIndex + 1);
                errMsg += 'th element in the map has type '
                errMsg += dict_type_to_str(index.type) + '.';
                errorFunction(errMsg,[node,index],[node.lineNo,index.lineNo],progText);

            allIndexTypes.append(index.type);
            allValueTypes.append(value.type);

        for typeCheckingIndex in range(0,len(allIndexTypes)):
            indexType = allIndexTypes[typeCheckingIndex];
            valueType = allValueTypes[typeCheckingIndex];
            potentialType = buildMapTypeSignatureFromTypeNames(
                indexType,valueType,False);
            
            node.type = moreSpecificListMapType(node.type,potentialType);
            for subTypeCheckingIndex in range(typeCheckingIndex+1,len(allIndexTypes)):
                firstIndexType = allIndexTypes[typeCheckingIndex];
                secondIndexType = allIndexTypes[subTypeCheckingIndex];

                firstValueType = allValueTypes[typeCheckingIndex];
                secondValueType = allValueTypes[subTypeCheckingIndex];
                if checkTypeMismatch(index,firstIndexType,secondIndexType,typeStack,progText):
                    errMsg = '\nError in Map.  Different elements in the map ';
                    errMsg += 'have different types.  The ' + str(typeCheckingIndex + 1);
                    errMsg += 'th item in the map has an index of '
                    errMsg += dict_type_to_str(firstIndexType) + '.  ';
                    errMsg += 'However, the ' + str(subTypeCheckingIndex +1)
                    errMsg += 'th has type ' 
                    errMsg += dict_type_to_str(secondIndexType) + '.\n'
                    errorFunction(errMsg,[node],[node.lineNo],progText)

                if checkTypeMismatch(value,firstValueType,secondValueType,typeStack,progText):
                    errMsg = '\nError in Map.  Different elements in the map ';
                    errMsg += 'have different types.  The ' + str(typeCheckingIndex + 1);
                    errMsg += 'th item in the map has a value of '
                    errMsg += dict_type_to_str(firstValueType) + '.  ';
                    errMsg += 'However, the ' + str(subTypeCheckingIndex +1)
                    errMsg += 'th has type ';
                    errMsg += dict_type_to_str(secondValueType) + '.\n';
                    errorFunction(errMsg,[node],[node.lineNo],progText);


    elif (node.label == AST_CONDITION_STATEMENT):
        #type check all children.  (type checks if, elseif, and
        #else statements).
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif ((node.label == AST_IF_STATEMENT) or
          (node.label == AST_ELSE_IF_STATEMENT)):
        boolCond = node.children[0];
        condBody = node.children[1];

        boolCond.typeCheck(progText,typeStack,avoidFunctionObjects)

        un_function_bool_cond_node_type = unwrap_function_call_type_checker(
            boolCond.type,node,
            ('Error in condition of if/else if statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use in condition.'),
            progText)
     
        if (not is_true_false(un_function_bool_cond_node_type)):
            errMsg = '\nError in If or ElseIf statement.  The condition ';
            errMsg += 'must evaluate to a TrueFalse type.  Instead, ';

            if (boolCond.type != None):
                errMsg += ('it evaluated to a type of ' +
                           dict_type_to_str(boolCond.type))
            else:
                errMsg += 'we could not infer the type';

            errMsg += '\n';
            errorFunction(errMsg,[boolCond],[boolCond.lineNo],progText);            

        if (condBody.label != AST_EMPTY):
            condBody.typeCheck(progText,typeStack,avoidFunctionObjects);


    elif(node.label == AST_BOOL_EQUALS) or (node.label == AST_BOOL_NOT_EQUALS):
        lhs = node.children[0];
        rhs = node.children[1];
        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        node.type = generate_type_as_dict(TYPE_BOOL,False)
        node.lineNo = lhs.lineNo;

        un_function_lhs_type = unwrap_function_call_type_checker(
            lhs.type,node,
            ('Error in equals/not equals statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for left hand side.'),
            progText)

        un_function_rhs_type = unwrap_function_call_type_checker(
            rhs.type,node,
            ('Error in equals/not equals statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for right hand side.'),
            progText)

        if un_function_lhs_type == None:
            errMsg = '\nError when checking equality. ';
            errMsg += 'Cannot infer type of left-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;
        if un_function_rhs_type == None:
            errMsg = '\nError when checking equality. ';
            errMsg += 'Cannot infer type of right-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;

        if un_function_rhs_type != un_function_lhs_type:
            errMsg = '\nError when checking equality.  Both left-hand side ';
            errMsg += 'of expression and right-hand side of expression should ';
            errMsg += 'have same type.  Instead, left-hand side has type ';
            errMsg += dict_type_to_str(lhs.type)
            errMsg += ', and right-hand side has type '
            errMsg += dict_type_to_str(rhs.type)
            errMsg += '\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);


    elif ((node.label == AST_AND) or (node.label == AST_OR)):

        #keep track of separate expression types to simplify
        #error-reporting.
        expressionType = 'and';
        if (node.label == AST_OR):
            expressionType = 'or';

        lhs = node.children[0];
        rhs = node.children[1];
        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        node.type = generate_type_as_dict(TYPE_BOOL,False)
        node.lineNo = lhs.lineNo;

        un_function_lhs_type = unwrap_function_call_type_checker(
            rhs.type,node,
            ('Error in and/or statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for left hand side.'),
            progText)

        un_function_rhs_type = unwrap_function_call_type_checker(
            rhs.type,node,
            ('Error in and/or statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for right hand side.'),
            progText)

        if un_function_lhs_type == None:
            errMsg = '\nError when checking ' + expressionType + '. ';
            errMsg += 'Cannot infer type of left-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;
        if un_function_rhs_type == None:
            errMsg = '\nError when checking ' + expressionType + '. ';
            errMsg += 'Cannot infer type of right-hand side of expression.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
            return;
        if not is_true_false(un_function_rhs_type):
            errMsg = '\nError when checking ' + expressionType + '. ';
            errMsg += 'Right-hand side expression must be '
            errMsg += dict_type_to_str(
                generate_type_as_dict(TYPE_BOOL,False))
            errMsg += '.  Instead, has type '
            errMsg += dict_type_to_str(rhs.type) + '\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);
        if not is_true_false(un_function_lhs_type):
            errMsg = '\nError when checking ' + expressionType + '. ';
            errMsg += 'Left-hand side expression must be '
            errMsg += dict_type_to_str(
                generate_type_as_dict(TYPE_BOOL,False))
            errMsg += '.  Instead, has type '
            errMsg += dict_type_to_str(lhs.type) + '\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);

    elif (node.label == AST_ELSE_STATEMENT):
        #type check else statement
        for s in node.children:
            if (s.label != AST_EMPTY):
                s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_PLUS):
        #perform plus separately from other math operations to
        #allow plus overload for concatenating strings.
        lhs = node.children[0];
        rhs = node.children[1];
        node.lineNo = lhs.lineNo;

        lhs.typeCheck(progText,typeStack,avoidFunctionObjects)
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects)
        
        un_function_lhs_type = unwrap_function_call_type_checker(
            rhs.type,node,
            ('Error in and/or statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for left hand side.'),
            progText)

        un_function_rhs_type = unwrap_function_call_type_checker(
            rhs.type,node,
            ('Error in and/or statment: function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for right hand side.'),
            progText)

        errSoFar = False;
        if ((not is_number(un_function_lhs_type)) and (not is_text(un_function_lhs_type)) and
            (not is_wildcard_type(un_function_lhs_type))):
            errMsg = '\nError with PLUS expression.  ';
            errMsg += 'Left-hand side should be a Number or a String.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + dict_type_to_str(lhs.type) + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);
            errSoFar = True;

        if ((not is_number(un_function_rhs_type)) and (not is_text(un_function_rhs_type)) and
            (not is_wildcard_type(un_function_rhs_type))):
            errMsg = '\nError with PLUS expression.  ';
            errMsg += 'Right-hand side should be a Number or a String.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + dict_type_to_str(rhs.type) + '.\n';
                
            errorFunction(errMsg, [node],[node.lineNo],progText);
            errSoFar = True;

        #won't be able to do anything further without appropriate
        #type information.
        if (errSoFar):
            return;

        if ((un_function_rhs_type != un_function_lhs_type) and (not is_wildcard_type(un_function_rhs_type)) and
            (not is_wildcard_type(un_function_lhs_type))):
            errMsg = '\nError with PLUS expression.  Both the left- and ';
            errMsg += 'right-hand sides should have the same type.  Instead, ';
            errMsg += 'the left-hand side has type '
            errMsg += dict_type_to_str(lhs.type) + ' and the ';
            errMsg += 'right-hand side has type '
            errMsg += dict_type_to_str(rhs.type) + '.\n';
            errorFunction(errMsg, [node],[node.lineNo],progText);

        node.type = un_function_rhs_type


    elif ((node.label == AST_MINUS) or (node.label == AST_MULTIPLY) or
          (node.label == AST_DIVIDE) or (node.label == AST_GREATER_THAN) or
          (node.label == AST_GREATER_THAN_EQ) or (node.label == AST_LESS_THAN) or
          (node.label == AST_LESS_THAN_EQ)):
        #check type checking of plus, minus, times, divide;
        #left and right hand side should be numbers, returns a number.

        #for error reporting
        expressionType  = 'MINUS';
        node.type = generate_type_as_dict(TYPE_NUMBER,False)
        if (node.label == AST_MULTIPLY):
            expressionType = 'MULTIPLY';
        elif(node.label == AST_DIVIDE):
            expressionType = 'DIVIDE';
        elif(node.label == AST_GREATER_THAN):
            expressionType = 'GREATER THAN';
            node.type = generate_type_as_dict(TYPE_BOOL,False)
        elif(node.label == AST_GREATER_THAN_EQ):
            expressionType = 'GREATER THAN EQUAL';                
            node.type = generate_type_as_dict(TYPE_BOOL,False)
        elif(node.label == AST_LESS_THAN):
            expressionType = 'LESS THAN';
            node.type = generate_type_as_dict(TYPE_BOOL,False)
        elif(node.label == AST_LESS_THAN_EQ):
            expressionType = 'LESS THAN EQUAL';
            node.type = generate_type_as_dict(TYPE_BOOL,False)

        lhs = node.children[0];
        rhs = node.children[1];
        node.lineNo = lhs.lineNo;

        lhs.typeCheck(progText,typeStack,avoidFunctionObjects);
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_lhs_type = unwrap_function_call_type_checker(
            lhs.type,node,
            ('Error in ' + expressionType + ': function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for left hand side.'),
            progText)

        un_function_rhs_type = unwrap_function_call_type_checker(
            rhs.type,node,
            ('Error in ' + expressionType + ': function call ' +
            'returns more than one value.  Cannot determine which ' +
             'to use for right hand side.'),
            progText)

        if ((not is_number(un_function_lhs_type)) and
            (not is_wildcard_type(un_function_lhs_type))):
            errMsg = '\nError with ' + expressionType + ' expression.  ';
            errMsg += 'Left-hand side should be a Number.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + dict_type_to_str(lhs.type) + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);

        if ((not is_number(un_function_rhs_type)) and
            (not is_wildcard_type(un_function_rhs_type))):
            errMsg = '\nError with ' + expressionType + ' expression.  ';
            errMsg += 'Right-hand side should be a Number.  Instead, ';
            if (lhs.type == None):
                errMsg += 'could not infer type.\n';
            else:
                errMsg += 'inferred type ' + dict_type_to_str(rhs.type) + '.\n';

            errorFunction(errMsg, [node],[node.lineNo],progText);


    elif(node.label == AST_BOOLEAN_CONDITION):
        node.lineNo = node.children[0].lineNo;
        node.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);

        un_function_called_type = unwrap_function_call_type_checker(
            node.children[0].type,node,
            ('Error in predicate of condition statement: function call ' +
            'returns more than one value.'),
            progText)
        
        if not is_true_false(un_function_called_type):
            errMsg = '\nError in predicate of condition statement.  Should have ';
            errMsg += 'TrueFalse type.  Instead, ';
            if (node.children[0].type != None):
                errMsg += 'has type ' + dict_type_to_str(node.children[0].type)
            else:
                errMsg += 'cannot infer type';
            errMsg += '.\n';
            errorFunction(errMsg,[node],[node.lineNo],progText);
        else:
            node.type = generate_type_as_dict(TYPE_BOOL,False)

            
    elif(node.label == AST_ELSE_IF_STATEMENTS):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_ENDPOINT):
        # this will only check the body of endpoint functions. not the
        # global variables.

        #check if endpoint name matches previous endpoint name
        endName = node.children[0].value;

        #tell typestack that we are currently in this endpoint
        #body section.  unset it at end of elif.
        typeStack.setCurrentEndpointName(endName);

        currentLineNo = node.children[0].lineNo;
        if (not typeStack.isEndpoint(endName)):
            errMsg = 'Endpoint named ' + endName + ' was not defined at top of file ';
            errMsg = ' are you sure your endpoints match?';
            errLineNos = [currentLineNo,typeStack.endpoint1LineNo,typeStack.endpoint2LineNo];
            errorFunction(errMsg,[node],errLineNos,progText);

        #check endpoint body section
        if (len(node.children) >= 2):
            endpointBodySection = node.children[1];
            endpointBodySection.typeCheck(progText,typeStack,avoidFunctionObjects);
            
        #matches above set call.
        typeStack.unsetCurrentEndpointName();

    elif(node.label == AST_ENDPOINT_BODY_SECTION):            
        #typecheck global section
        node.children[0].typeCheck(progText,typeStack,avoidFunctionObjects);
        #check function section.
        node.children[1].typeCheck(progText,typeStack,avoidFunctionObjects);

        #note: perform extra pop for stack that endpoint global
        #section put on.
        typeStack.popContext();

    elif(node.label == AST_ENDPOINT_GLOBAL_SECTION):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif(node.label == AST_DECLARATION):

        # type check the declared type statement (necessary
        # because of function statements).
        typeNode = node.children[0];
        typeNode.typeCheck(progText,typeStack,avoidFunctionObjects);

        declaredType = typeNode.type
        node.lineNo = typeNode.lineNo;

        if (node.children[1].label != AST_IDENTIFIER):
            errMsg = '\nError at declaration statement. ';
            errMsg += 'Must have an identifier for left hand ';
            errMsg += 'side of declaration.\n';
            errorFunction(errMsg,[node],[currentLineNo],progText);
            return;

        nameNode = node.children[1];
        nameNode.type = declaredType
        name = nameNode.value;
        currentLineNo = node.children[0].lineNo;
        if len(node.children) == 3:
            rhs = node.children[2];
            rhs.typeCheck(progText,typeStack,avoidFunctionObjects);

            if rhs.label == AST_FUNCTION_CALL:
                # rhs will wrap the return type so that if the
                # function call was supposed to return a number,
                # calling .type on it produces:
                # {
                #   'Type': {
                #       'Type': [ {'Type': 'Number'}]
                #       }
                # }
                #
                # We first need to unwrap this to just the middle
                # type, Ie: [ {'Type': 'Number'}].  We check the
                # length of this.  If it is greater than 1, it means
                # that we cannot assign in in the course of the
                # declaration and we throw an error.  Otherwise, use
                # the internal type, {Type: Number} as rhsType


                if not is_wildcard_type(rhs.type):
                    func_call_type_array = get_type_array_from_func_call_returned_tuple_type(
                        rhs.type)

                    if len(func_call_type_array) != 1:
                        err_msg = (
                            'Error in declaration.  Function call produces ' +
                            'more return values than can assign into in a ' +
                            'declaration.')
                        errorFunction(err_msg,[node],[currentLineNo],progText)

                    rhsType = func_call_type_array[0]
                else:
                    rhsType = rhs.type
                    
            else:
                rhsType = rhs.type;

            if (checkTypeMismatch(rhs,declaredType,rhsType,typeStack,progText)):
                errMsg = 'Type mismatch for variable named "' + name + '".';
                errMsg += '  Declared with type '
                errMsg += dict_type_to_str(declaredType) + ', but ';
                errMsg += 'assigned to type '
                errMsg += dict_type_to_str(rhsType) + '.';
                errorFunction(errMsg,[node],[currentLineNo],progText);

            # uncomment the following if want to require
            # initialization of function arguments before start.
            # else:
            # # not initialization information.  There are several
            # # types that require initialization information.  Most
            # # importantly, user-defined functions do.  Throw an
            # # error if user-defined function does not.
            # if (isFunctionType(declaredType)):
            #     errMsg = 'Error when declaring a user-defined function ';
            #     errMsg += 'named "' + name + '".  Every user-defined ';
            #     errMsg += 'function requires that it should be initialized.  ';
            #     errMsg += 'That means that you have to set ' + name + ' ';
            #     errMsg += 'to a valid function when you declare it.';
            #     errorFunction(errMsg,[node],[currentLineNo],progText);

        #check if already have a function or variable with the
        #targetted name.
        prevId = typeStack.getIdentifierElement(name);
        prevFunc = typeStack.getFuncIdentifierType(name);
        if (prevId != None) or (prevFunc != None):
            nodes =[node];
            lineNos = [currentLineNo];
            if (prevId != None):
                nodes.append(prevId.astNode);
                lineNos.append(prevId.lineNum);
            if (prevFunc != None):
                nodes.append(prevFunc.element.astNode);
                lineNos.append(prevFunc.element.lineNum);

            errMsg = 'Error trying to name a variable "' + name;
            errMsg += '".  Already have a function or variable with ';
            errMsg += 'the same name.'
            errorFunction(errMsg,nodes,lineNos,progText);

        typeStack.addIdentifier(name,declaredType,None,node,currentLineNo);
        node.type = declaredType;

        
    elif(node.label == AST_RETURN_STATEMENT):
        node.type = generate_type_as_dict(TYPE_NOTHING,False)

        return_tuple_node = node.children[0]
        return_tuple_node.typeCheck(
            progText,typeStack,avoidFunctionObjects)
        
        typeCheckError = typeStack.checkReturnStatement(node,checkTypeMismatch);
        if (typeCheckError != None):
            errorFunction(
                typeCheckError.errMsg,typeCheckError.nodes,
                typeCheckError.lineNos,progText)

            
    elif node.label == AST_IDENTIFIER:
        name = node.value;
        typer,ctrldBy = typeStack.getIdentifierType(name);
        if (typer == None):
            # also check if it's an identifier for a non-variable
            # function.
            funcType = typeStack.getFuncIdentifierType(name);
            if (funcType == None):
                errMsg = 'Cannot infer type of ' + name + '.  Are you sure it is valid?  ';
                errMsg += 'Are you sure that you declared it first?';
                errorFunction(errMsg,[node],[node.lineNo],progText);
                node.type = 'Undefined';
            else:
                node.type = funcType.createTypeDict()
        else:
            node.type = typer;
            # need to copy external tag too
            ctxElm = typeStack.getIdentifierElement(name);
            if ctxElm == None:
                assert(False);

    elif(node.label == AST_ENDPOINT_FUNCTION_SECTION):
        # this just type checks the headers of each function.
        # Have to insert the header of each function
        for s in node.children:
            functionDeclarationTypeCheck(
                s,progText,typeStack,avoidFunctionObjects);

        # want to incorporate each messasge sequence function's
        # declaration into context as well.
        msgSeqSection = getMsgSeqSection(typeStack.rootNode);
        for msgSeq in msgSeqSection.children:
            # each msgSeq has label MessageSequence
            msgSeqFunctions = msgSeq.children[2];
            for msgSeqFunc in msgSeqFunctions.children:
                if isEndpointSequenceFunction(
                    msgSeqFunc,typeStack.currentEndpointName):
                    # ensure that this function's name gets mapped
                    # into current endpoint's function context.
                    functionDeclarationTypeCheck(
                        msgSeqFunc,progText,typeStack,avoidFunctionObjects);

        # now we type check the bodies of each function
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

        # now we type check the bodies of the message sequence
        # functions to ensure that they also are okay from type
        # checking.
        typeCheckMessageSequencesEndpoint(msgSeqSection,progText,typeStack);

            
    elif ((node.label == AST_PUBLIC_FUNCTION) or
          (node.label == AST_PRIVATE_FUNCTION) or
          (node.label == AST_ONCREATE_FUNCTION)):
        '''
        begins type check for body of the function, this code
        pushes arguments into context and then calls recursive
        type check on function body itself.
        '''
        ## create a new type context to insert intermediate data
        ## in.  context is popped at the end of the elif statement.
        typeStack.pushContext();
        funcName = node.children[0].value;            

        stackFunc = typeStack.getFuncIdentifierType(funcName);

        #set my line number to be the line number of when the
        #function type was declared.
        node.lineNo = node.children[0].lineNo;

        if stackFunc == None:
            errMsg = 'Behram error: should have inserted function ';
            errMsg += 'with name "' + funcName + '" into type stack ';
            errMsg += 'before type checking function body.'
            errPrint('\n\n');
            errPrint(errMsg);
            errPrint('\n\n');
            assert(False);

        #insert passed in arguments into context;
        if ((node.label == AST_PUBLIC_FUNCTION) or (node.label == AST_PRIVATE_FUNCTION)):
            funcDeclArgListIndex = 2;
            funcBodyIndex = 3;
            funcNameIndex = 0;
        elif(node.label == AST_ONCREATE_FUNCTION):
            funcBodyIndex = 2;
            funcDeclArgListIndex = 1;
            funcNameIndex = 0;
        else:
            errMsg = '\nBehram error: invalid function ';
            errMsg += 'type when type checking functions\n';
            errPrint(errMsg);


        if (funcDeclArgListIndex != None):
            #add all arguments passed in in function declaration to
            #current context.
            node.children[funcDeclArgListIndex].typeCheck(
                progText,typeStack,avoidFunctionObjects);


        # when type check body, 
        typeStack.addCurrentFunctionNode(node);

        # type check the actual function body
        node.children[funcBodyIndex].typeCheck(progText,typeStack,avoidFunctionObjects);

        ## remove the created type context
        typeStack.popContext();

    elif(node.label == AST_FUNCTION_BODY):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif (node.label == AST_FUNCTION_DECL_ARGLIST):
        #iterate through each individual declared argument
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif node.label == AST_FUNCTION_ARGLIST:
        for child in node.children:
            child.typeCheck(progText,typeStack,avoidFunctionObjects)
            
            
    elif node.label == AST_FUNCTION_DECL_ARG:
        '''
        for declared argument, checks for its collision
        with existing variables and functions, and then inserts
        it into a typestack context.
        '''
        arg_type_node = node.children[0]
        node.lineNo = arg_type_node.lineNo
        arg_type_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        argType = arg_type_node.type
        argName = node.children[1].value

        collisionObj = typeStack.checkCollision(argName,node);

        if (collisionObj != None):
            #FIXME: for this error message, may want to
            #re-phrase with something about scope, so do not
            #take the wrong error message away.

            errMsg = 'Error trying to name an argument "';
            errMsg += argName + '" in your function.  ';
            errMsg += 'You already have a function or variable ';
            errMsg += 'with the same name.';

            errorFunction(
                errMsg,collisionObj.nodes,collisionObj.lineNos,progText)
            
        else:
            if isFunctionType(argType) and avoidFunctionObjects:
                pass;
            else:
                typeStack.addIdentifier(
                    argName,argType,None,node,node.lineNo)

        node.type = argType
                

    elif (node.label == AST_FUNCTION_BODY_STATEMENT):
        for s in node.children:
            s.typeCheck(progText,typeStack,avoidFunctionObjects);

    elif (node.label == AST_STRING):
        node.type = generate_type_as_dict(TYPE_STRING,False)
    elif (node.label == AST_NUMBER):
        node.type = generate_type_as_dict(TYPE_NUMBER,False)
    elif (node.label == AST_BOOL):
        node.type = generate_type_as_dict(TYPE_BOOL,False)

    elif (node.label == AST_ASSIGNMENT_STATEMENT):
        # lhs can only hold a list of values if assignment is a result
        # of function call.
        lhs_list = node.children[0]
        node.lineNo = lhs_list.lineNo
        rhs = node.children[1]
        rhs.typeCheck(progText,typeStack,avoidFunctionObjects)

        for to_assign_to_counter in range(0,len(lhs_list.children)):
            to_assign_to_node = lhs_list.children[to_assign_to_counter]

            typeStack.in_lhs_assign = True
            to_assign_to_node.typeCheck(
                progText,typeStack,avoidFunctionObjects)
            typeStack.in_lhs_assign = False

            _check_single_assign(
                to_assign_to_node,rhs,to_assign_to_counter,
                progText,typeStack,avoidFunctionObjects)


    #remove the new context that we had created.  Note: shared
    #section is intentionally missing.  Want to maintain that 
    #context while type-checking the endpoint sections 
    #skip global section too.
    if ((node.label == AST_ROOT) or
        (node.label == AST_ENDPOINT_FUNCTION_SECTION)):
        
        typeStack.popContext();
        
        
def functionDeclarationTypeCheck(node, progText,typeStack,avoidFunctionObjects):
    '''
    Takes a node of type public function, private function,
    AST_MESSAGE_SEND_SEQUENCE_FUNCTION,
    AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION, ONCREATE_FUNCTION, ONCOMPLETE_FUNCTION

    Does not set any types itself, but rather loads functions into the
    typeStack itself.
    '''
    if ((node.label != AST_PUBLIC_FUNCTION) and
        (node.label != AST_PRIVATE_FUNCTION) and
        (node.label != AST_MESSAGE_SEND_SEQUENCE_FUNCTION) and
        (node.label != AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION) and
        (node.label != AST_ONCREATE_FUNCTION) and
        (node.label != AST_ONCOMPLETE_FUNCTION)):

        err_msg = '\nBehram error.  Sending an incorrect tag to be loaded '
        err_msg += 'into functionDeclarationTypeCheck.\n'
        errPrint(err_msg)
        assert(False)


    if ((node.label == AST_PUBLIC_FUNCTION) or
        (node.label == AST_PRIVATE_FUNCTION)):
        
        # get declared return type (only applicable for functions and
        # public functions)
        return_type_node = node.children[1]
        return_type_node.typeCheck(progText,typeStack,avoidFunctionObjects)
        returnType = return_type_node.type;
        argDeclIndex = 2;
        funcNameIndex = 0;
        
    elif(node.label == AST_ONCREATE_FUNCTION):
        returnType = generate_returned_tuple_type(
            [ generate_type_as_dict(TYPE_NOTHING,False) ] )
        argDeclIndex = 1;
        funcNameIndex = 0;
        
    elif node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        argDeclIndex = 2;

        # return_type_node has label functiondeclarglist.  for each
        # element, grab the return type and append it to a list to
        # create an overall return type for calling the send message
        # function.
        return_type_node = node.children[4]
        return_type_tuple_list = []
        for func_decl_arg_node in return_type_node.children:
            type_node = func_decl_arg_node.children[0]
            
            type_node.typeCheck(progText,typeStack,avoidFunctionObjects)
            if is_external(type_node.type):
                err_msg = 'Externals may not appear in sequence peered data.  '
                err_msg += 'Return types are sequence peered.'
                errorFunction(
                    err_msg,[type_node],[type_node.lineNo],progText)
            
            return_type_tuple_list.append(
                type_node.type)
            
        if len(return_type_tuple_list) == 0:
            return_type_tuple_list.append(
                generate_type_as_dict(TYPE_NOTHING,False) )
        
        returnType = return_type_tuple_list

        funcNameIndex = 1;

    elif node.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        # does not take any arguments
        argDeclIndex = None;
        funcNameIndex = 1;
        returnType = generate_returned_tuple_type(
            [ generate_type_as_dict(TYPE_NOTHING,False) ] )
        
    elif node.label == AST_ONCOMPLETE_FUNCTION:
        # should never load an oncomplete function into stack because
        # it will never get called.
        return;
    
    funcName = node.children[funcNameIndex].value;
    node.lineNo = node.children[funcNameIndex].lineNo;
    
    #get types of function arguments

    #add a context to type stack for arg declarations and pop it
    #later so that arg decl arguments do not persist after the
    #type check of arg text.
    typeStack.pushContext();
    if (argDeclIndex != None):
        # fill in type information of all the arguments.
        node.children[argDeclIndex].typeCheck(
            progText,typeStack,avoidFunctionObjects);

        
    typeStack.popContext();

    # build the input argument type list for arguments.
    argTypeList = [];
    if (argDeclIndex != None):
        args = node.children[argDeclIndex].children;

        for t in args:
            #each t should now be of type FUNCTION_DECL_ARG

            if (len(t.children) == 0):
                #means that we have a function that takes no arguments.
                continue;

            #set the type of t to the type identifier of the argument.
            t.children[0].typeCheck(progText,typeStack,avoidFunctionObjects)
            t.type = t.children[0].type

            #add the argument type to the typeStack representation for this function.
            argTypeList.append(t.type);

            if node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
                if is_external(t.type):
                    err_msg = 'Externals may not appear in sequence peered data.  '
                    err_msg += 'Argument types are sequence peered.'
                    errorFunction(err_msg,[t],[t.lineNo],progText)
            
    else:
        # means that we are a message receive fucntion or oncomplete
        # function.  we do not actually need to be careful here,
        # because you cannot directly call a message receive function
        # (the system calls it for you when you receive a message).
        # So just insert gibberish for argument.
        argTypeList.append(generate_type_as_dict(TYPE_NOTHING,False))

    collisionObj = typeStack.checkCollision(funcName,node);
    if collisionObj != None:
        #FIXME: for this error message, may want to
        #re-phrase with something about scope, so do not
        #take the wrong error message away.
        errMsg = 'Error trying to name a function "' + funcName;
        errMsg += '".  Already have a function or variable with ';
        errMsg += 'the same name.'
        errorFunction(errMsg,collisionObj.nodes,collisionObj.lineNos,progText);
    else:
        traceError = typeStack.addFuncIdentifier(funcName,returnType,argTypeList,node,node.lineNo);
        if traceError != None:
            errorFunction(traceError.errMsg,traceError.nodes,traceError.lineNos,progText);
            

def typeCheckMapBracket(toReadFrom,index,typeStack,progText):
    '''
    @param {astNode with label map} toReadFrom --- map ... already
    type checked before entering this function.
    
    @param {astNode} index ... already type checked before entering
    this function.

    @return (a,b,c,d)
      a {Bool} --- True if there is an error.  False otherwise.

      b {String or None} --- Type to apply to parent node or None if
        error.
      
      c {String or None} --- String with error message or none if no
        error.  
      
      d {Array of ast nodes or None} --- None if no error.  Otherwise,
        a list of nodes that caused the errors.
      '''

    un_function_called_index_type = unwrap_function_call_type_checker(
        index.type,index,
        ('Error in map index: method call ' +
         'returns more than one value.'),
        progText)

    un_function_called_to_read_from_type = unwrap_function_call_type_checker(
        toReadFrom.type,toReadFrom,
        ('Error in map toReadFrom: method call ' +
         'returns more than one value.'),
        progText)

    
    if not isValueType(un_function_called_index_type):
        errMsg = '\nYou can only index into a map using Text, TrueFalse, ';
        errMsg += 'or Number.  Instead, your index has type '
        errMsg += dict_type_to_str(un_function_called_index_type) + '.\n';
        astErrorNodes = [ index ];
        return True,None,errMsg,astErrorNodes;

    if is_empty_map(un_function_called_to_read_from_type):
        # reading from a value that is empty
        errMsg = '\nYou cannot read from an empty map.\n';
        astErrorNodes = [ toReadFrom ];
        return True, None, errMsg, astErrorNodes;

    # ensure that the type of the index we are reading from in
    # readingFrom matches the type of the index actually doing the
    # reading.
    toReadFromIndexType = getMapIndexType(un_function_called_to_read_from_type);
    indexType = un_function_called_index_type;
    if checkTypeMismatch(index,toReadFromIndexType,indexType,typeStack,progText):
        errMsg = '\nError reading from map.  You were supposed to index into the ';
        errMsg += 'map with an indexer of type [ ' + dict_type_to_str(toReadFromIndexType) + ' ].  ';
        errMsg += 'Instead, you indexed in with type [ ' + dict_type_to_str(indexType) + ' ].\n';
        astErrorNodes = [ toReadFrom, index ];
        return True, None, errMsg, astErrorNodes;
    
    statementType = getMapValueType(un_function_called_to_read_from_type)
    return False,statementType,None,None;

def typeCheckListBracket(toReadFrom,index,typeStack,progText):
    '''
    @see typeCheckMapBracket
    '''
    un_function_called_index_type = unwrap_function_call_type_checker(
        index.type,index,
        ('Error in list index: method call ' +
         'returns more than one value.'),
        progText)
    
    un_function_called_to_read_from_type = unwrap_function_call_type_checker(
        toReadFrom.type,toReadFrom,
        ('Error in list toReadFrom: method call ' +
         'returns more than one value.'),
        progText)
    
    if is_empty_list(un_function_called_to_read_from_type):
        errMsg = '\nError indexing into empty list.\n';
        astErrorNodes = [ toReadFrom ];
        return True, None, errMsg, astErrorNodes;

    if not is_number(un_function_called_index_type):
        errMsg = '\nError.  Can only index into a list using a number.  ';
        errMsg += ('Instead, you used a type [ ' +
                   dict_type_to_str(un_function_called_index_type) +
                   ' ].\n')
        astErrorNodes = [ index ];
        return True, None, errMsg, astErrorNodes;

    # no type error that we can catch.  Return that the statement will
    # have value of whatever is being accessed.
    listValType = getListValueType(un_function_called_to_read_from_type)
    return False,listValType,None,None;

def typeCheckMessageSequencesGlobals(msgSeqSectionNode,progText,typeStack):
    '''
    Need to ensure that all of the globals defined do not rely on
    variables that aren't in the type stack.  (Ie, initializers for
    message sequence globals can only be from shared global
    variables.)  Just relying on type checking by the time we get to
    type checking endpoint functions does not work because by then
    endpoint globals are already on the type stack.  Therefore, call
    this function first (and early).

    Note: cannot have any external arguments into message sequences,
    so throw error here if do.
    
    @see comment in addSequenceGlobals for a further discussion.
    '''
    for msgSeqNode in msgSeqSectionNode.children:
        msgSeqGlobalsNode = msgSeqNode.children[1];
        typeStack.pushContext();
        for declNode in msgSeqGlobalsNode.children:
            declNode.typeCheck(progText,typeStack,True);
            if is_external(declNode.type):
                err_msg = 'Externals may not appear in sequence peered data'
                errorFunction(
                    err_msg,[declNode],[declNode.lineNo],progText)

        typeStack.popContext();


def typeCheckMessageSequencesEndpoint(msgSeqSectionNode,progText,typeStack):
    '''
    Type checks the bodies of all message sequences for the current
    endpoint.  For each sequence, create a typestack context, loading
    all shared variables into it (including those passed into message
    send function).

    Then, type check all functions for the current enpdoint name.

    When type checking, be careful to throw an error if a function
    object is tried to be used as shared.  Similarly, do not load
    function object into shared section of other endpoint.
    '''

    if msgSeqSectionNode.label != AST_MESSAGE_SEQUENCE_SECTION:
        errMsg = '\nBehram error: should pass message sequence ';
        errMsg += 'section node as first argument to ';
        errMsg += 'typeCheckMessageSequencesEndpoint.  Instead, got: "';
        errMsg += msgSeqSectionNode.label + '"\n';
        print(errMsg);
        assert(False);

    currentEndpointName = typeStack.currentEndpointName;
    
    # perform the type checking of function bodies for sequences
    for msgSeqNode in msgSeqSectionNode.children:
        addSequenceGlobals(msgSeqNode,progText,typeStack,currentEndpointName);
        typeCheckMessageFunctions(msgSeqNode,progText,typeStack,currentEndpointName);
        removeSequenceGlobals(typeStack);

        
def typeCheckMessageFunctions(msgSeqNode,progText,typeStack,currentEndpointName):
    '''
    For each message function in the message sequence that belongs to
    currentEndpointName, type check its body.
    '''
    otherEndpointName = typeStack.endpoint1;
    if typeStack.endpoint1 == currentEndpointName:
        otherEndpointName = typeStack.endpoint2;

    onCompleteSeenNode = None;
    msgSeqFunctionsNode = msgSeqNode.children[2];
    
    sequenceNameTuples = [];
    for msgSeqFuncNode in msgSeqFunctionsNode.children:
        endpointName = msgSeqFuncNode.children[0].value;
        funcName = msgSeqFuncNode.children[1].value;
        sequenceNameTuples.append( (endpointName,funcName) );


    typeStack.sequenceSectionNameTuples= sequenceNameTuples;
    typeStack.inSequencesSection = True;
    for msgSeqFuncNode in msgSeqFunctionsNode.children:
        # keeps line numbers straight
        msgSeqFuncNode.lineNo = msgSeqFuncNode.children[0].lineNo;

        # checks that each 
        if isEndpointSequenceFunction(msgSeqFuncNode,currentEndpointName):
            name = msgSeqFuncNode.children[1].value;

            if ((msgSeqFuncNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION) or
                (msgSeqFuncNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION)):
                # checking that onComplete node does not appear after 
                if onCompleteSeenNode != None:
                    errMsg = 'Error: You must specify your onComplete function ';
                    errMsg += 'after your other message sequence functions.';
                    errNodes = [onCompleteSeenNode,msgSeqFuncNode];
                    errLineNos = [ x.lineNo for x in errNodes ];
                    errorFunction(errMsg,errNodes,errLineNos,progText);
            
            if msgSeqFuncNode.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
                msgBodyNode = msgSeqFuncNode.children[3];
            elif msgSeqFuncNode.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
                msgBodyNode = msgSeqFuncNode.children[2];
            elif msgSeqFuncNode.label == AST_ONCOMPLETE_FUNCTION:
                msgBodyNode = msgSeqFuncNode.children[2];

                typeStack.inOnComplete = True;
                
                if onCompleteSeenNode != None:
                    errMsg = 'Error: you cannot specify two onComplete functions ';
                    errMsg += 'for the same endpoint in a single message sequence.  ';
                    errNodes = [onCompleteSeenNode,msgSeqFuncNode];
                    errLineNos = [onCompleteSeenNode.lineNo,msgSeqFuncNode.lineNo];
                    errorFunction(errMsg,errNodes,errLineNos,progText);
                onCompleteSeenNode = msgSeqFuncNode;
            else:
                errMsg = '\nBehram error: Unknown label when expecting ';
                errMsg += 'message function in typeCheckMessageFunctions.\n';
                print(errMsg);
                assert(False);

            typeStack.pushContext();
            
            # when type check body, need to keep track of current
            # function so can ensure return type is valid.
            typeStack.addCurrentFunctionNode(msgSeqFuncNode);
            msgBodyNode.typeCheck(progText,typeStack,False);
            typeStack.popContext();

            if msgSeqFuncNode.label == AST_ONCOMPLETE_FUNCTION:
                typeStack.inOnComplete = False;
                
            
        elif isEndpointSequenceFunction(msgSeqFuncNode,otherEndpointName):
            pass;
        else:
            # means that this function's name declaration had an
            # incorrect endpoint name.  Throw an error.
            errMsg = 'Error.  Must precede message functions with ';
            errMsg += 'a valid endpoint name (either "' + otherEndpointName;
            errMsg += '" or "' + currentEndpointName + '").';
            errorFunction(errMsg,[msgSeqFuncNode],[msgSeqFuncNode.lineNo],progText);

    typeStack.inSequencesSection = False;
    typeStack.sequenceSectionNameTuples = [];
    
            
def removeSequenceGlobals(typeStack):
    '''
    Complements addSequenceGlobals.  Discards extra context that
    addSequenceGlobals creates.
    '''
    typeStack.popContext();

    
def addSequenceGlobals(msgSeqNode,progText,typeStack,currentEndpointName):
    '''
    @param {AstNode} msgSeqNode --- Should have label
    AST_MESSAGE_SEQUENCE.

    @param {AstTypeStack} typeStack

    @param {String} currentEndpointName

    Runs through variables whose lifetimes are only for the scope of
    the message sequence and adds them to context.  (Note: this
    includes any variables that are passed in through the initial
    message send function, however, the proscription against function
    objects does not apply if the function object is used by the same
    endpoint as uses it later.)

    Remember to call removeSequenceGlobals after calling this
    function, or you'll end up with a garbage context on the
    typeStack.
    '''
    typeStack.pushContext();

    if msgSeqNode.label != AST_MESSAGE_SEQUENCE:
        errMsg = '\nBehram error: should only add globals to a sequence.\n';
        print(errMsg);
        assert(False);

    # add variables from variables explicitly shared at top of sequence.
    globalsSectionNode = msgSeqNode.children[1];
    for declNode in globalsSectionNode.children:
        # note: we know that all of these sequence globals rely on
        # valid data (ie, shared variable data and constants) because
        # of call to typeCheckMessageSequencesGlobals that we
        # performed before actually type checking either endpoint.  if
        # had not performed this call because the type stack we are
        # working with now contains all of an endpoint's global
        # variables, we may have gotten into trouble if our sequence
        # global variable relied on an endpoint global variable that
        # just happened to be in type stack.

        # should add the node to the newly-pushed context.
        declNode.typeCheck(progText,typeStack,False);
        
        if isFunctionType(declNode.type):
            errMsg = 'Error with sequence shared variables.  You cannot share ';
            errMsg += 'a function object across multiple nodes.';
            errNodes = [declNode];
            astLineNos = [declNode.lineNo];
            errorFunction(errMsg,errNodes,astLineNos,progText);

    # add variables from variables that are shared by being arguments
    # to send message.
    msgSequenceFunctionsNode = msgSeqNode.children[2];
    msgSendNode = msgSequenceFunctionsNode.children[0];
    msgSendNodeEndpointName = msgSendNode.children[0];
    msgSendEndpointName = msgSendNodeEndpointName.value;
    argList = msgSendNode.children[2];

    # include each of the arguments to the message send function as
    # sequence-global variables.
    if msgSendEndpointName == currentEndpointName:
        # do not add function objects to context when type check them
        argList.typeCheck(progText,typeStack,False);
    else:
        # add function objects to context when type check them
        argList.typeCheck(progText,typeStack,True);


def unwrap_function_call_type_checker(type_dict,node,err_msg,prog_text):
    # function calls have additional level of indirection in type
    # dict.  however, we still want to treat function calls that
    # return only a single value as though there types are just
    # the types of that single value.  unwrapping the function
    # call with the command at bottom takes care of this.
    un_function_called_type, more_in_tuple = get_single_type_if_func_call_reg_type(
        type_dict)

    if more_in_tuple:
        errorFunction(err_msg,[node],[node.lineNo],prog_text)

    return un_function_called_type

        
def _check_single_assign(
    to_assign_to_node,rhs_node,to_assign_to_index,
    progText,typeStack,avoidFunctionObjects):
    '''
    @param{AstNode} to_assign_to_node --- Type check has already been
    called on this element.
    
    @param{AstNode} rhs_node --- Type check has already been called on
    this element
    
    @param{Int} to_assign_to_index --- If rhs_node is a function
    call, function may return a tuple.  In this case, we're only
    supposed to type check the return value of the
    to_assign_to_counter-th element of the return type against
    to_assing_to_node's type.

    Calls errorFunction on any type check errors.
    '''

    if ((to_assign_to_node.label != AST_BRACKET_STATEMENT) and
        (to_assign_to_node.label != AST_IDENTIFIER) and
        (to_assign_to_node.label != AST_EXT_ASSIGN_FOR_TUPLE) and
        (to_assign_to_node.label != AST_EXT_COPY_FOR_TUPLE) and
        (to_assign_to_node.label != AST_DOT_STATEMENT)):
        
        # This disallows the following types of calls:
        #   public function a () returns External int{}
        #   a() = 3;
        #
        # But these were disallowed anyways because you must use
        # extAssign and extCopy to affect externals.
        err_msg = 'Error in assignment statement.  '
        
        if ((rhs_node.label == AST_FUNCTION_CALL) and
            (len(rhs_node.type) > 1)):
            err_msg += 'When trying to assign to the '
            err_msg += str(to_assign_to_index + 1) + ' element '

        err_msg += 'on the left hand side of the = sign, must '
        err_msg += 'either be a variable or a bracket statment.'

        err_nodes = [to_assign_to_node]
        err_line_nos = [to_assign_to_node.lineNo]
        
        errorFunction(err_msg,err_nodes,err_line_nos,progText)
        
    elif to_assign_to_node.label == AST_BRACKET_STATEMENT:
        # check that the root of the bracket statement is an
        # identifier

        lhs_bracket = to_assign_to_node.children[0]
        if lhs_bracket.label != AST_IDENTIFIER:
            err_msg = 'When performing assignment, left hand side of '
            err_msg += 'assignment must be rooted in a variable.  '
            err_nodes = [to_assign_to_node]
            err_line_nos = [to_assign_to_node.lineNo]
            errorFunction(err_msg,err_nodes,err_line_nos,progText)


    # note that this will handle brackets okay because their types the
    # entire statement will have the type of the list/map value.
    lhs_type = to_assign_to_node.type
    rhs_type = rhs_node.type
    
    if rhs_node.label == AST_FUNCTION_CALL:
        
        if not is_wildcard_type(rhs_type):
            if isinstance(rhs_type, dict):
                #### FIXME: ugly code because can't figure out whether
                #### type of function call is {Type: [...]} or [..].
                #### handling both cases in an ugly manner.
                actual_type = rhs_type['Type']
                if isinstance(actual_type,list):
                    rhs_type = actual_type

        
            if to_assign_to_index >= len(rhs_type):
                err_msg = 'Error in assignment statement.  The function '
                err_msg += 'call on the right only returns ' + str(len(rhs_node.type))
                err_msg += ' element.  But you are trying to assign to at least '
                err_msg += str(to_assign_to_index + 1) + ' elements.'

                err_nodes = [to_assign_to_node]
                err_line_nos = [to_assign_to_node.lineNo]
                errorFunction(err_msg,err_nodes,err_line_nos,progText)


            rhs_type = rhs_type[to_assign_to_index]

            
    if checkTypeMismatch(to_assign_to_node,lhs_type,rhs_type,typeStack,progText):
        err_msg = 'Error in assignment statement.  '

        if ((rhs_node.label == AST_FUNCTION_CALL) and
            (len(rhs_node.type) > 1)):
            err_msg += 'The '
            err_msg += str(to_assign_to_index + 1) + ' element of '
            err_msg += 'the left hand side of the assignment statment '
        else:
            err_msg += 'The left hand side side of the assignment statement '
            
        err_msg += 'has type ' + dict_type_to_str(lhs_type)
        err_msg += ', but the right hand side has '
        err_msg += 'type ' + dict_type_to_str(rhs_type) + '.'

        err_nodes = [to_assign_to_node]
        err_line_nos = [to_assign_to_node.lineNo]
        errorFunction(err_msg, err_nodes,err_line_nos,progText);

    
        
    # check controls by statement to ensure writes are okay
    to_assign_to_var_name = to_assign_to_node.value
    if to_assign_to_node.label == AST_BRACKET_STATEMENT:
        to_assign_to_var_name = to_assign_to_node.children[0].value

    unused,controlled_by = typeStack.getIdentifierType(to_assign_to_var_name);
    if (controlled_by != None) and (controlled_by != TYPE_NOTHING):
        if (typeStack.currentEndpointName != controlled_by):
            err_msg = 'Error when trying to assign to ' + to_assign_to_var_name
            err_msg += ' while in ' + typeStack.currentEndpointName + '\'s '
            err_msg += 'body.  ' + typeStack.currentEndpointName + ' does not '
            err_msg += 'control this variable (is not allowed to write to this '
            err_msg += 'variable) because of a controls annotation in the Shared '
            err_msg += 'section.  Only ' + typeStack.getOtherEndpointName()
            err_msg += ' is allowed to write to it.'

            err_nodes = [to_assign_to_node]
            err_line_nos = [to_assign_to_node.lineNo]
            errorFunction(err_msg,err_nodes,err_line_nos,progText)
            
    # FIXME: unsure how to handle assignments to externals 
