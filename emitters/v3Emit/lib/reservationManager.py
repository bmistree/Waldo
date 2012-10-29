#!/usr/bin/env python

import threading;

class ReservationManager(object):

    def __init__(self):
        self._mutex = threading.Lock();
        
        # each object shared between multiple endpoints has a unique
        # id.
        self._nextIdToAssign = 0;

        self._writeSet = {};
        self._readSet = {};
        
        # FIXME: Maybe catch garbage collection of shared object so
        # know can remove it from map
        
    def acquire(self,readIdArray,writeIdArray):
        '''
        @param{Array} readIdArray --- Each element is the integer id of a
        shared object that a Waldo pair is trying to acquire for reading.

        @param{Array} writeIdArray --- Each element is the integer id of a
        shared object that a Waldo pair is trying to acquire for writing.
        
        @returns {Bool} --- true if could acquire (and did acquire).
        false otherwise.  
        '''
        self._lock();

        # check if will have any write conflicts
        for writeId in writeIdArray:

            #### DEBUG
            if not writeId in self._writeSet:
                print(self._writeSet.keys())
                print(writeId)
                assert(False);
            if not writeId in self._readSet:
                assert(False);
            #### END DEBUG

            if self._writeSet[writeId] != 0:
                self._unlock();
                return False;

            if self._readSet[writeId] != 0:
                self._unlock();
                return False;

        # check if will have any read conflicts
        for readId in readIdArray:
            #### DEBUG
            if not readId in self._writeSet:
                assert(False);
            if not readId in self._readSet:
                assert(False);
            #### END DEBUG
            
            if self._writeSet[writeId] != 0:
                self._unlock();
                return False;

        # no conflicts --- acquire the resources
        for readId in readIdArray:
            self._readSet[readId] += 1;
        for writeId in writeIdArray:
            self._writeSet[writeId] += 1;
                
        self._unlock();
        return True;

    def release(self,readIdArray,writeIdArray,commitObjectArray):
        '''
        @param {Array} readIdArray --- @see acquire
        @param {Array} writeIdArray --- @see acquire
        
        @param {Array} commitObjectArray --- An array of external
        objects that must be committted before being released.  Must
        commit all changes within the reservation manager loop to
        ensure that all committed changes are exposed atomically.
        '''
        self._lock();

        for readId in readIdArray:
            #### DEBUG
            if not readId in self._writeSet:
                assert(False);
            if not readId in self._readSet:
                assert(False);
            #### END DEBUG

            self._readSet[readId] -= 1;

        for writeId in writeIdArray:
            #### DEBUG
            if not writeId in self._writeSet:
                assert(False);
            if not writeId in self._readSet:
                assert(False);
            #### END DEBUG

            self._writeSet[writeId] -= 1;

        
        for sharedObj in commitObjectArray:
            sharedObj._commit();
            
        self._unlock();
    
    def registerShared(self,sharedObj):
        self._lock();
        sharedObj.id = self._newId();
        self._writeSet[sharedObj.id] = 0;
        self._readSet[sharedObj.id] = 0;
        self._unlock();
        
    def _lock(self):
        self._mutex.acquire();

    def _unlock(self):
        self._mutex.release();

    def _newId(self):
        '''
        MUST BE CALLED WITHIN LOCK
        '''
        toReturn = self._nextIdToAssign;
        self._nextIdToAssign += 1;
        return toReturn;
