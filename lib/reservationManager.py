#!/usr/bin/env python

import threading;


class _ExternalLockedRecord(object):
    # FIXME: This is a duplicate of what's emitted in the uniformHeader.py file
    def __init__(
        self,waldo_initiator_id,endpoint_initiator_id,
        priority,act_event_id,external_id):
        
        self.waldo_initiator_id = waldo_initiator_id
        self.endpoint_initiator_id = endpoint_initiator_id
        self.priority = priority
        self.act_event_id = act_event_id
        self.external_id = external_id
        


class ReservationManager(object):

    def __init__(self):
        self._mutex = threading.Lock();
        
        # each object shared between multiple endpoints has a unique
        # id.
        self._nextIdToAssign = 0;

        # indices are the unique ids of each external (each assigned
        # from _newId incrementing self._nextIdToAssign).  Each value
        # is an array containing _ExternalLockedRecord-s.  (Note: even
        # though writeSet should hold at most one element in its
        # array, we're still using an array to keep the logic similar
        # to _readSet)
        self._writeSet = {};
        self._readSet = {};
        
        # FIXME: Maybe catch garbage collection of shared object so
        # know can remove it from map

        
    def acquire(
        self,readIdArray,writeIdArray,priority,waldo_initiator_id,
        endpoint_initiator_id,event_id):
        '''
        @param{Array} readIdArray --- Each element is the integer id of an
        external object that a Waldo pair is trying to acquire for reading.
        
        @param{Array} writeIdArray --- Each element is the integer id of an
        external object that a Waldo pair is trying to acquire for writing.

        @param {float} priority --- The priority of the transaction
        that is trying to acquire the read/write locks on the externals
        in readIdArray and writeIdArray.

        @param {float} waldo_initiator_id --- The waldo id of the host
        that initiated the transaction that is trying to acquire the
        read/write locks on the externals in readIdArray and
        writeIdArray.

        @param {float} endpoint_initiator_id --- The endpoint id of
        the endpoint that initiated the transaction that is trying to
        acquire the read/write locks on the externals in readIdArray
        and writeIdArray.

        @param {int} event_id --- The id of the active event on the
        local endpoint that is trying to acquire the external.

        @returns {Bool} --- true if could acquire (and did acquire).
        false otherwise.  
        '''
        self._lock()

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

            if len(self._writeSet[writeId]) != 0:
                self._unlock();
                return False;

            if len(self._readSet[writeId]) != 0:
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
            
            if len(self._writeSet[writeId]) != 0:
                self._unlock();
                return False;

        # no conflicts --- acquire the resources
        for readId in readIdArray:

            locked_record = _ExternalLockedRecord(
                waldo_initiator_id,endpoint_initiator_id,priority,
                event_id,readId)
            
            self._readSet[readId].append(locked_record)


            
        for writeId in writeIdArray:
            locked_record = _ExternalLockedRecord(
                waldo_initiator_id,endpoint_initiator_id,priority,
                event_id,writeId)
            self._writeSet[writeId].append(locked_record)
                
        self._unlock();
        return True;

    
    def release(
        self,readIdArray,writeIdArray,commitObjectArray,
        priority,waldo_initiator_id,endpoint_initiator_id,event_id):
        '''
        @param {Array} readIdArray --- @see acquire
        @param {Array} writeIdArray --- @see acquire
        
        @param {Array} commitObjectArray --- An array of external
        objects that must be committted before being released.  Must
        commit all changes within the reservation manager loop to
        ensure that all committed changes are exposed atomically.

        @param {float} priority --- @see acquire
        @param {float} waldo_initiator_id --- @see acquire
        @param {float} endpoint_initiator_id --- @see acquire
        @param {int} event_id --- @see acquire
        '''
        self._lock();

        # remove read locks
        for readId in readIdArray:
            #### DEBUG
            if not readId in self._writeSet:
                assert(False);
            if not readId in self._readSet:
                assert(False);
            #### END DEBUG

            # FIXME: inefficient to use lists here. why not just hash
            # identifying information together and use a dict?
            self._removed_locked_record(
                self._readSet[readId],priority,waldo_initiator_id,
                endpoint_initiator_id,event_id,'reads')

            
        # remove write locks
        for writeId in writeIdArray:
            #### DEBUG
            if not writeId in self._writeSet:
                assert(False);
            if not writeId in self._readSet:
                assert(False);
            #### END DEBUG
            self._removed_locked_record(
                self._writeSet[writeId],priority,waldo_initiator_id,
                endpoint_initiator_id,event_id,'writes')

        
        for sharedObj in commitObjectArray:
            sharedObj._commit();
            
        self._unlock();

        
    def _removed_locked_record(
        self,array_to_remove_from,priority,waldo_initiator_id,
        endpoint_initiator_id,event_id,code_tag):
        '''
        @param {Array} array_to_remove_from --- An array of
        _ExternalLockedRecords.  Either self._writeSet or
        self._readSet.

        @param {float} priority --- @see release
        @param {float} waldo_initiator_id --- @see release
        @param {float} endpoint_initiator_id --- @see release
        @param {int} event_id --- @see release
        
        @param {String} code_tag --- Use this function on either the
        read lock array or the write lock array.  This function can
        throw an error.  Want to report whether it was the read array
        or write array that caused the error, and use the code_tag to
        distinguish between them.
        '''
        for index in range(0,len(array_to_remove_from)):
            locked_record = array_to_remove_from[index]

            if ((locked_record.waldo_initiator_id == waldo_initiator_id) and
                (locked_record.endpoint_initiator_id == endpoint_initiator_id) and
                (locked_record.priority == priority) and
                (locked_record.act_event_id == event_id)):

                to_remove_index = index

        #### DEBUG
        if to_remove_index == None:
            err_msg = '\nBehram error: no locked record '
            err_msg += 'to remove lock in reservation manager.  '
            err_msg += 'Code tag: ' + code_tag + '.\n'
            print err_msg
            assert(False)
        #### END DEBUG

        # actually remove from the write set
        del array_to_remove_from[to_remove_index]
        

    
    def registerShared(self,sharedObj):
        self._lock();
        sharedObj.id = self._newId();
        self._writeSet[sharedObj.id] = []
        self._readSet[sharedObj.id] = []
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
