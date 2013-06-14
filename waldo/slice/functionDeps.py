#!/usr/bin/env python

from typeStack import TypeStack;
from typeStack import NameTypeTuple;
import util;

class FunctionDeps(object):

    '''
    Vastly over-simplifying because cannot gain any real traction by
    not simplifying.  For now, any global/shared mutable that is in a
    read set automatically gets added to the write set.
    '''
    
    def __init__(self,funcName,srcFuncName,endpointName,funcNode,isOnComplete):
        '''
        @param {String} funcName --- a name for this function that is
        guaranteed not to conflict with any other function.
        Additionally, used by funcCalls to match FunctionDeps objects
        to function calls.

        @param {String} srcFuncName --- The name of this function as
        it appears in the program source.  

        @param {String} endpointName --- The name of the endpoint on
        which this function is defined.

        @param {AstNode} funcNode --- 

        @param{Bool} isOnComplete --- True if this is an
        onCompleteFunction
        
        '''
        
        # name to an array of NameTypeTuple-s each variable in here
        # may change and depends on reading other variables in the
        # list NameTypeTuple-s
        # dict is indexed by int ntt id
        self.varReadSet = {}; 

        # the variables that this function reads from. dict from var
        # name to NameTypeTuple.
        # dict is indexed by int ntt id
        self.mReadSet = {};

        # a dictionary of ntt-s with varType
        # TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL.  Will have to run
        # through this dictionary to further check read/write status
        # of these functions.
        # dictionary is indexed by ntt id.
        self.funcCalls = {};

        # string: name of function
        self.funcName = funcName;

        self.srcFuncName = srcFuncName;
        self.endpointName = endpointName;

        self.funcNode = funcNode;
        
        # ntt id to ntt-s with varType
        # TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT or 
        # TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT
        # should contain all arguments passed to this function.
        self.funcArgs = {};

        # id to return statement ntt
        self.returnStatements = {};

        self.isOnComplete = isOnComplete;

        # FIXME: the below is ugly.
        # message send functions are now able to return values.  to
        # accomodate this, store the names of the global values that
        # the sequence is supposed to return in msg_send_returns.
        self.msg_send_returns = []
        
        
    def addReturnStatement(self,ntt):
        self.returnStatements[ntt.id] = ntt;

    def addFuncArg(self,ntt):
        if ((ntt.varType != TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT) and
            (ntt.varType != TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
            errMsg = '\nBehram error: should not be adding a funcArg in functionsDeps ';
            errMsg += 'unless it is a function argument.\n';
            print(errMsg);
            assert(False);

        self.funcArgs[ntt.id] = ntt;

        
    def addFuncCall(self,ntt):
        '''
        @param {NameTypeTuple} ntt --- of type
        TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL.
        '''
        if ntt.varType != TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL:
            errMsg = '\nBehram error: in addFuncCall in functionDeps.py.  ';
            errMsg += 'Should have received a varType of INDENTIFIER_TYPE_FUNCTION_CALL, ';
            errMsg += 'but did not.\n';
            print(errMsg);
            assert(False);

        self.funcCalls[ntt.id] = ntt;


    def addReturnStatment(self,ntt):
        '''
        @param {NameTypeTuple} ntt --- of type
        TypeStack.IDENTIFIER_TYPE_RETURN_STATEMENT
        '''
        if ntt.varTyep != TypeStack.IDENTIFIER_TYPE_RETURN_STATEMENT:
            errMsg = '\nBehram error: in addReturnStatement of functionDeps.py.  ';
            errMsg += 'Sould have received a varType of IDENTIFIER_TYPE_RETURN_STATEMENT, ';
            errMsg += 'but did not.\n';
            
        self.returnStatements[ntt.id] = ntt;

                    
    def addToVarReadSet(self,nameTypeTuple):
        if self.varReadSet.get(nameTypeTuple.id,None) == None:
            self.varReadSet[nameTypeTuple.id] = VarReadSet(nameTypeTuple);
            
    def addReadsToVarReadSet(self,ntt,reads):
        '''
        variable with NameTypeTuple of ntt is being written to.  Its
        write is dependent on all the ntt-s stored in the array reads.
        '''
        if self.varReadSet.get(ntt.id,None) == None:
            print('\nBehram error need to ensure exists before write to\n');
            assert(False);
        else:
            self.varReadSet[ntt.id].addReads(reads);

        # ensures that all reads that affect the written to value of
        # the function get stored as well.
        self.addFuncReads(reads);

    def addFuncReads(self,reads):
        for read in reads:
            ### FIXME: this is gross: for some reason on bank code
            ### getting a read that is a list.  instead of debugging
            ### it for now, taking easy way out...
            if isinstance(read,list):
                if len(read) == 0:
                    return
                read = read[0]            
            self.mReadSet[read.id] = read;
            
    def jsonize(self,funcDepsDict):
        '''
        @param {dictionary} funcDepsDict --- a dictionary from
        name of each functionDep to FunctionDep object.
        '''
        returner = {};
        returner['funcName'] = self.funcName;
        
        returner['readSet'] =[];
        for ider in sorted(self.mReadSet.keys()):
            returner['readSet'].append(self.mReadSet[ider].varName);

        # write read set list
        varReadSetList = [];
        for itemKey in sorted(self.varReadSet.keys()):
            varReadSetItem = self.varReadSet[itemKey];
            jsonString = varReadSetItem.jsonize();
            varReadSetList.append(
                util.fromJsonPretty(jsonString));

        # definite global/shared reads
        globSharedReads = [];
        for ntt in self.definiteSharedGlobalReads(funcDepsDict):
            jsoned = ntt.jsonize();
            globSharedReads.append(
                util.fromJsonPretty(jsoned));

        returner['definiteGlobalSharedReads'] = globSharedReads;

        #definite global/shared writes
        globSharedWrites = [];
        for ntt in self.definiteSharedGlobalWrites(funcDepsDict):
            jsoned = ntt.jsonize();
            globSharedWrites.append(
                util.fromJsonPretty(jsoned));

        returner['definiteGlobalSharedWrites'] = globSharedWrites;

        # conditional global/shared reads
        conditionalGlobSharedReads = [];
        for ntt in self.conditionalSharedGlobalReads(funcDepsDict):
            jsoned = ntt.jsonize();
            conditionalGlobSharedReads.append(
                util.fromJsonPretty(jsoned));

        returner['conditionalGlobalSharedReads'] = conditionalGlobSharedReads;

        # conditional global shared writes
        conditionalGlobSharedWrites = [];
        for ntt in self.conditionalSharedGlobalWrites(funcDepsDict):
            jsoned = ntt.jsonize();
            conditionalGlobSharedWrites.append(
                util.fromJsonPretty(jsoned));

        returner['conditionalGlobalSharedWrites'] = conditionalGlobSharedWrites;
        
        # return the json
        return util.toJsonPretty(returner);


    def seqGlobals(self,funcDepsDict):
        '''
        @returns {Array} --- Returns an array of ntt-s.  Each ntt
        corresponds to a separate sequence global that I might hit by
        calling this function.
        '''
        seqGlobalDict = {};
        self._seqGlobals(seqGlobalDict,funcDepsDict,{});

        # flatten seqGlobalDict into an array.
        returner = [];
        for seqGlobKey in sorted(seqGlobalDict.keys()):
            seqGlobalNtt = seqGlobalDict[seqGlobKey];
            returner.append(seqGlobalNtt);
        
        return returner;


    def _seqGlobals(self,allFound,funcDepsDict,alreadyCheckedFuncDict):
        '''
        @returns Nothing ---- Use the parameter allFound for storing results.

        @param {dict} allFound --- Keys are ids of sequence global
        ntt-s.  Values are actual sequence global ntt-s.  Each
        function inserts all the sequence globals that it accesses to
        this dictionary.

        @param{dict} alreadyCheckedFuncDict --- funcName to boolean.
        Just ensures that we do not infinitely loop through two
        functions that call each other.
        '''

        # add all the sequence globals that *I* directly touch here.
        for readNttKey in sorted(self.mReadSet.keys()):
            readNtt = self.mReadSet[readNttKey];
            if ((readNtt.varType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL) or
                (readNtt.varType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
                allFound[readNtt.id] = readNtt;
                

        # now run through all function calls to see if they touch any
        # additional sequence globals.
        for funcCallNttKey in sorted(self.funcCalls.keys()):
            funcCallNtt = self.funcCalls[funcCallNttKey];
            funcCallName = funcCallNtt.varName;
            
            if funcCallName in alreadyCheckedFuncDict:
                continue;

            alreadyCheckedFuncDict[funcCallName] = True;
            fdep = funcDepsDict[funcCallName];
            fdep._seqGlobals(allFound,funcDepsDict,alreadyCheckedFuncDict);
            
    
    def definiteSharedGlobalReads(self,funcDepsDict,already_checked=None):
        if already_checked == None:
            already_checked = {}
            
        return self._definiteSharedGlobalReads(funcDepsDict,already_checked);
    
    def _definiteSharedGlobalReads(self,funcDepsDict,already_checked):
        '''
        Runs through all variables that are read and returns a list of
        all shared or global variable ntt-s that this function may
        read from.  ASSUMES THAT THIS FDEP DOES NOT HAVE ANY FUNCTION
        CALLS IN IT.

        Eg.
        someVar = someShared

        would return [ ntt of someShared ].

        Note that other shared variables may be read depending on
        conditions (eg, what's passed in etc.).  This is because maps
        and lists are reference types: one shared map may also be a
        shared global etc.

        @param {dict} funcDepsDict --- (String:FunctionDeps object).
        '''
        returnerDict = {};

        # add my own definite dependencies to the dictionary
        for key in sorted(self.mReadSet.keys()):
            item = self.mReadSet[key];
            if ((item.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                (item.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL) or
                (item.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_OBJECT_CALL)):

                if returnerDict.get(item.id,None) == None:
                    # we did not already have this global.  add it.
                    returnerDict[item.id] = item;


        for funcCallNtt in self.funcCalls.values():
            func_call_name = funcCallNtt.varName
            if already_checked.get(func_call_name,None) == None:
                already_checked[func_call_name] = True;
                fdep = funcDepsDict.get(func_call_name,None);
                if fdep == None:
                    errMsg = '\nBehram error: Looking up function named "';
                    errMsg += func_call_name + '" that ';
                    errMsg += 'was not defined.\n';
                    print(errMsg);
                    assert(False);
                    
                def_reads_array = fdep._definiteSharedGlobalReads(
                    funcDepsDict,already_checked)

                for read_item in def_reads_array:
                    returnerDict[read_item.id] = read_item

                    
        # flatten the returner dictionary and return it.
        returner = [];
        for key in sorted(returnerDict.keys()):
            returner.append(returnerDict[key]);

        return returner;



    def getTouchedExternals(self,funcDepsDict,alreadyChecked=None):
        '''
        Runs through this function to see what external variables this
        could potentially touch while it's being executed.
        Returns dict: <String:bool>
        '''
        if alreadyChecked == None:
            alreadyChecked = {}
        return self._getTouchedExternals(funcDepsDict,alreadyChecked);

    def _getTouchedExternals(self,funcDepsDict,alreadyChecked):
        toReturn= {}
        if self.funcName in alreadyChecked:
            return toReturn
        
        alreadyChecked[self.funcName] = True;

        for item in self.varReadSet.values():
            ntt = item.ntt;
            if (ntt.astNode != None) and (ntt.astNode.external != None):
                toReturn[ntt.getUniqueName()] = True

        for funcCallNtt in self.funcCalls.values():
            funcCallName = funcCallNtt.varName;
            if alreadyChecked.get(funcCallName,None) == None:
                alreadyChecked[funcCallName] = True;
                fdep = funcDepsDict.get(funcCallName,None);
                if fdep == None:
                    errMsg = '\nBehram error: Looking up function named "';
                    errMsg += funcCallName + '" that ';
                    errMsg += 'was not defined.\n';
                    print(errMsg);
                    assert(False);
        
                touchedExternals = fdep.getTouchedExternals(funcDepsDict,alreadyChecked)
                for tExt in touchedExternals.keys():
                    toReturn[tExt] = True;

        return toReturn;

    
    def definiteSharedGlobalWrites(self,funcDepsDict,alreadyChecked=None):
        if alreadyChecked == None:
            alreadyChecked = {};
        return self._definiteSharedGlobalWrites(funcDepsDict,alreadyChecked);

    
    def _definiteSharedGlobalWrites(self,funcDepsDict,alreadyChecked):
        '''
        Be really conservative about chasing function calls.  See note
        at top of function.
        
        @see definitieSharedGlobalReads, except for writes.

        Importantly, have to take into account some transitivity.
        Consider the notation <- as "rhs may write to lhs at some
        point in the function."  If

            a <- b
              <- c
              <- d

            b <- e
              <- f
        
        And a,b,e are global or shared variables that are all mutable,
        then [a,b,e] must be returned, because b might be e, and a
        might be b.  

        Note that if a is not mutable, but b and e are, then this
        means that only [b] is returned, because any write to a
        cannot possible affect the shared/global variable.

        Each element in self.varReadSet has the following form:
          writtenTo : dependency1,dependency2,dependency3,...
        where writtenTo and all dependency-s are ntts.

        Note that all ntts in self.varReadSet are references.  Meaning
        that changing dependency1 may change other dependencies
        throughout self.varReadSet.

        The pseudocode for doing this is as follows:

           0: Generate a dictionary of type <varName:ntt> named
              toReturn.
              
           1: Run through the self.varReadSet.  For each writtenTo
              value that is global, add it to toReturn.

           2: Run through self.varReadSet and mark all ntts
              (writtenTo-s and dependency-s) with a 0.
           
           3: Create a dirty bit and set it to False.

           4: For each element in self.varReadSet:
           
                 a: if a writtenTo element is mutable, mark all of its
                    dependency-s that are also mutable with a 1.

                 b: If any of its dependency-s were not already marked
                    with a 1, then set the dirty bit to true.

                 c: If any marked dependency is a shared/global, add
                    it to toReturn.

           5: If dirty bit is true, goto 3.

           6: Unmark all.  (ie, repeat 2)

           9: Convert toReturn to a list and return it.
        '''
        
        # step 0
        toReturn = {};

        # step 1
        for item in self.varReadSet.values():
            potentialNtt = item.ntt;
            if ((potentialNtt.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                (potentialNtt.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):
                toReturn[potentialNtt.id] = potentialNtt;
                
        # step 2
        self._unmarkAll();

        # step 3-5
        dirtyBit = True;
        while dirtyBit:
            dirtyBit = False; # step 3

            for readSetItem in self.varReadSet.values():
                writtenToNtt = readSetItem.ntt;

                # step 4 a
                if writtenToNtt.mutable:
                    for dependencyNtt in readSetItem.mReads.values():
                    #for dependencyNtt in writtenToNtt.values():
                        if ((not dependencyNtt.isMarked()) and dependencyNtt.mutable):
                            # step 4 b
                            dirtyBit = True;
                            dependencyNtt.mark();

                            # step 4 c
                            if ((dependencyNtt.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                                (dependencyNtt.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):
                                toReturn[dependencyNtt.id] = dependencyNtt;


        # step 6
        self._unmarkAll();

        # step 7
        for funcCallNtt in self.funcCalls.values():
            funcCallName = funcCallNtt.varName;
            if alreadyChecked.get(funcCallName,None) == None:
                alreadyChecked[funcCallName] = True;
                fdep = funcDepsDict.get(funcCallName,None);
                if fdep == None:
                    errMsg = '\nBehram error: Looking up function named "';
                    errMsg += funcCallName + '" that ';
                    errMsg += 'was not defined.\n';
                    print(errMsg);
                    assert(False);

                
                subDeps = fdep.definiteSharedGlobalWrites(
                    funcDepsDict,alreadyChecked);
                for defWriteNtt in subDeps:
                    # doesn't reall matter if overwriting
                    toReturn[defWriteNtt.id] = defWriteNtt;


        # step 8: very ugly.  should eventually get fixed.  For now,
        # treating all reads to mutable global/shared as writes.
        # FIXME: lkjs;
        allReads = self.definiteSharedGlobalReads(funcDepsDict);
        for readNtt in allReads:
            if ((readNtt.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                (readNtt.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):
                    toReturn[readNtt.id] = readNtt;
                        
        # step 9

        # for debugging, always want to return this list in the same
        # order, that's why not just returning list(toReturn.values);
        returner = [];
        for nttKey in sorted(toReturn.keys()):
            returner.append(toReturn[nttKey]);
                
        return returner;


    def conditionalSharedGlobalReads(self,funcDepsDict,alreadyChecked=None):
        '''
        Can read a global that wasn't returned by
        definiteSharedGlobalReads.  This is because maps and lists are
        reference types.  That means that if one global map could
        point at another global map.  We can only know whether this
        happens or not at runtime (sort of).  So this function lists
        all read references that should be checked in a function for
        being tainted by another global/shared piece of data.

        This function returns an array of all variables passed in that
        we should check for taints with other global/shared variables.

        Essentially, if any global or shared mutable is read, we
        should check whether that global/shared has additional taints.
        
        Similarly, for all mutable arguments that are passed in, we
        should check whether these have taints at run time.

        Do not need to check through function calls.  This is because
        the only way that conditional reads will occur is if one of
        the arguments to the function is mutable and global/shared.
        But the caller already knows if the argument is global/shared.
        '''
        defSGR = self.definiteSharedGlobalReads(funcDepsDict);
        # need to keep track of function argument reads as well
        # because may get taint through them.
        returner = self._getConditionalGlobalShareds(
            defSGR + self.funcArgReads(funcDepsDict));
        return returner;

    def _getConditionalGlobalShareds(self,arrayToCheck):
        '''
        @see conditionalSharedGlobalReads
        '''
        dynamicCheckDict = {};
        for ntt in arrayToCheck:
            if ntt.mutable:
                if ((ntt.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                    (ntt.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL) or
                    (ntt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT) or
                    (ntt.varType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
                    dynamicCheckDict[ntt.id] = ntt;


        # actually return the array of items to check taint for.
        returner = [];
        # using sorted keys to make it easier to debug compiler
        # through test cases: everything always returns in same order
        # -> we can write test cases and compare to previous outputs.
        for nttKey in sorted(dynamicCheckDict.keys()):
            returner.append(dynamicCheckDict[nttKey]);
            
        return returner;

    def conditionalSharedGlobalWrites(self,funcDepsDict):
        '''
        @see conditionalSharedGlobalReads, but does not go through
        function calls as well.
        '''
        return self._getConditionalGlobalShareds(
            self.definiteSharedGlobalWrites(funcDepsDict) +
            self.mutableFuncArgWrites(funcDepsDict));
    


    def _unmarkAll(self):
        for vReadSetKey in self.varReadSet.keys():
            vReadSet = self.varReadSet[vReadSetKey];
            vReadSet.ntt.unmark();
            for readNttKey in vReadSet.mReads.keys():
                readNtt = vReadSet.mReads[readNttKey];
                readNtt.unmark();


    
    def funcArgReads(self,funcDepsDict):
        '''
        This should return all function arguments that were passed in
        and later read as an array of ntt-s.

        Importantly, if the function arguments that we use are
        TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT,
        then this means that another function may actually read that
        argument as a global in a message sequence, even if this
        function does not.

        To deal with this edge case, first check if a function has
        above type.  If it does, then check if it's in my read set.
        If it is not, then check run through all other function deps
        and check their read sets.  If it's in any of theirs then add
        it.  Otherwise, do not add.

        For all other arguments, just run through read set, adding
        function arguments to it.
        
        Just run through mReadSet and return any reads made to passed
        in arguments, returning the ntts of those arguments in an
        array, guaranteeing there will only be one ntt per item in the
        array.
        '''
        returnDict = {};
        for nttKey in sorted(self.mReadSet.keys()):
            ntt = self.mReadSet[nttKey];
            if ((ntt.varType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT) or
                (ntt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT)):
                returnDict[ntt.id] = ntt;


        for nttKey in sorted(self.funcArgs.keys()):
            ntt = self.funcArgs[nttKey];

            # First line: already have it; don't worry about it
            # second check: don't already have it, but no one else can either
            if ((ntt.id in returnDict) or
                (ntt.varType != TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
                continue;

            # do not already have argument in read set, and know that
            # other functions might be able to access it becuase it's
            # a message sequence global.  run through all other
            # function dependencies to see if they use it in their
            # read set.  If they do, then add it to returner.
            # Otherwise, do not.
            goToNext = False;
            for fdepKey in sorted(funcDepsDict.keys()):
                if goToNext:
                    break;

                fdep = funcDepsDict[fdepKey];
                
                for fdep_nttKey in sorted(fdep.mReadSet.keys()):
                    fdep_ntt = fdep.mReadSet[fdep_nttKey];

                    if fdep_ntt.id == ntt.id:
                        returnDict[ntt.id] = ntt;
                        goToNext = True;
                        break;

        # collapse returnDict...note sorting for easier debugging.
        returner = [];
        for nttKey in returnDict:
            nttItem = returnDict[nttKey];
            returner.append(nttItem);
        return returner;
    
    def mutableFuncArgWrites(self,funcDepsDict):
        '''
        Returns an array of ntt-s of mutable function arguments that
        may get written to throughout the course of this function.
        This is useful because it means that the calling function may
        need to examine the taint on arguments that it passes in to
        know whether any globals or shareds may change.

        1) any mutable function argument that gets directly written to
        is added to a list.

        2) for any mutable that is written to that depends on a
        mutable function argument, then that dependent mutable func
        argument is added.

        3) for any mutable argument that is a shared global and is not
        written to in the body of the first function, check if it is
        written to in any other function.  If it is, then add it to
        this list.
        
        '''
        returnDict = {};

        for vrsKey in sorted(self.varReadSet.keys()):
            # any item in self.varReadSet may get written to in this
            # function.

            vrsItem = self.varReadSet[vrsKey];
            if vrsItem.ntt.mutable:
                
                # doing #1
                if ((vrsItem.ntt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT) or
                    (vrsItem.ntt.varType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
                    
                    returnDict[vrsItem.ntt.id] = vrsItem.ntt;
                else:
                    # doing #2
                    for nttReadKeys in sorted(vrsItem.mReads.keys()):
                        nttReadItem = vrsItem.mReads[nttReadKeys];
                        if ((nttReadItem.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT) or
                            (nttReadItem.varType == TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
                            returnDict[nttReadItem.id] = nttReadItem;



        # doing #3
        for funcArgKey in sorted(self.funcArgs.keys()):
            funcArgNtt = self.funcArgs[funcArgKey]

            # First line: already have it; don't worry about it
            # second check: don't already have it, but no one else can either
            if ((funcArgNtt.id in returnDict) or
                (funcArgNtt.varType != TypeStack.IDENTIFIER_TYPE_MSG_SEQ_GLOBAL_AND_FUNCTION_ARGUMENT)):
                continue;

            # do not already have argument in read set, and know that
            # other functions might be able to access it becuase it's
            # a message sequence global.  run through all other
            # function dependencies to see if they use it in their
            # read set.  If they do, then add it to returner.
            # Otherwise, do not.
            goToNext = False;
            for fdepKey in sorted(funcDepsDict.keys()):
                if goToNext:
                    break;

                fdep = funcDepsDict[fdepKey];
                
                for fdep_nttKey in sorted(fdep.varReadSet.keys()):
                    fdep_ntt = fdep.varReadSet[fdep_nttKey].ntt;

                    if fdep_ntt.id == funcArgNtt.id:
                        returnDict[funcArgNtt.id] = funcArgNtt;
                        goToNext = True;
                        break;


        # collapse the dictionary into a sorted list and return it.
        returner = [];
        for returnKey in sorted(returnDict.keys()):
            nttToReturn = returnDict[returnKey];
            returner.append(nttToReturn);
            
        return returner;


class VarReadSet(object):
    def __init__(self,ntt):
        self.ntt = ntt;
        self.mReads = {};

    def addReads(self,reads):
        '''
        @param {array of ntt-s} reads.
        '''
        for read in reads:
            ### FIXME: this is gross: for some reason on bank code
            ### getting a read that is a list.  instead of debugging
            ### it for now, taking easy way out...
            if isinstance(read,list):
                if len(read) == 0:
                    return
                read = read[0]

            self.mReads[read.id] = read;


    def jsonize(self):
        returner = {};
        jsoned = self.ntt.jsonize();
        returner['readSetNtt'] = util.fromJsonPretty(jsoned);

        readArray = [];
        for readKey in sorted(self.mReads.keys()):
            readItem = self.mReads[readKey];
            jsoned = readItem.jsonize();
            readArray.append(
                util.fromJsonPretty(jsoned));

        returner['reads'] = readArray;
        return util.toJsonPretty(returner);

            
    def _debugPrint(self,prepend=''):
        '''
        @param {String} prepend --- prepend gets put in front of each
        new line that we are going to print.  Makes more readable: for
        instance if want to indent everything that we're printing.
        '''
        toPrint = self.ntt.varName + ': \n';
        for element in self.mReads.keys():
            toPrint += '\t' + element;
        toPrint += '\n';

        toPrint = prepend + toPrint.replace('\n','\n' + prepend);
        print(toPrint);

