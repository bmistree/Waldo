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
import pickle
import itertools

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



class _RetryAbortLoopServicer(threading.Thread):
    RETRY = 'retry'
    ABORT = 'abort'
    '''
    Reads from threadsafe_queue.  Each item read is a 5-tuple: <a,b,c,d,e>.

      a {String} --- either RETRY or ABORT
      b {float}  --- context id
      c {float}  --- priority
      d {float}  --- endpoint initiator id
      e {float}  --- waldo initiator id

    Looks up the event and either aborts the event (forwarding on the
    abort message) or it retries the event if the event previously did
    not succeed or forwards the event on if it did.
    '''    

    def __init__(self,threadsafe_queue,endpoint):
        self.threadsafe_queue = threadsafe_queue
        self.endpoint = endpoint
        threading.Thread.__init__(self)
        self.daemon = True
        
    def run(self):

        while True:
            cmd_tuple = self.threadsafe_queue.get()

            cmd = cmd_tuple[0]
            if cmd == self.RETRY:
                self.process_retry_cmd(cmd_tuple)
            elif cmd == self.ABORT:
                self.process_abort_cmd(cmd_tuple)
            #### DEBUG                
            else:

                err_msg = '\nBehram error: unknown command tuple '
                err_msg += 'passed into retry abort loop servicers.\n'
                print err_msg
                assert(False)
            #### END DEBUG

    def process_retry_cmd(self,cmd_tuple):
        '''
        1: If command did not succeed here, then retry it.

        2: Tell everyone else to retry too
        '''
        parent_context_id = cmd_tuple[1]
        priority = cmd_tuple[2]
        endpoint_initiator_id = cmd_tuple[3]
        waldo_initiator_id = cmd_tuple[4]
        
        # to determine if event had been running, lookup in runandholddict
        self.endpoint._lock()

        ### PART 1 from comments above: retry any command that did not
        ### succeed here.
        
        failed_run_and_holds = self.endpoint._failed_run_and_holds

        # warning: the size of failed_run_and_holds may change in this
        # loop because calls to _run_and_hold_local may append to it.
        # for this reason, getting indices to check over early.  I did
        # a test, and I don't think this is strictly necessary, but
        # can't be too safe.
        indices_to_del_from_failed = []
        indices_to_check_over = range(0,len(failed_run_and_holds))
        for act_event_index in indices_to_check_over:
            act_event = failed_run_and_holds[act_event_index]

            if self.act_event_match(
                act_event,parent_context_id,priority,endpoint_initiator_id,
                waldo_initiator_id):

                # re-entrantness of endpoint locks means that it is
                # okay to run this from here.
                self.endpoint._run_and_hold_local(
                    act_event.return_queue,act_event.reservation_result_request_queue,
                    act_event.to_run,act_event.parent_context_id,act_event.priority,
                    act_event.event_initiator_waldo_id,
                    act_event.event_initiator_endpoint_id,
                    *act_event.args)
                
                indices_to_del_from_failed.append(act_event_index)

        for to_del_index in reversed(indices_to_del_from_failed):
            del failed_run_and_holds[to_del_index]

            
        ### PART 2 from comments above: tell everyone else to retry too.
        ### get dict element and tell it to forward....

        # FIXME: it's probably slow to look through all of these at
        # once.  oh well.
        
        # each active event we match may have a separate context id.
        # each one, we need to keep track of so that we can look for
        # corresponding dict elements in our loop detector and tell
        # them to backout.
        context_id_map_for_retry_forward = {}

        for active_event_id in self.endpoint._activeEventDict:
            active_event_element = self.endpoint._activeEventDict[active_event_id]

            act_event = active_event_element.actEvent
            context_id = active_event_element.eventContext.id

            if self.act_event_match(
                act_event,parent_context_id,priority,
                endpoint_initiator_id,waldo_initiator_id):

                context_id_map_for_retry_forward[context_id] = True


        for context_id in context_id_map_for_retry_forward.keys():

            dict_element = self.endpoint._loop_detector.get(
                context_id,priority,endpoint_initiator_id,
                waldo_initiator_id)

            if dict_element != None:
                dict_element.forward_retry()

        self.endpoint._unlock()            


    def act_event_match(
        self,active_event,parent_context_id,priority,endpoint_initiator_id,
        waldo_initiator_id):
        '''
        @returns{Bool} --- True if the active event, active_event, has
        the same parent_context_id, priority, endpoint_initiator_id,
        and waldo_initiator_id as the other arguments passed in.
        '''

        return ((active_event.parent_context_id == parent_context_id) and
                (active_event.priority == priority) and
                (active_event.event_initiator_waldo_id == waldo_initiator_id) and
                (active_event.event_initiator_endpoint_id == endpoint_initiator_id))


    def process_abort_cmd(self,cmd_tuple):
        '''
        1: end any active event that is running that was initiated
        because of the run and hold request represented in cmd_tuple.

        2: Remove any failed events that we had been waiting on.
        
        3: forward on the abort command
        '''
        parent_context_id = cmd_tuple[1]
        priority = cmd_tuple[2]
        endpoint_initiator_id = cmd_tuple[3]
        waldo_initiator_id = cmd_tuple[4]

        
        self.endpoint._lock()
        ### PART 1 from method comment above: end any active event
        ### that had been using....

        act_event_dict = self.endpoint._activeEventDict
        for act_event_element in act_event_dict.values():
            act_event = act_event_element.actEvent
            context = act_event_element.eventContext

            if self.act_event_match(
                act_event,parent_context_id,priority,endpoint_initiator_id,
                waldo_initiator_id):

                act_event.cancelActiveEvent()

        
        ### PART 2 from comment above: remove any failed events that
        ### we had been waiting on
        failed_run_and_holds = self.endpoint._failed_run_and_holds

        # warning: the size of failed_run_and_holds may change in this
        # loop because calls to _run_and_hold_local may append to it.
        # for this reason, getting indices to check over early.  I did
        # a test, and I don't think this is strictly necessary, but
        # can't be too safe.
        indices_to_del_from_failed = []


        indices_to_check_over = range(0,len(failed_run_and_holds))
        for act_event_index in indices_to_check_over:
            act_event = failed_run_and_holds[act_event_index]
            
            if self.act_event_match(
                act_event,
                parent_context_id,priority,endpoint_initiator_id,
                waldo_initiator_id):
                
                indices_to_del_from_failed.append(act_event_index)


        for to_del_index in reversed(indices_to_del_from_failed):
            del failed_run_and_holds[to_del_index]

        ### PART 3 from method comment above: forward backout to all
        ### other endpoints and remove dict element from loop
        ### detector.

        # FIXME: it's probably slow to look through all of these at
        # once.  oh well.
        
        # each active event we match may have a separate context id.
        # each one, we need to keep track of so that we can look for
        # corresponding dict elements in our loop detector and tell
        # them to backout.
        context_id_map_for_backout = {}

        for active_event_id in self.endpoint._activeEventDict:
            active_event_element = self.endpoint._activeEventDict[active_event_id]

            act_event = active_event_element.actEvent
            context_id = active_event_element.eventContext.id

            if self.act_event_match(
                act_event,parent_context_id,priority,
                endpoint_initiator_id,waldo_initiator_id):

                context_id_map_for_backout[context_id] = True


        for context_id in context_id_map_for_backout.keys():

            dict_element = self.endpoint._loop_detector.get(
                context_id,priority,endpoint_initiator_id,
                waldo_initiator_id)

            if dict_element != None:
                dict_element.notify_backout()
                
                self.endpoint._loop_detector.remove_if_exists(
                    context_id,priority,endpoint_initiator_id,
                    waldo_initiator_id)

        self.endpoint._unlock()



class _RestartEventThread(threading.Thread):
    def __init__(self,endpoint):
        self.endpoint = endpoint
        threading.Thread.__init__(self)
        self.daemon = True
    def run(self):
        # FIXME: make this programmable.  It is the time to wait before retrying
        # when a run and hold was blocked.
        _time.sleep(.1)
        self.endpoint._tryNextEvent()
    

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


def _value_deep_copy(to_copy):
    to_return_str = pcikle.dumps(to_copy)
    return pickle.loads(to_return_str)

class _EndpointDict(object):
    def __init__(self):
        # _internal_dict:
        #    indices: endpoint id
        #    values: dict
        #       indices: waldo id
        #       values: anything want to store
        self._internal_dict = {}

        self._mutex = threading.RLock();

    def lock(self):
        self._mutex.acquire()
    def unlock(self):
        self._mutex.release()

    def set(self,endpoint_id,waldo_id,to_set_to):
        if not (endpoint_id in self._internal_dict):
            self._internal_dict[endpoint_id] = {}
        waldo_dict = self._internal_dict[endpoint_id]
        waldo_dict[waldo_id] = to_set_to
        return to_set_to

    def exists(self,endpoint_id,waldo_id):
        '''
        @returns {bool} --- Whether or not the 2-tuple appears in our
        dictionary.
        '''
        if endpoint_id in self._internal_dict:
            endpoint_dict = self._internal_dict[endpoint_id]
            if waldo_id in endpoint_dict:
                # the value existed!
                return True
        return False

    def clear(self):
        '''
        Remove all values stored
        '''
        self._internal_dict = {}

        
    def get(self,endpoint_id,waldo_id,*args):
        '''
        Similar to python's .get method on dicts, which can take a
        default value to return if the value is not in dict, this
        supports a 3rd argument for what default value to use if do
        not have value in dictionary.
        '''
            
        if self.exists(priority,endpoint_id,waldo_id):
            return self._internal_dict[endpoint_id][waldo_id]

        has_default = len(args) != 0
        if has_default:
            return args[0]

        err_msg = '\nBehram error: when getting from a Endpoint dict, '
        err_msg += 'have a key error.\n'
        print err_msg
        assert(False)


    def __iter__(self):
        # generate empty iterator, which we then use to collect
        iter_to_return = {}.values()
        for endpoint_key in self._internal_dict.keys():
            waldo_indexed_dict = self._internal_dict[endpoint_key]
            iter_to_return = itertools.chain(
                iter_to_return,waldo_indexed_dict.values())

        return iter_to_return


    def remove(self,endpoint_id,waldo_id):

        #### DEBUG
        if not (self.exists(endpoint_id,waldo_id)):
            err_msg = '\nBehram error: trying to remove from a '
            err_msg += '_Endpoint dict that does not contain '
            err_msg += 'specified index values.\n'
            print err_msg
            assert(False)
        #### END DEBUG

        # actually remove the element
        del self._internal_dict[endpoint_id][waldo_id]

        # if there are still intermediate dicts open that have nothing
        # in them, delete them too: memory management
        if len(self._internal_dict[endpoint_id]) == 0:
            del self._internal_dict[endpoint_id]


