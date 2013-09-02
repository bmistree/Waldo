import threading
import waldo.lib.util as util

class AllEndpoints(object):

    def __init__(self):
        self._mutex = threading.Lock()
        self.endpoint_map = {}

        # each element will be a map of endpoints.  send_clock_update
        # will put copies of self.endpoint_map into the queue and a
        # separate thread (clock_update_thread) running
        # sep_thread_listening_for_updates will read off the queue and
        # then request each endpoint in the map to send a clock update
        # to its partner.
        self.endpoints_to_update_queue = util.Queue.Queue()
        
        clock_update_thread = threading.Thread(
            target = self.sep_thread_listening_for_updates)
        clock_update_thread.daemon = True
        clock_update_thread.start()

    def sep_thread_listening_for_updates(self):
        '''
        Run from clock_update_thread
        @see comment above self.endpoints_to_update_queue
        '''
        while True:
            copied_endpoint_map = self.endpoints_to_update_queue.get()
            # FIXME: add a check in endpoint to ensure that the endpoints
            # have not suffered a network exception or been stopped?
            for endpt in copied_endpoint_map.values():
                endpt._send_clock_update()
        
        
    def _lock(self):
        self._mutex.acquire()
    def _unlock(self):
        self._mutex.release()

    def send_clock_update(self):
        self._lock()
        copied_endpoint_map = dict(self.endpoint_map)
        self._unlock()
        # note: okay that running through after release lock because
        # new endpoints will already grab new clock dates
        self.endpoints_to_update_queue.put(copied_endpoint_map)

            
    def add_endpoint(self,endpoint):
        self._lock()
        self.endpoint_map[endpoint._uuid] = endpoint
        self._unlock()

    def _remove_endpoint_if_exists(self,endpoint):
        self._lock()
        self.endpoint_map.pop(endpoint._uuid,None)
        self._unlock()
        
    def endpoint_stopped(self,which_endpoint_stopped):
        self._remove_endpoint_if_exists(which_endpoint_stopped)

    def network_exception(self,which_endpoint_excepted):
        self._remove_endpoint_if_exists(which_endpoint_excepted)
    
