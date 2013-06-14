#!/usr/bin/env python

import sys, os


from waldo.parser.ast.astLabels import *;
from typeStack import TypeStack;
from typeStack import NameTypeTuple;
from functionDeps import FunctionDeps;
import waldo.parser.ast.typeCheck.templateUtil as templateUtil

def slicer(node,functionDeps=None,typeStack=None):
    '''
    @param{AstNode} node --- An astNode
    
    @param{None or array} functionDeps --- An array of FunctionDep
    classes.  Each one mentions which variables the function depends
    on.  Should only be none for initial call.
    
    @returns{Array} (functionDeps).
    '''
    
    if functionDeps == None:
        if node.label != AST_ROOT:
            errMsg = '\nBehram error in slicer.  Should only ';
            errMsg += 'have empty functionDeps on root node.\n';
            print(errMsg);
            assert(False);
        functionDeps = [];
        
        
    if node.label == AST_ROOT:
        # create two separate type stacks for each endpoint
        sharedSecNode = node.children[3];

        endpoint1Node = node.children[4];
        endpoint2Node = node.children[5];
        
        end1Name = endpoint1Node.children[0].value;
        end2Name = endpoint2Node.children[0].value;
        
        typeStack1 = TypeStack(typeStack);
        typeStack1.addMyEndpointName(end1Name);
        typeStack1.addOtherEndpointName(end2Name);

        typeStack2 = TypeStack(typeStack);
        typeStack2.addMyEndpointName(end2Name);
        typeStack2.addOtherEndpointName(end1Name);

        # both typestacks should hold shared variables...load shared
        # variables into typestack1 and then copy the ntt-s over to
        # typeStack2.

        # first push a context for shared variables onto each.
        typeStack1.pushContext(TypeStack.IDENTIFIER_TYPE_SHARED,None);
        typeStack2.pushContext(TypeStack.IDENTIFIER_TYPE_SHARED,None);

        # keep track of ntt-s created on typestack1 in shared.
        slicer(sharedSecNode,functionDeps,typeStack1);
        sharedReadsDict = typeStack1.getTopStackIdentifierDict();
        
        ##### copy over the shared variables from typeStack1 to
        ##### typeStack2
        
        # this context should never get removed because want shared
        # section variables to always be accessible.
        for sharedNttKey in sharedReadsDict.keys():
            sharedNtt = sharedReadsDict[sharedNttKey];
            typeStack2.addIdentifierAsNtt(sharedNtt);

        # now go through each endpoint node
        slicer(endpoint1Node,functionDeps,typeStack1);
        slicer(endpoint2Node,functionDeps,typeStack2);

        msgSeqSecNode = node.children[6];
        sliceMsgSeqSecNode(msgSeqSecNode,functionDeps,typeStack1,typeStack2);
        
    elif ((node.label == AST_ONCREATE_FUNCTION) or (node.label == AST_PUBLIC_FUNCTION) or
          (node.label == AST_PRIVATE_FUNCTION)):

        funcName = node.children[0].value;
        if node.label == AST_ONCREATE_FUNCTION:
            funcDeclArgsIndex = 1;
            funcBodyIndex = 2;
        elif (node.label == AST_PRIVATE_FUNCTION) or (node.label == AST_PUBLIC_FUNCTION):
            funcDeclArgsIndex = 2;
            funcBodyIndex = 3;
        else:
            errMsg = '\n\nBehram error.  Should only handle oncreate,private,public ';
            errMsg += 'functions in this branch of slicer.py.\n';
            print(errMsg);
            assert(False);

        # create a new function dependency on the stack.
        fDep = FunctionDeps(typeStack.hashFuncName(funcName),
                            funcName,typeStack.mEndpointName,
                            node,False);
        functionDeps.append(fDep);

        
        # set up new context so that identifiers that are added will
        # be added as function arguments.
        typeStack.pushContext(
            TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT,fDep);
        declArgsNode = node.children[funcDeclArgsIndex]
        slicer(declArgsNode,functionDeps,typeStack);

        # when go through function body, need to change label as of
        # type stack to be local so that subsequent identifiers that
        # are added are added as local.
        typeStack.changeLabelAs(TypeStack.IDENTIFIER_TYPE_LOCAL);
        funcBodyNode = node.children[funcBodyIndex];
        slicer(funcBodyNode,functionDeps,typeStack);
                
        typeStack.popContext();

    elif node.label == AST_WHILE_STATEMENT:
        bool_cond = node.children[0]
        body = node.children[1]

        slicer(bool_cond,functionDeps,typeStack)
        slicer(body,functionDeps,typeStack)
        
    elif ((node.label == AST_BREAK) or
          (node.label == AST_CONTINUE)):
        pass
    
    elif node.label == AST_SELF:
        pass
    
    elif node.label == AST_FOR_STATEMENT:
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
            identifierNameNode = node.children[identifierNodeIndex];
            identifierName = identifierNameNode.value;
            isMute = isMutable(typeNode);

            ntt = typeStack.addIdentifier(identifierName,isMute,
                                          typeNode);

        identifierNode = node.children[identifierNodeIndex];
        toIterateNode = node.children[toIterateNodeIndex];
        forBodyNode = node.children[forBodyNodeIndex];
        slicer (identifierNode,functionDeps,typeStack);
        slicer (toIterateNode,functionDeps,typeStack);
        slicer (forBodyNode,functionDeps,typeStack);

    elif node.label == AST_IN_STATEMENT:
        lhsNode = node.children[0];
        rhsNode = node.children[1];
        slicer(lhsNode,functionDeps,typeStack);
        slicer(rhsNode,functionDeps,typeStack);

    elif node.label == AST_MAP_ITEM:
        lhsNode = node.children[0];
        rhsNode = node.children[1];
        slicer(lhsNode,functionDeps,typeStack);
        slicer(rhsNode,functionDeps,typeStack);

        
    elif ((node.label == AST_APPEND_STATEMENT) or
          (node.label == AST_REMOVE_STATEMENT)):
        toAppendToNode = node.children[0];
        toAppendNode = node.children[1];
        slicer(toAppendToNode,functionDeps,typeStack);
        slicer(toAppendNode,functionDeps,typeStack);
        # FIXME: Need to improve slicing for append/remove statement.
        # Should specify that toAppendToNode got written to.

    elif node.label == AST_INSERT_STATEMENT:
        to_insert_into_node = node.children[0]
        to_insert_index_node = node.children[1]
        what_to_insert_node = node.children[2]

        slicer(to_insert_into_node,functionDeps,typeStack)
        slicer(to_insert_index_node,functionDeps,typeStack)
        slicer(what_to_insert_node,functionDeps,typeStack)
        

    elif node.label == AST_REFRESH:
        # don't need to do anything for refresh statement.
        # it doesn't touch any additional data
        pass;
        
    elif node.label == AST_ENDPOINT_GLOBAL_SECTION:
        # note: do not pop the context, because want globals to always
        # be available.
        typeStack.pushContext(TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL,None);
        for child in node.children:
            slicer(child,functionDeps,typeStack);
        
    elif node.label == AST_SHARED_SECTION:
        # context for shared section should have already been added
        for sharedDeclNode in node.children:
            slicer(sharedDeclNode,functionDeps,typeStack);

            
    elif node.label == AST_ANNOTATED_DECLARATION:
        idName = node.children[2].value;
        typeNode = node.children[1];
        typeStack.addIdentifier(idName,isMutable(typeNode),typeNode);

        # gets passed to emitter
        typeStack.annotateNode(node.children[2],idName);

    elif ((node.label == AST_JUMP) or
          (node.label == AST_JUMP_COMPLETE)):
        # any control flow reached through a jump statement would have
        # been reached anyways.
        pass;
        
    elif node.label == AST_RETURN_STATEMENT:
        # should keep track of all identifiers that could be touched
        # by returning.

        return_list = node.children[0]

        readIndex = typeStack.getReadIndex();
        for childNode in return_list.children:
            slicer(childNode,functionDeps,typeStack);
            
        returnStatementReads = typeStack.getReadsAfter(readIndex);
        typeStack.addReturnStatement(returnStatementReads);

        
    elif node.label == AST_FUNCTION_CALL:
        funcCallNameNode = node.children[0]
        funcCallName = funcCallNameNode.value

        func_on_endpoint_object = False
        if funcCallNameNode.label == AST_DOT_STATEMENT:
            func_on_endpoint_object = True
            # need to annotate the endpoint passed in.  (We do the
            # same thing in the AST_IDENTIFIER section, but that won't
            # get called this way because the function call sidesteps
            # going through the identifier calls
            pre_dot_node = funcCallNameNode.children[0]            
            slicer(pre_dot_node,functionDeps,typeStack)

        funcArgListNode = node.children[1];
        
        # an aray of arrays....each element array contains the reads
        # performed on the corresponding positional argument that gets
        # passed into the function.
        funcArgReads = [];
        for funcArgNode in funcArgListNode.children:

            readIndex = typeStack.getReadIndex();
            slicer(funcArgNode,functionDeps,typeStack);
            argumentReads = typeStack.getReadsAfter(readIndex);
            
            funcArgReads.append(argumentReads);


        if func_on_endpoint_object:
            # the function is being called off of an endpoint object:
            # ie, endpt.func(), rather than being called from a
            # function object or from being called just as a function,
            # eg., some_func()

            # BIG FIXME:
            # notate the endpoint that the function is being called on
            # as a write.  and all function arguments passed to it as
            # a dependent read.  This is probably not the best thing
            # to do long term.  Better to import and use type
            # checking.
            # ntt = typeStack.getIdentifier(identifier_name)
            # typeStack.addToVarReadSet(ntt)
            # typeStack.addReadsToVarReadSet(ntt,funcArgReads)

            # When moved to v4, realized could ignore reads vs write
            # static dependency analyses.
            pass
            
        else:
            # the function call is either on a function object or a
            # function that was defined on a locally defined function
            # object.
            idExists = typeStack.getIdentifier(funcCallName);
            if idExists == None:
                # means that we are making a function call to an existing
                # function, not to a function object.
                typeStack.addFuncCall(
                    typeStack.hashFuncName(funcCallName),funcArgReads)
            else:
                # means that this is a function call being made on a
                # function object.  annotate the func call node
                typeStack.addFuncObjectCall(idExists) # idExists is an ntt
                typeStack.annotateNode(funcCallNameNode,funcCallName)

            

    elif node.label == AST_ASSIGNMENT_STATEMENT:

        # contains the tuple that we are assigning in to (note that unless
        # we're assigning from a function call, the tuple will only ever
        # have one vaue).
        to_assign_to_tuple_node = node.children[0]

        # the rhs of the assignment statement
        to_assign_from_node = node.children[1]


        # notes all the dependencies we get from rhs
        from_read_index = typeStack.getReadIndex()
        slicer(to_assign_from_node,functionDeps,typeStack)
        reads_made_by_to_assign_from = typeStack.getReadsAfter(from_read_index)


        for to_assign_to_node in to_assign_to_tuple_node.children:
            actual_assign_node = to_assign_to_node
            if ((to_assign_to_node.label == AST_EXT_ASSIGN_FOR_TUPLE) or
                (to_assign_to_node.label == AST_EXT_COPY_FOR_TUPLE)):
                actual_assign_node = to_assign_to_node.children[0]

            if actual_assign_node.label == AST_IDENTIFIER:

                nodeName = actual_assign_node.value
                # gets passed to emitter
                typeStack.annotateNode(actual_assign_node,nodeName)

                # tell typeStack that this variable may get written to and
                # its written to value depends on the values that the rhs reads made.
                ntt = typeStack.getIdentifier(nodeName)
                typeStack.addToVarReadSet(ntt)
                typeStack.addReadsToVarReadSet(ntt,reads_made_by_to_assign_from)

            elif actual_assign_node.label in [AST_DOT_STATEMENT,AST_BRACKET_STATEMENT]:
                
                root_identifier_node = get_root_node_from_bracket_dot(actual_assign_node)
                node_name = root_identifier_node.value

                # adds a globally unique label to root_identifier_node
                typeStack.annotateNode(root_identifier_node,node_name)
                
                ntt = typeStack.getIdentifier(node_name)
                typeStack.addToVarReadSet(ntt)

                
                typeStack.addReadsToVarReadSet(
                    ntt,
                    reads_made_by_to_assign_from)

                # don't forget to include reads made for instance to
                # index into maps/lists
                slicer(actual_assign_node,functionDeps,typeStack)

            else:
                errMsg = '\nError in assignment statement.  LHS is only '
                errMsg += 'allowed to be a bracket statement, identifier, '
                errMsg += 'or extAssign/extCopy tuple statement.\n'
                print(errMsg);
                assert(False);


            
            
    elif ((node.label == AST_STRING) or (node.label == AST_NUMBER) or
          (node.label == AST_BOOL)):
        # nothing to do on literals
        for child in node.children:
            slicer(child,functionDeps,typeStack);


    elif ((node.label == AST_AND) or (node.label == AST_OR) or
          (node.label == AST_BOOL_EQUALS) or (node.label == AST_BOOL_NOT_EQUALS) or
          (node.label == AST_GREATER_THAN) or (node.label == AST_GREATER_THAN_EQ) or
          (node.label == AST_LESS_THAN) or (node.label == AST_LESS_THAN_EQ) or
          (node.label == AST_PLUS) or (node.label == AST_MINUS) or
          (node.label == AST_MULTIPLY) or (node.label == AST_DIVIDE)):
        # nothing to do on binary operators
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif ((node.label == AST_PRINT) or (node.label == AST_CONDITION_STATEMENT) or
          (node.label == AST_IF_STATEMENT) or (node.label == AST_ELSE_IF_STATEMENTS) or
          (node.label == AST_ELSE_IF_STATEMENT) or (node.label == AST_ELSE_STATEMENT) or
          (node.label == AST_NOT_EXPRESSION) or (node.label == AST_BOOLEAN_CONDITION) or
          (node.label == AST_LIST)  or (node.label == AST_MAP) or (node.label == AST_LEN) or
          (node.label == AST_BRACKET_STATEMENT) or (node.label == AST_RANGE)):


        # nothing to do on unary operators
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif node.label == AST_SIGNAL_CALL:
        signal_func_args_node = node.children[0]

        for func_arg_node in signal_func_args_node.children:
            slicer(func_arg_node,functionDeps,typeStack)
            
    elif ((node.label == AST_FUNCTION_BODY_STATEMENT) or
          (node.label == AST_ENDPOINT) or
          (node.label == AST_ENDPOINT_BODY_SECTION) or
          (node.label == AST_ENDPOINT_BODY_SECTION) or
          (node.label == AST_ENDPOINT_FUNCTION_SECTION) or
          (node.label == AST_FUNCTION_BODY)):
        # nothing to do on these structural node labels.
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif node.label == AST_FUNCTION_DECL_ARGLIST:
        # actually add each argument to current type stack.
        argumentNumber = 0;
        for child in node.children:
            # each child is a function decl arg
            typeNode = child.children[0];
            nameNode = child.children[1];
            argName = nameNode.value;

            ntt = typeStack.addIdentifier(argName,
                                          isMutable(typeNode),
                                          typeNode,
                                          TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT,
                                          argumentNumber);

            # gets passed to emitter
            typeStack.annotateNode(nameNode,argName);
            
            typeStack.addFuncArg(ntt);
            
            argumentNumber +=1;

            

    elif node.label == AST_MESSAGE_SEND_SEQUENCE_FUNCTION:
        # sliceMsgSeqSecNode already handles adding a function dep and
        # context.  so do not need to do that here.
        msgBodyNode = node.children[3];
        for childNode in msgBodyNode.children:
            slicer(childNode,functionDeps,typeStack);
            
    elif node.label == AST_MESSAGE_RECEIVE_SEQUENCE_FUNCTION:
        # sliceMsgSeqSecNode already handles adding a function dep and
        # context.  so do not need to do that here.
        msgBodyNode = node.children[2];
        for childNode in msgBodyNode.children:
            slicer(childNode,functionDeps,typeStack);

    elif node.label == AST_ONCOMPLETE_FUNCTION:
        onCompleteBodyNode = node.children[2];
        for childNode in onCompleteBodyNode.children:
            slicer(childNode,functionDeps,typeStack);

            
    elif node.label == AST_IDENTIFIER:
        identifierName = node.value;

        if not typeStack.isEndpointName(identifierName):
            ntt = typeStack.getIdentifier(identifierName);
            typeStack.addRead(ntt);

        # gets passed to emitter
        typeStack.annotateNode(node,identifierName);

            
    elif node.label == AST_DECLARATION:
        nodeTypeNode = node.children[0];
        nameNode = node.children[1];
        nodeName = nameNode.value;
        isMute = isMutable(nodeTypeNode);

        ntt = typeStack.getIdentifier(nodeName);
        if ntt == None:
            ntt = typeStack.addIdentifier(nodeName,isMute,nodeTypeNode);
            
        if len(node.children) == 3:
            # means that we are initializing the declaration too.
            initializationNode = node.children[2];
            
            readIndex = typeStack.getReadIndex();
            slicer(initializationNode,functionDeps,typeStack);

            initializationReads = typeStack.getReadsAfter(readIndex);

            # tell current function that this node exists.
            typeStack.addToVarReadSet(ntt);
            
            # tell current function that this node has the read and
            # write sets below.
            ntt = typeStack.getIdentifier(nodeName);
            typeStack.addReadsToVarReadSet(
                ntt,initializationReads);
            
        # gets passed to emitter
        typeStack.annotateNode(nameNode,nodeName);

    elif node.label == AST_NOT_EXPRESSION:
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif node.label == AST_TOTEXT_FUNCTION:
        for child in node.children:
            slicer(child,functionDeps,typeStack);

    elif node.label == AST_DOT_STATEMENT:
        pre_dot_node = node.children[0]
        slicer(pre_dot_node,functionDeps,typeStack)

        # FIXME: level of granularity on object accesses is just
        # enough so that a read/write on any part of the object
        # will be treated as a read/write on the entire object.
        # post_dot_node = node.children[1]
            
    elif ((node.label == AST_EXT_ASSIGN) or
          (node.label == AST_EXT_COPY)):
        
        from_node = node.children[0]
        to_node = node.children[1]


        read_index = typeStack.getReadIndex()
        slicer(from_node,functionDeps,typeStack)
        assign_reads = typeStack.getReadsAfter(read_index)

        to_node_read_index = typeStack.getReadIndex()
        slicer(to_node,functionDeps,typeStack)
        to_node_assign_reads = typeStack.getReadsAfter(to_node_read_index)
        

        # FIXME: got rid of logic for dependency analysis here.

        # to_node_name = to_node.value
        
        # # actually add the read and write on the to node.  do not have
        # # to add read on from node because we slice that.
        # to_node_ntt = typeStack.getIdentifier(to_node_name)
        # typeStack.addToVarReadSet(to_node_ntt)
        # typeStack.addReadsToVarReadSet(to_node_ntt,assign_reads)

        
        # annotate the to and from nodes so that the emitter can use
        # their globally unique names

        if to_node.label == AST_IDENTIFIER:
            to_node_name = to_node.value
            typeStack.annotateNode(to_node,to_node_name)

        if from_node.label == AST_IDENTIFIER:
            # copy does not necessarily require an identifier to be
            # copied from
            from_node_name = from_node.value
            typeStack.annotateNode(from_node,from_node_name)

    elif node.label == AST_EMPTY:
        pass
    else:
        warn_msg = '\nBehram error: in slicer, still need to '
        warn_msg += 'process label for ' + node.label + '\n'
        print(warn_msg)

        for child in node.children:
            slicer(child,functionDeps,typeStack);

    printWarning();
    return functionDeps;


