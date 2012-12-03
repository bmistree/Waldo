#!/usr/bin/env python

import socket
from connectionObject import ConnectionObject

# import json

import pickle
import threading
import inspect


class TCPFireEvent(threading.Thread):
    '''
    Used to call msgReceive on endpoint from a separate thread
    whenever we have received enough incoming data
    '''
    def __init__(self,tcp_conn_obj, msg_dict):
        '''
        @param{TCPConnectionObject} tcp_conn_obj --- Should already
        have a valid local_endpoint
        '''
        self.tcp_conn_obj = tcp_conn_obj
        self.msg_dict = msg_dict
        threading.Thread.__init__(self)
        
    def run(self):
        local_endpoint = self.tcp_conn_obj.local_endpoint
        #### DEBUG
        if local_endpoint == None:
            assert(False)
        #### END DEBUG
            
        # actually handle message receive
        local_endpoint._msgReceive(self.msg_dict)


class TCPListeningThread(threading.Thread):
    '''
    Just starts the "_start_listening_loop" on the
    tcp_connection_object.  Whenever this loop receives sufficient
    data, it spins off another thread TCPFireEvent, which calls
    msg_receive on connection's local endpoint
    '''
    def __init__(self,tcp_connection_object):
        self.tcp_connection_object = tcp_connection_object
        threading.Thread.__init__(self)
        self.setDaemon(True)
        
    def run(self):
        self.tcp_connection_object._start_listening_loop()
        