class _RunAndHoldQueueServiceLoop(threading.Thread):
    '''
    Reads elements from endpoint's run_and_hold_queue and sorts out
    whether need to retry or revoke run and hold requests as a
    a result.
    '''
    def __init__(self,endpoint):
        self.endpoint = endpoint
        threading.Thread.__init__(self)
        self.daemon = True
        
    def run(self):
        '''
        attempt to read _RunAndHoldRequestResult objects from the
        endpoint's run_and_hold_queue.  These tell us whether our
        events' run and hold requests were able to lock the
        resources necessary on foreign endpoints to continue.
        '''
        while True:
            run_and_hold_request_result = self.endpoint._run_and_hold_queue.get()

            context_id = run_and_hold_request_result.requesting_context_id
            priority = run_and_hold_request_result.priority
            waldo_initiator_id = run_and_hold_request_result.waldo_initiator_id
            endpoint_initiator_id = run_and_hold_request_result.endpoint_initiator_id

            self.endpoint._lock()

            dict_element = self.endpoint._loop_detector.get(
                context_id,priority,endpoint_initiator_id,
                waldo_initiator_id)

            if dict_element == None:
                # means that this is a response to an event that must
                # have finished or been revoked and therefore removed
                # from the loop detector dict.  Skip.
                pass
            else:
                act_event = dict_element.act_event
                self.endpoint._process_run_and_hold_request_result(
                    run_and_hold_request_result,act_event)

            self.endpoint._unlock()

class _RunAndHoldCommitThread(threading.Thread):
    def __init__(
        self,parent_context_id,priority,endpoint_initiator_id,
        waldo_initiator_id,endpoint):

        self.parent_context_id = parent_context_id
        self.priority = priority
        self.endpoint_initiator_id = endpoint_initiator_id
        self.waldo_initiator_id = waldo_initiator_id
        self.endpoint = endpoint
        
        threading.Thread.__init__(self)

    def run(self):
        self.endpoint._all_active_event_commit_and_forward(
            self.parent_context_id,self.priority,
            self.endpoint_initiator_id,self.waldo_initiator_id,
            None # nothing to return: should have already been
                 # returned through run and hold queues
            )
            
class _RunAndHoldLookupDict(object):
    '''
    Each run and hold event is uniquely addressed using a 4-tuple of
    (priority, endpoint_initiator_id, waldo_initiator_id,context_id).
    This class provides a mechanism for storing and setting values in
    a dictionary based on this three-tuple.

    Note that this dictionary is *not* thread safe.
    '''
    def __init__(self):

        # goes from most-specific to least-specific
        # outer-most dict:
        #   index: priority
        #   value: dict
        #     index: endpoint_initiator_id
        #     value: dict
        #        index: waldo_initiator_id
        #        value: dict
        #          index: context_id
        #          value: whatever had been stored
        self._internal_dict = {}

    def __iter__(self):

        # generate empty iterator, which we then use to collect
        iter_to_return = {}.values()
        for priority_key in self._internal_dict.keys():
            endpoint_indexed_dict = self._internal_dict[priority_key]

            for endpoint_key in endpoint_indexed_dict.keys():
                waldo_indexed_dict = endpoint_indexed_dict[endpoint_key]

                for context_id_key in waldo_indexed_dict:
                    context_id_indexed_dict = waldo_indexed_dict[context_id_key]
                    iter_to_return = itertools.chain(
                        iter_to_return,context_id_indexed_dict.values())

        return iter_to_return

    def remove_if_exists(
        self,context_id,priority, event_initiator_endpoint_id,
        event_initiator_waldo_id):
        '''
        @returns {_RunAndHoldDictElement or None} --- None if there
        was no element of that name.  Otherwise, the removed element
        '''

        # FIXME: as used, am I sure that only one thread of control
        # will access this so that exists check is consistent with remove 
        
        if self.exists(
            context_id,priority,event_initiator_endpoint_id,
            event_initiator_waldo_id):
            
            return self.remove(
                context_id,priority,event_initiator_endpoint_id,
                event_initiator_waldo_id)

        return None

        
    def exists(
        self,context_id,priority,endpoint_initiator_id,waldo_initiator_id):
        '''
        @returns {bool} --- Whether or not the 3-tuple appears in our
        dictionary.
        '''
        if priority in self._internal_dict:
            priority_dict = self._internal_dict[priority]
            if endpoint_initiator_id in priority_dict:
                endpoint_dict = priority_dict[endpoint_initiator_id]
                if waldo_initiator_id in endpoint_dict:
                    waldo_dict = endpoint_dict[waldo_initiator_id]
                    if context_id in waldo_dict:
                        # the value existed
                        return True

        return False

    def get(self,context_id,priority,endpoint_initiator_id,waldo_initiator_id,*args):
        '''
        Similar to python's .get method on dicts, which can take a
        default value to return if the value is not in dict, this
        supports a 4th argument for what default value to use if do
        not have value in dictionary.
        '''
            
        if self.exists(context_id,priority,endpoint_initiator_id,waldo_initiator_id):
            return self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id][context_id]

        has_default = len(args) != 0
        if has_default:
            return args[0]

        err_msg = '\nBehram error: when getting from a RunAndHoldLookup dict, '
        err_msg += 'have a key error.\n'
        print err_msg
        assert(False)

    def set(self,context_id,priority,endpoint_initiator_id,waldo_initiator_id,to_set_to):
        '''
        @param {anything} to_set_to --- Like a typical python dict,
        RunAndHoldLookup dict does not impose any constraints on what
        each element of the RunAndHoldLookup dict contains.  Can have
        any type.
        '''
        if not (priority in self._internal_dict):
            self._internal_dict[priority] = {}
        if not (endpoint_initiator_id in self._internal_dict[priority]):
            self._internal_dict[priority][endpoint_initiator_id] = {}
        if not (context_id in self._internal_dict[priority][endpoint_initiator_id]):
            self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id] = {}
                
            
        self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id][context_id] = to_set_to

    def remove(
        self,context_id,priority,endpoint_initiator_id,waldo_initiator_id):
        '''
        @returns {_RunAndHoldDictElement } --- The
        runAndHoldDictElement that was removed.
        '''

        #### DEBUG
        if not (self.exists(context_id,priority, endpoint_initiator_id,waldo_initiator_id)):
            err_msg = '\nBehram error: trying to remove from a '
            err_msg += 'RunAndHoldLookup dict that does not contain '
            err_msg += 'specified index values.\n'
            print err_msg
            assert(False)
        #### END DEBUG

        # actually remove the element
        to_return = self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id][context_id]
        del self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id][context_id]

        # if there are still intermediate dicts open that have nothing
        # in them, delete them too: memory management
        if len(self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id]) == 0:
            del self._internal_dict[priority][endpoint_initiator_id][waldo_initiator_id]
        if len(self._internal_dict[priority][endpoint_initiator_id]) == 0:
            del self._internal_dict[priority][endpoint_initiator_id]
        if len(self._internal_dict[priority]) == 0:
            del self._internal_dict[priority]

        return to_return

       
        
