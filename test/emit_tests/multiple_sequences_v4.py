# Waldo emitted file


def SideA (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SideA (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,print_debug_):

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
                '0__print_debug',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '0__print_debug', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)


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
                _to_return = self._onCreate(_root_event,_ctx ,print_debug_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done

                    # local endpoint's initialization has succeeded, tell other side that
                    # we're done initializing.
                    self._this_side_ready()

                    return _to_return

                
            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        def _onCreate(self,_active_event,_context,print_debug_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                print_debug_ = _context.func_turn_into_waldo_var(print_debug_,True,_active_event,self._host_uuid,False,[])

                pass

            else:
                print_debug_ = _context.func_turn_into_waldo_var(print_debug_,True,_active_event,self._host_uuid,False,[])

                pass

            _tmp0 = print_debug_
            if not _context.assign(_context.global_store.get_var_if_exists("0__print_debug"),_tmp0,_active_event):
                pass

        ### USER DEFINED METHODS ###

        def test_two_sequences(self,seq_one_txt,seq_two_txt):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_two_sequences(_root_event,_ctx ,seq_one_txt,seq_two_txt,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_two_sequences(self,_active_event,_context,seq_one_txt,seq_two_txt,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                seq_one_txt = _context.turn_into_waldo_var_if_was_var(seq_one_txt,True,_active_event,self._host_uuid,False)
                seq_two_txt = _context.turn_into_waldo_var_if_was_var(seq_two_txt,True,_active_event,self._host_uuid,False)

                pass

            else:
                seq_one_txt = _context.turn_into_waldo_var_if_was_var(seq_one_txt,True,_active_event,self._host_uuid,False)
                seq_two_txt = _context.turn_into_waldo_var_if_was_var(seq_two_txt,True,_active_event,self._host_uuid,False)

                pass

            return1 = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '4__return1', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo((self._partner_endpoint_msg_func_call_prefix__waldo__start_seq_a(_active_event,_context,seq_one_txt,) if _context.set_msg_send_initialized_bit_false() else None),_active_event)
            )

            return2 = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '6__return2', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo((self._partner_endpoint_msg_func_call_prefix__waldo__start_seq_b(_active_event,_context,seq_two_txt,) if _context.set_msg_send_initialized_bit_false() else None),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(return1 if 0 in _returning_to_public_ext_array else _context.de_waldoify(return1,_active_event),return2 if 1 in _returning_to_public_ext_array else _context.de_waldoify(return2,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(return1,return2)



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__start_seq_a(self,_active_event,_context,input_txt=None,_returning_to_public_ext_array=None):

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
                        "12__input_txt", _context.convert_for_seq_local(input_txt,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "12__input_txt", _context.convert_for_seq_local(input_txt,_active_event,self._host_uuid)
                    )

                    pass

                output_txt = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                    '13__output_txt', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "13__output_txt",_context.convert_for_seq_local(output_txt,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_seq_a',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("13__output_txt")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_seq_b(self,_active_event,_context,input_txt=None,_returning_to_public_ext_array=None):

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
                        "16__input_txt", _context.convert_for_seq_local(input_txt,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "16__input_txt", _context.convert_for_seq_local(input_txt,_active_event,self._host_uuid)
                    )

                    pass

                output_txt = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                    '17__output_txt', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "17__output_txt",_context.convert_for_seq_local(output_txt,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_seq_b',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("17__output_txt")

        ### User-defined message receive blocks ###

    return _SideA(_waldo_classes,_host_uuid,_conn_obj,*args)
def SideB (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SideB (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,print_debug_):

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
                '9__print_debug',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '9__print_debug', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)


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
                _to_return = self._onCreate(_root_event,_ctx ,print_debug_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done

                    # local endpoint's initialization has succeeded, tell other side that
                    # we're done initializing.
                    self._this_side_ready()

                    return _to_return

                
            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        def _onCreate(self,_active_event,_context,print_debug_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                print_debug_ = _context.func_turn_into_waldo_var(print_debug_,True,_active_event,self._host_uuid,False,[])

                pass

            else:
                print_debug_ = _context.func_turn_into_waldo_var(print_debug_,True,_active_event,self._host_uuid,False,[])

                pass

            _tmp0 = print_debug_
            if not _context.assign(_context.global_store.get_var_if_exists("9__print_debug"),_tmp0,_active_event):
                pass

        ### USER DEFINED METHODS ###
        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__recv_seq_a(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.sequence_local_store.get_var_if_exists("12__input_txt")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("13__output_txt"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__recv_seq_b(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.sequence_local_store.get_var_if_exists("16__input_txt")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("17__output_txt"),_tmp0,_active_event):
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
