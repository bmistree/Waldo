#!/usr/bin/env python

from typeStack import TypeStack;
from typeStack import NameTypeTuple;
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
            print('\nBehram error need to ensure exists before write to\n');
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


    def _changeArgIds(self):
        '''
        @see _constructMegaFunction
        
        current approach for "inline-ing" arguments and dependencies in
        _constructMegaFunction
        has a problem if re-use function argument ids between
        inlines.  In particular, we have two function calls,
           func(a1,b) and func(a2,b)
        and a1 and a2 are mutable.  The expression that constructs
        a1 includes a shared/global variable.  The expression that
        constructs a2 does not.
        The above should produce the dependency:
        
           a1 <- glob
           a2 <- notGlob
        
        However, if we re-use identifiers between a1 and a2, we'll
        actually get:
        
           a <- glob, notGlob
        
        This means that if notGlob later gets written to, we will
        insert glob into the shared write set, even if glob
        otherwise would have been in the read set.  To get around
        this problem, whenever we enter a FunctionDeps object when
        constructing a mega-function, we change all of its arguments
        identifiers so they will show up separately in the function.
        Do this in this function.
        '''

        # maps ids of ntt-s to replace with ntt-s of replacers.
        foundArgsDict = {};

        # adjust all ntts in read set
        for readNttKey in list(self.mReadSet.keys()):
            readNtt = self.mReadSet[readNttKey];

            if readNtt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT:
                # new name type tuple will automatically have a globally unique id.
                replacement = NameTypeTuple(
                    readNtt.varName,readNtt.varType,readNtt.mutable,readNtt.argPosition);

                # insert replacement into read set
                self.mReadSet[replacement.id] = replacement;

                # insert into foundArgsDict
                foundArgsDict[readNttKey] = replacement;
                
                # remove previous read from read set
                del self.mReadSet[readNttKey];

        for readNttKey in list(self.mReadSet.keys()):
            # in case the ntt is a function call that needs to
            # replace some of its reads as well.
            readNtt.replaceFuncArguments(foundArgsDict);
                

        # adjust all ntts in write set
        for vrsKey in list(self.varReadSet.keys()):
            vrs = self.varReadSet[vrsKey];

            # exchanges any reads made with replacement read in
            # foundArgsDict.  (also replaces ntt if necessary.)
            vrs.replaceFuncArguments(foundArgsDict);
            
            # cannot have a function argument that was in varReadSet,
            # but not read set.
            if vrsKey in foundArgsDict:
                # means that the written to variable was a function
                # argument.  We need to move the VarReadSet object
                # represented by vrs to a new position
                del self.varReadSet[vrsKey];

                newId = vrs.ntt.id;
                self.varReadSet[newId] = vrs;

        
        
    def _constructMegaFunction(self,funcDepsDict,alreadyAdded,argumentArray=None,newFDep=None):
        '''
        Take all reads and writes of current function and add them to
        newFDep (if it isn't None).  For each function call that I
        make, tell the associated FunctionDeps object to take all the
        reads and writes that it makes, and add them to newFDep.
        Finally, return newFDep.

        In a lot of ways, all this does is it inlines the read/write
        dependencies of a function call at the point that it's called.

        To ensure that we don't get into an infinite loop, eg in the following case:

        Function oneFunc (Number a)
        {
           twoFunc();
        }

        Function twoFunc()
        {
           oneFunc(1);
        }

        every time that we encounter a function call ntt, we hash it.
        If its hash exists in the dictionary alreadyAdded, then we do
        not inline the function.  If it does not, we add it and inline
        the function's read/writes.  @see hashSignature of
        FuncCallNtt, which guarantees that for two matching type
        signatures, they will only be the same if they definitely have
        the same shared/global read and write set.

        @param {dict <String:Bool>} alreadyAdded --- where string is
        generated by calling hashSignature on a FuncCallNtt object.
        
        @param {Array of array of ntt-s} argumentArray --- Each
        element of argumentArray contains a list of ntt-s.  Each ntt
        is an item that gets read to construct the function's
        positional argument.  Ensure that adding read dependencies for
        each argument's write.
        
        @param{FunctionDeps} --- A dummy function that should write
        all dependencies to (see above).
        '''
        if argumentArray == None:
            argumentArray = [];
        if newFDep == None:
            newFDep = FunctionDeps('megaTmp');

            
        # @see discussion at top of _changeArgIds.
        self._changeArgIds();
        
            
        # add all of my current reads and var reads to newFDep
        for readKey in self.mReadSet.keys():
            readNtt = self.mReadSet[readKey];
            if ((readNtt.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                (readNtt.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):
                newFDep.addFuncReads([readNtt]);
                
        # add all of my current writes and their dependencies to newFDep.
        for varReadSetKey in self.varReadSet.keys():
            vrs = self.varReadSet[varReadSetKey];
            setNtt = vrs.ntt;
            readNttArray = list(vrs.mReads.values());
            # using false here for redeclaration check because we
            # aren't really redeclaring this write variable when we're
            # composing this mega function.
            newFDep.addToVarReadSet(setNtt);
            newFDep.addReadsToVarReadSet(setNtt,readNttArray);


        # include function calls if we have not already included this
        # specific function call.
        for funcCallKey in self.funcCalls.keys():
            funcCallNtt = self.funcCalls[funcCallKey];
            funcCallName = funcCallNtt.varName;
            hashedFuncCallSignature = funcCallNtt.hashSignature();

            # only need to add a function once.
            if alreadyAdded.get(hashedFuncCallSignature,None) == None:
                alreadyAdded[hashedFuncCallSignature] = True;
                    
                fDep = funcDepsDict.get(funcCallName,None);
                if fDep == None:
                    errMsg = '\nBehram error: trying to call unknown function in ';
                    errMsg += '_constructMegaFunction with key ' + str(funcCallKey) + ' ';
                    errMsg += 'and name ' + funcCallName + '\n';
                    print(errMsg);
                    assert(False);

                # using funcCallNtt.funcArgReads as argument array so
                # because those are the arguments that the function
                # will be called with.
                fDep._constructMegaFunction(
                    funcDepsDict,alreadyAdded,funcCallNtt.funcArgReads,newFDep);

        # handling argument array: for each argument in argument
        # array, assign one of our positional arguments to it (unless
        # the positional argument isn't read.  then can ignore it.)
        for argIndex in range(0,len(argumentArray)):
            argumentsAtPositionArgIndex = argumentArray[argIndex];

            # find corresponding argument ntt
            argNtt = self._getArgNtt(argIndex);
            if argNtt != None:
                newFDep.addToVarReadSet(readNtt);
                newFDep.addReadsToVarReadSet(argNtt,argumentsAtPositionArgIndex);

        return newFDep;


    def _getArgNtt(self,argIndex):
        '''
        Returns the ntt of the argument in this function with arg
        position argIndex.  Returns None if does not exist (could
        happen if an argument isn't actually used in the body of a
        function).
        '''
        for readKey in self.mReadSet.keys():
            readNtt = self.mReadSet[readKey];
            if readNtt.varType == TypeStack.IDENTIFIER_TYPE_FUNCTION_ARGUMENT:
                if readNtt.argPosition == argIndex:
                    return readNtt;

        return None;
    
    def definiteSharedGlobalReads(self,funcDepsDict):
        newFDep = self._constructMegaFunction(funcDepsDict,{});
        return newFDep._definiteSharedGlobalReads(funcDepsDict);
    
    def _definiteSharedGlobalReads(self,funcDepsDict):
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
                (item.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):

                if returnerDict.get(item.id,None) == None:
                    # we did not already have this global.  add it.
                    returnerDict[item.id] = item;

        # flatten the returner dictionary and return it.
        returner = [];
        for key in sorted(returnerDict.keys()):
            returner.append(returnerDict[key]);

        return returner;

    def definiteSharedGlobalWrites(self,funcDepsDict):
        newFDep = self._constructMegaFunction(funcDepsDict,{});
        return newFDep._definiteSharedGlobalWrites(funcDepsDict);

    
    def _definiteSharedGlobalWrites(self,otherFuncDepsDict):
        '''
        WILL NOT CHASE FUNCTION CALLS.
        
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
        
        # for readSetItem in self.varReadSet.values():
        #     readSetItem.ntt.unmark();
        #     for innerNtt in readSetItem.mReads.values():
        #         innerNtt.unmark();
                

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
        
        # for readSetItem in self.varReadSet.values():
        #     readSetItem.ntt.unmark();
        #     for innerNtt in readSetItem.mReads.values():
        #         innerNtt.unmark();


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

    def conditionalSharedGlobalWrites(self,otherFuncDepsDict):
        '''
        @see conditionalSharedGlobalReads, but does not go through
        function calls as well.
        '''
        return self._getConditionalGlobalShareds(
            self.definiteSharedGlobalWrites(otherFuncDepsDict) + self.mutableFuncArgWrites());
    


    def _unmarkAll(self):
        for vReadSetKey in self.varReadSet.keys():
            vReadSet = self.varReadSet[vReadSetKey];
            vReadSet.ntt.unmark();
            for readNttKey in vReadSet.mReads.keys():
                readNtt = vReadSet.mReads[readNttKey];
                readNtt.unmark();


    
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

        
    def replaceFuncArguments(self,foundArgsDict):
        '''
        @param {dict} foundArgsDict --- integer:ntt.  Each integer is
        the id of an ntt (with var type
        IDENTIFIER_TYPE_FUNCTION_ARGUMENT) that should get replaced by
        the value ntt.
        
        @see _changeArgIds of functionDeps
        '''

        if self.ntt.id in foundArgsDict:
            self.ntt = foundArgsDict.get(self.ntt.id);
        else:
            self.ntt.replaceFuncArguments(foundArgsDict);
            
        for readNttKey in list(self.mReads.keys()):
            replacement = foundArgsDict.get(readNttKey,None);
            if replacement != None:
                # means that we need to replace the key

                # first insert new one with replacement id
                self.mReads[replacement.id] = replacement;

                # then remove old one
                del self.mReads[replacement];
            else:
                self.mReads[readNttKey].replaceFuncArguments(foundArgsDict);
        

        
    def addReads(self,reads):
        '''
        @param {array of ntt-s} reads.
        '''
        for read in reads:
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
