import threading
import waldo.lib.util as util


class ThreadPool(object):
    
    def __init__(self,num_threads):

        # Each item in threadsafe queue will be a service action (ie,
        # it has a service method)
        self.work_queue = util.Queue.Queue()

        for i in range(0,num_threads):
            t = threading.Thread(target = self.thread_listen_and_wait_for_work)
            t.daemon = True
            t.start()

    def add_service_action(self,service_action):
        '''
        @param {WaldoServiceAction} service_action --- 
        '''
        self.work_queue.put(service_action)
        
            
    def thread_listen_and_wait_for_work(self):
        while True:
            service_action = self.work_queue.get()
            service_action.service()
