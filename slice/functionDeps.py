#!/usr/bin/env python

from typeStack import TypeStack;
import json;

class FunctionDeps(object):

    def __init__(self,funcName):
        # name to an array of NameTypeTuple-s each variable in here
        # may change and depends on reading other variables in the
        # list NameTypeTuple-s
        self.varReadSet = {}; 

        # the variables that this function reads from. dict from var
        # name to NameTypeTuple.
        self.mReadSet = {}; 
        self.funcName = funcName;
        
    def addToVarReadSet(self,nodeName,nameTypeTuple):
        if self.varReadSet.get(nodeName,None) == None:
            self.varReadSet[nodeName] = VarReadSet(nameTypeTuple);
            
    def addReadsToVarReadSet(self,nodeName,reads):
        if self.varReadSet.get(nodeName,None) == None:
            print('\nBehram error.  Should not permit redeclaration.\n');
            assert(False);
        else:
            self.varReadSet[nodeName].addReads(reads);
            
        self.addFuncReads(reads);
            
    def addFuncReads(self,reads):
        for read in reads:
            self.mReadSet[read.varName] = read;

    def jsonize(self):
        returner = {};
        returner['funcName'] = self.funcName;
        returner['readSet'] = sorted(self.mReadSet.keys());

        # write read set list
        varReadSetList = [];
        for itemKey in sorted(self.varReadSet.keys()):
            varReadSetItem = self.varReadSet[itemKey];
            jsonString = varReadSetItem.jsonize();
            varReadSetList.append(json.loads(jsonString));

        # definite global/shared reads
        globSharedReads = [];
        for ntt in self.definiteSharedGlobalReads():
            jsoned = ntt.jsonize();
            globSharedReads.append(json.loads(jsoned));
        returner['definiteGlobalSharedReads'] = globSharedReads;

        #definite global/shared writes
        globSharedWrites = [];
        for ntt in self.definiteSharedGlobalWrites():
            jsoned = ntt.jsonize();
            globSharedWrites.append(json.loads(jsoned));
        returner['definiteGlobalSharedWrites'] = globSharedWrites;

        # return the json
        return json.dumps(returner);

        
    def _debugPrint(self):
        print('\n\n\n');
        print(self.funcName);
        print('\n*****read set:*****\n')
        for item in self.mReadSet.keys():
            print(item);

            
        print('\n****read set keys:****\n');
        for item in self.varReadSet.keys():
            self.varReadSet[item]._debugPrint('\t');

        print('\n***definite shared global reads:****\n');
        print '\t',
        for ntt in self.definiteSharedGlobalReads():
            print ntt.varName + '\t',
        print('\n');

        print('\n***definite shared global writes:****\n');
        print '\t',
        for ntt in self.definiteSharedGlobalWrites():
            print ntt.varName + '\t',
        print('\n\n');

        
            
    def definiteSharedGlobalReads(self):
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
        '''
        returner = [];
        for key in sorted(self.mReadSet.keys()):
            item = self.mReadSet[key];
            if ((item.varType == TypeStack.IDENTIFIER_TYPE_SHARED) or
                (item.varType == TypeStack.IDENTIFIER_TYPE_ENDPOINT_GLOBAL)):
                returner.append(item);
        return returner;

        
    def definiteSharedGlobalWrites(self):
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
                toReturn[potentialNtt.varName] = potentialNtt;
                
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
                                toReturn[dependencyNtt.varName] = dependencyNtt;


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
        
        
    # def conditionalSharedGlobalReads(self):
    #     '''
    #     Note: the below may all be hocum.
    #     The pseudocode for doing this is as follows:
        
    #        1: annotate all writtenTo ntts in self.varReadSet with a 1
    #           marker if they are global/shared.  Otherwise, annotate
    #           them with a 0.

    #        2: For each dependency, annotate it with a 1 marker if it
    #           is global/shared and it is mutable.  Otherwise, annotate
    #           it with a 0 marker.

    #        3: Set a dirty bit to false
           
    #        4: For each element in self.varReadSet, if writtenTo's
    #           marker is zero and it is mutable and one of its
    #           dependency's markers are 1, update its marker to 1 and
    #           set dirty bit to True.

    #        5: If the dirty bit is True, goto 3.

    #        6: Run through all elements in self.varReadSet.  If the
    #           writtenTo is marked with a 1 and it is global/shared
    #           append it to returner.  If the writtenTo is marked with
    #           a 1 and

    #        7: Remove all markers
    #     '''
    #     lkjs;
    #     pass;
        
    # def conditionalSharedGlobalWrites(self):
    #     lkjs;
    #     pass;

            

class VarReadSet(object):
    def __init__(self,ntt):
        self.ntt = ntt;
        self.mReads = {};
        # note: this should never really be populated because there
        # are not ways to return and modify....except through func call
        # actually.
        self.mWrites = {};
        
    def addReads(self,reads):
        for read in reads:
            self.mReads[read.varName] = read;

    def addWrites(self,writes):
        for write in writes:
            self.mWrites[write.varName] = write;

    def jsonize(self):
        returner = {};
        returner['readSetNtt'] = json.loads(self.ntt.jsonize());

        readArray = [];
        for readKey in sorted(self.mReads.keys()):
            readItem = self.mReads[readKey];
            jsoned = readItem.jsonize();
            readArray.append(json.loads(jsoned));

        returner['reads'] = readArray;
        return json.dumps(returner);

            
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
