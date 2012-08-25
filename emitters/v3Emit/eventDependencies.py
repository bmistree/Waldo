#!/usr/bin/env python

import emitUtils;


def specifyDependencies(fdepDict):
    '''
    @param {dictionary} fdepDict --- A dictionary mapping
    functionDep.funcName to functionDep objects, each of which was
    generated from slicing code. @see slice/functionDeps.py
    '''

    returner = """
_PROTOTYPE_EVENTS_DICT = {

""";


    for eventName in fdepDict.keys():
        fdep = fdepDict[eventName];
        returner += _emitIndividualEvent(eventName,fdep,fdepDict,1);
        returner += '\n';
    

    # closes the literal that is being assigned to
    # _PROTOTYPE_EVENTS_DICT
    returner += emitUtils.indentString('\n};\n\n',1);
    return returner;


def _emitIndividualEvent(eventName,fdep,fdepDict,amountToIndent):
    '''
    @returns {String}
    '''

    returner = '# prototype event from which active events will copy\n'
    returner += "'" + eventName + "': _Event(\n";

    # write the event name
    internal = "'" + eventName + "',\n";

    
    # write the definite global reads
    defGlobReads = fdep.definiteSharedGlobalReads(fdepDict);
    internal += _dictIzeGlobShareds(defGlobReads);
    internal += ', # def glob reads \n';

    # write the definite glob writes
    defGlobWrites = fdep.definiteSharedGlobalWrites(fdepDict);
    internal += _dictIzeGlobShareds(defGlobWrites);
    internal += ', # def glob writes \n';

    # write the conditional global reads
    condGlobReads = fdep.conditionalSharedGlobalReads(fdepDict);
    internal += _dictIzeGlobShareds(condGlobReads);
    internal += ', # cond glob reads \n';

    # write the conditional global writes
    condGlobWrites = fdep.conditionalSharedGlobalWrites(fdepDict);
    internal += _dictIzeGlobShareds(condGlobWrites);
    internal += ', # cond glob writes \n';

    # write the sequence globals
    # FIXME: currently do not have a way of accessing sequence globals
    # of functions.
    seqGlobs = fdep.seqGlobals(fdepDict);
    internal += _dictIzeGlobShareds(seqGlobs);
    internal += ', # seq globals \n';

    # write None to signify that this event does not yet have an
    # associated endpoint.
    internal += 'None), # Placeholder for endpoint obj, which gets set when each endpoint is init-ed\n'
    
    indentedInternal = emitUtils.indentString(internal,1);
    returner += indentedInternal;
    return emitUtils.indentString(returner,amountToIndent);
    

def _dictIzeGlobShareds(readsWritesToHandle):
    '''
    @param {array} readsWritesToHandle --- An array of NameTypeTuples
    (@see the declaration of a NameTypeTuple class at the bottom of
    slice/typeStack.py.

    @returns A string of the following form:
        {'1__otherPingNum': True, '5__nothingShared':True}

    Runs through all name type tuples passed in in
    readsWritesToHandle.  For each one, takes the unique name of the
    name type tuple and uses it as a key for a dict that we create.
    The value does not really matter.  I arbitrarily chose the bool
    True.
    '''
    returner = '{';
    for ntt in readsWritesToHandle:
        returner += "'" + ntt.getUniqueName() + "': True, ";
    returner += '}';
    return returner;
