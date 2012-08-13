#!/usr/bin/env python

from typeStack import TypeStack;
import util;

class FunctionDeps(object):

    def __init__(self,funcName):
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

                    
    def addToVarReadSet(self,nameTypeTuple):
        if self.varReadSet.get(nameTypeTuple.id,None) == None:
            self.varReadSet[nameTypeTuple.id] = VarReadSet(nameTypeTuple);
            
    def addReadsToVarReadSet(self,ntt,reads):
        '''
        variable with NameTypeTuple of ntt is being written to.  Its
        write is dependent on all the ntt-s stored in the array reads.
        '''
        if self.varReadSet.get(ntt.id,None) == None:
            print('\nBehram error.  Should not permit redeclaration.\n');
            assert(False);
        else:
            self.varReadSet[ntt.id].addReads(reads);

        # ensures that all reads that affect the written to value of
        # the function get stored as well.
        self.addFuncReads(reads);

        
    def addFuncReads(self,reads):
        for read in reads:
            self.mReadSet[read.id] = read;

            
    def jsonize(self,otherFuncDepsDict):
        '''
        @param {dictionary} otherFuncDepsDict --- a dictionary from
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
        for ntt in self.definiteSharedGlobalReads(otherFuncDepsDict):
            jsoned = ntt.jsonize();
            globSharedReads.append(
                util.fromJsonPretty(jsoned));

        returner['definiteGlobalSharedReads'] = globSharedReads;

        #definite global/shared writes
        globSharedWrites = [];
        for ntt in self.definiteSharedGlobalWrites(otherFuncDepsDict):
            jsoned = ntt.jsonize();
            globSharedWrites.append(
                util.fromJsonPretty(jsoned));

        returner['definiteGlobalSharedWrites'] = globSharedWrites;

        # conditional global/shared reads
        conditionalGlobSharedReads = [];
        for ntt in self.conditionalSharedGlobalReads(otherFuncDepsDict):
            jsoned = ntt.jsonize();
            conditionalGlobSharedReads.append(
                util.fromJsonPretty(jsoned));

        returner['conditionalGlobalSharedReads'] = conditionalGlobSharedReads;

        # conditional global shared writes
        conditionalGlobSharedWrites = [];
        for ntt in self.conditionalSharedGlobalWrites(otherFuncDepsDict):
            jsoned = ntt.jsonize();
            conditionalGlobSharedWrites.append(
                util.fromJsonPretty(jsoned));

        returner['conditionalGlobalSharedWrites'] = conditionalGlobSharedWrites;

        
        # return the json
        return util.toJsonPretty(returner);

    # def _debugPrint(self):
    #     print('\n\n\n');
    #     print(self.funcName);
    #     print('\n*****read set:*****\n')
    #     for item in self.mReadSet.keys():
    #         print(item);

            
    #     print('\n****read set keys:****\n');
    #     for item in self.varReadSet.keys():
    #         self.varReadSet[item]._debugPrint('\t');

    #     print('\n***definite shared global reads:****\n');
    #     print '\t',
    #     for ntt in self.definiteSharedGlobalReads():
    #         print ntt.varName + '\t',
    #     print('\n');

    #     print('\n***definite shared global writes:****\n');
    #     print '\t',
    #     for ntt in self.definiteSharedGlobalWrites():
    #         print ntt.varName + '\t',
    #     print('\n\n');

        
            
    def definiteSharedGlobalReads(self,funcDepsDict,alreadyCheckedDict=None):
        '''
        Runs through all variables that are read and returns a list of
        all shared or global variable ntt-s that this function may
        read from.  This does not include shared reads from function
        calls.

        Eg.
        someVar = someShared

        would return [ ntt of someShared ].

        Note that other shared variables may be read depending on
        conditions (eg, what's passed in etc.).  This is because maps
        and lists are reference types: one shared map may also be a
        shared global etc.

        @param {dict} funcDepsDict --- (String:FunctionDeps object).

        @param{dict} alreadyCheckedDict --- (String:FunctionDeps
        object) if it's None, then that means that this is the root
        call that we're going into.  Keeps track of the function
        dependencies that this function has that we've already
        checked.  If we've already checked a function, then we do not
        need to check it again.
        '''
        returnerDict = {};
                
        if alreadyCheckedDict == None:
            alreadyCheckedDict = {};
            
        # add ourselves onto the list of functions that we have
        # already checked.
        alreadyCheckedDict[self.funcName] = True;
            
        for funcCallKey in sorted(self.funcCalls.keys()):
            funcCallNtt = self.funcCalls[funcCallKey];
            funcCallName = funcCallNtt.varName;
            if alreadyCheckedDict.get(funcCallName,None) == None:
                # means that we haven't already checked the function
                # that we called here for definite global reads.

                # we shouldn't really need this call, because each
                # function should add itself, but this makes me more
                # comfortable.
                alreadyCheckedDict[funcCallName] = True;

                funcDep = funcDepsDict.get(funcCallName,None);
                if funcDep == None:
                    errMsg = '\nBehram error: Made function call to a function ';
                    errMsg += 'that we do not have a functionDep object for.\n';
                    print(errMsg);
                    assert(False);

                funcDep_defSharedGlobReads = funcDep.definiteSharedGlobalReads(
                    funcDepsDict,alreadyCheckedDict);

                # now remove redundancies with existing dependencies
                for singleDep in funcDep_defSharedGlobReads:
                    # each item should be a global or shared ntt.
                    if returnerDict.get(singleDep.id,None) == None:
                        returnerDict[singleDep.id] = singleDep;

        # now add my own definite dependencies to the dictionary
        for key in sorted(self.mReadSet.keys()):
            item = self.mReadSet[key];
            if ((item.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                (item.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):

                if returnerDict.get(item.id,None) == None:
                    # we did not already have this global.  add it.
                    returnerDict[item.id] = item;

        # flatten the returner dictionary and return it.
        returner = [];
        for key in sorted(returnerDict.keys()):
            returner.append(returnerDict[key]);

        return returner;

        
    def definiteSharedGlobalWrites(self,otherFuncDepsDict,alreadyCheckedDict=None):
        '''
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

           7: Run through all function calls in function.  For each
              that we haven't already processed, call
              definiteGlobSharedWrites on it.  Try to append the
              called function's global/shared writes to our existing
              shared/global writes (ie, append if we didn't already
              have it).
           
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
        for readSetItem in self.varReadSet.values():
            readSetItem.ntt.unmark();
            for innerNtt in readSetItem.mReads.values():
                innerNtt.unmark();
                

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
        for readSetItem in self.varReadSet.values():
            readSetItem.ntt.unmark();
            for innerNtt in readSetItem.mReads.values():
                innerNtt.unmark();


        if alreadyCheckedDict == None:
            alreadyCheckedDict = {};

        alreadyCheckedDict[self.funcName] = True;
        # now check all function calls that this function makes to see
        # if there are any definite writes to globals in any of the
        # functions that this function calls.

        for funcCallKey in sorted(self.funcCalls.keys()):
            funcCallNtt = self.funcCalls[funcCallKey];
            funcCallName = funcCallNtt.varName;
            
            if alreadyCheckedDict.get(funcCallName,None) == None:
                # we haven't already checked this subfunction
                # go ahead and do so.
                alreadyCheckedDict[funcCallName] = True;

                fDep = otherFuncDepsDict.get(funcCallName,None);
                if fDep == None:
                    errMsg = '\nBehram error: making a call to a function ';
                    errMsg += 'that does not have associated function dep ';
                    errMsg += 'object.\n';
                    print(errMsg);
                    assert(False);

                fDep_defGlobSharedWrites = fDep.definiteSharedGlobalWrites(
                    otherFuncDepsDict,alreadyCheckedDict);
                # check whether we already knew that there might be write conflicts.
                for defGlobSharedWrite in fDep_defGlobSharedWrites:
                    if toReturn.get(defGlobSharedWrite.id,None) == None:
                        toReturn[defGlobSharedWrite.id] = defGlobSharedWrite;
                        
        # step 9

        # for debugging, always want to return this list in the same
        # order, that's why not just returning list(toReturn.values);
        returner = [];
        for nttKey in sorted(toReturn.keys()):
            returner.append(toReturn[nttKey]);
                
        return returner;
        

    def conditionalSharedGlobalReads(self,otherFuncDepsDict):
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
        
        defSGR = self.definiteSharedGlobalReads(otherFuncDepsDict);
        # need to keep track of function argument reads as well
        # because may get taint through them.
        returner = self._getConditionalGlobalShareds(defSGR + self.funcArgReads());
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
                    (ntt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT)):

                    dynamicCheckDict[ntt.id] = ntt;
                

        # actually return the array of items to check taint for.
        returner = [];
        # using sorted keys to make it easier to debug compiler
        # through test cases: everything always returns in same order
        # -> we can write test cases and compare to previous outputs.
        for nttKey in sorted(dynamicCheckDict.keys()):
            returner.append(dynamicCheckDict[nttKey]);
                    
        return returner;

    # def nonFuncCallConditionalSharedGlobalWrites(self,otherFuncDepsDict):
    #     '''
    #     @see conditionalSharedGlobalReads, but does not go through
    #     function calls as well.
    #     '''
    #     return self._getConditionalGlobalShareds(
    #         self.definiteSharedGlobalWrites(otherFuncDepsDict) + self.mutableFuncArgWrites());

    def conditionalSharedGlobalWrites(self,otherFuncDepsDict):
        '''
        @see conditionalSharedGlobalReads

        Returns an array of ntt-s.  If any ntt in this array is
        tainted by a global or shared variable that is mutable, then
        that global or shared variable may be written to when this
        function is executed.
        '''

        # other than explicit global/shared writes that happen in the
        # body of the function (taken care of through call to
        # self.definiteSharedGlobalWrites below), the only other thing
        # that we need to check is that a mutable argument passed into
        # this function.  If that mutable
        # 
        #     * gets written to during as a result of this function
        #       invocation
        # 
        # then need to check that the mutable doesn't have
        # shared/global taint.  The first part of this function focuses
        # on determining the starred point above.
        mMutableArguments = self._getMutableArguments();

        mutablePotentialWrites = [];
        for mutableArg in mMutableArguments:
            positionIndex = mutableArg.argPosition;
            if self.referenceWritten(positionIndex,otherFuncDepsDict):
                mutablePotentialWrites.append(mutableArg);

        return self._getConditionalGlobalShareds(
            self.definiteSharedGlobalWrites(otherFuncDepsDict) + mutablePotentialWrites);

    
    def _getMutableArguments(self):
        '''
        Returns all arguments to this function that are mutable and at
        least read as an array of ntt-s.
        '''
        returnerDict = {};
        for readKey in self.mReadSet.keys():
            readNtt = self.mReadSet[readKey];
            if (readNtt.mutable and
                (readNtt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT)):
                returnerDict[readNtt.id] = readNtt;

        # flatten dictionary into an array
        returner = [];
        for itemKey in returnerDict.keys():
            item = returnerDict[itemKey];
            returner.append(item);

        return returner;


    def referenceWritten(
        self,argPosition,otherFuncDepsDict,alreadyChecked=None):
        '''
        @param{Int} argPosition
        
        @param{dictionary<funcName:FunctionDep object>}
        
        @param{dictionary<hashedFunctionName:bool>} --- Tells me
        previous function-position arguments we've tried when trying
        to answer this query.  (Note for hashedFunctionName, @see
        _hashCalledArgPos.
        
        @see conditionalSharedGlobalReads

        Recursively answers whether a shared or global variable in
        position argPosition could be written to by calling this
        function.

        First checks whether argument is mutable...if it's not, then
        any writes to it cannot affect a global/shared variable.

        Then, checks whether any non-function call code in the
        function writes to it....if it does, return True.

        Then goes through all function calls that this code executes.
        If any of these functions potentially write to the argument
        specified by posArg, then return True.  Otherwise, return
        False.
        '''
        if alreadyChecked == None:
            alreadyChecked = {};
            
        # Making a copy of dictionary because only want to update
        # checks made by sub-queries rooted in this query.  Do not
        # want to affect sibling queries.
        alreadyCheckedCopy = self._copyDict(alreadyChecked);
        mHash = self._hashCalledArgPos(
            self.funcName,argPosition);
        alreadyCheckedCopy[mHash] = True;

        
        # check if the argument is even mutable: return false if it's not.
        requireAdditionalChecking = False;
        for mutableArg in self._getMutableArguments():
            if mutableArg.argPosition == argPosition:
                nttArgToCheck = mutableArg;
                requireAdditionalChecking = True;
                break;
            
        if not requireAdditionalChecking:
            # means that the arugment was not mutable.  return right away.
            return False;


        ### now check if the function that we were in potentially
        ### wrote to this argument in this function (excluding
        ### function calls).
        
        # ignores potential function calls made.
        inFunctionMutableFuncArgWritesArray = self.mutableFuncArgWrites();
        for potentialWrite in inFunctionMutableFuncArgWritesArray:
            if potentialWrite.argPosition == argPosition:
                return True;
        
        ### now check if the argument got written to by any function
        ### calls.
        for fcKey in sorted(self.funcCall.keys()):
            funcCallNtt = self.funcCall[fcKey];
            funcCallName = funcCallNtt.varName;

            fDep = otherFuncDepsDict.get(funcCallName,None);
            if fDep == None:
                errMsg = '\nBehram error: in functionDeps.py, should ';
                errMsg += 'have had an associated function dependency ';
                errMsg += 'for name, but did not.\n';
                print(errMsg);
                assert(False);

            
            # posReadSet is an array of positions.  We need to check
            # if the nttArgToCheck (the argument that external
            # function wanted to know about) is passed in as an
            # argument to a further function call.  if it is, then
            # posReadSet returns the position of each argument that
            # the argument will be passed in as.  Need to recursively call
            # referenceWritten on this function call plus argument.
            posReadSet = self._checkArgInReadSetOfFuncCall (
                nttArgToCheck,funcCallNtt);

            additionalToCheck = [];
            for posArgument in posReadSet:
                # means that the mutable argument that we are trying to check
                # is actually one of the arguments that are passed
                hashedPosArguments = self._hashCalledArgPos(
                    funcCallName,posArg);

                # we already checked this one and know that it does not 
                if alreadyCheckedCopy.get(hashedPosArguments,None) != None:
                    continue;

                alreadyCheckedCopy[hashedPosArguments] = True;

                if fDep.referenceWritten(posArgument,otherFuncDepsDict,copyDict):
                    return True;

        # if got all the way through, then there's no way that this
        # variable will be reference-written.  return false.
        return False;

    def _copyDict(self,toCopyDict):
        
        returner = {};
        for key in toCopyDict.keys():
            returner[key] = toCopyDict[key];
        
        return returner;
        
    
    def _checkArgInReadSetOfFuncCall (self,nttArgToCheck,funcCallNtt):
        '''
        @param {NameTypeTuple} nttArgToCheck --- Should have varType
        of TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT.  

        @param {FuncCallNtt} funcCallNtt --- Should have varType of
        TypeStack.IDENTIFIER_TYPE_FUNCTION_CALL

        @return {Array<int>} --- All the positional arguments that
        nttArgToCheck gets passed
        
        Want to when nttArgToCheck may be read when constructing
        arguments to funcCallNtt.  Returns the positions (as numbers
        in an array) of each argument that requires a read to
        nttArgToCheck.  If none, then return empty array.
        '''

        returner = [];


        for positionIndex in range(0,len(funcCallNtt.funcArgReads)):
            readArray = funcCallNtt.funcArgReads[positionIndex];
            for read in readArray:
                if self._inMutableEffectChain(nttArgToCheck,read):
                    returner.append(positionIndex);
                    break;
                
        return returner;
        


    def _unmarkAll(self):
        for vReadSetKey in self.varReadSet.keys():
            vReadSet = self.varReadSet[vReadSetKey];
            vReadSet.ntt.unmark();
            for readNttKey in vReadSet.mReads.keys():
                readNtt = vReadSet.mReads[readNttKey];
                readNtt.unmark();

    
    def _inMutableEffectChain(self,root,toCheck):
        '''
        @param {NameTypeTuple} root
        @param {NameTypeTuple} toCheck

        @returns {bool}
        
        Returns True if toCheck potentially writes to root (minus
        function calls) and root and toCheck are both mutable...ie
        returns true if a change to root might affect a change in
        toCheck and vice versa. False otherwise.

        Algorithm:

        -2: If root is not mutable or toCheck is not mutable, return
            False: write to one won't be able to indirectly affect the
            other.

        -1: If root and toCheck are the same, return true
            
        0: Run through all writes and write dependencies unmarking all.

        1: Add root to workDict

        2: Remove an element from workDict, named toWorkOn

        3: If toWorkOn gets written to, then run through all of its
           dependencies.

             a) If the dependency is toCheck, then return True.  Otherwise:

             b) If the dependency is mutable and unmarked, then add it
                to workDict and mark it.


        4: If workDict is empty, run the same algorithm replacing
           toCheck with root and vice versa.  If still do not return
           True, then return False.
        '''
        # step -2
        if (not root.mutable) or (not toCheck.mutable):
            return False;

        # step -1
        if root.id == toCheck.id:
            return True;

        
        def _helper(fDep,root,toCheck):
            '''
            Implements steps 0-4
            '''
            # step 0
            fDep._unmarkAll();
            
            workDict = {};
            root.mark();
            workDict[root.id] = root;

            while len(workDict) != 0:
                # step 2
                toWorkOn = list(workDict.values())[0];
                del workDict[toWorkOn.id];

                for vReadSetKey in fDep.varReadSet.keys():
                    if toWorkOn.id == vReadSetKey:
                        # step 3
                        varReadSet = fDep.varReadSet[vReadSetKey];
                        for depKey in varReadSet.mReads.keys():
                            dependency = varReadSet.mReads[depKey];
                            # step 3 a
                            if dependency.id == toCheck.id:
                                fDep._unmarkAll();
                                return True;
                            # step 3 b
                            if dependency.mutable and (not dependency.isMarked()):
                                workDict[dependency.id] = dependency;
                                dependency.mark();

            # did not find it.
            fDep._unmarkAll();
            return False;

        # see comment at step 4.
        return _helper(self,root,toCheck) or _helper(self,toCheck,root);


    
    def _hashCalledArgPos(self,funcCallName,posArg):
        '''
        @param{String} funcCallName --- The name of the function that
        we're calling
        
        @param{Int} posArg --- The positional argument that we're checking.
        '''
        return funcCallName + ':*:' + str(posArg);
                                
            
        


    # def conditionalSharedGlobalWrites(self,otherFuncDepsDict):
    #     '''
    #     @see conditionalSharedGlobalReads
    #     '''
    #     return self._getConditionalGlobalShareds(
    #         self.definiteSharedGlobalWrites(otherFuncDepsDict) + self.mutableFuncArgWrites());

    
