import threading

class AllEndpoints(object):

    def __init__(self):
        self._mutex = threading.Lock()
        self.endpoint_map = {}

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
        for endpt in copied_endpoint_map.values():
            endpt._send_clock_update()
            
            
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
    