def sliceMsgSeqSecNode(msgSeqSecNode,functionDeps,typeStack1,typeStack2):
    '''
    @param {AstNode} msgSeqSecNode --- with label msgSequenceSection...

    Runs through all message sequence nodes and adds their functions
    to functionDeps as well as their reads and writes to globals,
    locals, and shareds.
    '''
    for msgSeqNode in msgSeqSecNode.children:

        # pop context before exiting for loop.
        typeStack1.pushContext(TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,None);
        typeStack2.pushContext(TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,None);

        msgSeqFunctionsNode = msgSeqNode.children[2];

        # add the identifiers of sequence global variables
        # directly to each type stack.
        msgSeqGlobalsNode = msgSeqNode.children[1];
        for declGlobNode in msgSeqGlobalsNode.children:
            identifierNode = declGlobNode.children[1];
            identifierName = identifierNode.value;
            identifierTypeNode = declGlobNode.children[0];
            isMute = isMutable(identifierTypeNode);
            newNtt = typeStack1.addIdentifier(
                identifierName,isMute,identifierTypeNode,
                TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL);

            typeStack2.addIdentifierAsNtt(newNtt);
            
            # does not matter which type stack annotates the node
            typeStack1.annotateNode(identifierNode,identifierName);
            


        # now grab any arguments to first function and insert them as
        # sequence globals.
        firstFuncNode = msgSeqFunctionsNode.children[0];
        firstFuncDeclArgsNode = firstFuncNode.children[2];
        functionArgs = [];
        for funcDeclArgNode in firstFuncDeclArgsNode.children:
            typeNode = funcDeclArgNode.children[0];
            isMute = isMutable(typeNode);
            identifierNode = funcDeclArgNode.children[1];
            identifierName = identifierNode.value;
            newNtt = typeStack1.addIdentifier(
                identifierName,isMute,typeNode,
                TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT);
            
            typeStack2.addIdentifierAsNtt(newNtt);
            functionArgs.append(newNtt);

            # does not matter which type stack annotates the node
            typeStack2.annotateNode(identifierNode,identifierName);

        return_node_names = []
        first_func_return_nodes = firstFuncNode.children[4]
        for decl_arg_node in first_func_return_nodes.children:
            type_node = decl_arg_node.children[0]
            is_mute = isMutable(type_node)

            id_name_node = decl_arg_node.children[1]
            id_name = id_name_node.value
            new_ntt = typeStack1.addIdentifier(
                id_name, is_mute, type_node,
                TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)

            typeStack2.addIdentifierAsNtt(new_ntt)
            typeStack2.annotateNode(id_name_node,id_name)
            return_node_names.append(
                id_name_node.sliceAnnotationName)
            

            
        # want to ensure that the first function has all the
        # read/write dependencies.  Need to know which type stack to
        # use for it.
        firstFuncEndpointName = firstFuncNode.children[0].value;
        if firstFuncEndpointName == typeStack1.mEndpointName:
            firstFuncEndpointTypeStack = typeStack1;
            secondFuncEndpointTypeStack = typeStack2;
        elif firstFuncEndpointName == typeStack2.mEndpointName:
            firstFuncEndpointTypeStack = typeStack2;
            secondFuncEndpointTypeStack = typeStack1;
        else:
            errMsg = '\nBehram error.  could not match enpdoint specified ';
            errMsg += 'by function as "' + firstFuncEndpointName + '" to ';
            errMsg += 'existing type stack.\n';
            print(errMsg);
            assert(False);


        # now, run through each function.  Importantly, ensure that
        # all initializations of msg seq globals happens in first
        # function.  note: do not need to specially add arguments
        # because they're already in the context.
        for funcIndex in range(0,len(msgSeqFunctionsNode.children)):
            funcNode = msgSeqFunctionsNode.children[funcIndex];
            funcName = funcNode.children[1].value;
            
            endpointName = funcNode.children[0].value;
            typeStack = secondFuncEndpointTypeStack;
            otherTypeStack = firstFuncEndpointTypeStack;
            if endpointName == firstFuncEndpointName:
                typeStack = firstFuncEndpointTypeStack;
                otherTypeStack = secondFuncEndpointTypeStack;


            hashedFuncName = typeStack.hashFuncName(funcName);
            isOnComplete = False;
            if funcNode.label == AST_ONCOMPLETE_FUNCTION:
                # need to give oncomplete functions special names so
                # they do not collide.
                isOnComplete = True;
                msgSeqIdentifierNode = msgSeqNode.children[0];
                hashedFuncName = typeStack.onCompleteHashFuncName(
                    funcName,msgSeqIdentifierNode);

                # annotate onComplete functions
                typeStack.annotateOnComplete(funcNode,hashedFuncName);

            fDep = FunctionDeps(hashedFuncName,funcName,
                                typeStack.mEndpointName,
                                funcNode,isOnComplete);
            
            functionDeps.append(fDep);

            typeStack.pushContext(TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL,fDep);
            if funcIndex == 0:
                # for the msg send function, needs to know the
                # annotation names of nodes it might return.  
                fDep.msg_send_returns = return_node_names
                
                # special case the first function so that it contains
                # all the initializations of sequence globals
                for declGlobNode in msgSeqGlobalsNode.children:
                    slicer(declGlobNode,functionDeps,typeStack);

                # also, ensure that first function gets loaded with
                # its proper arguments.
                for funcArgNtt in functionArgs:
                    typeStack.addFuncArg(funcArgNtt);

            typeStack.changeLabelAs(TypeStack.IDENTIFIER_TYPE_LOCAL);
            # handle rest of function and body in slicer.
            slicer(funcNode,functionDeps,typeStack);

            # if there is a message receive function coming, then make
            # a function call to it explicitly.
            if funcIndex != (len(msgSeqFunctionsNode.children) -1):
                nextMsgFuncNode = msgSeqFunctionsNode.children[funcIndex+1];
                nextMsgName = nextMsgFuncNode.children[1].value;
                
                hashedFuncNameNextCall = otherTypeStack.hashFuncName(
                    nextMsgName);
                
                if nextMsgFuncNode.label == AST_ONCOMPLETE_FUNCTION:
                    # use special function hashes for oncomplete
                    # functions...can't just use the name
                    # "oncomplete," because might conflict with
                    # another sequence's onComplete
                    msgSeqIdentifierNode = msgSeqNode.children[0];

                    # need to ask the type stack associated with the
                    # oncomplete function's endpoint to do the
                    # hashing.  because oncomplete functions may
                    # appear in arbitrary order, can't just assume
                    # that otherTypeStack is the next onComplete
                    # function's type stack.
                    onCompleteEndpointIdentifierNode = nextMsgFuncNode.children[0];
                    onCompleteEndpointName = onCompleteEndpointIdentifierNode.value;
                    onCompleteOtherTypeStack = otherTypeStack;
                    if otherTypeStack.mEndpointName != onCompleteEndpointName:
                        onCompleteOtherTypeStack = typeStack;

                    hashedFuncNameNextCall = onCompleteOtherTypeStack.onCompleteHashFuncName(
                        nextMsgName,msgSeqIdentifierNode);

                typeStack.addFuncCall(
                    hashedFuncNameNextCall,
                    # note, message sequence functions do not take any
                    # arguments, so can just pass blank array.
                    []);  

            # remove the context added for latest function.
            typeStack.popContext();
            
        # pop the pushed contexts
        typeStack1.popContext();
        typeStack2.popContext();



