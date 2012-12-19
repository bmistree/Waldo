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

    # emit special-cased events for refresh keyword
    refreshKeywordStr = """
# load refresh events into dictionary
# refresh by itself does not touch any data
_REFRESH_KEY:_Event(
    _REFRESH_KEY,
    {}, 
    {}, 
    {}, 
    {}, 
    {},
    [], # doesn't touch any externals directly
    None), 

_REFRESH_RECEIVE_KEY: _Event(
    _REFRESH_RECEIVE_KEY,
    {}, 
    {}, 
    {}, 
    {}, 
    {},
    [], # doesn't touch any externals directly
    None),

""";
    returner += emitUtils.indentString(refreshKeywordStr,1);

    # now emit all user-defined events
    for eventName in fdepDict.keys():
        fdep = fdepDict[eventName];
        returner += _emitIndividualEvent(eventName,fdep,fdepDict,1);
        returner += _emit_individual_run_and_hold_event(
            eventName,fdep,fdepDict,1)
        returner += '\n';
    

    # closes the literal that is being assigned to
    # _PROTOTYPE_EVENTS_DICT
    returner += emitUtils.indentString('};\n\n',1);
    return returner;


def _emit_individual_run_and_hold_event(
    event_name,fdep,fdep_dict,amount_to_indent):
    '''
    Require to add special names for run and hold events.  They have
    essentially the same data as regular events, but are named
    slightly differently.  This is because external callers into Waldo
    only know the external name of the public function that begins an
    action rather than the internal keys that index into prototype
    dict array.
    '''

    endpoint_name = fdep.endpointName
    src_func_name = fdep.srcFuncName # the actual name of the public
                                     # function that starts the event
    event_dict_key = emitUtils.construct_hold_func_name(
        src_func_name,endpoint_name)
    
    return _emitIndividualEvent(event_dict_key,fdep,fdep_dict,amount_to_indent)    
    
    
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
    
    touchedExternalVarNames = fdep.getTouchedExternals(fdepDict)

    internal += '['
    for touchedExternal in touchedExternalVarNames.keys():
        internal += "'" + touchedExternal + "',"
    internal += '], # all external var names that this event may touch\n';

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