class _RunAndHoldDictElement(object):

    STATE_NONE = -1
    STATE_RUNNING = 0
    STATE_SENT_COMPLETE = 1
    STATE_SENT_REVOKE = 2

    
        
    def __init__(
        self,context_id,act_event,res_req_result,endpoint):
        '''
        @param {int} context_id --- The id of the context that is
        processing this event.
        
        @param {_Endpoint object} endpoint --- The endpoint that holds
        the run and hold dict element.

        @param {_ReservationRequestResult object } res_req_result ---
        Contains a list of all the variable read/write locks that this
        run and hold call is holding onto.

        '''
        self.context_id = context_id
        self.act_event = act_event
        self.endpoint = endpoint

        # these should only contain the fully-qualified variables that
        # we currently hold locks on for events that we initiated.  it
        # should not contain results for variables that we were unable
        # to grab locks for.  it should not contain variables that
        # were locked from an active event that was initiated from
        # another endpoint.
        self.res_req_result = res_req_result
        
        
        # If we are committing the event or backing it out, we must
        # notify this list of other endpoints letting them know that
        # they should do the same.
        
        # # fixme: need to determine how to populate the
        self.endpoint_to_notify_or_commit_to = _EndpointDict()

        # this should be the endpoint object that requested us to
        # perform a run and hold.  we notify this object of overlaps
        # from our requests to others to run and hold.
        # # if we were the endpoint that began the run and hold, then 
        # self.run_and_hold_controller = controller


        # the state only really matters on the initiator.  by default,
        # we set the state to be running.
        self.state = self.STATE_RUNNING

    def debug_print(self):
        print_msg = '\nThis is context id: ' + str(self.context_id) + '.\n'
        print_msg += 'This is active event priority: '
        print_msg += str(self.act_event.priority) + '.\n'
        print_msg += 'This is endpoint initiator id: '
        print_msg += str(self.act_event.event_initiator_endpoint_id) + '\n'
        print_msg += 'This is waldo initiator id: '
        print_msg += str(self.act_event.event_initiator_waldo_id) + '\n'
        print print_msg

        
    def add_read_writes(self,res_req_results):
        '''
        FIXME: CALLED WITHIN ENDPOINT LOCK
        
        Assumes that res_req_results has succeeded and add its
        overlapping reads and writes to res_req_results.
        '''
        
        #### DEBUG
        if not res_req_results.succeeded:
            err_msg = '\nBehram error: expectation of add_read_writes function '
            err_msg += 'is that you only add res_req_result overlapping_reads '
            err_msg += 'and overlapping_writes if it has succeeded.\n'
            print err_msg
            assert (False)
        #### END DEBUG
            
        overlapping_reads = res_req_results.overlapping_reads
        overlapping_writes = res_req_results.overlapping_writes

        self.res_req_result.append_overlapping_external_locked_records(
            True,overlapping_reads)
        self.res_req_result.append_overlapping_external_locked_records(
            False,overlapping_writes)


    def add_run_and_hold_on_endpoint(
        self,endpoint_obj):
        '''
        CALLED WITHIN ENDPOINT LOCK (but may not need to be).
        
        Any time we issue a run_and_hold request to an endpoint, we
        should

        Called inside of endpoint lock.  FIXME: may not be strictly
        necessary to call within endpoint lock.


        @returns{_RunAndHoldDictElement object} --- What was set
        '''
        # FIXME: currently unnecessary to have separate lock on
        # endpoint_to_notify_or_commit_to because we are
        # taking an endpoint lock before calling.

        # self.endpoint_to_notify_of_commit_or_backout.lock()
        self.endpoint_to_notify_or_commit_to.lock()

        to_return = self.endpoint_to_notify_or_commit_to.set(
            endpoint_obj._endpoint_id,
            endpoint_obj._waldo_id,
            endpoint_obj)

        self.endpoint_to_notify_or_commit_to.unlock()

        # FIXME: may want to consider returning whether the context
        # and active event have matching ids so can short-circuit
        # execution of wasted context.

        return to_return


    def notify_backout(self):
        '''
        When a context is postponed or canceled, it calls this
        '''
        # FIXME: could we just make a copy of the endpoint objects
        # while in lock and then iterate afterwards on copy?
        self.endpoint_to_notify_or_commit_to.lock()

        # notify all listening to back out
        for endpoint in self.endpoint_to_notify_or_commit_to:
            endpoint._notify_run_and_hold_backout(
                self.context_id,                
                self.act_event.priority,
                self.act_event.event_initiator_endpoint_id,
                self.act_event.event_initiator_waldo_id)

        self.endpoint_to_notify_or_commit_to.unlock()            


    def revoke(self):
        '''
        Gets called *only* when we detect a loop.  and backout.
        Cancels context.  We also start notifications of backouts to
        be sent if we initiated the run and hold.

        If we initiated the run_and_hold:
          * Set a timer to retry the action.
          * Set state to STATE_SENT_REVOKE

        If we did not initiate the run_and_hold:
          * Remove the dict element (this object) from
            _RunAndHoldLoopDetector's run_and_hold_dict.
            Done through call to cancelActiveEvent.
        '''
        ## Common section

        # either postponing or cancelling will handle the notification
        if self.i_initiated():
            # will automatically re-schedule.
            
            # FIXME: provide additional argument so that can specify a
            # time to wait before re-scheduling.
            self.endpoint._postponeActiveEvent(
                self.act_event.id)

            self.notify_backout()
            
        else:
            # release all resources being held by the action
            self.endpoint._cancelActiveEvent(
                act_event.id)    

        # FIXME: see message below 
        fixme_msg = '\nFIXME: When issuing a revoke, should remove '
        fixme_msg += ' the run and hold dict element.  Not doing so '
        fixme_msg += 'is a memory leak.\n'
        # print fixme_msg
        self.state = self.STATE_SENT_REVOKE


    def forward_retry(self):
        '''
        SHOULD BE CALLED WITHIN ENDPOINT's LOCK

        Forward retry message to all others that I asked to perform a
        run_and_hold for me.
        '''
        self.endpoint_to_notify_or_commit_to.lock()        

        for endpoint in self.endpoint_to_notify_or_commit_to:
            # this is the endpoint that we issued our run and holds
            # on...not the endpoint we issued them from.
            endpoint._notify_run_and_hold_retry(
                self.context_id,
                self.act_event.priority,
                self.act_event.event_initiator_endpoint_id,
                self.act_event.event_initiator_waldo_id)

        self.endpoint_to_notify_or_commit_to.unlock()


    def forward_reservation_result_to_controller(
        self,run_and_hold_request_result):
        '''
        Forwards on all run and hold requests that resulted from an
        early endpoint function call that we did not initiate.  We
        must forward both successes and failures so that root endpoint
        has enough information to back out.  (Root must know of all
        resources it is currently holding as well as resources it
        tried and failed to hold.)
        '''

        #### DEBUG
        if self.i_initiated():
            err_msg = '\nBehram error: should not forward reservation '
            err_msg += 'request result when we are the root endpoint '
            err_msg += 'that began the foreign endpoint function call.\n'
            print err_msg
            assert(False)
        #### END DEBUG

        if self.act_event.reservation_request_result_queue == None:
            # means that this was the root initiator of the run and
            # hold request.  can just ignroe forwarding the request
            # because we're the root endpoint and there's no one to
            # forward it to.
            pass
        else:
            self.act_event.reservation_request_result_queue.put(
                run_and_hold_request_result)

        
    def forward_commit(self):
        self.endpoint_to_notify_or_commit_to.lock()
        
        self.state = self.STATE_SENT_COMPLETE

        for endpoint in self.endpoint_to_notify_or_commit_to:
            endpoint._notify_run_and_hold_commit(
                self.context_id,
                self.act_event.priority,
                self.act_event.event_initiator_endpoint_id,
                self.act_event.event_initiator_waldo_id)

        self.endpoint_to_notify_or_commit_to.unlock()


    def is_running(self):
        return self.state == self.STATE_RUNNING
        
    def i_initiated(self):
        '''
        @returns {bool} --- True if the endpoint contained in
        self.endpoint is the one that initiated the active event
        that this element contains.
        '''
        if ((self.endpoint._endpoint_id == self.act_event.event_initiator_endpoint_id) and
            (self.endpoint._waldo_id == self.act_event.event_initiator_waldo_id)):
            
            return True

        return False


        
