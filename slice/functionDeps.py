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

        
    def definiteSharedGlobalWrites(self,otherFuncDepsDict):
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

           7: Convert toReturn to a list and return it.
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


        # step 7

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

        '''
        defSGR = self.definiteSharedGlobalReads(otherFuncDepsDict);
        # need to keep track of function argument reads as well
        # because may get taint through them.
        returner = self._getConditionalGlobalShareds(defSGR + self.funcArgReads());
        return returner;

    def _getConditionalGlobalShareds(self, arrayToCheck):
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
        @see conditionalSharedGlobalReads
        '''
        return self._getConditionalGlobalShareds(
            self.definiteSharedGlobalWrites(otherFuncDepsDict) + self.mutableFuncArgWrites());

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
