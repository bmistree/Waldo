#!/usr/bin/env python


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

    def _debugPrint(self):
        print('\n\n\n');
        print(self.funcName);
        print('\nread set:\n')
        for item in self.mReadSet.keys():
            print(item);
        print('\nread set keys:\n');
        for item in self.varReadSet.keys():
            self.varReadSet[item]._debugPrint();
        # for item in self.mWriteSet.keys():
        #     print(item);


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

    def _debugPrint(self):
        toPrint = self.ntt.varName + ': \n';
        for element in self.mReads.keys():
            toPrint += '\t' + element;
        toPrint += '\n';
        print(toPrint);