class _RunAndHoldLoopDetector(object):
    '''
    This keeps track of all the active events associated with a run
    and hold request either that this endpoint initiated or that was
    initiated by its partner endpoint.
    '''
    
    def __init__(self,endpoint):
        self.endpoint = endpoint

        # indexed by priority,endpoint_initiator_id,
        # waldo_initiator_id.  each value is a _RunAndHoldDictElement
        self.run_and_hold_dict = _RunAndHoldLookupDict()

    def remove_if_exists(
        self,context_id,priority,event_initiator_endpoint_id,
        event_initiator_waldo_id):
        '''
        If this event exists within loop detector dictionary, remove
        it.

        @returns{_RunAndHoldDictElement or None} --- None if no match
        in run_and_hold_dict.  Otherwise, the dict element that was
        deleted.
        '''
        return self.run_and_hold_dict.remove_if_exists(
            context_id,priority, event_initiator_endpoint_id,
            event_initiator_waldo_id)

            
    def debug_print(self):

        print '\n *** Printing all elements in run and hold dict: '
        for dict_element in self.run_and_hold_dict:
            dict_element.debug_print()
        print '\n\n'

    def get(
        self,context_id,priority,endpoint_initiator_id,
        waldo_initiator_id):            
        '''
        @returns {_RunAndHoldDictElement object or None} --- None if
        do not have a dict element indexed by arguments to function.
        Otherwise, returns dict element
        '''
        
        return self.run_and_hold_dict.get(
            context_id,priority,endpoint_initiator_id,
            waldo_initiator_id,None) # None is the default value to
                                     # return if do not have element
                                     # in dict.
            
    def append_result_or_add_if_dne(
        self,context_id,act_event,run_and_hold_res_req_result):
        '''
        MUST BE CALLED WITHIN ENDPOINT LOCK
        
        @param {int} context_id --- The id of the local context that
        we are using to issue this run and hold request.

        @param {_ActiveEvent object} act_event --- The active event
        object that issued the run and hold request (but not
        necessarilly the root event).

        @param{_ReservationRequestResult object}
        run_and_hold_res_req_result


        If have an entry in run_and_hold_dict that matches the
        context_id, priority, and initiator ids, append the write/read
        locks to the existing run and hold dict element.  Otherwise,
        create a new dict element and insert it into dict.

        @returns{_RunAndHoldDictElement object} --- The dict element
        that we added to our dictionary.  Can later call things, such
        as forward results on it.
        
        DOES NOT FORWARD THE RES_REQUEST_RESULT ON TO THE INITIATOR OF
        THE CALL.
        
        '''
        priority = act_event.priority
        endpoint_initiator_id = act_event.event_initiator_endpoint_id        
        waldo_initiator_id = act_event.event_initiator_waldo_id
        

        dict_element = self.run_and_hold_dict.get(
            context_id,priority,endpoint_initiator_id,
            waldo_initiator_id,None)

        if dict_element == None:
            # did not already have a corresponding dict element: must
            # be first endpoint function call on this
            # context-endpoint-waldo user.  Create a new dict element
            # for it.
            new_dict_element = _RunAndHoldDictElement(
                context_id,act_event,run_and_hold_res_req_result,
                self.endpoint)

            # actually add to internal dict
            self.run_and_hold_dict.set(
                context_id,priority,endpoint_initiator_id,waldo_initiator_id,
                new_dict_element)

        else:
            # already had a corresponding dict element: just add the
            # res_req_result overlapping reads and overlapping writes
            # to the existing dict element
            if dict_element.i_initiated():
                dict_element.add_read_writes(run_and_hold_res_req_result)            
            else:
                # Note: caller is responsible for forwarding results
                # of reservation lock requests if we did not initiate.
                pass

        return dict_element

    def exists(
        self,context_id,priority,endpoint_initiator_id,
        waldo_initiator_id):

        return self.run_and_hold_dict.exists(
            context_id,priority,endpoint_initiator_id,waldo_initiator_id)

        
        
    def add_run_and_hold(self,context_id,act_event,res_req_result):
        '''
        Called when requested by another endpoint to run_and_hold some
        resources or when we initiate a run_and_hold and send it to
        someone else.  When receive the run and hold request, message
        still gets called even if we cannot acquire the resources (the
        endpoint that initiated the run and hold request itself has to
        tell us to retry or release).

        @param {_ActiveEvent object} act_event ---

        @param {_ReservationRequestResult object} res_req_result ---
        @see _ReservationRequestResult class in lib/reservationManager.py.
        '''

        priority = act_event.priority
        endpoint_initiator_id = act_event.event_initiator_endpoint_id        
        waldo_initiator_id = act_event.event_initiator_waldo_id

        
        #### DEBUG
        if self.run_and_hold_dict.exists(
            context_id,priority,endpoint_initiator_id,waldo_initiator_id):
            err_msg = '\nBehram error in loop detector.  Got collision '
            err_msg += 'in run_and_hold events.\n'
            print err_msg
            assert(False)
        #### END DEBUG

        dict_element = _RunAndHoldDictElement(
            context_id,act_event,res_req_result,self.endpoint)

        # actually add to internal dict
        self.run_and_hold_dict.set(
            context_id,priority,endpoint_initiator_id,waldo_initiator_id,
            dict_element)

        return dict_element

    
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
        self,return_queue,closure_to_execute,
        active_event,context,*args):
        '''
        @param {Queue.Queue} return_queue --- Passed by the calling endpoint.
        Put the result of the operation into return_queue, from which the other
        side reads it.
        
        @param {closure} closure_to_execute --- The closure 
        @param {_ActiveEvent} active_event ---

        @param {*args} *args --- The arguments that get passed to the
        closure to execute.
        
        '''
        self.return_queue = return_queue
        self.closure_to_execute = closure_to_execute
        self.active_event = active_event
        self.context = context
        self.args = args
        threading.Thread.__init__(self)

    def run(self):
        # actually run the function
        to_return = self.closure_to_execute(
            self.active_event,self.context,*self.args)

        self.return_queue.put(_RunAndHoldResult(to_return))

        
class _RunAndHoldResult(object):
    R_AND_H_RESULT = 'run_and_hold_result'
    def __init__(self,result):
        self.result = result
    def _type(self):
        return R_AND_H_RESULT

