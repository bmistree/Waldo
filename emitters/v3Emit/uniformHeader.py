#!/usr/bin/env python

import emitUtils;

def uniformHeader():
    '''    
    All Waldo files have the same header code regardless of what is
    specified in their contents.  This header code imports libraries,
    creates base classes from which each endpoint forms and from which
    active events form, etc.

    This file returns that header section.  Note that it still
    contains a lot of debugging checks, comments, etc.
    
    @returns {String} --- The beginning of a Waldo file common to all
    Waldo files regardless of source text.
    '''
    
    return r"""#!/usr/bin/env python

import inspect as _inspect
import time as _time
import threading
import Queue
import numbers
import random

'''
Designed message sequencing so that the sender of a message
specifices which function gets called on the receiver.  It also
specifies the name of the event that is requesting this function to be
called.  It specifies the event name so that the receiver knows what
variables are going to be read from and written to and can either not
accept the sequence, or allow it to continue.

Given the name of a function to call, the receiver should know what
function to tell the sender to call next in its reply (or to tell the
receiver that the sequence has completed).

-----------------------
Note: We will update shared/global variables on both endpoints if
and only if a message is sent in one of the functions.

A receiver can tell a sender that he/she will not executed the
requested function only if this is the first time that the sender has
requested that the action with a given id be run.  After the receiver
agrees to add the event, the event must run to completion, and cannot
be postponed on either side.

We ensure that an entire function is atomic.  If I have a function,
func that initiates several message sequences through calls msgA,
msgB, msgC, how does the other endpoint know when to commit the final
changes?

func()
{
   msgA();
   //operate on some data here
   msgB();
   //operate on some data here
   msgC();
   //operate on some data here
}

Note that if we send a stream completion message at the end of msgA
and return the variables that A held to process, then what happens if
the other endpont starts a sequence that interferes with b?

If the other endpoint calls a local function that reads data that A
committed as part of func?  Would be exposing intermediate data.  Bad.

What this implementation does is send back two types of sentinels.
One is a sentinel that a stream has completed.  When an event
initiator receives this sentinel, it knows that it can resume
processing in the function body where it left off.  (If the endpoint
that did not initiate an event receives a stream completed sentinel,
it ignores it.)

The second type of sentinel is a release_event_sentinel (roughly,
notifies that event is complete).  An event completed sentinel tells
the endpoint that did not initiate the event that it should commit the
data from the event and release the locks on the local and global
variables that the event used.

These sentinels get sent whenever a function that sent a message
during the course of its execution completes.

This strategy can be particularly problematic if a lot of work was
backloaded to the end of the function because we lock a lot of data
that we do not really need.
''' """ + """

# emitting empty oncomplete dict for now, will need to specially
# populate it with oncomplete functions in future commits.
_OnCompleteDict = { };

# special-casing keys for the refresh keyword
_REFRESH_KEY = '%s';
_REFRESH_RECEIVE_KEY = '%s';
_REFRESH_SEND_FUNCTION_NAME = '%s';
_REFRESH_RECEIVE_FUNCTION_NAME = '%s';
""" % (emitUtils._REFRESH_KEY,emitUtils._REFRESH_RECEIVE_KEY,
       emitUtils._REFRESH_SEND_FUNCTION_NAME,
       emitUtils._REFRESH_RECEIVE_FUNCTION_NAME) + r"""

def _deepCopy(srcDict,dstDict,fieldNamesToSkipCopy=None):
    '''
    @param {dict} fieldNamesToSkipCopy --- If not None, then if a key
    is in source and in fieldNamesToSkipCopy, then do not copy value
    for dst.
    
    FIXME: for now, just copy by value.  Will eventually need to deep
    copy.  Note that this does not ensure that src and dst will both
    have the same fields as each other.  dst can be a superset of src.
    '''
    if fieldNamesToSkipCopy == None:
        fieldNamesToSkipCopy = {};
    
    for srcKey in srcDict.keys():
        if srcKey in fieldNamesToSkipCopy:
            continue;
        dstDict[srcKey] = srcDict[srcKey];

class _OnComplete(threading.Thread):
    def __init__(self,function,onCompleteFuncKey,endpoint,context):
        self.function = function;
        self.onCompleteFuncKey = onCompleteFuncKey; # for debugging
        self.endpoint = endpoint;
        self.context = context;

        threading.Thread.__init__(self);
        
    def run(self):

        self.function(self.endpoint,
                      _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED,
                      None,
                      self.context);
       
    def fire(self):
        self.start();

class _RunnerAndHolder(threading.Thread):
    '''
    If a call to run and hold a resource has been accepted, then
    create a _RunnerAndHolder thread, which actually executes what had
    been requested to be run and held.  Note that we have already
    reserved the resources (on our end) to run and hold the function,
    so closure_to_execute does not have to as well.
    '''
    def __init__(
        self,closure_to_execute,priority,waldo_initiator_id,
        endpoint_initiator_id,*args):
        '''
        @param {closure} closure_to_execute --- The closure 
        @param {float} priority ---
        @param {float} waldo_initiator_id ---
        @param {float} endpoint_initiator_id
        
        @param {*args} *args --- The arguments that get passed to the
        closure to execute.
        
        '''
        self.closure_to_execute = closure_to_execute
        self.priority = priority
        self.waldo_initiator_id = waldo_initiator_id
        self.endpoint_initiator_id = endpoint_initiator_id
        self.args = args
        threading.Thread.__init__(self)

    def run(self):
        # actually run the function
        self.closure_to_execute(
            self.priority,self.waldo_initiator_id,
            self.endpoint_initiator_id,*self.args)

        
class _LockedRecord(object):
    def __init__(
        self,waldo_initiator_id,endpoint_initiator_id,priority,act_event_id):
        
        self.waldo_initiator_id = waldo_initiator_id
        self.endpoint_initiator_id = endpoint_initiator_id
        self.priority = priority
        self.act_event_id = act_event_id 

        
class _ExtInterfaceCleanup(threading.Thread):
    '''
    If we begin an internal event by being called externally, we need
    to do two things:
    
      1) If we were passed any external objects as function arguments,
         we put these in the external store and increased their
         reference counts by one.  After finishing the event, we need
         to decrement the reference counts for each of these objects
         to their original state.

      2) Check whether to remove any external objects from the shared
         store because nothing is pointing at them (ie, call
         gcCheckEmptyRefCounts)
    
    This class contains a separate class to do each.
    '''
    def __init__(self, externalsArray,externalStore,endpointName):
        '''
        @param {Array} externalsArray --- An array of external
        (_External) objects.

        @param {ExternalStore object} --- externalStore
        '''
        self.externalsArray = externalsArray;
        self.externalStore = externalStore;
        self.endpointName = endpointName;

        threading.Thread.__init__(self);
        
    def run(self):

        # FIXME: Could eventually be much faster if passed the array
        # of externalObjects to decrease reference counts for and did
        # them as a batch rather than doing each successively.
        for extObj in self.externalsArray:
            self.externalStore.changeRefCountById(self.endpointName,extObj.id,-1)
            
        self.externalStore.gcCheckEmptyRefCounts();

def _generate_transaction_priority(previous_priority=None):
    '''
    @param{float} previous_priority --- If the transaction was aborted, contains
    the float id of the previous transaction
    '''
    
    # FIXME: for now, generating transaction ids with no forethought
    # to previous ids' value.  ids are used to determine which
    # transaction wins in cases of potential deadlock (higher ids
    # always win).  If want to add fairness, may want to increase
    # value of transaction id each time it fails
    
    return random.random()
    
        
class _MsgSelf(threading.Thread):
    '''
    Used by an endpoint to start a new thread to send a message to
    itself (arises eg from jump statements)
    '''
    def __init__(self,endpoint,msgDict):
        self.endpoint = endpoint;
        self.msgDict = msgDict;
    def start(self):
        self.endpoint._msgReceive(self.msgDict);

        
class _NextEventLoader(threading.Thread):
    '''
    Separate thread kicks the endpoint to see if there is another
    event that it can schedule.  
    '''
    def __init__(self,endpoint):
        self.endpoint = endpoint;
        threading.Thread.__init__(self);
    def run(self):
        self.endpoint._checkNextEvent();


_EXT_ID_KEY_SEPARATOR = '________'

def _externalIdKey(endpointName,extId):
    return str(extId) + _EXT_ID_KEY_SEPARATOR + endpointName;

def _keyToExternalId(key):
    '''
    @param {String} key --- Should have been generated from _externalIdKey;

    @returns{int} --- the id of the external object (ie, the first
    part of the key.
    '''
    index = key.find(_EXT_ID_KEY_SEPARATOR);
    #### DEBUG
    if index == -1:
        assert(False);
    #### END DEBUG

    return int( key[0:index] );

def _getExtIdIfMyEndpoint(key,endpointName):
    '''
    @returns {int or None} --- Returns None if this key does not match
    this endpoint. Otherwise, return the external id.
    '''
    index = key.find(_EXT_ID_KEY_SEPARATOR);

    #### DEBUG
    if index == -1:
        assert(False);
    #### END DEBUG

    if key[index + len(_EXT_ID_KEY_SEPARATOR):] != endpointName:
        return None;
    
    return _keyToExternalId(key);       

class _WaldoListMapObj(object):
    '''
    Waldo lists and maps support special operations that are like
    regular maps and lists, but allow us to instrument external lists
    and maps to do special things.  For instance, if we have an
    external list/map that represents the file system, for each get
    performed on it, we could actually read the file from the file
    system.  That way, do not have to hold full file system in memory,
    but just fetch resources whenever they are required.
    '''
    def __init__(self,initial_val,requires_copy=False):
        if not requires_copy:
            self.val = initial_val
        else:
            # FIXME: we need to perform a deep copy when application
            # code passes us a map or a list.  That way, we won't have
            # side effects.  For now though, skipping deep copy.  Must
            # fix later.
            self.val = initial_val

    def _map_list_serializable_obj(self):
        '''
        Must be able to serialize maps and lists to send across the
        network to the opposite side.  This function call returns an
        object that can be string-ified by a call to json.dumps.

        If values in list/map are lists or maps themselves, need to
        get serializable objects for these too.
        '''

        # pure virtual function in parent class.  must define in each
        # of map and list itself.
        assert(False)

    def _map_list_remove(self,index_to_del):
        del self.val[index_to_del]
        
    def _map_list_bool_in(self,val_to_check):
        return val_to_check in self.val

    def _map_list_iter(self):
        return iter(self.val)

    def _map_list_index_insert(self,index_to_insert,val_to_insert):
        self.val[index_to_insert] = val_to_insert

    def _map_list_len(self):
        return len(self.val)
        
    def _map_list_index_get(self,index_to_get):
        '''
        @param{anything} index_to_get --- Index to use to get a field
        from the map.
        '''
        return self.val[index_to_get]

    def _map_list_copy_return(self):
        '''
        When returning data from out of Waldo to application code,
        perform a deep copy of Waldo list/map so that have isolation
        between Waldo and non-Waldo code.
        '''
    
        def _copied_dict(to_copy):
            '''
            Produces a copy of to_copy, where all the WaldoLists
            and maps are replaced by python lists and dicts.
            '''
            new_dict = {}
            for key in to_copy.keys():
                to_add = to_copy[key]

                if isinstance(to_add,_WaldoMap):
                    to_add = _copied_dict(to_add._map_list_serializable_obj())
                elif isinstance(to_add,_WaldoList):
                    to_add = _copied_list(to_add._map_list_serializable_obj())

                elif isinstance(to_add,dict):
                    to_add = _copied_dict(to_add)
                elif isinstance(to_add,list):
                    to_add = _copied_list(to_add)

                new_dict[key] = to_add
            return new_dict

        def _copied_list(to_copy):
            '''
            Produces a copy of to_copy, where all the WaldoLists
            and maps are replaced by python lists and dicts.
            '''        
            new_array = []
            for item in to_copy:
                to_add = item
                if isinstance(to_add,_WaldoMap):
                    to_add = _copied_dict(to_add._map_list_serializable_obj())
                elif isinstance(to_add,_WaldoList):
                    to_add = _copied_list(to_add._map_list_serializable_obj())

                elif isinstance(to_add,dict):
                    to_add = _copied_dict(to_add)
                elif isinstance(to_add,list):
                    to_add = _copied_list(to_add)

                    
                new_array.append(to_add)

            return new_array

        
        # FIXME: Actually need to perform deep copy of data out.
        if isinstance(self.val,list):
            return _copied_list(self.val)
        return _copied_dict(self.val)
    

class _WaldoList(_WaldoListMapObj):
    '''
    All Waldo lists, external and internal inherit or instantiate this
    class.
    '''
    
    def _list_append(self,to_append):
        self.val.append(to_append)

    def _map_list_serializable_obj(self):
        '''
        @see _map_list_serializable_obj in parent class
        '''
        to_return = self.val
        if len(self.val) > 0:
            # note that this probably doesn't need to be a dynamic
            # check if restructured a lot of emitting and added
            # different list types for lists of value types vs lists
            # of container types.  for now though, this is easier and
            # should work
            if isinstance (self.val[0],_WaldoListMapObj):
                
                # if this list contains lists and maps, then construct
                # a list to return from calling
                # map_list_serializable_obj on each element in the
                # list. 
                to_return = [ x._map_list_serializable_obj()
                              for x in self.val ]

        return to_return
        

class _WaldoMap(_WaldoListMapObj):
    '''
    All Waldo maps, internal or external inherit or instantiate this
    base class.
    '''
    def _map_list_serializable_obj(self):
        '''
        @see _map_list_serializable_obj in parent class
        '''
        to_return = self.val
        if len(self.val) > 0:
            
            # note that this probably doesn't need to be a dynamic
            # check if restructured a lot of emitting and added
            # different list types for lists of value types vs lists
            # of container types.  for now though, this is easier and
            # should work
            if isinstance (self.val.values()[0],_WaldoListMapObj):

                # if this map contains lists and maps, then construct
                # a map to return from calling
                # map_list_serializable_obj on each element in the
                # map
                to_return = {}
                for key in self.val.keys():
                    item = self.val[key] 
                    to_return[key] = item._map_list_serializable_obj()

        return to_return


    
class _ExternalStoreElement(object):
    def __init__(self,externalObject):
        self.referenceCount = 0;
        self.externalObject = externalObject;

        
class _ExternalStore(object):
    def __init__(self):
        # maps what is returned from _externalIdKey to
        # _ExternalStoreElement (reference count + object itself)
        self.dict = {};
        self._mutex = threading.RLock();

    def gcCheckEmptyRefCounts(self):
        '''
        We do not want to hold onto a reference to to the externally
        shared object forever because this would prevent the shared
        object from being garbage collected when no other references
        point at it.  Therefore, after commit check if need to hold
        onto the external any longer.
        '''
        self._lock();
        
        toRemove = [];
        for keys in self.dict.keys():
            element = self.dict[keys];
            if element.referenceCount == 0:
                toRemove.append(keys);
                
        for keyToRemove in toRemove:
            del self.dict[keyToRemove];

        self._unlock();

    def getExternalObject(self,endpointName,extId):
        '''
        @returns{External shared object or None} --- None if does not
        exist in dictionary.
        '''
        self._lock();

        key = _externalIdKey(endpointName,extId);
        returner = self.dict.get(key,None);

        self._unlock();

        if returner == None:
            return None;
        
        return returner.externalObject;


    def incrementRefCountAddIfNoExist(self,endpointName,extObj):
        '''
        Only interface for adding external objects if they do not
        already exist.  When add (or even if it already exists),
        increment reference count by 1.
        '''
        self._lock();
        key = _externalIdKey(endpointName,extObj.id);
        extElement = self.dict.get(key,None);
        if extElement == None:
            self.dict[key] = _ExternalStoreElement(extObj);

        self.changeRefCountById(endpointName,extObj.id,1,True);
        
        self._unlock();
    
    def changeRefCountById(self,endpointName,extId,howMuch,alreadyLocked=False):
        '''
        @param{String} endpointName
        @param{int} extId
        @param{int} howMuch
        
        Throws an error if the external does not already exist in dict.
        '''
        if not alreadyLocked:
            self._lock();

        key = _externalIdKey(endpointName,extId);
        extElement = self.dict.get(key,None);

        #### DEBUG
        if extElement == None:
            assert(False);
        #### END DEBUG
                        
        extElement.referenceCount += howMuch;

        #### DEBUG        
        if extElement.referenceCount < 0:
            assert(False);
        #### END DEBUG
            
        if not alreadyLocked:
            self._unlock();
        
        
    def _lock(self):
        self._mutex.acquire();
    def _unlock(self):
        self._mutex.release();

        

class _ExecuteActiveEventThread(threading.Thread):
    '''
    Each _ActiveEvent only performs the internal execution of its
    relevant code on a separate thread from the calling thread.  This
    ensures that when checking whether any inactive threads can run,
    we do not have to actually wait for each to finish executing
    before scheduling the next.
    '''

    def __init__(self,toExecEvent,context,callType,endpoint,extsToRead,extsToWrite):
        '''
        @param{_ActiveEvent} toExecEvent
        @param{_Context} context
        '''
        self.toExecEvent = toExecEvent;
        self.context = context;
        self.callType = callType;

        self.endpoint = endpoint;
        self.extsToRead = extsToRead;
        self.extsToWrite = extsToWrite;

        threading.Thread.__init__(self);


        
    def run(self):
        try:
            self.toExecEvent.executeInternal(self.context,self.callType);
        except _PostponeException as postExcep:

            # FIXME: It sucks that we have to wait until an event got
            # postponed to actually remove the read-write locks we
            # generated *if* shared external resources are heavily in
            # demand and do a lot of computation on top of them.
            # Instead, could do something like we do with the rest of
            # our data (make deep copy of data first, and use
            # that...which we then couldn't commit)
            
            # should release read/write locks held on external data
            # here and backout changes because know that we were
            # postponed and that there can be no further operations
            # made on them.  note that any call into internal
            # functions must be through this function.  So we're good
            # if we just catch all postpones here.


            # calls backout on everything that we read/wrote to as
            # well as cleaning up reference counts for the external
            # store.  note: we know nothing else will subsequently
            # touch internal data of this context.
            self.context.backoutExternalChanges();

            
            # remove the read/write locks made on externals for this event
            # in reservation manager.
            self.endpoint._reservationManager.release(
                self.extsToRead,
                self.extsToWrite,
                []);

            
class _PostponeException(Exception):
    '''
    Used by executing active events when they know that they have been
    postponed.  Unrolls back to handler that had been waiting for them
    to execute.
    '''
    pass;

def _defaultFunction(*args,**kwargs):
    '''
    Used as an initializer for Waldo function objects.
    '''
    return;

class _Context(object):
    SHARED_DICT_NAME_FIELD = 'shareds';
    END_GLOBALS_DICT_NAME_FIELD = 'endGlobals';
    SEQ_GLOBALS_DICT_NAME_FIELD = 'seqGlobals';
    DNE_DICT_NAME_FIELD = 'dnes';
    
    DNE_PLACE_HOLDER = None;
    
    # Guarantee that no context can have this id.
    INVALID_CONTEXT_ID = -1;

    def __init__(self,extStore,endpointName):
        # actively executing events that start message sequences block
        # until those message sequences are complete before
        # continuing.  to communicate to those active events that the
        # sequence they requested has either completed or that it was
        # required to be postponed, use the msgReceivedQueue thread
        # safe queue.  
        self.msgReceivedQueue = Queue.Queue();

        # oncreate initializes shared, endglobals, and seqglobals
        # dicts for each endpoint's committed contexts
        # for contexts created from message receptions, these fields
        # are populated by _ActiveEvent's knowledge of what to select
        # from each endpoint's committed context.
        self.shareds = {};
        self.endGlobals = {};
        self.seqGlobals = None;
        
        self.id = None;

        # for active events, we need to know whether to send a release
        # event sentinel to the other side.
        # The conditions under which we do this are:
        #    1: At some point across the event, we sent the other side
        #       a message
        #    2: Our event has run to completion.
        #
        # The messageSent flag handles the first of these conditions.
        # It gets set to true any time we send a message to the other
        # side.
        self.messageSent = False;

        # Whenever we finish a message sequence, append the
        # information about its onComplete handler to this context's
        # array.  when we commit this context object, we can fire all
        # the handlers.  Each element is an _OnComplete object.
        self.onCompletesToFire = [];

        # contains the _externalIdKey-d version of all externals that
        # got written to on the local endpoint during this event
        # sequence.  during this event sequence (and therefore all the
        # externals that we'll either need to commit to or back out
        # depending on whether the event proceeds to completion.
        self.writtenToExternalsOnThisEndpoint = {};
        self.externalStore = extStore;

        # maps external ids to integers.  The idea is that if we
        # postpone an event, we also need to remove all of the changes
        # made to the external store's reference counts.
        self.refCounts = {};

        # @see holdExternalReferences
        self.heldExternalReferences = [];
        self.endpointName = endpointName;

    def notateWritten(self,extId):
        '''
        @param{unique int} --- extId
        
        We keep track of all the externals that have been written to
        during the course of this active event.  This is so that we
        know what externals we'll need to commit or to roll back when
        event gets postponed or committed.
        '''
        key = _externalIdKey(self.endpointName,extId);
        self.writtenToExternalsOnThisEndpoint[key] = True;

    def increaseContextRefCountById(self, extId):
        key = _externalIdKey(self.endpointName,extId);
        if not (key in self.refCounts):
            self.refCounts[key] = 0;
        self.refCounts[key] += 1;

    def increaseContextRefCount(self, externalObject):
        return increaseContextRefCountById(externalObject.id);

    def decreaseContextRefCountById(self,extId):
        key = _externalIdKey(self.endpointName,extId);
        if not (key in self.refCounts):
            self.refCounts[key] = 0;
        self.refCounts[key] -= 1;
    
    def decreaseContextRefCount(self, externalObject):
        decreaseContextRefCountById(externalObject.id);


    def holdExternalReferences(self,externalVarNames):
        '''
        @param {Array} externalVarNames --- Each element is a string
        that represents the internal name of the external variable
        that is being passed in.

        Should only be called once: when initially create context
        
        When create an active context for an event, run through all
        variable names for externals that could be used during the
        execution of the function.  For each, increment its reference
        count by 1 in the external data store (this happens in @see
        holdExternalReferences).  If the event gets postponed, must
        decrement each of taken references.  Similarly, if event runs
        to completion, must decrement the references taken.
        
        '''
        # externalVarNames is a list of all the names of global
        # variables that this event touches that have external types.
        for externalVarName in externalVarNames:

            #### DEBUG
            if not (externalVarName in self.endGlobals):
                assert(False);
            
            #### END DEBUG
                
            externalId = self.endGlobals[externalVarName];
            
            if externalId != None:
                # the external id can equal none if the external is
                # unitialized to a value.

                # ensures that this external object will not go away
                # while we are operating on it.
                self.externalStore.changeRefCountById(
                    self.endpointName,externalId,1);

                key = _externalIdKey(self.endpointName,externalId);
                self.heldExternalReferences.append(key);
        
        
    def mergeContextIntoMe(self,otherContext):
        '''
        Take all the shared/globals from the other context and put it
        into this one.

        Should only call this function on each endpoint's committed
        context.
        '''
        _deepCopy(otherContext.shareds,self.shareds);
        _deepCopy(otherContext.endGlobals,self.endGlobals);

        # no need to copy seqGlobals, because committed contexts do
        # not have sequence globals.

    def copyForActiveEvent(self,activeEvent,contextId):
        '''
        Any time that I start a new sequence, copy an existing context
        from the committed context.  then apply the copy to committed
        later.
        
        @param {_ActiveEvent object} activeEvent --- only copies into
        the active event object all the data that activeEvent is known
        to read from/write to.
        '''
        returner = _Context(self.externalStore,self.endpointName);        
        for readKey in activeEvent.activeGlobReads.keys():
            if readKey in self.shareds:
                returner.shareds[readKey] = self.shareds[readKey];
            elif readKey in self.endGlobals:
                returner.endGlobals[readKey] = self.endGlobals[readKey];
            else:
                # means that this endpoint does not have the field
                # that we are copying (ie, this event relies on the
                # other endpoint's endpoint global variable.  put in a
                # does not exist placeholder.
                returner.endGlobals[readKey] = _Context.DNE_PLACE_HOLDER;


        for writeKey in activeEvent.activeGlobWrites.keys():
            if writeKey in self.shareds:
                returner.shareds[writeKey] = self.shareds[writeKey];
            elif writeKey in self.endGlobals:
                returner.endGlobals[writeKey] = self.endGlobals[writeKey];
            else:
                # means that this endpoint does not have the field
                # that we are copying (ie, this event relies on the
                # other endpoint's endpoint global variable.  put in a
                # does not exist placeholder.
                returner.endGlobals[writeKey] = _Context.DNE_PLACE_HOLDER;
                

        returner.seqGlobals = activeEvent.seqGlobals;
        returner.id = contextId;

        return returner;


    def generateEnvironmentData(self,activeEventObj):
        '''
        Should take all the shared variables and write them to a
        dictionary.  The context of the other endpoint should be able
        to take this dictionary and re-constitute the global variables
        from it from its updateEnvironmentData function.

        @see _Mesasge class's _endpointMsg function and @see
        _msgReceive functions.
        
        FIXME: must be able to preserver reference structures.
        '''

        # the filter operation ensures that only need to transmit and
        # update data that are read/written by this event
        returner = {
            self.DNE_DICT_NAME_FIELD: activeEventObj.filterDoesNotExist(self.endGlobals),
            self.SHARED_DICT_NAME_FIELD: activeEventObj.filterSharedsForMsg(self.shareds),
            self.END_GLOBALS_DICT_NAME_FIELD: activeEventObj.filterEndGlobalsForMsg(self.endGlobals),
            self.SEQ_GLOBALS_DICT_NAME_FIELD: activeEventObj.filterSeqGlobalsForMsg(self.seqGlobals)
            };
        
        return returner;

    def updateEnvironmentData(self,contextMsgDict,endpoint):
        '''
        The other side sends us a dictionary like produced from @see
        generateEnvironmentData.  Given this dictionary, we need to
        update our local self.shareds, self.endglobals, and
        self.seqGlobals.

        Importantly, the other side inserts DNE_SENTINEL values for
        messages that do not exist

        @see generateEnvironmentData
        '''
        dneDict = contextMsgDict[self.DNE_DICT_NAME_FIELD];
        
        # FIXME: right now, just doing a "deep" copy of the data (that
        # doesn't do anything).  In actuality, will need to handle
        # references etc.
        _deepCopy(contextMsgDict[self.SHARED_DICT_NAME_FIELD],self.shareds);
        _deepCopy(contextMsgDict[self.END_GLOBALS_DICT_NAME_FIELD],self.endGlobals,dneDict);
        _deepCopy(contextMsgDict[self.SEQ_GLOBALS_DICT_NAME_FIELD],self.seqGlobals);


    def postpone(self):
        '''
        Gets called when postponing an event.  Note that because the
        actual execution of event code is on another thread that may
        continue to run after postpone is called, cannot do clean up
        of external references and backout of external objects here
        (ie, call self.backoutExternalChanges).  That gets done from
        the exception-catching block of the _ExecuteActiveEventThread
        object.
        '''
        self.signalMessageSequenceComplete(
            _Context.INVALID_CONTEXT_ID,None,None,None);

    def backoutExternalChanges(self):
        '''
        Resets all the changes that were made external objects along
        the way.  (Including reference count changes in external
        store.)
        '''
        for key in self.writtenToExternalsOnThisEndpoint.keys():
            extId = _keyToExternalId(key);
            
            extObj = self.externalStore.getExternalObject(
                self.endpointName,extId);
            #### DEBUG
            if extObj == None:
                assert(False);
            #### END DEBUG
            extObj._backout();


        self._unholdExternalReferences();


    def commit(self):
        for key in self.refCounts.keys():
            amountToChangeBy = self.refCounts[key];

            extId = _keyToExternalId(key)
            
            # adds changes made to reference counters during
            # course of execution of postponed task.
            self.externalStore.changeRefCountById(
                self.endpointName,extId,amountToChangeBy);
    
        self._unholdExternalReferences();


    def _unholdExternalReferences(self):
        '''
        When initiated this event, we incremented the reference counts
        of all external objects that we might encounter.  This was to
        ensure that they would not disappear if we rolled back.  If we
        finish the associated event or if we postpone the associated
        event however, we should decrement the references that we had
        previously incremented (ie, unhold them).  This function does that.
        '''

        for key in self.heldExternalReferences:

            # only change reference counts in the external store for
            # my own objects.  trust other side to handle its own.
            myExtId = _getExtIdIfMyEndpoint(key,self.endpointName)
            if myExtId == None:
                continue;

            self.externalStore.changeRefCountById(
                self.endpointName,myExtId,-1);

        self.heldExternalReferences = [];
        
            
    def signalMessageSequenceComplete(
        self,contextId,onCompleteFunctionToAppendToContext,
        onCompleteKey,endpoint):
        '''
        @param {int} contextId --- The id of the most up-to-date
        context that we should be using.  If the executing code is
        using a context with this same id, it continues.  Otherwise,
        it abandons execution immediately. 
        
        When the other side completes a message sequence that is part
        of a function, or when this side finishes a message sequence,
        signal to any waiting code that it can now resume execution.

        This does not necessarily mean that the event is done running.
        The message sequence may have been called by a function that
        must continue processing after having performed the message
        sequence.
        '''

        # add oncomplete function if exists
        if onCompleteFunctionToAppendToContext != None:
            self.addOnComplete(
                onCompleteFunctionToAppendToContext,
                onCompleteKey,endpoint);        
        
        # execution thread that had been blocking on reading queue now
        # can continue.  depending on result of this read, it keeps
        # executing or raises a _PostponeException that the caller
        # catches.
        self.msgReceivedQueue.put(contextId);


    def addOnComplete(self,funcToExec,onCompleteFuncKey,endpoint):
        '''
        CAN BE CALLED WITHIN OR OUTSIDE LOCK

        @param {Function object} funcToExec --- One of the non-None
        values in the _OnCompleteDict.

        @param {String} onCompleteFuncKey --- Used for debugging.
        '''

        # FIXME: Should deep copy all of context's memory here so that
        # operations on mutables in onComplete do not affect internal
        # state.  And so that will not have over-written sequence
        # globals if have multiple message sequences with onCompletes

        
        self.onCompletesToFire.append(
            _OnComplete(funcToExec,onCompleteFuncKey,endpoint,self));        

            
    def fireOnCompletes(self):
        '''
        SHOULD BE CALLED OUTSIDE OF LOCK
        
        Runs through array of oncomplete functions to fire and does so.
        '''
        for onCompleteToFire in self.onCompletesToFire:
            onCompleteToFire.fire();


        
class _Event(object):
    '''
    Every public-facing function requires an associated event.  The
    event object keeps track of all reads and writes to global/shared
    objects.
    '''
    
    def __init__(
        self,eventName,defGlobReads,defGlobWrites,condGlobReads,
        condGlobWrites,seqGlobals,externalVarNames,endpoint):
        '''
        @param {dict} defGlobReads --- string to bool.  can use the
        same indices to index into context objects.

        @param {dict} defGlobWrites,condGlobReads,condGlobWrites ---
        same as above, except for conditional and global reads and
        writes,seqGlobals

        @param {Endpoint) endpoint --- either of the user-defined
        endpoints subclassed from class _Endpoint

        @param{array} externalVarNames --- An array of all the
        (unique) variable identifiers for externals that this active
        event touches.  Can use these to increase their reference
        counts to ensure that they do not get removed from external
        store.
        
        '''
        # mostly used for debugging.
        self.eventName = eventName;

        self.defGlobReads = defGlobReads;
        self.defGlobWrites = defGlobWrites;
        self.condGlobReads = condGlobReads;
        self.condGlobWrites = condGlobWrites;
        
        self.externalVarNames = externalVarNames;
        
        self.seqGlobals = seqGlobals;
        self.endpoint = endpoint;

    def copy(self,endpoint):
        '''
        Create a new _Event object with endpoint, endpoint.
        '''
        return _Event(self.eventName,self.defGlobReads,self.defGlobWrites,
                      self.condGlobReads,self.condGlobWrites,self.seqGlobals,
                      self.externalVarNames,endpoint);
        
        
    def generateActiveEvent(self):
        '''
        MUST BE CALLED WITHIN LOCK
        
        The reason this must be called within lock is that it has to
        assess whether the conditional variable taints will actually
        get written to/read from.        
        '''

        # warnMsg = '\nWarning: not actually keeping track of conditional ';
        # warnMsg += 'taints when generating an active event in _Event class.\n';
        # # see fixme below.
        # print(warnMsg);

        # FIXME: For now, just using definite global reads and writes
        # and not thinking about conditional.

        return _ActiveEvent(
            self.eventName,self.defGlobReads,self.defGlobWrites,
            self.seqGlobals,self.endpoint,self.externalVarNames,
            self.endpoint._waldo_id,self.endpoint._endpoint_id);
    
    
class _ActiveEventDictElement(object):
    '''
    Each element of an endpoint's _activeEventDict contains one of
    these objects.  Each object contains both the active event as well
    as the context that that event should execute in.
    '''
    def __init__(self,actEvent,eventContext):
        '''
        @param {_ActiveEvent} actEvent --- 
        @param {_Context} eventContext --- 
        '''
        self.actEvent = actEvent;
        self.eventContext = eventContext;


class _ReturnQueueElement(object):
    '''
    Each active event has a returnable queue.  This queue is used to
    signal to a blocking caller when the event has run to completion.
    This is a simple container for the information that must get
    passed through.
    '''
    def __init__(self,returnVal,contextToCommit):
        '''
        @param {Anything} returnVal
        @param {_Context} contextToCommit
        '''
        self.returnVal = returnVal;
        self.contextToCommit = contextToCommit;



class _Message(object):
    '''
    Lots of constants for field names for received messages as well as
    several sentinel values for these fields.
    '''
    
    # what method to call on other side of the receiver.  or, it might
    # just be a notification that because of locally-running
    # processes, we can't actually process your command.
    CONTROL_FIELD = 'control';


    # When a function that sends a message completes, it sends a
    # message to the other side to release the lock on the variables
    # that it holds.  This message has CONTROL_FIELD of
    # RELEASE_EVENT_SENTINEL.  The context that is shipped with the
    # message is applied to the committed context of the receiving
    # endpoint.
    RELEASE_EVENT_SENTINEL = '_____release_event_____';
    
    # if this is specified for target_field, then clean up the
    # outstanding context on receiver, including committing the
    # incoming context data.
    MESSAGE_SEQUENCE_SENTINEL_FINISH = '_____msg_sequence_finish_____';
    

    # if this is specified for target field, then 
    NOT_ACCEPTED_SENTINEL = '____n_accept____';


    # ids are constructed in such a way that two endpoints cannot
    # generate the same id.  this ensures that we can always tell
    # which endpoint initiated the event. Note that if the id does not
    # exist in the receiver's _activeEventDict, then that means that
    # the other side is requesting us to reserve/lock the resources
    # associated with the event in EVENT_NAME_FIELD. 
    EVENT_ID_FIELD = 'eventId';


    ###### only guaranteed to get the below fields if the message is
    ###### not a not accepted message.
    
    # contains the message generated from call to a _Context object's 
    # generateEnvironmentData function.  Should be a dictionary.
    CONTEXT_FIELD = 'context';

    # each endpoint have an event dictionary that contains the names
    # of all events (regardless of which endpoint that event was
    # initiated on) and the resources that each event requires.  These
    # dictionaries are indexed by event names.  The name of the event
    # that is running is provided in this field.
    EVENT_NAME_FIELD = 'eventName';

    # each message should contain the name of the sequence that is
    # executing.  Use this name to add onComplete functions to a
    # context's onCompletesToFire array.
    SEQUENCE_NAME_FIELD = 'sequenceName';    


    # Each transaction has its own priority 
    PRIORITY_FIELD = 'priority'

    # Which host initiated the transaction
    EVENT_INITIATOR_WALDO_ID_FIELD = 'initiator_waldo_id_field'

    # Which endpoint on a target host initiated the transaction
    EVENT_INITIATOR_ENDPOINT_ID_FIELD = 'initiator_endpoint_id_field'


    # fields to use to return results of run and hold operations
    RUN_AND_HOLD_NOT_ACCEPTED_SENTINEL = '__run_and_hold_n_accept__'
    RUN_AND_HOLD_ACCEPTED_SENTINEL = '__run_and_hold_accept__'    
    PRIORITY_FIELD = 'priority'
    WALDO_INITIATOR_ID_FIELD = 'waldo_initiator_id'
    ENDPOINT_INITIATOR_ID_FIELD = 'endpoint_initiator_id'
    RESERVATION_REQUEST_RESULT_FIELD = 'reservation_request_result_field'


    
    
    @staticmethod
    def eventNotAcceptedMsg(eventId):
        '''
        Constructs a message dictionary that can be sent to the other
        endpoint telling it that its request to process an event with
        the above eventId has been rejected.
        
        @param {Int} eventId --- The id of the event that the other
        side requested that we are not accepting.
        '''

        # @see FIXME about not knowing the interface that connection
        # objects require in the _Endpoint._writeMsg function.
        returner = {
            _Message.CONTROL_FIELD: _Message.NOT_ACCEPTED_SENTINEL,
            _Message.EVENT_ID_FIELD: eventId,
            };

        return returner;


    @staticmethod
    def run_and_hold_msg(
        to_run,priority,waldo_initiator_id,endpoint_initiator_id,
        reservation_request_result):
        '''

        @param {_ReservationRequestResult} reservation_request_result
        --- @see reservationManager.py.  Contains the
        overlapping_reads and overlapping_writes that caused the
        run_and_hold request to fail.
        
        Constructs a message dictionary that can be sent to the other
        endpoint telling it that its request to run and hold to_run
        was not accepted.  
        
        '''

        returner = {
            _Message.PRIORITY_FIELD: priority,
            _Message.WALDO_INITIATOR_ID_FIELD: waldo_initiator_id,
            _Message.ENDPOINT_INITIATOR_ID_FIELD: endpoint_initiator_id,
            _Message.RESERVATION_REQUEST_RESULT_FIELD: reservation_request_result
            }

        # to tell whether the message was accepted or not
        if reservation_request_result.succeeded:
            returner[_Message.CONTROL_FIELD] = _Message.RUN_AND_HOLD_ACCEPTED_SENTINEL
        else:
            returner[_Message.CONTROL_FIELD] = _Message.RUN_AND_HOLD_NOT_ACCEPTED_SENTINEL            
        return returner
        
    @staticmethod
    def eventReleaseMsg(context,activeEvent,sequenceName=None):
        '''
        Constructs a message dictionary that can be sent to the other
        endpoint telling it that the event that it is actively
        processing has completed.
        '''

        if sequenceName == None:
            # sentinel known to not be a valid key in the 
            # oncomplete dict
            sequenceName = '@#@#@#';
        
        return _Message._endpointMsg(
            context,activeEvent,_Message.RELEASE_EVENT_SENTINEL,
            sequenceName);


    @staticmethod
    def _endpointMsg(context,activeEvent,controlMsg,sequenceName):
        '''
        Constructs a message dictionary that can be sent to the other
        endpoint via a call to _Endpoint.writeMsg function.

        @param {_Context object} context
        @param {_ActiveEvent ojbect} activeEvent
        
        @param {String} controlMsg --- Fills in the control field of
        the sent message.  Either the function on the opposite
        endpoint to execute, or the 
        '''
        returner = {
            _Message.CONTEXT_FIELD: context.generateEnvironmentData(activeEvent),
            _Message.CONTROL_FIELD: controlMsg,
            _Message.EVENT_ID_FIELD: activeEvent.id,
            _Message.EVENT_NAME_FIELD: activeEvent.eventName,
            _Message.SEQUENCE_NAME_FIELD: sequenceName,
            _Message.PRIORITY_FIELD: activeEvent.priority,
            _Message.EVENT_INITIATOR_WALDO_ID_FIELD: activeEvent.event_initiator_waldo_id,
            _Message.EVENT_INITIATOR_ENDPOINT_ID_FIELD: activeEvent.event_initiator_endpoint_id,
            };
        return returner;


class _ActiveEvent(object):

    def __init__ (
        self,eventName,activeGlobReads,activeGlobWrites,
        seqGlobals,endpoint,externalVarNames, waldo_id,endpoint_id):
        '''
        @param{Int} eventId --- Unique among all other active events.

        @param{array} externalVarNames --- An array of all the
        (unique) variable identifiers for externals that this active
        event touches.  These should only be variable identifiers for
        shared and endpoint global references.  Can use these to
        increase their reference counts to ensure that they do not get
        removed from external store.


        
        '''
        self.activeGlobReads = activeGlobReads;
        self.activeGlobWrites = activeGlobWrites;

        self.eventName = eventName;

        self.seqGlobals = seqGlobals;
        
        # each active event has a unique id, which is used to index
        # into each endpoint's _activeEventDict.
        self.endpoint = endpoint;
        self.id = self.endpoint._getNextActiveEventIdToAssign();
        self.active = False;

        self.priority = _generate_transaction_priority(None)

        # keep track of the initiator of the event.  the initiator 
        self.event_initiator_waldo_id = waldo_id
        self.event_initiator_endpoint_id = endpoint_id

        # @see setArgsArray
        self.argsArray=[];
        
        # active events can be postponed and restarted.  we do not
        # lock the internal execution of an active event however.  Nor
        # can we provide a signal when we postpone an active event to
        # the executing function.  Instead, we use this monotonically
        # increasing number to track the version of the
        # internally-executing function that has not been postponed.
        # Ie, if we are about to commit a context to the endpoint's
        # master committed context, need to ensure that the
        # _activeEvent's contextId is the same as this value.
        self.contextId = 0;


        # each element of return queue has type _ReturnQueueElement.
        # The purpose of this queue is to notify the
        # externally-initiated, blocking code that this event is done.
        self.returnQueue = Queue.Queue();

        self.toExecFrom = None;

        self.extsToRead = [];
        self.extsToWrite = [];
        self.externalVarNames = externalVarNames;


    def set_event_attributes_from_msg(
        self,_id,_priority,_event_initiator_waldo_id,
        _event_initiator_endpoint_id):
        '''
        @param {int} _id

        @param {float}
        _priority,_event_initiator_waldo_id,_event_initiator_endpoint_id

        
        Should only really be called from _msgReceive function so that
        can use the same ids across endpoints for the same event.
        '''
        self.id = _id
        self.priority = _priority
        self.event_initiator_waldo_id = _event_initiator_waldo_id
        self.event_initiator_endpoint_id = _event_initiator_endpoint_id


    def setToExecuteFrom(self,entryPointToExecFrom):
        '''
        @param {String} entryPointFunctionName --- The name of the
        event allows us to index into prototypeEventDict and discover
        all the read/write locks necessary for the event.  However,
        the entryPointFunctionName tells us which internal function to
        call to execute the event.

        In many cases, these are the same.  For instance, if this
        event is located on the endpoint that initiated the event.

        However, you may not know where to begin execution from if
        this event was the result of a message reception.  In this
        case, you are asked to execute different functions locally
        (for instance, depending on which step of a message
        sequence you are processing).

        Note that this must be called before executeInternal
        because executeIntneral uses toExecFrom to decide what
        function to execute next.

        Further note that if entryPointToExecFrom != eventName,
        then this event cannot be postponed.  (This is because it
        means that both sides have agreed to accept this event.)
        '''

        # will later be used when 
        self.toExecFrom = entryPointToExecFrom;


        
    def setCompleted(self,returnVal,context):
        '''
        NOT CALLED FROM WITHIN LOCK.  It assumes the endpoint's lock.
        @raises _PostponeException
        
        @param{Anything} returnVal --- This is what should get
        returned to the function that initiated this event (if
        anything did).

        @param{_Context} context --- This is the context that must get
        committed back to the endpoint's master context.

        @returns True if the context that we're trying to commit with
        matches the expected context.  False otherwise.
        
        Blocking events keep trying to read from the returnQueue for a
        returnQueueElement, which they can use to know that the event
        is done.
        '''
        self.endpoint._lock();
        
        # there is a chance that this active event was postponed
        # before it completed.  if this is the case, then do not state
        # this event actually completed.
        if context.id != self.contextId:
            self.endpoint._unlock();
            raise _PostponeException();
            return False;

        # Tell blocking function that it is now safe to return
        # returnVal.
        retQueueElement = _ReturnQueueElement(returnVal,context);
        self.returnQueue.put(retQueueElement);

        # now actually commit the context
        self.endpoint._commitActiveEvent(self,context);
        self.endpoint._unlock();

        # now send a release message to the other side if this event
        # sent a message as it was processing the active event.
        # this ensures that the other side will:
        #   1: release the read/write locks on the variables that it
        #      had been holding
        #   2: update itself with the most recent context.
        if context.messageSent:
            self.endpoint._writeMsg (
                _Message.eventReleaseMsg(context,self)  );

        # after committing a context, check whether it had any
        # oncomplete functions that we should call
        context.fireOnCompletes();

                
        return True;


    def setArgsArray(self,argsArray):
        '''
        FIXME: watch out for cross-talk in lists/dict args arrays
        from postponements....ie, if pre-postponed code removed an
        element from a list/dict, then the resumed code would start
        with an incorrect argument.
        
        @param{array of arguments} -- argsArray....if this event
        requires us to call a function on our endpoint, we keep track
        of the necessary arguments to that function in argsArray
        (except for self).  Note that the ordering of the array
        reflects the ordering of the arguments.
        '''
        self.argsArray = argsArray;


    def postpone(self,context):
        '''
        GETS CALLED FROM WITHIN LOCK

        @param {_Context} context --- Context that the postponed
        active event was actually using to execute.  Need to send
        postpone message to it on its queue.
        
        If I started an event at the same time as another side started
        an event, there's a chance that I'll have to back out my
        event.  This function does that backing out.  It inserts the
        event back into the endpoint's queue of inactive events and
        gets rid of the event context that we had generated.

        NOTE that by calling cancel inside of this function, we take
        care of removing from active events dictionary as well as
        releasing our locks on shared/endpoint variables.
        '''
        self.eventContext = None;
        self.cancelActiveEvent();
        self.active = False;

        # ensures that when the currently-executing context completes,
        # we will not commit its associated context to the endpoint's
        # committed context.
        self.contextId += 1;
        
        self.endpoint._inactiveEvents.insert(0,self);

        # if the active event was waiting for a message to be
        # executed, we now tell the active event that it no longer
        # needs to wait because it has been postponed.  this will
        # raise a _PostponeException that whoever requested the
        # execution of the active event would catch.
        context.postpone();


    def _conflicts(self,otherActiveEvent):
        '''
        @param {_ActiveEvent object} --- 
        
        @returns{Bool} --- True if otherActiveEvent and this event
        cannot run simultaneously.  (Eg it is writing to variables
        that I read/write to or I am writing to variables that it is
        reading/writing to.
        '''
        for writeVarKey in self.activeGlobWrites:

            if writeVarKey in otherActiveEvent.activeGlobWrites:
                return True;
            if writeVarKey in otherActiveEvent.activeGlobReads:
                return True;

        for writeVarKey in otherActiveEvent.activeGlobWrites:
            if writeVarKey in self.activeGlobWrites:
                return True;
            if writeVarKey in self.activeGlobReads:
                return True;

        return False;
        
    def _postponeConflictingEvents(self):
        '''
        Runs through all active events and postpones those that
        conflict with this active event.
        '''
        actEventDict = self.endpoint._activeEventDict;

        for actEventKey in actEventDict.keys():
            actEvent = actEventDict[actEventKey].actEvent;

            if self._conflicts(actEvent):
                # automatically removes from endpoint's active event
                # dict
                self.endpoint._postponeActiveEvent(actEventKey);


    def _find_external_reads_or_writes_dict(self,read,argument_array):
        '''
        @param{bool} read --- True if we are finding the externals
        associated with reading.  False if we are finding externals
        associated with writing.

        @param {Array} argument_array --- Each element is the argument
        to the function that is being executed.  Externals that are
        passed through to a function as an argument are not named
        using the same globally-unique string ids.  Instead, they take
        on the index in the argument array that corresponds to them.  
        

        @returns{dict} --- indices are the externals' ids.  Values are
        arbitrary bools.  
        '''
        externals_to_read_or_write = {}
        active_glob_var_map = self.activeGlobWrites
        if read:
            active_glob_var_map = self.activeGlobReads
            
        # for actWriteKey in self.activeGlobWrites.keys():
        for actVarKey in active_glob_var_map.keys():
            
            if self.endpoint._isExternalVarId(actVarKey):
                ##### get external id associated with external's key

                # the ext_id will be the integer id of the shared
                # data.  (ie, it won't be in its string-ified key form)
                ext_id = self.endpoint._committedContext.endGlobals.get(actVarKey,None)
                if ext_id == None:
                    # means that the external variable that we are
                    # writing to/reading from did not already contain
                    # an external object to work with.  do not need to
                    # try to acquire a lock on it
                    continue
                
                externals_to_read_or_write[ext_id] = True;

            # if it's not a write key for me, then it is either an
            # argument id (which can be used to index into the
            # argument array) or it is for the other endpoint.
            # below tests if it's an index into the argument
            elif isinstance(actVarKey,numbers.Number):
                #### DEBUG
                if argument_array == None:
                    assert(False);
                
                if len(actVarKey) > len(argument_array):
                    assert(False);
                #### END DEBUG
                    
                extObj = argument_array[actVarKey];

                #### DEBUG
                if not isinstance(extObj,_External):
                    assert(False);
                #### END DEBUG
                    
                externals_to_read_or_write[extObj.id]= True;

        return externals_to_read_or_write

    
    def request_resources_for_run_and_hold(self,force=False,argument_array=None):
        '''
        CALLED FROM WITHIN LOCK
        
        Attempts to grab resources necessary to run active event.

        @param {Array} argument_array --- Each element is the argument
        to the function that is being executed.  Externals that are
        passed through to a function as an argument are not named
        using the same globally-unique string ids.  Instead, they take
        on the index in the argument array that corresponds to them.  

        
        @returns {_ReservationRequestResult} --- @see
        reservationManager.py.  It's succeeded field tells you whether
        the resources were acquired or not.  
        '''
        # if an event touches any external objects, need to request
        # the resource manager for permission to either write to it or
        # read from it.
        externalsToRead = self._find_external_reads_or_writes_dict(
            True,argument_array)
        externalsToWrite = self._find_external_reads_or_writes_dict(
            False,argument_array)
        
        # start by attempting to gather external resources
        res_req_result = self._try_add_externals(externalsToRead,externalsToWrite)
        got_externals = res_req_result.succeeded
        
        if force and res_req_result.succeeded:
            # by calling this, we guarantee that there will be no
            # local conflicts if we add this event.
            self._postponeConflictingEvents();
        else:
            # can modify res_req_result by reference
            # want to tell other end of *all* conflicts, not just external
            self._check_local_conflicts(res_req_result)

        if not res_req_result.succeeded:
            # we could not acquire some of the resources we needed.
            # return that we could not acquire.
            if got_externals:
                # we could acquire the externals, but could not acquire
                # locals.  Should release the externals that we acquired.
                self._release_externals(externalsToRead,externalsToWrite)

            return res_req_result
            
        # we can acquire all the resources that we wanted.  actually
        # acquire local resources
        self._acquire_local()
        return res_req_result

    
    def _try_add_externals(self,externalsToRead,externalsToWrite):
        '''
        @returns{_ReservationRequestResult object} --- succeeded field
        tells us whether we were actually able to grab the resources.
        '''
        # now check if can add externals
        self.extsToRead = list(externalsToRead.keys());
        self.extsToWrite = list(externalsToWrite.keys());
        if (len(self.extsToRead) == 0) and (len(self.extsToWrite) == 0):
            # short-circuits acquiring lock in reservation manager if
            # don't need to.
            res_req_result = self.endpoint._reservationManager.empty_reservation_request_result(True)
        else:
            res_req_result = self.endpoint._reservationManager.acquire(
                self.extsToRead,
                self.extsToWrite,
                self.priority,
                self.event_initiator_waldo_id,
                self.event_initiator_endpoint_id,
                self.id)

        return res_req_result


    def _check_local_conflicts(self,res_req_result):
        '''
        Check if local resources have read-write conflicts.  Returns
        conflicts by modifying res_req_result.
        '''
        endpointGlobSharedReadVars = self.endpoint._globSharedReadVars;
        endpointGlobSharedWriteVars = self.endpoint._globSharedWriteVars;

        # we are not forcing adding this event, and must check if
        # the event would pose any conflicts.  if it does, then do
        # not proceed with adding the active event.
        for actReadKey in self.activeGlobReads.keys():

            if ((actReadKey in endpointGlobSharedWriteVars) and
                (len(endpointGlobSharedWriteVars[actReadKey]) > 0)):

                res_req_result.succeeded = False
                res_req_result.append_overlapping(
                    True, # append as read
                    actReadKey,
                    endpointGlobSharedWriteVars[actReadKey])

        for actWriteKey in self.activeGlobWrites.keys():

            if (((actWriteKey in endpointGlobSharedWriteVars) and
                 (len(endpointGlobSharedWriteVars[actWriteKey]) > 0))

                or

                ((actWriteKey in endpointGlobSharedReadVars) and
                 (len(endpointGlobSharedReadVars[actWriteKey]) > 0))):

                res_req_result.succeeded = False
                res_req_result.append_overlapping(
                    False, #append as write
                    actWriteKey,
                    endpointGlobSharedWriteVars[actWriteKey])
                 
    
    def _acquire_local(self):
        '''
        Assumes that there have been no conflicts when tried to lock
        internal and external variables (ie, _check_local_conflicts
        has turned up clean).  Actually tell endpoint that these
        resources are being held.
        '''
        endpointGlobSharedReadVars = self.endpoint._globSharedReadVars;
        endpointGlobSharedWriteVars = self.endpoint._globSharedWriteVars;

        # no conflict, can add event.
        for actReadKey in self.activeGlobReads.keys():
            # have to do additional check because there is a chance
            # that this is a read/write for a variable that the other
            # endpoint controls.  In that case, do not have value to
            # increment.  We trust that the other endpoint is
            # functioning appropriately to schedule reads/writes in
            # such a way that won't have conflicts.
            if actReadKey in endpointGlobSharedReadVars:
                locked_record = _LockedRecord(
                    self.event_initiator_waldo_id,
                    self.event_initiator_endpoint_id,
                    self.priority,self.id)
                    
                endpointGlobSharedReadVars[actReadKey].append(locked_record)

        for actWriteKey in self.activeGlobWrites.keys():
            # @see note in above for loop.
            if actWriteKey in endpointGlobSharedWriteVars:
                locked_record = _LockedRecord(
                    self.event_initiator_waldo_id,
                    self.event_initiator_endpoint_id,
                    self.priority,self.id)
                    
                endpointGlobSharedWriteVars[actWriteKey].append(locked_record)


    def addEventToEndpointIfCan(self,argument_array=None,force=False,newId=False):
        '''
        CALLED WITHIN ENDPOINT's LOCK
        
        @param {Array} argument_array --- Each element is the argument
        to the function.
        
        @param{bool} force --- If true, this means that we should
        postpone all other active events that demand the same
        variables.

        @param{bool} newId --- If true, then assign a new (globally
        unique) id to this active event before trying to add it.
        
        @returns {bool,_Context} --- False,None if cannot add event.
        True,context to use if can add event.
        '''

        if newId:
            self.id = self.endpoint._getNextActiveEventIdToAssign();

        res_req_result = self.request_resources_for_run_and_hold(
            force,argument_array)

        if not res_req_result.succeeded:
            return False,None

        
        # we were able to acquire read/write locks on the resources.
        # go ahead and add event to active event dict and create context
        

        #### DEBUG
        if self.id in self.endpoint._activeEventDict:
            errMsg = '\nBehram error.  Trying to add ';
            errMsg += 'event already in event dict.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG


        # the context for this event should be freshly copied as soon
        # as activated.  (If had copied the context in the constructor
        # instead, would have run into a problem where context may
        # have been outdated by the time the event became active.)
        self.contextId += 1;
        if self.contextId == _Context.INVALID_CONTEXT_ID:
            self.contextId += 1;
        eventContext = self.endpoint._committedContext.copyForActiveEvent(self,self.contextId);

        
        # actually add event to active event dictionary.
        self.endpoint._activeEventDict[self.id] = _ActiveEventDictElement(self,eventContext);
        
        self.active = True;

        # self.externalVarNames is a list of all the names of global
        # variables that this event touches that have external types.
        eventContext.holdExternalReferences(self.externalVarNames);
            
        return True,eventContext;

        
    def cancelActiveEvent(self):
        '''
        @returns {Bool} --- True if canceling this active event may
        lead to events' being able to fire (eg. it was the only event
        performing a write on a variable that waiting events needed to
        be able to red.  False otherwise.
        '''
        potentialTransition = False;

        #### DEBUG
        if not self.active:
            errMsg = '\nBehram error.  Trying to cancel ';
            errMsg += 'an _ActiveEvent object that had never ';
            errMsg += 'been made active.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        # remove from endpoint dictionary.
        del self.endpoint._activeEventDict[self.id];

        # decrement the reference counter for each of the reads and
        # writes that we had been using as part of these events.
        for globReadKey in self.activeGlobReads.keys():
            # check if in dict so that do not try to decrement
            # value for global variable this endpoint does not own.
            if globReadKey in self.endpoint._globSharedReadVars:

                # removes the _LockedRecord from the list of records
                # that are holding a read lock on this variable.
            
                read_lock_list = self.endpoint._globSharedReadVars[globReadKey]

                to_remove_counter = None
                for counter in range(0,len(read_lock_list)):
                    item = read_lock_list[counter]
                    if ((item.waldo_initiator_id == self.event_initiator_waldo_id) and
                        (item.endpoint_initiator_id == self.event_initiator_endpoint_id) and
                        (item.act_event_id == self.id)):
                        to_remove_counter = counter
                        break
                if to_remove_counter != None:
                    del read_lock_list[to_remove_counter]

                    if len(read_lock_list) == 0:
                        # means that something that we previously
                        # could not acquire a lock for we can now.
                        potentialTransition = True


        for globWriteKey in self.activeGlobWrites.keys():
            # check if in dict so that do not try to decrement
            # value for global variable this endpoint does not own.
            if globWriteKey in self.endpoint._globSharedWriteVars:

                # removes the _LockedRecord from the list of records
                # that are holding a write lock on this variable.
                # (Note: in practice, this list can only ever have a
                # single entry in it since two active events cannot
                # write to the same variable at the same time.)
                
                write_lock_list = self.endpoint._globSharedWriteVars[globWriteKey]
                to_remove_counter = None
                for counter in range(0,len(write_lock_list)):
                    item = write_lock_list[counter]
                    if ((item.waldo_initiator_id == self.event_initiator_waldo_id) and
                        (item.endpoint_initiator_id == self.event_initiator_endpoint_id) and
                        (item.act_event_id == self.id)):
                        to_remove_counter = counter
                        break
                if to_remove_counter != None:
                    del write_lock_list[to_remove_counter]

                    if len(write_lock_list) == 0:
                        # means that something that we previously
                        # could not acquire a lock for we can now.
                        potentialTransition = True

        
        return potentialTransition;

    def executeInternal(self,contextToUse,functionArgumentType):
        '''
        Execute the function that this event was spurred by, this time
        setting all incoming arguments so that the function call
        appears internally.

        @param {_Context} contextToUse --- The endpoint context to
        pass in as argument to function we are calling.  Note that if
        this active event was postponed, then this context may be out
        of date, and we do not need to proceed with execute internal
        because whatever else happens the changes will not be written
        to the endpoint's committed context.
        '''

        #### DEBUG
        if self.argsArray == None:
            errMsg = '\nBehram error: should have a non-empty args ';
            errMsg += 'array inside of activeEvent\'s executeInternal.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG


        #### DEBUG
        if self.toExecFrom == None:
            errMsg = '\nBehram error: should have a non-empty toExecFrom ';
            errMsg += 'inside of activeEvent\'s executeInternal.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        #### DEBUG
        if not (self.toExecFrom in self.endpoint._execFromToInternalFuncDict):
            errMsg = '\nBehram error: trying to execute a function that is ';
            errMsg += 'not defined in the endpoint\'s internal function dict.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG


            
        # construct the string that will be eval-ed to give the function.
        funcName = self.endpoint._execFromToInternalFuncDict[self.toExecFrom];
        funcArgs = '';

        # _callType, _actEvent, and _context, respectively
        funcArgs += str(functionArgumentType) + ',self,contextToUse';

        if functionArgumentType != _Endpoint._FUNCTION_ARGUMENT_CONTROL_FROM_MESSAGE:
            for argIndex in range(0,len(self.argsArray)):
                funcArgs += ',self.argsArray[%s]' % str(argIndex);

        funcCall = ('self.endpoint.%s(%s)' %
                    (funcName,funcArgs));

        if contextToUse.id != self.contextId:
            # can short-circuit because know that won't actually use
            # the results of any of this computation.
            return; 
        
        # actually compile and eval the string
        obj = compile(funcCall,'','exec');

        if contextToUse.id != self.contextId:
            return;
        # actually evaluate the internal function.
        eval(obj);


    def filterSharedsForMsg(self,sharedsDict):
        '''
        Next three functions are used by context to generate a message
        that then gets sent to other endpoint.  each one takes in the
        context's shareds, endpoint globals, or sequence globals dict,
        respectively.  Then returns what should be transmitted to
        other side.
        '''
        # FIXME:
        # only shareds that this endpoint can write to need to get sent
        # to the other side.
        return sharedsDict;  # all shareds should be sent to other side
    
    def filterEndGlobalsForMsg(self,endGlobalsDict):
        # The other endpoint does not need to know about any of my
        # endpoint globals.
        return {};
    
    def filterSeqGlobalsForMsg(self,seqGlobals):
        # Both sides should send sequence globals
        return seqGlobals;

    def filterDoesNotExist(self,endGlobals):
        '''
        This function returns an dictionary with keys of the names of
        endpoint global arguments that have dne values from a dict of
        endGlobals.  (And values of dict are bools.)
        
        When an event starts, one endpoint may not have the values for
        the endpoint globals of the other endpoint (that the other
        endpoint will use during the event's computation).  When an
        endpoint builds its initial event context, for the values of
        these events, the endpoint fills in their values with
        _Context.DNE_PLACE_HOLDER-s.  When one endpoint sends its
        initial context to another placeholder, we run through all the
        DNE-s and label them.  When the receiver re-constructs its
        context, it fills all these values in with its committed
        values.

        After the initial transmission of a context, neither endpoint
        should have any dne values.
        '''
        returner = {};
        for globName in endGlobals.keys():
            globVal = endGlobals[globName];
            if globVal == _Context.DNE_PLACE_HOLDER:
                returner[globName] = True;
        return returner;


    
class _Endpoint(object):

    # FUCNTION_ARGUMENT_CONTROL_*-s are passed in as the third from
    # last argument to any function.  They specify whether the
    # function should try to create a new active event and context,
    # whether they should notify a blocking call when their execution
    # is complete, and/or whether they should return normally.  @see
    # comments above any internal version of a public function.

    # means that anything that we return will
    # not be set in return statement of context, but rather will
    # just be returned.
    _FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED = 1;

    # means that we should return anything that
    # we get via the _context return queue, but that we should
    # *not* create a new active event or context.
    _FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE = 2;

    # means that we should return anything that
    # we get via the _context return queue, but that we should
    # *not* create a new active event or context.    
    _FUNCTION_ARGUMENT_CONTROL_FIRST_FROM_EXTERNAL = 3;

    # if the execution of this function was the result of a message
    # (eg. jump or fall through) rather than called from internal
    # code.  message send functions, use this argument so
    # knows not to re-initialize sequence shared data.
    _FUNCTION_ARGUMENT_CONTROL_FROM_MESSAGE = 4;
    
    
    def __init__ (self,connectionObj,globSharedReadVars,globSharedWriteVars,
                  lastIdAssigned,myPriority,theirPriority,context,
                  execFromToInternalFuncDict, prototypeEventsDict,endpointName,
                  externalGlobals,reservationManager,waldo_id,endpoint_id):
        '''
        @param {dict} externalGlobals --- used for reference counting
        reads and writes to external variables.  (ie, the variable
        named by the key).  <String:Bool>
        
        @param {ReservationManager object} reservationManager

        @param {float} waldo_id --- Unique per host.

        @param {float} endpoint_id --- Unique per connection
        
        '''
                  

        # <_ActiveEvent.id:_ActiveEventDictElement (which contains
        # _ActiveElement and context)>
        self._activeEventDict = {};
        self._mutex = threading.RLock();
        
        # these are events that are not executing because a read/write
        # conflict is blocking them.  they may have tried to start
        # executing, but became postponed (through call to
        # _postponeActiveEvent) because other endpoint simultaneously
        # started an event that conflicted and we had to back out our
        # event.  Each element is an 
        self._inactiveEvents = [];

        ###### data specific to this endpoint

        # events from which we can copy to create active events.
        self._prototypeEventsDict = prototypeEventsDict;
        
        self._connectionObj = connectionObj;

        
        # dict<id__varName : int> the int is the number of active events
        # that still are performing either a read of a write to the
        # shared/global with the assigned id.
        # never remove ... if get to zero, leave as zero.
        self._globSharedReadVars = globSharedReadVars;
        self._globSharedWriteVars = globSharedWriteVars;
        
        # the other one will be set to 1
        self._lastIdAssigned = lastIdAssigned;

        # one side must be greater than the other
        # used to resolve which side will back out its changes when
        # there is a conflict.
        self._myPriority = myPriority;
        self._theirPriority = theirPriority;

        self._endpoint_id = endpoint_id
        self._waldo_id = waldo_id
        
        self._committedContext = context;

        self._endpointName = endpointName;
        
        # every event needs to be able to map its name to the internal
        # function that should be called to initiate it.
        # string(<id>__<iniating function name>) : string ... string
        # is name of function on endpoint to call.
        self._execFromToInternalFuncDict = execFromToInternalFuncDict;


        # FIXME: unclear what the actual interface should be between
        # connection object and endpoint.
        self._connectionObj.addEndpoint(self);

        self._externalGlobals = externalGlobals;
        self._reservationManager = reservationManager;

        
    ##### helper functions #####

    def _run_and_hold(
        self,
        to_run,
        
        priority,waldo_initiator_id,endpoint_initiator_id,


        *args):
        '''
        @param{String} to_run --- The name of the public function to
        attempt to run locally.

        For re-entrantness
        @param{float} priority
        @param{float} waldo_initiator_id
        @param{float} endpoint_initiator_id

        @param *args --- The arguments to the public function that we
        are calling.

        @return _RunAndHold object --- sentinel that could not acquire
        (and telling you who is actually holding the resources)
        
        Execute a function and hold onto the resources for a
        transaction and hold onto the read/write locks for its
        resources.  until 
        '''


        fixme_function_prefix = '_hold_func_prefix_' + self._endpointName

        try:
            to_execute = getattr(self,fixme_function_prefix + to_run)
        except AttributeError as exception:
            # FIXME: probably want to return a different, undefined
            # method or something.
            err_msg = '\nBehram error when calling ' + to_run
            err_msg += '.  It does not exist on this endpoint.\n'
            print err_msg
            assert(False);

        self._lock()
        # at
        res_request_result,active_event = self._acquire_run_and_hold_resources(
            to_run,priority,waldo_initiator_id,endpoint_initiator_id)
        
        self._unlock()


        # tell the other side whether run and hold request succeeded
        # or failed
        self._send_run_and_hold_result_msg(
            to_run,priority,waldo_initiator_id,endpoint_initiator_id,
            res_request_result)

        if res_request_result.succeeded:
            # we could lock all resources. go ahead and run the method
            # on another thread (which assumes the required resources
            # are already held)
            run_and_hold = _RunnerAndHolder(
                to_execute,priority,waldo_initiator_id,
                endpoint_initiator_id,*args)
            run_and_hold.start()

    def _acquire_run_and_hold_resources(
        self,to_run,priority,waldo_initiator_id,endpoint_initiator_id):
        '''
        Attempt to grab the resources required to run to_run as part
        of a run_and_hold request.

        CALLED FROM WITHIN LOCK

        @returns (a,b) ---
           {_ReservationRequestResult} a ---
           
           {_ActiveEvent or None} b --- None if cannot acquire
           resources, otherwise, an active event, which we can later
           schedule to run.
        '''

        # FIXME: must add to_run to self._prototypeEventsDict
        # FIXME: must emit a special to_run
        
        #### DEBUG
        if not (to_run in self._prototypeEventsDict):
            err_msg = '\nBehram error.  Could not acquire resources '
            err_msg += 'for run and hold because '
            print err_msg
            assert(False)
        #### END DEBUG
        
        event_to_run_and_hold = self._prototypeEventsDict[to_run]
        act_event = event_to_run_and_hold.generateActiveEvent()
        reservation_request_result = act_event.request_resources_for_run_and_hold()

        return reservation_request_result,act_event


    def _send_run_and_hold_result_msg(
        self,to_run,priority,waldo_initiator_id,
        endpoint_initiator_id,reservation_request_result):
        '''
        Send a message to the partner endpoint telling it that we either:

           a: accepted the request to run and hold and are running now
              or
           b: did not accept the request and are not running now

        Can determine whether using a or b based on the succeeded flag
        of reservation_request_result.

        '''

        msg_to_send = _Message.run_and_hold_msg(
            to_run,priority,waldo_initiator_id,endpoint_initiator_id,
            reservation_request_result)
        self._writeMsg(msg_to_send)
        
    
    def _generateOnCompleteNameToLookup(self,sequenceName):
        '''
        For each sequence, we want to be able to lookup its oncomplete
        handler in _OnCompleteDict.  This is indexed by "_EndpointName
        sequenceName".  This function generates that key.
        
        @param {String} sequenceName --- 
        '''
        return _onCompleteKeyGenerator(self._endpointName,sequenceName);

    
    def _postponeActiveEvent(self,activeEventId):
        '''
        SHOULD BE CALLED FROM WITHIN LOCK
        
        @returns Nothing
        '''
        # note we are not guaranteed to have the event in our event
        # dictionary.  this can occur if two endpoints try to initiate
        # an event that uses colliding reads/writes at the same time.
        # in this case, we will receive a not accepted message that
        # triggers _postponeActiveEvent.  However, this side may have
        # already postponed the event when it received the message
        # from the other side initiating its event.

        if (not (activeEventId in self._activeEventDict)):
            return;

        actEventDictObj = self._activeEventDict[activeEventId];
        actEvent = actEventDictObj.actEvent;
        actEventContext = actEventDictObj.eventContext;

        # note that this function will take care of removing the
        # active event from active event dict as well as releasing
        # locks on read/write variables.
        actEvent.postpone(actEventContext);


    def _cancelActiveEvent(self,activeEventId):
        '''
        @param {int} activeEventId ---

        Removes the active event's holds on shared and global
        variables.

        @returns{bool} If any of the shared/global variables are no
        longer being read/written to, then there's a chance that
        additional events that were on the event queue can now be
        scheduled.
        '''

        #### DEBUG
        self._checkHasActiveEvent(activeEventId,'_cancelActiveEvent');
        #### END DEBUG

        # The actual active event handles all the cleanup with
        # reference counters to the global/shared reads and writes.
        activeEvent = self._activeEventDict[activeEventId].actEvent;
        return activeEvent.cancelActiveEvent();

    def _isExternalVarId(self,varId):
        return varId in self._externalGlobals;

    def _commitActiveEvent(self,activeEvent,contextToCommit):
        '''
        SHOULD ONLY BE CALLED FROM WITHIN LOCKED CODE

        Takes all outstanding data in the active event's context and
        translates it into committed context.
        '''
        #### DEBUG
        self._checkHasActiveEvent(activeEvent.id,'_commitActiveEvent');
        #### END DEBUG

        writtenExternals = [];

        for key in contextToCommit.writtenToExternalsOnThisEndpoint.keys():
            # note that each context
            extId = _getExtIdIfMyEndpoint(key,self._endpointName);
            extObj = self._externalStore.getExternalObject(self._endpointName, extId);
            
            #### DEBUG
            if extObj == None:
                assert(False);
            #### END DEBUG

            writtenExternals.append(extObj);
            
        extIdsRead = activeEvent.extsToRead;
        extIdsWrite = activeEvent.extsToWrite;
            
        self._reservationManager.release(
            extIdsRead,
            extIdsWrite,
            writtenExternals,
            activeEvent.priority,
            activeEvent.event_initiator_waldo_id,
            activeEvent.event_initiator_endpoint_id,
            activeEvent.id)
            
        contextToCommit.commit();

        # actually update the committed context's data
        self._committedContext.mergeContextIntoMe(contextToCommit);
        # Removes read/write locks on global and shared variables.
        self._cancelActiveEvent(activeEvent.id);


    def _executeActive(self,execEvent,execContext,callType):
        '''
        @param {_ActiveEvent} execEvent --- Should already be in active queue

        Tries to execute the event from the internal code.  if
        internal execution finishes the transaction, then removes the
        active event, execEvent, from active dict.
        '''

        if execEvent.id in self._activeEventDict:
            # may not still be in active event dict if got postponed
            # between when called _executeActive and got here.

            # if we postpone an active event, then that postponing
            # raises a _PostponeException.  we do not need to
            # reschedule the event, the system will do this
            # automatically, we can just wait for its
            # returnQueue to have data in it.

            executeEventThread = _ExecuteActiveEventThread(
                execEvent,
                execContext,
                callType,
                self,
                execEvent.extsToRead,
                execEvent.extsToWrite);
            executeEventThread.start();


    def _checkNextEvent(self):
        '''
        Checks if there are any inactive events waiting to be
        processed, and, if there are and the state that they require
        does not "conflict" with currently executing events, then
        schedule these events.

        "conflict" above means that we do not read a variable that
        another event is writing and that we do not write a variable
        the other side is reading.
        '''
        # must lock access for the _inactiveEvents array
        self._lock();

        # FIXME: this could start more threads than want.
        
        # do not need to worry about invalidation of iterator here
        # because python handles for me.
        counter = 0;
        for inactiveEvent in self._inactiveEvents:
            # note that we need this condition here because we unlock
            # to actually execute the event below.  this means that
            # another thread that interceded after we unlocked may
            # have made this event active already.  in that case, we
            # ignore this event and continue.
            if inactiveEvent.active:
                continue;

            eventAdded, context = inactiveEvent.addEventToEndpointIfCan(
                inactiveEvent.argsArray,False,True);
            if eventAdded:
                self._unlock();
                self._executeActive(
                    inactiveEvent,
                    context,
                    # so that the other side knows that this is from a resume.
                    _Endpoint._FUNCTION_ARGUMENT_CONTROL_RESUME_POSTPONE);

                # remove item from inactive
                del self._inactiveEvents[counter];
                self._lock();
            else:
                counter += 1;
                
        self._unlock();

    def _getNextActiveEventIdToAssign(self):
        '''
        SHOULD BE CALLED FROM WITHIN LOCK
        
        We want to know which endpoint an event
        '''
        self._lastIdAssigned += 2;
        return self._lastIdAssigned;


    def _processReleaseEventSentinel(self,eventId,contextData):
        '''
        SHOULD BE CALLED FROM OUTSIDE LOCK
        
        The other side is telling us that we can remove the read/write
        locks for event with id eventId and commit all data in the
        context contextData.
        '''
        #### DEBUG
        self._checkHasActiveEvent(eventId,'_processReleaseEventSentinel');
        #### END DEBUG
            
        self._lock();

        #### DEBUG
        if (not (eventId in self._activeEventDict)):
            errMsg = '\nBehram error: Should only be asked ';
            errMsg += 'to process a release event for an event ';
            errMsg += 'we already have.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        # get active element from dict
        actEventElement = self._activeEventDict[eventId];
        actEvent = actEventElement.actEvent;
        
        # update the committed context
        context = actEventElement.eventContext;
        context.updateEnvironmentData(contextData,self);

        # commit the context data, release read/write locks, and
        # remove the active event from the dict.
        self._commitActiveEvent(actEvent,context);
        self._unlock();

        # after committing a context, check whether it had any
        # oncomplete functions that we should call
        context.fireOnCompletes();

        

    def _processSequenceSentinelFinished(
        self,eventId,contextData,sequenceName):    
        '''
        SHOULD BE CALLED FROM OUTSIDE OF LOCK
        
        Gets called whenever we receive a message with its control
        field set to MESAGE_SEQUENCE_SENTINEL_FINISHED.
        
        @param {int} eventId
        
        @param {dict} contextData --- The contents of the received
        message's context field.  @see generateEnvironmentData of
        _Context for the format of this dictionary.

        @param{String} sequenceName --- The name of the sequence that
        just completed
        
        # Case 1:
        #
        #   I was the one that initiated the message sequence,
        #   then I can now update my context from the message
        #   and resume work on the function that called the
        #   message.
        
        # Case 2:
        #
        #   I was not the one that initiated the message
        #   sequence.  Then, I can just ignore the message
        #   because I will receive a RELEASE_EVENT_SENTINEL
        #   control message when I need to actually apply the
        #   new context, or subsequent message sequences will
        #   include new contexts.
        '''

        # add to context's oncomplete if necessary
        onCompleteKey = self._generateOnCompleteNameToLookup(sequenceName);
        onCompleteFunctionToAppendToContext = _OnCompleteDict.get(onCompleteKey,None);
        
        
        # case 2
        if not self._iInitiated(eventId):
            
            if onCompleteFunctionToAppendToContext != None:
                # we must add the context
                self._lock();
                actEventDictObj = self._activeEventDict.get(eventId,None);
                self._unlock();
                context = actEventDictObj.eventContext;
                context.addOnComplete(
                    onCompleteFunctionToAppendToContext,onCompleteKey,self);                
            return;

            
        # FIXME: I don't think that I really need these locks.  I'm a
        # little unclear though on Python's guarantees about
        # concurrent reads/writes on a dict.
        self._lock();

        actEventDictObj = self._activeEventDict.get(eventId,None);

        #### DEBUG
        if actEventDictObj == None:
            errMsg = '\nBehram error: should not have received a ';
            errMsg += 'MESSAGE_SEQUENCE_SENTINEL_FINISHED control ';
            errMsg += 'message for an event that got postponed.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        self._unlock();

        # at this point, we know that the event cannot be postponed:
        # the other side has agreed to lock and hold variables 

        # therefore, do not need to execute next set of actions with
        # lock open.

        # case 1
        actEvent = actEventDictObj.actEvent;
        actEventContext = actEventDictObj.eventContext;

        # could just straight up replace context, but want to leave
        # possibility for doing something more intelligent, vis-a-vis
        # not sending full frames.
        actEventContext.updateEnvironmentData(contextData,self);

        # notify active event that had been waiting that it can resume
        # its execution.
        actEventContext.signalMessageSequenceComplete(
            actEventContext.id,onCompleteFunctionToAppendToContext,
            onCompleteKey,self);


    def _writeMsgSelf(self,msgDictionary):
        '''
        @param {dict} msgDictionary --- @see _writeMsg
        '''
        msgSelf = _MsgSelf(self,msgDictionary);
        msgSelf.start();
            
    def _writeMsg(self,msgDictionary):
        '''
        @param {dict} msgDictionary --- Should have at least some of
        the fields specified in _Message.
        '''

        #### DEBUG
        if not (_Message.CONTROL_FIELD in msgDictionary):
            errMsg = '\nBehram error: in _writeMsg, had an incorrectly ';
            errMsg += 'formatted message dictionary.  It was missing a ';
            errMsg += 'control field.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        # now trying to convert context dictionary to msg to
        # send...change all _WaldoMap objects in the context field to
        # regular python dicts.  Similarly, change all _WaldoList
        # objects in the context field to python lists.
        def _copied_dict(to_copy):
            '''
            Produces a copy of to_copy, where all the WaldoLists
            and maps are replaced by python lists and dicts.
            '''
            new_dict = {}
            for key in to_copy.keys():
                to_add = to_copy[key]

                if isinstance(to_add,_WaldoMap):
                    to_add = _copied_dict(to_add._map_list_serializable_obj())
                elif isinstance(to_add,_WaldoList):
                    to_add = _copied_list(to_add._map_list_serializable_obj())

                elif isinstance(to_add,dict):
                    to_add = _copied_dict(to_add)
                elif isinstance(to_add,list):
                    to_add = _copied_list(to_add)

                    
                new_dict[key] = to_add
            return new_dict

        def _copied_list(to_copy):
            '''
            Produces a copy of to_copy, where all the WaldoLists
            and maps are replaced by python lists and dicts.
            '''        
            new_array = []
            for item in to_copy:
                to_add = item
                if isinstance(to_add,_WaldoMap):
                    to_add = _copied_dict(to_add._map_list_serializable_obj())
                elif isinstance(to_add,_WaldoList):
                    to_add = _copied_list(to_add._map_list_serializable_obj())

                elif isinstance(to_add,dict):
                    to_add = _copied_dict(to_add)
                elif isinstance(to_add,list):
                    to_add = _copied_list(to_add)

                    
                new_array.append(to_add)

            return new_array

        self._connectionObj.writeMsg(
            _copied_dict(msgDictionary),
            self);


    def _msgReceive(self,msg):
        '''
        @param {dict} msg --- @see _Message for list of fields and
        their meanings.
        
        '''

        # FIXME: Intended rule was supposed to be to postpone
        # currently executing functions if the other side's
        # priority was higher.  Right now, just saying that will
        # not take on an event the other side requests if
        # resources are not available, regardless of priority.

        ctrlMsg = msg[_Message.CONTROL_FIELD];
        eventId = msg[_Message.EVENT_ID_FIELD];

        if ctrlMsg == _Message.NOT_ACCEPTED_SENTINEL:
            # means that we need to postpone current outstanding event and 
            self._lock();
            self._postponeActiveEvent(eventId);
            self._unlock();

            # when we postponed one event, we may have made way
            # for another event to execute.  similarly, may want
            # to reschedule the event that we postponed.
            self._tryNextEvent();
            return;

            
        # only guaranteed to get these data if it is not a message
        # not accepted message.
        eventName = msg[_Message.EVENT_NAME_FIELD];
        sequenceName = msg[_Message.SEQUENCE_NAME_FIELD];
        contextData = msg[_Message.CONTEXT_FIELD];        

        priority = msg[_Message.PRIORITY_FIELD]
        event_initiator_waldo_id = msg[_Message.EVENT_INITIATOR_WALDO_ID_FIELD]
        event_initiator_endpoint_id = msg[_Message.EVENT_INITIATOR_ENDPOINT_ID_FIELD]

        # Should change all python lists and dicts in contextData back
        # to Waldo list and map objects, respectively
        def _dict_vals_to_waldo(to_convert):
            to_return = {}
            for key in to_convert.keys():
                item = to_convert[key]
                if isinstance(item,dict):
                    to_return[key] = _WaldoMap(
                        _dict_vals_to_waldo(item),False)
                elif isinstance(item,list):
                    to_return[key] = _WaldoList(
                        _list_vals_to_waldo(item),False)
                else:
                    to_return[key] = item

            return to_return

        def _list_vals_to_waldo(to_convert):
            to_return = []
            for item in to_convert:
                if isinstance(item,dict):
                    to_return.append(_WaldoMap(
                        _dict_vals_to_waldo(item),False))
                elif isinstance(item,list):
                    to_return.append(_WaldoList(
                        _list_vals_to_waldo(item),False))
                else:
                    to_return.append(item)

            return to_return

        # actually changes context data to use waldo lists and maps.
        for key in contextData.keys():
            contextData[key] = _dict_vals_to_waldo(contextData[key])

        
        if ctrlMsg == _Message.RELEASE_EVENT_SENTINEL:
            # means that we should commit the specified outstanding
            # event and release read/write locks that the event was
            # holding.
            self._processReleaseEventSentinel(eventId,contextData);
            self._tryNextEvent();
            return;

        if ctrlMsg == _Message.MESSAGE_SEQUENCE_SENTINEL_FINISH:
            # means that the message sequence that was called is
            # finished.
            self._processSequenceSentinelFinished(
                eventId,contextData,sequenceName);

            # reception of this message cannot have changed what
            # read/write locks were happening, so do not need to tryNext.
            return;


        # FIXME: it may be okay in python not to take a lock here
        # when checking if the event exists in the active event
        # dictionary (nothing else should be inserting it into the
        # dictionary and other operations on the dictionary that
        # might affect our lookup are guaranteed not to occur
        # because of the global interpretter lock.  For another
        # language, this may not be true.

        # note we do not need a lock here because once we accept
        # an active event from the other side, it must run to
        # completion.  It cannot be removed and re-added later.
        actEventDictObj = self._activeEventDict.get(eventId,None);

        createdNewEvent = False;
        if actEventDictObj != None:
            actEvent = actEventDictObj.actEvent;
            eventContext = actEventDictObj.eventContext;
        else:
            # means that the other side is requesting us to
            # schedule an event for the first time.

            # Case 1:
            # 
            #   We cannot lock the requested resources because
            #   they are being used.  And our priority is higher
            #   than the other side's priority.  Send a reply back
            #   to the other side saying that we are not accepting
            #   the event (ie, in the control field, use the
            #   NOT_ACCEPTED_SENTINEL).

            # Case 2:
            #
            #   We can lock the requested resources.  Do so, and
            #   begin executing the function requested.

            # Note that for both cases, we know the requested
            # resources based on the event name.

            #### DEBUG
            if self._iInitiated(eventId):
                errMsg = '\nBehram error: eventId says that I initiated this ';
                errMsg += 'event, but I do not have a copy of it in my active ';
                errMsg += 'event dictionary.  That means that I must have postponed ';
                errMsg += 'it.  But then, the other side should not have accepted the ';
                errMsg += 'message.\n';
                assert(False);
            #### END DEBUG


            
            self._lock();

            actEvent = self._prototypeEventsDict[eventName].generateActiveEvent();
            actEvent.set_event_attributes_from_msg(
                eventId,priority,event_initiator_waldo_id,
                event_initiator_endpoint_id)


            # FIXME: seems as though it would be slower to create
            # a new context and then update it rather than passing
            # in the context that we were given (in its dictionary
            # form).

            # To avoid livelock where both sides keep trying to
            # initiate an event, and both sides keep backing it out
            # and retrying, the endpoint with the higher priority can
            # force its event to be processed at the expense of the
            # endpoint with lower priority.  In this case,
            # forceAddition is True, and all events that conflicted
            # are postponed.
            forceAddition = self._myPriority < self._theirPriority;
            eventAdded,eventContext = actEvent.addEventToEndpointIfCan(
                None,forceAddition);

            self._unlock();


            if not eventAdded:
                # Case 1: reply back that we are not accepting the message
                self._writeMsg ( _Message.eventNotAcceptedMsg(eventId)  );
                return;


            createdNewEvent = True;
            
            # Case 2: we do the same thing that we would do if
            # the event had existed in self._activeEventDict.  so
            # we just fall through to execute the code that we
            # otherwise would have.


        # tell the active event which function to execute from.
        actEvent.setToExecuteFrom(ctrlMsg);


        # update the context that this active event should use to
        # execute from.
        if createdNewEvent:
            # if we created a new event, we may need to fill in dne-s
            # from the other side with a stable snapshot of endpoint
            # data.  to ensure snapshot is stable, must take lock.
            self._lock();
            eventContext.updateEnvironmentData(contextData,self);
            self._unlock();
        else:
            eventContext.updateEnvironmentData(contextData,self);

        # actually run the function on my side
        self._executeActive(
            actEvent,
            eventContext,
            # specified so that internal message function does not
            # use return message queue, etc.
            _Endpoint._FUNCTION_ARGUMENT_CONTROL_FROM_MESSAGE);
        
    def _iInitiated(self,actEventId):
        '''
        @param{int} eventId --- usaully the id field of an
        _ActiveEvent object.

        Returns true if this endpoint initiated the action with id
        actEventId and False if it did not.
        '''

        # if both are even, return true.  if both are odd, return
        # true.
        return (actEventId % 2) == (self._lastIdAssigned % 2);
    
        
    def _lock(self):
        self._mutex.acquire();

    def _unlock(self):
        self._mutex.release();

    def _tryNextEvent(self):
        tryNextEventObj = _NextEventLoader(self);
        tryNextEventObj.start();

        
    #### DEBUG
    def _checkHasActiveEvent(self,activeEventId,whoCalled):
        if not (activeEventId in self._activeEventDict):
            errMsg = '\nBehram error: trying to access ';
            errMsg += 'active event that does not appear in ';
            errMsg += 'the _activeEventDict from ' + whoCalled;
            errMsg += '.\n';
            print(errMsg);
            assert(False);
    #### END DEBUG

    #### Special-cased refresh operations.
    def _refresh(self,_callType,_actEvent=None,_context=None):
        '''
        Each endpoint comes prepopulated with the ability to send
        empty messages from one side to the other in order to refresh
        shared and global variables.

        This is the msg send function for the refresh statment
        '''
        #### DEBUG
        if _callType != _Endpoint._FUNCTION_ARGUMENT_CONTROL_INTERNALLY_CALLED:
            errMsg = '\nBehram error.  A message send function for now must be ';
            errMsg += 'called with an internally_called _callType.\n';
            print(errMsg);
            assert(False);

        if _actEvent == None:
            errMsg = '\nBehram error.  A message send function was ';
            errMsg += 'called without an active event.\n';
            print(errMsg);
            assert(False);

        if _context == None:
            errMsg = '\nBehram error.  A message send function was called ';
            errMsg += 'without a context.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        # note that we may have postponed this event before we got to
        # writing the message.  This check ensures that we do not use
        # the network extra when we do not have to.
        if _actEvent.contextId != _context.id:
            return;

        
        # request the other side to receive refresh
        self._writeMsg(
            _Message._endpointMsg(
                _context,_actEvent,_REFRESH_RECEIVE_KEY,
                # using a dummy name that we know no sequence can be
                # named so that know not to execute any oncomplete
                _REFRESH_SEND_FUNCTION_NAME));


    def _Text(self,_callType,_actEvent=None,_context=None):
        '''
        The refresh receive method.  using the name _Text to ensure no
        collision with user-defined functions
        '''
        #### DEBUG
        if _callType != _Endpoint._FUNCTION_ARGUMENT_CONTROL_FROM_MESSAGE:
            errMsg = '\nBehram error.  A message receive function was ';
            errMsg += 'called without an internally_called _callType.\n';
            print(errMsg);
            assert(False);

        if _actEvent == None:
            errMsg = '\nBehram error.  A message receive function was ';
            errMsg += 'called without an active event.\n';
            print(errMsg);
            assert(False);

        if _context == None:
            errMsg = '\nBehram error.  A message receive function was called ';
            errMsg += 'without a context.\n';
            print(errMsg);
            assert(False);
        #### END DEBUG

        #### Unique to last sequence
        # tell other side that the sequence is finished and tell our
        # event that it should no longer wait on the message sequence
        # to complete.  Note that should not have to do two of these.
        # Should only have to do one.  But does not hurt to do both.
        self._writeMsg(
            _Message._endpointMsg(
                _context,_actEvent,
                _Message.MESSAGE_SEQUENCE_SENTINEL_FINISH,
                # dummy key into oncomplete dict so that guaranteed
                # not to add an oncomplete when this finishes
                _REFRESH_SEND_FUNCTION_NAME));

        _context.signalMessageSequenceComplete(_context.id,None,None,None);

        # note because know that no oncomplete function for refresh,
        # do not need to check oncomplete dict.
        
""";