class TCPConnectionObject(ConnectionObject):
    MSG_HEADER = 'a'
    MSG_FOOTER = 'b'
    
    def __init__(self,dst_host,dst_port,sock=None):
        '''
        @param {
        Either pass in the 
        '''
        
        if sock == None:
            # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            # self.sock.connect((dst_host,dst_port))
            
            self.sock = socket.create_connection((dst_host,dst_port))
            # self.sock = socket.create_connection((dst_host,80))            
        else:
            self.sock = sock


        self.received_data = ''
        self.local_endpoint = None

    @staticmethod
    def accept(host_listen_on,port_listen_on,cb,
               endpoint_constructor,reservation_manager,waldo_id,
               endpoint_id_generator,*args):
        '''
        @param{String} host_listen_on --- The ip/host to listen for
        new connections on.

        @param{int} port_listen_on --- The prot to listen for new
        connections on.

        @param{function}endpoint_constructor --- An _Endpoint object's
        constructor.  It takes in a tcp connection object, reservation
        manager object, and any additional arguments specified in its
        oncreate method.

        @param{ReservationManager object} reservation_manager --- Gets
        passed in to endpoint's constructor.

        @param{float} waldo_id ---

        @param{function: in: ; returns: float) endpoint_id_generator
        --- Calling this generates a unique id.  Each created endpoint
        should have one.
        
        @param{*args} --- Any other arguments to pass into the
        oncreate argument of the endpoint constructor.

        When receive a new connection, execute the callback, passing
        in a new Endpoint object in its callback.

        This function does not return.
        '''
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind((host_listen_on, port_listen_on))
        sock.listen(1)
        while True:
            conn, addr = sock.accept()
            tcp_conn_obj = TCPConnectionObject(None,None,conn)

            created_endpoint = endpoint_constructor(
                tcp_conn_obj,reservation_manager,waldo_id,
                endpoint_id_generator(),*args)

            if cb != None:
                cb(created_endpoint)

        
    def addEndpoint(self,local_endpoint):
        '''
        @param {_Endpoint object} local_endpoint --- @see the emitted
        code for a list of _Endpoint object methods.  Importantly,
        we're most concerned about _msgReceive, which the connection
        object automatically calls whenever it has data to send to the
        other side.

        Once we have an attached endpoint, we start listening for data
        to send to that endpoint.
        '''
        self.local_endpoint = local_endpoint
        listening_thread = TCPListeningThread(self)
        listening_thread.start()

    def _start_listening_loop(self):
        while 1:
            data = self.sock.recv(1024)
            self.received_data += data
            self._decapsulate_msg_and_dispatch()


    def _convert_string_remove_funcs(self,dict_to_convert):
        '''
        @param {dict} dict_to_convert
        '''
        # FIXME: hard coded context field name

        seq_field = None
        old_seq_dict = None
        if 'context' in dict_to_convert:

            new_seq_dict = {}
            seq_field = dict_to_convert['context']['seqGlobals']
            
            for key in seq_field:
                # trying to filter out functions
                item = seq_field[key]
                if not inspect.isroutine(item):
                    new_seq_dict[key] = item

            old_seq_dict = seq_field

            dict_to_convert['context']['seqGlobals'] = new_seq_dict

        to_return = pickle.dumps(dict_to_convert)
        # to_return =  json.dumps(dict_to_convert)

        if old_seq_dict != None:
            dict_to_convert['context']['seqGlobals'] = old_seq_dict
        
        return to_return
        
        
            
    def _encapsulate_msg(self,dict_to_write):
        str_to_escape = self._convert_string_remove_funcs(dict_to_write)
        to_return = str_to_escape.replace(
            self.MSG_HEADER,self.MSG_HEADER+self.MSG_HEADER)

        to_return = to_return.replace(
            self.MSG_FOOTER,self.MSG_FOOTER + self.MSG_FOOTER)

        return self.MSG_HEADER + to_return + self.MSG_FOOTER

    def _decapsulate_msg_and_dispatch(self):
        '''
        Checks received_data field of TCPConnectionObject, which keeps
        track of all the data that has arrived over the network, but
        isn't a complete packet.  This is the format of received_data
        A message should just be a string-ified json object that has
        exactly one MSG_HEADER character to delimit its beginning and
        exactly one MSG_FOOTER character to delimit its ending.  All
        MSG_HEADER and MSG_FOOTER characters that are not delmiters in
        the stringified json object are guaranteed to occur in pairs.
        Ie, for MSG_HEADER and MSG_FOOTER pairs in the json string,
        each time I see a pair of MSG_HEADERs or MSG_FOOTERs,
        transform that pair into a single MSG_FOOTER or MSG_HEADER.

        When receive a full message, fire callback into endpoint code
        to handle the message.
        
        @returns {Nothing} 
        '''
        
        header_index = self.received_data.find(self.MSG_HEADER)
        if header_index == -1:
            return 
        if header_index + 1 >= len(self.received_data):
            return 

        ####DEBUG
        if self.received_data[header_index + 1] == self.MSG_HEADER:
            # the first time we encountered msg header, we followed it
            # with another msg header.  this shouldn't happen.  the
            # first time we see a header should be at the beginning of
            # a string.
            assert(False)
        #### END DEBUG

            
        footer_to_search_from = header_index
        while True:
            footer_index = self.received_data.find(self.MSG_FOOTER,
                                                   footer_to_search_from)

            if footer_index == -1:
                return

            potential_str = self.received_data[header_index+1:footer_index]
            try:
                potential_str = potential_str.replace(
                    self.MSG_HEADER+self.MSG_HEADER, self.MSG_HEADER)
                potential_str = potential_str.replace(
                    self.MSG_FOOTER+self.MSG_FOOTER, self.MSG_FOOTER)

                # dispatch to endpoint
                # decapsulated_msg_dict = json.loads(potential_str)
                decapsulated_msg_dict = pickle.loads(potential_str)
                tcp_fire_event = TCPFireEvent(self,decapsulated_msg_dict)
                tcp_fire_event.start()

                # recurse in case received two messages worth of
                # information simultaneously.
                self.received_data = self.received_data[footer_index+1:]                
                self._decapsulate_msg_and_dispatch()
                return

            except Exception as inst:
                # FIXME: this try catch loop might be overly-expensive for decoding.
                footer_to_search_from = footer_index + 1

    
    def writeMsg(self,dict_to_write,sender_endpoint_obj):
        '''
        Gets called from endpoint to send message from one side to the
        other.
        '''
        msg_to_send = self._encapsulate_msg(dict_to_write)
        self.sock.send(msg_to_send)

    def ready(self):
        # FIXME: need to actually wait until this is ready.
        return True 
        