class _RunAndHoldRequestResult(object):
    '''
    Each RunAndHoldRequestResult is put into an endpoint's
    _run_and_hold_queue, which it is passed when we call _run_and_hold
    on that endpoint.

    It is then read from _RunAndHoldQueueService loop, which will call
    _process_run_and_hold_result with it as an argument.

    This object just tells the calling endpoint whether the run and
    hold request was able to lock all the resources that are necessary
    for the run and hold request to proceed.  
    '''

    def __init__(
        self,reservation_request_result,
        waldo_initiator_id,endpoint_initiator_id,priority,
        requesting_context_id,force=False):

        self.reservation_request_result = reservation_request_result
        self.priority = priority
        self.waldo_initiator_id = waldo_initiator_id
        self.endpoint_initiator_id = endpoint_initiator_id
        self.requesting_context_id = requesting_context_id

        # whether we should force backout if there's a conflict.
        self.force = force
        
        
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

                else:
                    to_add = _value_deep_copy(to_add)                    
                    
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

                else:
                    # FIXME: be careful not copying external objects
                    to_add = _value_deep_copy(to_add)                    
                    
                new_array.append(to_add)

            return new_array

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
                [],
                self.toExecEvent.priority,
                self.toExecEvent.event_initiator_waldo_id,
                self.toExecEvent.event_initiator_endpoint_id,
                self.toExecEvent.id)

            
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

    def __init__(self,extStore,endpointName,endpoint):
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

        self.endpoint = endpoint
        
        self.id = None;

        # re-entrant run and hold requests may cause multiple active
        # events to share the same contexts.  it simplifies logic to
        # reuse the same code for canceling an active event.  This
        # logic however, attempts to commit and merge context data
        # each time.  To ensure that a context is only merged and
        # committed once, we keep track of whether a context has
        # already been committed or merged and return early in the
        # mergeIntoMe and commit functions if it has.
        self.committed = False
        self.merged_into_me = False
        self.fired_on_completes = False
        self.release_message_sent = False

        
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

        # wait for reponses to run and hold messages by reading from
        # this queue.  If the run and hold got revoked in the interim,
        # then we will write None to every threadsafe queue in this
        # array.
        self.run_and_hold_queues = []

        # this collects return statements from message send sequence
        # steps.  any time we call a sequence, we first put the names
        # of sequence globals that we want returned to us in to this
        # list.  when the sequence returns, the context runs through
        # this list and grabs the named sequence globals from itself
        # when returning
        self.waiting_returns_list = []
        
        
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

        if otherContext.merged_into_me:
            return

        otherContext.merged_into_me = True        
        
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
        returner = _Context(
            self.externalStore,self.endpointName,activeEvent.endpoint)
        
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

        if self.committed:
            return

        self.committed = True

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


        Note: self.waiting_returns_list has type {list} --- Each element is a string
        representing the connection-unique name of a sequence global
        that we want to return from our context id.  We put each of
        these variables in a return array that gets passed, with
        contextId into msgReceiveQueue.
        
        eg. self.waiting_returns_list might be ['kj__a'].  Then we look up
        'kj__a' in our seqGlobals. and pass its value back through
        when putting.

        
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


        to_return_array = []
        for seq_glob_name in self.waiting_returns_list:
            #### DEBUG
            if self.seqGlobals == None:
                err_msg = '\nBehram error: trying to return '
                err_msg += 'a sequence global when had none '
                err_msg += 'part of context.\n'
                print err_msg
                assert(False)


            if seq_glob_name not in self.seqGlobals:
                err_msg = '\nBehram error: trying to return '
                err_msg += 'a sequence global that did not '
                err_msg += 'exist in context.\n'
                print err_msg
                assert (False)
            #### END DEBUG

            to_return_array.append(
                self.seqGlobals[seq_glob_name])
        
            
        # execution thread that had been blocking on reading queue now
        # can continue.  depending on result of this read, it keeps
        # executing or raises a _PostponeException that the caller
        # catches.
        self.msgReceivedQueue.put(
            (contextId,to_return_array));


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
        if self.fired_on_completes:
            return
        self.fired_on_completes = True

        
        for onCompleteToFire in self.onCompletesToFire:
            onCompleteToFire.fire();

    def send_event_release_message(self,active_event):
        if self.release_message_sent:
            return
        self.release_message_sent = True
        
        if not self.messageSent:
            return

        active_event.endpoint._writeMsg(
            _Message.eventReleaseMsg(self,active_event))


        
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
        
    def generateActiveEvent(self,run_and_hold_parent_context_id):
        '''
        MUST BE CALLED WITHIN LOCK

        @param{int or None} run_and_hold_parent_context_id --- If this
        event was occasioned by a run and hold request from another
        endpoint, then this will be the integer id of the context on
        the calling endpoint.  (Note: not the id of the context of the
        root endpoint, but instead the parent context.)  Otherwise, it
        is None.

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
            self.endpoint._waldo_id,self.endpoint._endpoint_id,
            run_and_hold_parent_context_id)        
    
    
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

    # control field for run and hold messages
    RUN_AND_HOLD_VAR_SENTINEL = '_run_and_hold_var'
    
    # to keep track of who started the transaction
    WALDO_INITIATOR_ID_FIELD = 'waldo_initiator_id'
    ENDPOINT_INITIATOR_ID_FIELD = 'endpoint_initiator_id'

    R_AND_H_CONTEXT_ID_FIELD = '_r_and_h_context_id__'
    CALLER_CONTEXT_ID_FIELD  =  '__caller_context_id__'    

    RESERVATION_REQUEST_RESULT_FIELD = '__reservation_req_result__'

    
    @staticmethod
    def eventNotAcceptedMsg(eventId,reservation_request_result):
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
            _Message.RESERVATION_REQUEST_RESULT_FIELD: reservation_request_result
            };

        return returner;    

    @staticmethod
    def run_and_hold_msg(
        priority,waldo_initiator_id,endpoint_initiator_id,
        reservation_request_result,active_event_id,r_and_h_context_id):
        '''

        @param {_ReservationRequestResult} reservation_request_result
        --- @see reservationManager.py.  Contains the
        overlapping_reads and overlapping_writes that caused the
        run_and_hold request to fail.
        
        Constructs a message dictionary that can be sent to the other
        endpoint telling it what variables the run and hold relies on.
        
        '''
        returner = {
            _Message.PRIORITY_FIELD: priority,
            _Message.WALDO_INITIATOR_ID_FIELD: waldo_initiator_id,
            _Message.ENDPOINT_INITIATOR_ID_FIELD: endpoint_initiator_id,
            _Message.CONTROL_FIELD: _Message.RUN_AND_HOLD_VAR_SENTINEL,
            _Message.RESERVATION_REQUEST_RESULT_FIELD: reservation_request_result,
            _Message.R_AND_H_CONTEXT_ID_FIELD: r_and_h_context_id,
            _Message.EVENT_ID_FIELD: active_event_id
            }
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
            _Message.CALLER_CONTEXT_ID_FIELD: context.id            
            };
        return returner;


class _ActiveEvent(object):

    def __init__ (
        self,eventName,activeGlobReads,activeGlobWrites,
        seqGlobals,endpoint,externalVarNames, waldo_id,endpoint_id,
        run_and_hold_parent_context_id):
        '''
        @param{Int} eventId --- Unique among all other active events.

        @param{array} externalVarNames --- An array of all the
        (unique) variable identifiers for externals that this active
        event touches.  These should only be variable identifiers for
        shared and endpoint global references.  Can use these to
        increase their reference counts to ensure that they do not get
        removed from external store.

        @param {int or None} run_and_hold_parent_context_id --- See
        the comment right above assigning it to
        self.run_and_hold_parent_context_id for usage.
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

        # If this event was occasioned by a run and hold request from
        # another endpoint, then this will be the integer id of the
        # context on the calling endpoint.  (Note: not the id of the
        # context of the root endpoint, but instead the parent
        # context.)  Otherwise, it is None.
        self.run_and_hold_parent_context_id = run_and_hold_parent_context_id

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
        self.contextId = _Context.INVALID_CONTEXT_ID + 1

        self.parent_context_id = None

        # each element of return queue has type _ReturnQueueElement.
        # The purpose of this queue is to notify the
        # externally-initiated, blocking code that this event is done.
        self.returnQueue = Queue.Queue();

        self.toExecFrom = None;

        self.extsToRead = [];
        self.extsToWrite = [];
        self.externalVarNames = externalVarNames;

        # If this active event was occasioned by a run and hold
        # request, then we should forward all reservation request
        # results back to root endpoint through this queue.
        self.reservation_request_result_queue = None

        
    def set_run_and_hold_request_result_forward_queue(
        self,reservation_request_result_queue):
        '''
        @see comment above self.reservation_request_result_queue in
        __init__
        '''
        self.reservation_request_result_queue = reservation_request_result_queue
        

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
        NOT CALLED FROM WITHIN LOCK.  Parts of it will grab an
        endpoint's lock.

        Ensures that all active events with priority, parent context ids,
        etc. are committed and release their resources.
        '''
        self.endpoint._all_active_event_commit_and_forward(
            self.run_and_hold_parent_context_id,
            self.priority,self.event_initiator_endpoint_id,
            self.event_initiator_waldo_id,returnVal)
        
        

    def _single_active_event_set_completed(self,returnVal,context):
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
        context.send_event_release_message(self)
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

    def _release_externals(self,externals_to_read,externals_to_write):
        '''
        '''
        self.endpoint._reservationManager.release(
            externals_to_read,
            externals_to_write,
            [],
            self.priority,
            self.event_initiator_waldo_id,
            self.event_initiator_endpoint_id,
            self.id)

    
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

        Note that it is not considered a conflict if an event 
        '''

        def filter_reentrant(to_filter):
            '''
            @param{Array} to_filter --- Each element is a
            _LockedRecord object.

            @returns{Array} --- Each element is a _LockedRecord
            object.

            Runs through to_filter and copies records that have
            different priority, event_initiator_id, event_id, and waldo_id-s
            compared to the current event's priority and ids (found in
            self.priority, self.event_initiator_waldo_id,
            self.event_initiator_endpoint_id, self.id)
            '''
            to_return = []

            for record in to_filter:
                if ((record.waldo_initiator_id == self.event_initiator_waldo_id) and
                    (record.endpoint_initiator_id == self.event_initiator_endpoint_id) and
                    (record.priority == self.priority)):
                    continue

                to_return.append(record)
            
            return to_return


        
        endpointGlobSharedReadVars = self.endpoint._globSharedReadVars;
        endpointGlobSharedWriteVars = self.endpoint._globSharedWriteVars;
        
        # we are not forcing adding this event, and must check if
        # the event would pose any conflicts.  if it does, then do
        # not proceed with adding the active event.
        for actReadKey in self.activeGlobReads.keys():


            if actReadKey in endpointGlobSharedWriteVars:
                # check that the overlap isn't from my own action that
                # is now re-entering
                reentrant_filtered = filter_reentrant(
                    endpointGlobSharedWriteVars[actReadKey])

                if len(reentrant_filtered) > 0:
                    res_req_result.succeeded = False
                    res_req_result.append_overlapping(
                        True, # append as read
                        actReadKey,
                        reentrant_filtered)

        for actWriteKey in self.activeGlobWrites.keys():


            if actWriteKey in endpointGlobSharedWriteVars:
            
                # check that the overlap isn't from my own action that
                # is now re-entering
                reentrant_filtered_writes = filter_reentrant(
                    endpointGlobSharedWriteVars[actWriteKey])            

                if len(reentrant_filtered_writes) > 0:
                    res_req_result.succeeded = False
                    res_req_result.append_overlapping(
                        False, #append as write
                        actWriteKey,
                        reentrant_filtered_writes)


            if actWriteKey in endpointGlobSharedReadVars:
            
                # check that the overlap isn't from my own action that
                # is now re-entering
                reentrant_filtered_reads = filter_reentrant(
                    endpointGlobSharedReadVars[actWriteKey])
                
                if len(reentrant_filtered_reads) > 0:
                    res_req_result.succeeded = False
                    res_req_result.append_overlapping(
                        False, #append as write
                        actWriteKey,
                        reentrant_filtered_reads)

        
        
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
        
        @returns {bool,_Context,reservation_request_result} ---
        False,None if cannot add event.  True,context to use if can
        add event.
        '''

        if newId:
            self.id = self.endpoint._getNextActiveEventIdToAssign();

        res_req_result = self.request_resources_for_run_and_hold(
            force,argument_array)

        if not res_req_result.succeeded:
            return False,None,res_req_result

        
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
            
        return True,eventContext,res_req_result

        
    def cancelActiveEvent(self):
        '''
        CALLED FROM WITHIN ENDPOINT LOCK
        
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

                to_remove_counter_list = []
                for counter in range(0,len(read_lock_list)):
                    item = read_lock_list[counter]
                    if ((item.waldo_initiator_id == self.event_initiator_waldo_id) and
                        (item.endpoint_initiator_id == self.event_initiator_endpoint_id) and
                        (item.act_event_id == self.id)):
                        to_remove_counter_list.append(counter)

                for to_remove_counter in reversed(to_remove_counter_list):
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
                to_remove_counter_list = []
                for counter in range(0,len(write_lock_list)):
                    item = write_lock_list[counter]
                    if ((item.waldo_initiator_id == self.event_initiator_waldo_id) and
                        (item.endpoint_initiator_id == self.event_initiator_endpoint_id) and
                        (item.act_event_id == self.id)):
                        to_remove_counter_list.append( counter)

                for to_remove_counter in reversed(to_remove_counter_list):
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
                  externalGlobals,reservationManager,waldo_id,endpoint_id,
                  waldo_timeout_excep):
        '''
        @param {dict} externalGlobals --- used for reference counting
        reads and writes to external variables.  (ie, the variable
        named by the key).  <String:Bool>
        
        @param {ReservationManager object} reservationManager

        @param {float} waldo_id --- Unique per host.

        @param {float} endpoint_id --- Unique per connection
        
        @param {Exception} waldo_timeout_excep --- WaldoTimeoutExcep:
        supposed to be raised when an operation times out.
        
        '''
        self._waldo_timeout_excep = waldo_timeout_excep
                  

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

        self._loop_detector = _RunAndHoldLoopDetector(self)

        # we have a threadsafe queue, r_and_h_threadsafe_queue.  when
        # we issue a run and hold request, then whether the endpoint
        # we issued the request to was able to lock relevant resources
        # or it wasn't gets put into this queue.  we pass the queue as
        # part of a run and hold request.  similarly, we start an
        # external thread to read from this queue and process
        # responses from it.
        # other endpoints should put 
        self._run_and_hold_queue = Queue.Queue()
        
        # note, do not need endpoint to hold reference to service_loop.
        # will stop automatically when exit.
        service_loop = _RunAndHoldQueueServiceLoop(self)
        service_loop.start()

        self._run_and_hold_retry_abort_loop = Queue.Queue()
        retry_abort_loop_service = _RetryAbortLoopServicer(
            self._run_and_hold_retry_abort_loop,self)
        retry_abort_loop_service.start()
            
        # when someone requests a run and hold from us and we can't
        # schedule it (because someone else is holding the resources,
        # then append it to this list.  When we get a request to
        # retry, remove the request from this list and retry it.  when
        # we get an abort, remove the request from this list with no
        # retry.
        self._failed_run_and_holds = []

    ##### helper functions #####

    def _i_initiated_run_and_hold(
        self, run_and_hold_request_result):
        '''
        @param {_RunAndHoldRequestResult object}
        run_and_hold_request_result --- Want to see if this is a
        result to a run and hold request that was rooted on this
        endpoint.
        
        @returns {bool} --- True if this endpoint was the root of the
        run and hold request.  False otherwise.
        '''

        if ((run_and_hold_request_result.waldo_initiator_id == self._waldo_id) and
            (run_and_hold_request_result.endpoint_initiator_id == self._endpoint_id)):
            return True

        return False

    def _notify_run_and_hold_backout(
        self,parent_context_id,priority,endpoint_initiator_id,
        waldo_initiator_id):
        '''
        @param{int} parent_context_id
        @param{float} priority ---
        @param{float} endpoint_initiator_id ---
        @param{float} waldo_initiator_id ---

        This gets called whenever we are asked to abort a currently
        executing run and hold call.
        
        It puts an element in the run_and_hold_retry_abort loop.  When
        that element is read, it kills any active events that ran as a
        result of that run and hold call.  It also forwards the
        backout request further back.
        '''

        self._run_and_hold_retry_abort_loop.put(
            (_RetryAbortLoopServicer.ABORT,
             parent_context_id,
             priority,endpoint_initiator_id,waldo_initiator_id))             
        
    def _notify_run_and_hold_retry(
        self,parent_context_id,priority,endpoint_initiator_id,
        waldo_initiator_id):
        '''
        @param{float} priority ---
        @param{float} endpoint_initiator_id ---
        @param{float} waldo_initiator_id ---

        This gets called whenever we are asked to retry a run and hold
        call.  It puts an element in the run_and_hold_retry_abort
        loop.  When that element is read, it tries to reschedule any
        paused events and forwards on the run and hold request to
        endpoints it called a run and hold on.
        '''

        self._run_and_hold_retry_abort_loop.put(
            (_RetryAbortLoopServicer.RETRY,
             parent_context_id,
             priority,endpoint_initiator_id,waldo_initiator_id))
        
    def _notify_run_and_hold_commit(
        self,parent_context_id,priority,endpoint_initiator_id,
        waldo_initiator_id):
        '''
        @param {int} parent_context_id --- The id of the parent
        context that called for the run and hold.
        
        Called from an external endpoint when we are told that the
        work that we have done with our current run and hold operation
        can be committed on this endpoint.

        Should a) forward the run and hold commit message and b)
        commit the context.

        Does so by spinning up a new thread so that does not block the
        caller.
        '''
        # FIXME: this should probably eventaully use the same code
        # path as _notify_run_and_hold_retry (ie, thrgouh the
        # run_and_hold_retry_abort_loop).
        run_and_hold_commit_thread = _RunAndHoldCommitThread(
            parent_context_id,priority,endpoint_initiator_id,
            waldo_initiator_id,self)
        run_and_hold_commit_thread.start()

        
    def _all_active_event_commit_and_forward(
        self,parent_context_id,priority,
        endpoint_initiator_id,waldo_initiator_id,return_val):
        '''
        When a run and hold's calling endpoint tells you it is time to
        commit the changes made by the run and hold, then we receive a
        _notify_run_and_hold_commit call.  This spins up a separate
        thread, which calls this function.  We spin up a separate
        thread so that we do not block the calling endpoint while we
        actually perform the commit.

        This function:

             Commits the context that we had been using for the run
             and hold. When committing, will also forward notification
             to other endpoints that I called run and hold on.
        '''
        self._lock()


        # 1: find context to commit

        # note because we may have a reentrant run and hold request,
        # we may have several active events per initiator
        # id/priority/context id tuple.  We want to ensure that they
        # all release their locks on variables.  Therefore, we run
        # through all elements in active event dict (for now...FIXME:
        # this is very inefficient), and cancel all active events that
        # are associated.
        matching_active_events = []
        contexts_to_commit = []
        act_event_dict = self._activeEventDict
        for act_event_element_key in act_event_dict.keys():
            act_event = act_event_dict[act_event_element_key].actEvent
            ctx = act_event_dict[act_event_element_key].eventContext

            if ((act_event.priority == priority) and
                (act_event.event_initiator_waldo_id == waldo_initiator_id) and
                (act_event.event_initiator_endpoint_id == endpoint_initiator_id) and
                (act_event.run_and_hold_parent_context_id == parent_context_id)):

                matching_active_events.append(act_event)
                contexts_to_commit.append(ctx)

        self._unlock()

        for counter in range(0,len(matching_active_events)):
            matching_active_event = matching_active_events[counter]
            context_to_commit = contexts_to_commit[counter]
            
            # actually commit the context (if it hasn't been already)
            # and active event will also remove the active event from
            # endpoint's active event dict and forward the commit
            # onwards (if it hasn't been forwarded already)
            matching_active_event._single_active_event_set_completed(
                return_val, 
                context_to_commit)


        
    def _run_and_hold_local(
        self,return_queue,reservation_request_result_queue,
        to_run,parent_context_id,priority,waldo_initiator_id,
        endpoint_initiator_id,*args):
        '''

        @param {Int} parent_context_id --- The id of the context on
        the calling endpoint that occasioned this run and hold
        request.  Whenever send back reservation request results, must
        include this in the message so can demultiplex who the
        reservation request result is for.
        
        @param {Queue.Queue} return_queue --- Created on other endpoint for each
        run_and_hold call.  When the run and hold request completes, put the
        result into this queue (wrapped in a _RunAndHoldResult object).

        @param {Queue.Queue} reservation_request_result_queue --- The
        _run_and_hold_queue on the endpoint that is issuing the
        _run_and_hold_local call.  When we attempt to process the run
        and hold call, we try to acquire read and write locks on the
        variables that it touches.  We put the results of attempting
        to acquire those resources into this queue.  If we were unable
        to acquire the resources, the root of the run and hold request
        can then tell us whether to retry or back out.
        
        '''
        
        fixme_function_prefix = '_hold_func_prefix_' + self._endpointName + '_'       
        to_run_internal_name = fixme_function_prefix + to_run

        try:
            to_execute = getattr(self,to_run_internal_name)
        except AttributeError as exception:
            # FIXME: probably want to return a different, undefined
            # method or something.
            err_msg = '\nBehram error when calling ' + to_run
            err_msg += '.  It does not exist on this endpoint.  '
            err_msg += 'Trying to look it up with name '
            err_msg += to_run_internal_name + '.\n'
            print err_msg
            assert(False);

        self._lock()
        
        # attempt to acquire read/write locks on resources for this
        # action.  put results in reservation_request_result_queue so
        # that service loop on other endpoint can read result.

        res_request_result,active_event,context = self._acquire_run_and_hold_resources(
            to_run_internal_name,priority,waldo_initiator_id,endpoint_initiator_id,
            parent_context_id)

        ### FIXME: it is gross to do this here... it is necessary to
        ### keep track of all information necessary to retry the event
        ### in the case that process_retry_cmd is called.
        active_event.return_queue = return_queue
        active_event.reservation_result_request_queue = reservation_request_result_queue
        active_event.to_run = to_run
        active_event.parent_context_id = parent_context_id
        active_event.args = args


        # wraps the reservation request result with ancillary
        # information necessary for other side to determine which
        # request this is a response for.
        run_and_hold_request_result = _RunAndHoldRequestResult(
            res_request_result,waldo_initiator_id,endpoint_initiator_id,
            priority,parent_context_id)
            
        if res_request_result.succeeded:
            # go ahead and add run and to active event dict, because
            # it's going to run.
            self._activeEventDict[active_event.id] = _ActiveEventDictElement(
                active_event,context)
            active_event.active = True
        else:
            self._failed_run_and_holds.append(active_event)            


        reservation_request_result_queue.put(run_and_hold_request_result)
        self._unlock()

        active_event.set_run_and_hold_request_result_forward_queue(
            reservation_request_result_queue)
        
        # tell the other side whether run and hold request succeeded
        # or failed commented for now because unclear if actually
        # should ever send run and hold messages over the wire
        # ... probably should, but still unclear how.
        # self._send_run_and_hold_result_msg(
        #     to_run,priority,waldo_initiator_id,endpoint_initiator_id,
        #     res_request_result)

        if res_request_result.succeeded:
            # we could lock all resources. go ahead and run the method
            # on another thread (which assumes the required resources
            # are already held)
            run_and_hold = _RunnerAndHolder(
                return_queue,
                to_execute,active_event,context, *args)
            run_and_hold.start()

        return res_request_result.succeeded


    def _process_run_and_hold_request_result(
        self,run_and_hold_req_result,act_event):
        '''
        MUST BE CALLED FROM WITHIN ENDPOINT LOCK
        
        This gets called when we receive a run and hold result request
        from performing a function call on an endpoint.  At this
        point, the run and hold request may have succeeded or failed.

        @param {_RunAndHoldRequestResult object}
        run_and_hold_req_result --- The result of a function call on a
        foreign endpoint.  
        
        @param {_ActiveEvent object} act_event --- The active event
        object that made the request on the endpoint object.
        

        What to do:
            0: If we were the root of the run and hold request chain
               and the request succeeded, then just append the result
               to the loop detector.

            1: If we were the root of the run and hold request chain
               and the result failed, then:

               a: If our priority is lower than one of the reasons
                  that we failed, then notify all that we have already
                  talked to to release resources and reschedule.

               
               b: If all the reasons that it failed were from
                  lower priority events, then go ahead and retry.


            2: if it is a response to a run and hold request that
               another endpoint's event initiated, then just forward
               on the resource failure and do nothing.

        '''

        reservation_request_result = run_and_hold_req_result.reservation_request_result
        priority = run_and_hold_req_result.priority
        waldo_initiator_id = run_and_hold_req_result.waldo_initiator_id
        endpoint_initiator_id = run_and_hold_req_result.endpoint_initiator_id
        requesting_context_id = run_and_hold_req_result.requesting_context_id
        
        if self._i_initiated_run_and_hold(run_and_hold_req_result):
            # means that this endpoint was the root of the run and
            # hold request.

            if reservation_request_result.succeeded:
                # CASE 0 from the comments at the top of the function

                # FIXME: unclear if truly need lock here or not.
                # Performing operation on internal dict of loop_detector.

                # FIXME: probably shouldn't add the event if it does
                # not exist.  if it does not exist, probably menas
                # that the run and hold has been revoked or completed.

                self._lock()
                dict_element = self._loop_detector.append_result_or_add_if_dne(
                    requesting_context_id,act_event,reservation_request_result)
                self._unlock()
            else:
                # CASE 1 from the comments at the top of the function

                highest_priority_overlap = reservation_request_result.get_highest_priority_overlap()
                #### DEBUG
                if highest_priority_overlap == None:
                    err_msg = '\nBehram error: if there are no overlaps, then '
                    err_msg += 'why did the request not succeed?\n'
                    print err_msg
                    assert(False)
                #### END DEBUG

                # FIXME: unsure if actually need to take locks here
                # for loop detectors
                self._lock()


                dict_element = self._loop_detector.get(
                    requesting_context_id,priority,endpoint_initiator_id,
                    waldo_initiator_id)

                if dict_element == None:
                    # Ignore message: must have come after revoke was sent
                    pass
                else:
                    # the endpoint that forwarded the run and hold
                    # reservation request result should already be in
                    # dict element's list of
                    # endpoint_to_notify_or_commit_to Endpoint dict.
                    # therefore, should just be able to call revoke or
                    # forward_retry directly.
                    if ((highest_priority_overlap > dict_element.act_event.priority) or
                        run_and_hold_req_result.force):                    
                        # CASE 1a from the comments at the top of the function

                        # FIXME: when revoke, not removing the dict
                        # element from the loop detector's run and
                        # hold dict.  This is because the running
                        # context may try to execute a run and hold
                        # and if the dict element is not there, then
                        # it will create a new one and proceed.  Need
                        # a safe way to garbage collect run and hold
                        # dict elements.
                        dict_element.revoke()
                        
                        # wait some time and then try to restart the event.
                        # FIXME: this is gross.  is there a way to make it event
                        # based, or at least not hardcode the time to wait?
                        restart_event_thread = _RestartEventThread(self)
                        restart_event_thread.start()
                        

                    else:
                        # CASE 1b from the comments at the top of the function
                        dict_element.forward_retry()

                self._unlock()
        else:
            # CASE 2 from the comments at the top of the function
            
            # FIXME: unsure if actually need to take locks here
            # for loop detectors
            self._lock()


            dict_element = self._loop_detector.get(
                requesting_context_id,priority,endpoint_initiator_id,
                waldo_initiator_id)
            
            if dict_element == None:
                # Ignore: may be receiving a response for an event
                # that was already revoked.
                pass
            else:
                # must forward the run and hold request on to the
                # controller.  The controller will forward it on to
                # its controller, which will forward on to its
                # controller ... until the root initiator of the event
                # receives the forwarded response.  This root
                # initiator then can decide whether to retry or
                # whether to release
                dict_element.forward_reservation_result_to_controller(
                    run_and_hold_req_result)

            self._unlock()


    def _acquire_run_and_hold_resources(
        self,to_run_internal_name,priority,waldo_initiator_id,
        endpoint_initiator_id,run_and_hold_parent_context_id):
        '''
        Attempt to grab the resources required to run to_run as part
        of a run_and_hold request.

        CALLED FROM WITHIN LOCK

        @returns (a,b,c) ---
           {_ReservationRequestResult} a ---
           
           {_ActiveEvent or None} b --- None if cannot acquire
           resources, otherwise, an active event, which we can later
           schedule to run.

           {_Context or None} c --- None if cannot acquire resources.
           Otherwise, a context.  Note that if we've already created
           an active event with the same initiator id, edpoint id, and
           priority, then we re-use its context, potentially
           copying-in data that it does not already have and that this
           event needs.
        '''

        #### DEBUG
        if not (to_run_internal_name in self._prototypeEventsDict):
            err_msg = '\nBehram error.  Could not acquire resources '
            err_msg += 'for run and hold because '
            print err_msg
            assert(False)
        #### END DEBUG
            

        event_to_run_and_hold = self._prototypeEventsDict[to_run_internal_name]
        act_event = event_to_run_and_hold.generateActiveEvent(
            run_and_hold_parent_context_id)

        # set the attributes of the active event correctly so will
        # correctly re-use context.
        act_event.set_event_attributes_from_msg(
            act_event.id,priority,waldo_initiator_id,endpoint_initiator_id)

        reservation_request_result = act_event.request_resources_for_run_and_hold()


        # generate context
        context_to_use = None
        if reservation_request_result.succeeded:
            context_to_use = self._generate_run_and_hold_context(
                priority,waldo_initiator_id,endpoint_initiator_id,act_event)

        return reservation_request_result,act_event,context_to_use


    def _generate_run_and_hold_context(
        self,priority,waldo_initiator_id,endpoint_initiator_id,act_event):
        '''
        CALLED FROM WITHIN LOCK

        @param{float} priority
        @param{float} waldo_initiator_id
        @param{float} endpoint_initiator_id
        @param{ActiveEvent object} act_event

        @returns{_Context object}
        
        Runs through the list of active event elements.  If any of the
        active event elements have the same priority,
        waldo_initiator_id, and endpoint_initiator_id, then grab its
        context and add to it to include any data this event needs
        that the other did not.
        '''

        context_to_use = None
        matching_active_event = None
        act_event_dict = self._activeEventDict
        for act_event_element_key in act_event_dict.keys():
            act_event_element = act_event_dict[act_event_element_key].actEvent
            ctx = act_event_dict[act_event_element_key].eventContext
            

            if ((act_event_element.priority == priority) and
                (act_event_element.event_initiator_waldo_id == waldo_initiator_id) and
                (act_event_element.event_initiator_endpoint_id == endpoint_initiator_id)):

                matching_active_event = act_event_element
                context_to_use = ctx
                break


        if context_to_use == None:
            # means that we didn't already have a context in our dict
            # to use.  create a new one.  note that we do not need to
            # advance our context id because we will only run this at
            # the beginning (ie, there are no other contexts that we
            # need to clear out).
            context_to_use =  self._committedContext.copyForActiveEvent(
                act_event,act_event.contextId)
        else:

            # need to grab the id of the contex that we'll be using.
            # that way, this active event will be synchronized to
            # reject the context's changes if they have been rolled
            # back.
            act_event.contextId = matching_active_event.contextId

            # FIXME: Should not copy over sequence variables
            dummy_context = self._committedContext.copyForActiveEvent(
                act_event,act_event.contextId)


            # copy over the shareds
            for index in dummy_context.shareds.keys():
                if not (index in context_to_use.shareds):
                    context_to_use.shareds[index] = _value_deep_copy(
                        dummy_context.shareds[index])
                    
            # copy over the end globals
            for index in dummy_context.endGlobals.keys():
                if not (index in context_to_use.endGlobals):
                    context_to_use.endGlobals[index] = _value_deep_copy(
                        dummy_context.endGlobals[index])
                    
            # copy over the seq globals
            if dummy_context.seqGlobals != None:
                # FIXME: potentially copying over sequence variables
                # for run and hold if reuse context.
                
                for index in dummy_context.seqGlobals.keys():
                    if context_to_use.seqGlobals == None:
                        context_to_use.seqGlobals = {}

                    if not (index in context_to_use.seqGlobals):
                        context_to_use.seqGlobals[index] = _value_deep_copy(
                            dummy_context.seqGlobals[index])

            
        return context_to_use

    
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

        # this way, when revoke an active event, queues waiting on
        # values from that event get read from and restarted.
        for r_and_h_queue in actEventContext.run_and_hold_queues:
            r_and_h_queue.put(None)
        
        # note that this function will take care of removing the
        # active event from active event dict as well as releasing
        # locks on read/write variables.
        actEvent.postpone(actEventContext);


    def _cancelActiveEvent(self,activeEventId):
        '''
        SHOULD ONLY BE CALLED FROM WITHIN ENDPOINT LOCK
        
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
        active_event_element = self._activeEventDict[activeEventId]
        active_event = active_event_element.actEvent
        current_context = active_event_element.eventContext


        for r_and_h_queue in current_context.run_and_hold_queues:
            # putting a value in return queue of None tells the waiting
            # context to abort waiting for a run-and-hold and end.
            r_and_h_queue.put(None)


        # Potential fixme: 
        fixme_msg = '\nBehram warn: may need to add code for backing '
        fixme_msg += 'out partials.\n'

        return active_event.cancelActiveEvent();


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

        # if part of this sequence was any run and hold sequence, then
        # tell the other endpoints to commit their run and holds-es as
        # well.
        dict_element = self._loop_detector.remove_if_exists(
            contextToCommit.id,activeEvent.priority,
            activeEvent.event_initiator_endpoint_id,
            activeEvent.event_initiator_waldo_id)

        if dict_element != None:
            # we had issued a run and hold request when we executed
            # this context go and notify all other endpoints that were
            # part of this commit that they can also release their
            # resources.
            dict_element.forward_commit()



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

            eventAdded, context, res_req_result = inactiveEvent.addEventToEndpointIfCan(
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
            onCompleteKey,self)


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

    def _unpack_and_process_message_not_accepted_sentinel_msg(self,msg):
        '''
        @param {dict} msg --- @see _Message for list of fields and
        their meanings.
        
        When we tried to initiate a non-run-and-hold style message,
        the other side rejected our request.  Postpone the event that
        tried to send the message and try scheduling another event.
        '''
        ctrlMsg = msg[_Message.CONTROL_FIELD];
        eventId = msg[_Message.EVENT_ID_FIELD];

        res_req_result = msg[_Message.RESERVATION_REQUEST_RESULT_FIELD]
        
        #### DEBUG
        if ctrlMsg != _Message.NOT_ACCEPTED_SENTINEL:
            err_msg = '\nBehram error.  Should never call '
            err_msg += '_process_message_not_accepted_sentinel '
            err_msg += 'on a message that does not have the '
            err_msg += 'correct control field.\n'
            print(err_msg)
            assert(False)
        #### END DEBUG

        ### IF this was not the result of a run and hold event, just
        ### postpone the event and try the next one.

        ### Otherwise, forward the result_request object on to the
        ### root run and hold caller.  For this case, the run and hold
        ### requester will abandon and restart.

        self._lock()
        act_event_dict_element = self._activeEventDict.get(eventId,None)
        if ((act_event_dict_element == None) or
            (act_event_dict_element.actEvent.reservation_request_result_queue != None)):

            # not result of run and hold.  CASE 2 above
            # means that we need to postpone current outstanding event and 
            self._postponeActiveEvent(eventId)

        else:
            # result of run and hold: CASE 1 above
            active_event = act_event_dict_element.actEvent
            active_event.reservation_request_result_queue.put(
                _RunAndHoldRequestResult(
                    res_request_result,
                    active_event.event_initiator_waldo_id,
                    active_event.event_initiator_endpoint_id,
                    active_event.priority,
                    active_event.parent_context_id,
                    True # force the root of run and hold to back out
                         # conflicts
                    
                         # FIXME: probably do not want to outrightly
                         # force the run and hold to abort because of
                         # a local event.                    
                    ))
        
        self._unlock()        
        
        # when we postponed one event, we may have made way
        # for another event to execute.  similarly, may want
        # to reschedule the event that we postponed.
        self._tryNextEvent();


    def _update_context_data(self,contextData):
        '''
        @param {dict} contextData --- Should be a version of the
        context object used on the other end of the connection.  Need
        to convert it so that it uses Waldo lists and maps instead of
        their serialized forms.
        '''
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

        return contextData
        

    def _unpack_and_process_release_event_sentinel_msg(self,msg):
        '''
        @param {dict} msg --- @see _Message for list of fields and
        their meanings.

        Full transaction is complete: Commit incoming context data and
        clean up outstanding context on receiver.
        '''
        ctrlMsg = msg[_Message.CONTROL_FIELD]
        eventId = msg[_Message.EVENT_ID_FIELD]
        
        # only guaranteed to get these data if it is not a not
        # accepted message.
        eventName = msg[_Message.EVENT_NAME_FIELD]
        sequenceName = msg[_Message.SEQUENCE_NAME_FIELD]
        contextData = self._update_context_data(
            msg[_Message.CONTEXT_FIELD])

        # means that we should commit the specified outstanding
        # event and release read/write locks that the event was
        # holding.
        self._processReleaseEventSentinel(eventId,contextData);
        self._tryNextEvent();
        return;


    def _unpack_and_process_sequence_sentinel_finish_msg(self,msg):
        '''
        @see processSequenceSentinelFinished
        
        @param {dict} msg --- @see _Message for list of fields and
        their meanings.
        '''
        ctrlMsg = msg[_Message.CONTROL_FIELD]
        eventId = msg[_Message.EVENT_ID_FIELD]
        
        # only guaranteed to get these data if it is not a not
        # accepted message.
        eventName = msg[_Message.EVENT_NAME_FIELD]
        sequenceName = msg[_Message.SEQUENCE_NAME_FIELD]
        contextData = self._update_context_data(
            msg[_Message.CONTEXT_FIELD])

        
        #### DEBUG
        if ctrlMsg != _Message.MESSAGE_SEQUENCE_SENTINEL_FINISH:
            err_msg = '\nBehram error.  Should never call '
            err_msg += '_process_sequence_sentinel_finish_msg '
            err_msg += 'on a message that does not have the '
            err_msg += 'correct control field.\n'            
            print err_msg
            assert(False)
        #### END DEBUG


        # means that the message sequence that was called is
        # finished.
        self._processSequenceSentinelFinished(
            eventId,contextData,sequenceName);

        # reception of this message cannot have changed what
        # read/write locks were happening, so do not need to tryNext.
        return

    
        
    def _unpack_and_process_request_execution(self,msg):
        '''
        The other side has requested us to perform some action
        locally.  Ie, none of other specified control fields.
        '''
        ctrlMsg = msg[_Message.CONTROL_FIELD]
        eventId = msg[_Message.EVENT_ID_FIELD]
        
        # only guaranteed to get these data if it is not a not
        # accepted message.
        eventName = msg[_Message.EVENT_NAME_FIELD]
        sequenceName = msg[_Message.SEQUENCE_NAME_FIELD]
        contextData = self._update_context_data(
            msg[_Message.CONTEXT_FIELD])
        priority = msg[_Message.PRIORITY_FIELD]
        event_initiator_waldo_id = msg[_Message.EVENT_INITIATOR_WALDO_ID_FIELD]
        event_initiator_endpoint_id = msg[_Message.EVENT_INITIATOR_ENDPOINT_ID_FIELD]
        callers_context_id = msg[_Message.CALLER_CONTEXT_ID_FIELD]
        
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

            actEvent = self._prototypeEventsDict[eventName].generateActiveEvent(None);
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
            eventAdded,eventContext,reservation_request_result = actEvent.addEventToEndpointIfCan(
                None,forceAddition)

            self._unlock()


            if not eventAdded:
                # Case 1: reply back that we are not accepting the message

                self._writeMsg (
                    _Message.eventNotAcceptedMsg(
                        eventId,reservation_request_result) )
                return;

            createdNewEvent = True;
            
            # Case 2: we do the same thing that we would do if
            # the event had existed in self._activeEventDict.  so
            # we just fall through to execute the code that we
            # otherwise would have.


        # tell the active event which function to execute from.
        actEvent.setToExecuteFrom(ctrlMsg)


        # update the context that this active event should use to
        # execute from.
        if createdNewEvent:
            # if we created a new event, we may need to fill in dne-s
            # from the other side with a stable snapshot of endpoint
            # data.  to ensure snapshot is stable, must take lock.
            self._lock();
            eventContext.updateEnvironmentData(contextData,self)
            self._unlock();

            # means that reservation_request_result will be valid.
            # FIXME: this is ugly code.
            # Go ahead and forward back what is being held
            self._writeMsg(
                _Message.run_and_hold_msg(
                    priority,event_initiator_waldo_id,event_initiator_endpoint_id,
                    reservation_request_result,actEvent.id,callers_context_id))            

        else:
            eventContext.updateEnvironmentData(contextData,self)

        # actually run the function on my side
        self._executeActive(
            actEvent,
            eventContext,
            # specified so that internal message function does not
            # use return message queue, etc.
            _Endpoint._FUNCTION_ARGUMENT_CONTROL_FROM_MESSAGE);

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
        
        if ctrlMsg == _Message.NOT_ACCEPTED_SENTINEL:
            self._unpack_and_process_message_not_accepted_sentinel_msg(msg)
        elif ctrlMsg == _Message.RELEASE_EVENT_SENTINEL:
            self._unpack_and_process_release_event_sentinel_msg(msg)
        elif ctrlMsg == _Message.MESSAGE_SEQUENCE_SENTINEL_FINISH:
            self._unpack_and_process_sequence_sentinel_finish_msg(msg)
        elif ctrlMsg == _Message.RUN_AND_HOLD_VAR_SENTINEL:
            self._unpack_and_process_run_and_hold(msg)
        else:
            self._unpack_and_process_request_execution(msg)

    def _unpack_and_process_run_and_hold(self,msg):
        '''
        @param {dict} msg --- @see _Message for list of fields and
        their meanings.

        Forward the request result on to
        _process_run_and_hold_request_result.  (Read there what it
        does.
        
        '''
        #### DEBUG
        ctrl_msg = msg[_Message.CONTROL_FIELD];                
        if ctrl_msg != _Message.RUN_AND_HOLD_VAR_SENTINEL:
            err_msg = '\nBehram error.  Should never call '
            err_msg += '_process_run_and_hold_accepted_sentinel_msg '
            err_msg += 'on a message that does not have the '
            err_msg += 'correct control field.\n'            
            print err_msg
            assert(False)
        #### END DEBUG



        reservation_request_result = msg[_Message.RESERVATION_REQUEST_RESULT_FIELD]
        priority = msg[_Message.PRIORITY_FIELD]
        waldo_initiator_id = msg[_Message.WALDO_INITIATOR_ID_FIELD]
        endpoint_initiator_id = msg[_Message.ENDPOINT_INITIATOR_ID_FIELD]
        act_event_id = msg[_Message.EVENT_ID_FIELD]
        context_id = msg[_Message.R_AND_H_CONTEXT_ID_FIELD]
        
        self._lock()
        active_event_element = self._activeEventDict.get(act_event_id,None)

        if active_event_element == None:
            self._unlock()
            return

        active_event = active_event_element.actEvent
        
        r_and_h_reqeust_result =  _RunAndHoldRequestResult(
            reservation_request_result,
            active_event.event_initiator_waldo_id,
            active_event.event_initiator_endpoint_id,
            active_event.priority, context_id)


        dict_element = self._loop_detector.get(
            context_id,priority,endpoint_initiator_id,
            waldo_initiator_id)

        if dict_element == None:
            # means that this is a response to an event that must
            # have finished or been revoked and therefore removed
            # from the loop detector dict.  Skip.
            pass
        else:
            act_event = dict_element.act_event
            self._process_run_and_hold_request_result(
                r_and_h_request_result,act_event)

        self._unlock()



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