HavePrinted = False;
def printWarning():
    global HavePrinted;
    if not HavePrinted:
        # all of these concern less conservative slicing algorithm.
        # when/if decide to switch back to that, then need to
        # re-consider all these problems.
        
        # warnMsg = '\nBehram error: need to write something ';
        # warnMsg += 'intelligent for slicing function call.\n';
        # print(warnMsg);
        # warnMsg = '\nBehram error: still need to write something ';
        # warnMsg += 'intelligent for message sequences.\n';
        # print(warnMsg);

        # warnMsg = '\nBehram error: still need to handle returns\' ';
        # warnMsg += 'subsequently being written to in mega-'
        # warnMsg += 'constructor in functionDeps.py.\n';
        # print(warnMsg);

        # warnMsg = '\nBehram error: handle post-it problem on ';
        # warnMsg += 'second monitor.\n';
        # print(warnMsg);
        
        HavePrinted = True;
    
def isMutable(nodeTypeNode):
    '''
    @returns{Bool} True if typeNode indicates this is a map or a list.
    False otherwise.
    '''
    if nodeTypeNode.label == AST_TYPE:
        if templateUtil.isListType(nodeTypeNode.type):
            return True;
        if templateUtil.isMapType(nodeTypeNode.type):
            return True;

    return False;