# lkjs;
# do not need to type check through function calls because a calling function will already have sorted out the read.

# need to handle returned global that was a read, but then got written to in the local area.  (only for mutables).
# lkjs;

    
    def funcArgReads(self):
        '''
        Just run through mReadSet and return any reads made to passed
        in arguments, returning the ntts of those arguments in an
        array, guaranteeing there will only be one ntt per item in the
        array.
        '''
        returnDict = {};
        for nttKey in sorted(self.mReadSet.keys()):
            ntt = self.mReadSet[nttKey];
            returnDict[ntt.id] = ntt;
            

        # collapse returnDict...note sorting for easier debugging.
        returner = [];
        for nttKey in returnDict:
            nttItem = returnDict[nttKey];
            returner.append(nttItem);
        return returner;
    
    def mutableFuncArgWrites(self):
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
        
        '''
        returnDict = {};

        for vrsKey in sorted(self.varReadSet.keys()):
            # any item in self.varReadSet may get written to in this
            # function.

            vrsItem = self.varReadSet[vrsKey];
            if vrsItem.ntt.mutable:
                
                # doing #1
                if vrsItem.ntt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT:
                    returnDict[vrsItem.ntt.id] = vrsItem.ntt;
                else:
                    # doing #2
                    for nttReadKeys in sorted(vrsItem.mReads.keys()):
                        nttReadItem = vrsItem.mReads[nttReadKeys];
                        if nttReadItem.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARUGMENT:
                            returnDict[nttReadItem.ntt.id] = nttReadItem;
                            

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
        # note: this should never really be populated because there
        # are not ways to return and modify....except through func call
        # actually.
        self.mWrites = {};
        
    def addReads(self,reads):
        '''
        @param {array of ntt-s} reads.
        '''
        for read in reads:
            self.mReads[read.id] = read;

    def addWrites(self,writes):
        for write in writes:
            self.mWrites[write.id] = write;

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
