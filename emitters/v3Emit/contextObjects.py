#!/usr/bin/env python


def writeContextObjects(astRootNode):
    '''
    Each endpoint has its own unique context object that it uses to
    read data from, write data to, and copy when asked to begin an
    event.  This function returns the text for each of these context
    objects.

    @param {AstNode} astRootNode
    
    @returns {String}
    '''
    returner = '';
    allSharedIdentifiers = _getAllSharedIdentifiers(astRootNode);
    endpointNames = _getEndpointNames(astRootNode);

    for endpointName in endpointNames:
        returner += _writeEndpointContext(
            endpointName,allSharedIdentifiers,astRootNode);

    return returner;
    
def _writeEndpointContext(endpointName,sharedIdentifiers,astRoot):
    '''
    @param {String} endpointName
    @param {Array} sharedIdentifiers --- Each element is a string containing

    @returns {String} a string with the endpoint's context in it.
    '''
    print('\nBehram error: ignoring initializers for shared and endpoint global vars.\n');
    return '';
    
    


def _getEndpointNames(astRoot):
    returner = [];
    aliasSection = astRoot.children[1];
    returner.append(aliasSection.children[0].value);
    returner.append(aliasSection.children[1].value);
    return returner;
    

def _getAllSharedIdentifiers(astRoot):
    returner = [];
    
    sharedSectionNode = astRoot.children[3];
    for annotatedDeclarationNode in sharedSectionNode.children:
        # have an annotatedDeclarationNode for each shared variable.
        identifierNode = annotatedDeclarationNode.children[2];
        identifierNode._debugErrorIfHaveNoAnnotation('_getAllSharedIdentifiers');
        returner.append(identifierNode.sliceAnnotationName);

    return returner;