def reset():
    '''
    Ensures that all static variables are reset to their original values.
    '''
    NameTypeTuple.staticId = 0;



def get_root_node_from_bracket_dot(node):
    '''
    @param{AstNode} node --- Either a bracket node or a dot node.
    Otherwise, throws error.

    When we have an assignment statement, eg
    a[b][c].d, returns the identifier node of a.


    @returns{AstNode} --- An identifier node containing the name of
    the root-most value that is changing.  (In the above example,
    'a'.)
    
    '''

    if not (node.label in [AST_BRACKET_STATEMENT,
                           AST_DOT_STATEMENT]):
        err_msg = '\nBehram error.  Cannot slice in '
        err_msg += 'get_root_node_from_bracket_dot a non-'
        err_msg += 'bracket/dot node.\n'
        print err_msg
        assert(False)

    lhs_node = node.children[0]

    if lhs_node.label != AST_IDENTIFIER:

        if (lhs_node.label not in [AST_BRACKET_STATEMENT,
                                  AST_DOT_STATEMENT]):
            # FIXME: note that this disqualifies statements, such as
            # func_call()[0]
            err_msg = '\nBehram error in get_root_node_from_bracket_dot.  '
            err_msg += 'Expected an identifier node as first child of root/'
            err_msg += 'dot, but received something else.\n'
            print err_msg
            assert(False)

        else:
            lhs_node = get_root_node_from_bracket_dot(lhs_node)
    
        
    return lhs_node

