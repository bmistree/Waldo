# Waldo emitted file


def SideA (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SideA (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj):

            # a little ugly in that need to pre-initialize _host_uuid, because
            # code used for initializing variable store may rely on it.  (Eg., if
            # initializing nested lists.)
            self._waldo_classes = _waldo_classes
            self._host_uuid = _host_uuid
            self._global_var_store = self._waldo_classes["VariableStore"](_host_uuid)
            _active_event = None
            _context = self._waldo_classes["ExecutingEventContext"](
                self._global_var_store,
                # not using sequence local store
                self._waldo_classes["VariableStore"](_host_uuid))

            self._global_var_store.add_var(
                '0__num',self._waldo_classes["WaldoExtNumVariable"](  # the type of waldo variable to create
                '0__num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def load_ext_num(self,to_load):

            # ensure that both sides have completed their onCreate calls
            # before continuing
            self._block_ready()

            while True:  # FIXME: currently using infinite retry 
                _root_event = self._act_event_map.create_root_event()
                _ctx = self._waldo_classes["ExecutingEventContext"](
                    self._global_var_store,
                    # not using sequence local store
                    self._waldo_classes["VariableStore"](self._host_uuid))

                # call internal function... note True as last param tells internal
                # version of function that it needs to de-waldo-ify all return
                # arguments (while inside transaction) so that this method may
                # return them....if it were false, might just get back refrences
                # to Waldo variables, and de-waldo-ifying them outside of the
                # transaction might return over-written/inconsistent values.
                _to_return = self._endpoint_func_call_prefix__waldo__load_ext_num(_root_event,_ctx ,to_load,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__load_ext_num(self,_active_event,_context,to_load,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_load = _context.turn_into_waldo_var_if_was_var(to_load,False,_active_event,self._host_uuid,False)

                pass

            else:
                to_load = _context.turn_into_waldo_var_if_was_var(to_load,False,_active_event,self._host_uuid,False)

                pass

            _context.global_store.get_var_if_exists("0__num").write_val(_active_event,to_load.get_val(_active_event))
            self._endpoint_func_call_prefix__waldo__something(_active_event,_context,_context.global_store.get_var_if_exists("0__num"),)


        def test_seq_arg(self,amt_to_increment):

            # ensure that both sides have completed their onCreate calls
            # before continuing
            self._block_ready()

            while True:  # FIXME: currently using infinite retry 
                _root_event = self._act_event_map.create_root_event()
                _ctx = self._waldo_classes["ExecutingEventContext"](
                    self._global_var_store,
                    # not using sequence local store
                    self._waldo_classes["VariableStore"](self._host_uuid))

                # call internal function... note True as last param tells internal
                # version of function that it needs to de-waldo-ify all return
                # arguments (while inside transaction) so that this method may
                # return them....if it were false, might just get back refrences
                # to Waldo variables, and de-waldo-ifying them outside of the
                # transaction might return over-written/inconsistent values.
                _to_return = self._endpoint_func_call_prefix__waldo__test_seq_arg(_root_event,_ctx ,amt_to_increment,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_seq_arg(self,_active_event,_context,amt_to_increment,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                amt_to_increment = _context.turn_into_waldo_var_if_was_var(amt_to_increment,True,_active_event,self._host_uuid,False)

                pass

            else:
                amt_to_increment = _context.turn_into_waldo_var_if_was_var(amt_to_increment,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__arguments_check_exchange(_active_event,_context,_context.global_store.get_var_if_exists("0__num"),amt_to_increment,) if _context.set_msg_send_initialized_bit_false() else None) if 0 in _returning_to_public_ext_array else _context.de_waldoify((self._partner_endpoint_msg_func_call_prefix__waldo__arguments_check_exchange(_active_event,_context,_context.global_store.get_var_if_exists("0__num"),amt_to_increment,) if _context.set_msg_send_initialized_bit_false() else None),_active_event),_context.global_store.get_var_if_exists("0__num") if 1 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__arguments_check_exchange(_active_event,_context,_context.global_store.get_var_if_exists("0__num"),amt_to_increment,) if _context.set_msg_send_initialized_bit_false() else None),_context.global_store.get_var_if_exists("0__num"))




        def something(self,a):

            # ensure that both sides have completed their onCreate calls
            # before continuing
            self._block_ready()

            while True:  # FIXME: currently using infinite retry 
                _root_event = self._act_event_map.create_root_event()
                _ctx = self._waldo_classes["ExecutingEventContext"](
                    self._global_var_store,
                    # not using sequence local store
                    self._waldo_classes["VariableStore"](self._host_uuid))

                # call internal function... note True as last param tells internal
                # version of function that it needs to de-waldo-ify all return
                # arguments (while inside transaction) so that this method may
                # return them....if it were false, might just get back refrences
                # to Waldo variables, and de-waldo-ifying them outside of the
                # transaction might return over-written/inconsistent values.
                _to_return = self._endpoint_func_call_prefix__waldo__something(_root_event,_ctx ,a,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__something(self,_active_event,_context,a,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False)

                pass

            else:
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False)

                pass


        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__arguments_check_exchange(self,_active_event,_context,some_number=None,amt_to_increment=None,_returning_to_public_ext_array=None):

            _first_msg = False
            if not _context.set_msg_send_initialized_bit_true():
                # we must load all arguments into sequence local data and perform
                # initialization on sequence local data....start by loading
                # arguments into sequence local data
                # below tells the message send that it must serialize and
                # send all sequence local data.
                _first_msg = True
                if _context.check_and_set_from_endpoint_call_false():

                    _context.sequence_local_store.add_var(
                        "9__some_number", _context.convert_for_seq_local(some_number,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "10__amt_to_increment", _context.convert_for_seq_local(amt_to_increment,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "9__some_number", _context.convert_for_seq_local(some_number,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "10__amt_to_increment", _context.convert_for_seq_local(amt_to_increment,_active_event,self._host_uuid)
                    )

                    pass

                to_return = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '11__to_return', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "11__to_return",_context.convert_for_seq_local(to_return,_active_event,self._host_uuid))

                pass

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("9__some_number"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("10__amt_to_increment"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("9__some_number"),_tmp0,_active_event):
                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_arguments_check_exchange',_threadsafe_queue, '_first_msg')
            _queue_elem = _threadsafe_queue.get()

            if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                raise self._waldo_classes["BackoutException"]()

            _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

            # apply changes to sequence variables.  (There shouldn't
            # be any, but it's worth getting in practice.)  Note: that
            # the system has already applied deltas for global data.
            _context.sequence_local_store.incorporate_deltas(
                _active_event,_queue_elem.sequence_local_var_store_deltas)

            # send more messages
            _to_exec_next = _queue_elem.to_exec_next_name_msg_field
            if _to_exec_next != None:
                # means that we do not have any additional functions to exec
                _to_exec = getattr(self,_to_exec_next)
                _to_exec(_active_event,_context)
            else:
                # end of sequence: reset to_reply_with_uuid in context.  we do
                # this so that if we go on to execute another message sequence
                # following this one, then the message sequence will be viewed as
                # a new message sequence, rather than the continuation of a
                # previous one.
                _context.reset_to_reply_with()


            return _context.sequence_local_store.get_var_if_exists("11__to_return")

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__handle_other(self,_active_event,_context,_returning_to_public_ext_array=None):

            pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out
                    raise self._waldo_classes["BackoutException"]()

                _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

                # apply changes to sequence variables.  Note: that
                # the system has already applied deltas for global data.
                _context.sequence_local_store.incorporate_deltas(
                    _active_event,_queue_elem.sequence_local_var_store_deltas)

                # send more messages
                _to_exec_next = _queue_elem.to_exec_next_name_msg_field
                if _to_exec_next != None:
                    # means that we do not have any additional functions to exec
                    _to_exec = getattr(self,_to_exec_next)
                    _to_exec(_active_event,_context)


    return _SideA(_waldo_classes,_host_uuid,_conn_obj,*args)
def SideB (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SideB (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj):

            # a little ugly in that need to pre-initialize _host_uuid, because
            # code used for initializing variable store may rely on it.  (Eg., if
            # initializing nested lists.)
            self._waldo_classes = _waldo_classes
            self._host_uuid = _host_uuid
            self._global_var_store = self._waldo_classes["VariableStore"](_host_uuid)
            _active_event = None
            _context = self._waldo_classes["ExecutingEventContext"](
                self._global_var_store,
                # not using sequence local store
                self._waldo_classes["VariableStore"](_host_uuid))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###
        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__other(self,_active_event,_context,_returning_to_public_ext_array=None):

            _first_msg = False
            if not _context.set_msg_send_initialized_bit_true():
                # we must load all arguments into sequence local data and perform
                # initialization on sequence local data....start by loading
                # arguments into sequence local data
                # below tells the message send that it must serialize and
                # send all sequence local data.
                _first_msg = True
                if _context.check_and_set_from_endpoint_call_false():

                    pass

                else:

                    pass


                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'handle_other',_threadsafe_queue, '_first_msg')
            _queue_elem = _threadsafe_queue.get()

            if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                raise self._waldo_classes["BackoutException"]()

            _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

            # apply changes to sequence variables.  (There shouldn't
            # be any, but it's worth getting in practice.)  Note: that
            # the system has already applied deltas for global data.
            _context.sequence_local_store.incorporate_deltas(
                _active_event,_queue_elem.sequence_local_var_store_deltas)

            # send more messages
            _to_exec_next = _queue_elem.to_exec_next_name_msg_field
            if _to_exec_next != None:
                # means that we do not have any additional functions to exec
                _to_exec = getattr(self,_to_exec_next)
                _to_exec(_active_event,_context)
            else:
                # end of sequence: reset to_reply_with_uuid in context.  we do
                # this so that if we go on to execute another message sequence
                # following this one, then the message sequence will be viewed as
                # a new message sequence, rather than the continuation of a
                # previous one.
                _context.reset_to_reply_with()


            return 

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__receive_arguments_check_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.sequence_local_store.get_var_if_exists("9__some_number")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("11__to_return"),_tmp0,_active_event):
                pass




            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out
                    raise self._waldo_classes["BackoutException"]()

                _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

                # apply changes to sequence variables.  Note: that
                # the system has already applied deltas for global data.
                _context.sequence_local_store.incorporate_deltas(
                    _active_event,_queue_elem.sequence_local_var_store_deltas)

                # send more messages
                _to_exec_next = _queue_elem.to_exec_next_name_msg_field
                if _to_exec_next != None:
                    # means that we do not have any additional functions to exec
                    _to_exec = getattr(self,_to_exec_next)
                    _to_exec(_active_event,_context)


    return _SideB(_waldo_classes,_host_uuid,_conn_obj,*args)
