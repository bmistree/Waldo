import util
import Queue
import threading

class _WaldoConnectionObject(object):

    def register_endpoint(self,endpoint):
        util.logger_assert(
            'Error register_endpoint in _WaldoConnectionObject ' +
            'is pure virtual')
    
    def write(self,string_to_write,endpoint_writing):
        util.logger_assert(
            'Error write in _WaldoConnectionObject is pure ' +
            'virtual.')

class _WaldoSingleSideConnectionObject(_WaldoConnectionObject):

    def __init__(self):
        self.endpoint = None
    
    def register_endpoint(self,endpoint):
        self.endpoint = endpoint

        # force a message to other side that fakes saying that the
        # other side's onCreate has completed
        self.endpoint._receive_partner_ready()

    def write(self,to_write,endpoint_writing):
        pass

    
class _WaldoSameHostConnectionObject(_WaldoConnectionObject,threading.Thread):
    def __init__(self):
        self.queue = Queue.Queue()

        self.endpoint_mutex = threading.Lock()
        self.endpoint1 = None
        self.endpoint2 = None

        threading.Thread.__init__(self)
        self.daemon = True

    def register_endpoint (self, endpoint):
        self.endpoint_mutex.acquire()
        if self.endpoint1 == None:
            self.endpoint1 = endpoint
        else:
            self.endpoint2 = endpoint
            self.endpoint1._set_partner_uuid(
                self.endpoint2._uuid)
            self.endpoint2._set_partner_uuid(
                self.endpoint1._uuid)

            self.start()

        self.endpoint_mutex.release()
            

    def write(self,msg,endpoint):
        self.queue.put((msg,endpoint))

    def run(self):
        while True:
            msg,msg_sender_endpt = self.queue.get()
            msg_recvr_endpt = self.endpoint1
            if msg_sender_endpt == self.endpoint1:
                msg_recvr_endpt = self.endpoint2

            msg_recvr_endpt._receive_msg_from_partner(msg)
                


    
