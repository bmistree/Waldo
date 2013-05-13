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
                '0__struct_map',self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '0__struct_map', # variable's name
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

        def input_struct_sequence(self,inc1,inc2):

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
                _to_return = self._endpoint_func_call_prefix__waldo__input_struct_sequence(_root_event,_ctx ,inc1,inc2,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__input_struct_sequence(self,_active_event,_context,inc1,inc2,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                inc1 = _context.turn_into_waldo_var_if_was_var(inc1,True,_active_event,self._host_uuid,False)
                inc2 = _context.turn_into_waldo_var_if_was_var(inc2,True,_active_event,self._host_uuid,False)

                pass

            else:
                inc1 = _context.turn_into_waldo_var_if_was_var(inc1,True,_active_event,self._host_uuid,False)
                inc2 = _context.turn_into_waldo_var_if_was_var(inc2,True,_active_event,self._host_uuid,False)

                pass

            ss = self._waldo_classes["WaldoUserStructVariable"]("3__ss",self._host_uuid,False,{"a": 0, })

            _tmp0 = (self._partner_endpoint_msg_func_call_prefix__waldo__start_input_struct(_active_event,_context,ss,inc1,inc2,) if _context.set_msg_send_initialized_bit_false() else None)
            if not _context.assign(ss,_tmp0,_active_event):
                ss = _tmp0


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(ss.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def get_struct(self,init_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_struct(_root_event,_ctx ,init_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_struct(self,_active_event,_context,init_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            s_struct = self._waldo_classes["WaldoUserStructVariable"]("7__s_struct",self._host_uuid,False,{"a": 0, })

            _tmp0 = init_val
            _context.assign_on_key(s_struct,"a",_tmp0, _active_event)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(s_struct if 0 in _returning_to_public_ext_array else _context.de_waldoify(s_struct,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(s_struct)




        def get_struct_from_other_side(self,other_side,init_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_struct_from_other_side(_root_event,_ctx ,other_side,init_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_struct_from_other_side(self,_active_event,_context,other_side,init_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                other_side = _context.turn_into_waldo_var_if_was_var(other_side,True,_active_event,self._host_uuid,False)
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                other_side = _context.turn_into_waldo_var_if_was_var(other_side,True,_active_event,self._host_uuid,False)
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            weirdly_named = _context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(other_side,_active_event),"get_struct",init_val,)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(weirdly_named.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(weirdly_named.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(weirdly_named.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def get_partner_struct(self,init_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_partner_struct(_root_event,_ctx ,init_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_partner_struct(self,_active_event,_context,init_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            s_struct = (self._partner_endpoint_msg_func_call_prefix__waldo__start_test(_active_event,_context,init_val,) if _context.set_msg_send_initialized_bit_false() else None)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(s_struct.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(s_struct.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(s_struct.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def test_struct_map(self,index,num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_struct_map(_root_event,_ctx ,index,num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_struct_map(self,_active_event,_context,index,num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                num = _context.turn_into_waldo_var_if_was_var(num,True,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                num = _context.turn_into_waldo_var_if_was_var(num,True,_active_event,self._host_uuid,False)

                pass

            ss = (self._partner_endpoint_msg_func_call_prefix__waldo__start_test(_active_event,_context,(_context.get_val_if_waldo(num,_active_event) + _context.get_val_if_waldo(23 ,_active_event)),) if _context.set_msg_send_initialized_bit_false() else None)

            _tmp0 = ss
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__struct_map"),index,_tmp0, _active_event)

            (_context.get_val_if_waldo(0 ,_active_event) + _context.get_val_if_waldo(4 ,_active_event))
            _tmp0 = num
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__struct_map").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),"a",_tmp0, _active_event)

            (_context.get_val_if_waldo(1 ,_active_event) + _context.get_val_if_waldo(2 ,_active_event))
            _tmp0 = _context.global_store.get_var_if_exists("0__struct_map").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event))
            if not _context.assign(ss,_tmp0,_active_event):
                ss = _tmp0

            (_context.get_val_if_waldo(3 ,_active_event) + _context.get_val_if_waldo(6 ,_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(ss.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def test_sequence_struct_map(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_sequence_struct_map(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_sequence_struct_map(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            ss = self._waldo_classes["WaldoUserStructVariable"]("22__ss",self._host_uuid,False,{"a": 0, })

            _tmp0 = 390 
            _context.assign_on_key(ss,"a",_tmp0, _active_event)

            mapper = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '23__mapper', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = ss
            _context.assign_on_key(mapper,'hi' ,_tmp0, _active_event)

            (self._partner_endpoint_msg_func_call_prefix__waldo__start_map_of_structs(_active_event,_context,mapper,'wow' ,) if _context.set_msg_send_initialized_bit_false() else None)

        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__start_test(self,_active_event,_context,num_to_load=None,_returning_to_public_ext_array=None):

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
                        "51__num_to_load", _context.convert_for_seq_local(num_to_load,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "51__num_to_load", _context.convert_for_seq_local(num_to_load,_active_event,self._host_uuid)
                    )

                    pass

                to_return = self._waldo_classes["WaldoUserStructVariable"]("52__to_return",self._host_uuid,False,{"a": 0, })

                _context.sequence_local_store.add_var(
                    "52__to_return",_context.convert_for_seq_local(to_return,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_test',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("52__to_return")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_input_struct(self,_active_event,_context,input_struct=None,inc1=None,inc2=None,_returning_to_public_ext_array=None):

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
                        "56__input_struct", _context.convert_for_seq_local(input_struct,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "57__inc1", _context.convert_for_seq_local(inc1,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "58__inc2", _context.convert_for_seq_local(inc2,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "56__input_struct", _context.convert_for_seq_local(input_struct,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "57__inc1", _context.convert_for_seq_local(inc1,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "58__inc2", _context.convert_for_seq_local(inc2,_active_event,self._host_uuid)
                    )

                    pass

                to_return = self._waldo_classes["WaldoUserStructVariable"]("59__to_return",self._host_uuid,False,{"a": 0, })

                _context.sequence_local_store.add_var(
                    "59__to_return",_context.convert_for_seq_local(to_return,_active_event,self._host_uuid))

                pass

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("56__input_struct").get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("57__inc1"),_active_event))
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("56__input_struct"),"a",_tmp0, _active_event)



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_input_struct',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("59__to_return")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_map_of_structs(self,_active_event,_context,mapper=None,index_to_insert=None,_returning_to_public_ext_array=None):

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
                        "62__mapper", _context.convert_for_seq_local(mapper,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "63__index_to_insert", _context.convert_for_seq_local(index_to_insert,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "62__mapper", _context.convert_for_seq_local(mapper,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "63__index_to_insert", _context.convert_for_seq_local(index_to_insert,_active_event,self._host_uuid)
                    )

                    pass

                returner = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                    '64__returner', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "64__returner",_context.convert_for_seq_local(returner,_active_event,self._host_uuid))

                pass

            strangely_named_struct = self._waldo_classes["WaldoUserStructVariable"]("65__strangely_named_struct",self._host_uuid,False,{"a": 0, })

            _tmp0 = strangely_named_struct
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("62__mapper"),_context.sequence_local_store.get_var_if_exists("63__index_to_insert"),_tmp0, _active_event)



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_map_of_structs',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("64__returner")

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__recv_test(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = self._endpoint_func_call_prefix__waldo__get_struct(_active_event,_context,_context.sequence_local_store.get_var_if_exists("68__num_to_load"),)
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("69__to_return"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__recv_input_struct(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("73__input_struct").get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("75__inc2"),_active_event))
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("73__input_struct"),"a",_tmp0, _active_event)

            _tmp0 = _context.sequence_local_store.get_var_if_exists("73__input_struct")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("76__to_return"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__recv_map_of_structs(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.sequence_local_store.get_var_if_exists("79__mapper")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("81__returner"),_tmp0,_active_event):
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

            self._global_var_store.add_var(
                '25__struct_map',self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '25__struct_map', # variable's name
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

        def input_struct_sequence(self,inc1,inc2):

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
                _to_return = self._endpoint_func_call_prefix__waldo__input_struct_sequence(_root_event,_ctx ,inc1,inc2,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__input_struct_sequence(self,_active_event,_context,inc1,inc2,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                inc1 = _context.turn_into_waldo_var_if_was_var(inc1,True,_active_event,self._host_uuid,False)
                inc2 = _context.turn_into_waldo_var_if_was_var(inc2,True,_active_event,self._host_uuid,False)

                pass

            else:
                inc1 = _context.turn_into_waldo_var_if_was_var(inc1,True,_active_event,self._host_uuid,False)
                inc2 = _context.turn_into_waldo_var_if_was_var(inc2,True,_active_event,self._host_uuid,False)

                pass

            ss = self._waldo_classes["WaldoUserStructVariable"]("28__ss",self._host_uuid,False,{"a": 0, })

            _tmp0 = (self._partner_endpoint_msg_func_call_prefix__waldo__start_input_struct(_active_event,_context,ss,inc1,inc2,) if _context.set_msg_send_initialized_bit_false() else None)
            if not _context.assign(ss,_tmp0,_active_event):
                ss = _tmp0


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(ss.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def get_struct(self,init_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_struct(_root_event,_ctx ,init_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_struct(self,_active_event,_context,init_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            s_struct = self._waldo_classes["WaldoUserStructVariable"]("32__s_struct",self._host_uuid,False,{"a": 0, })

            _tmp0 = init_val
            _context.assign_on_key(s_struct,"a",_tmp0, _active_event)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(s_struct if 0 in _returning_to_public_ext_array else _context.de_waldoify(s_struct,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(s_struct)




        def get_struct_from_other_side(self,other_side,init_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_struct_from_other_side(_root_event,_ctx ,other_side,init_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_struct_from_other_side(self,_active_event,_context,other_side,init_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                other_side = _context.turn_into_waldo_var_if_was_var(other_side,True,_active_event,self._host_uuid,False)
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                other_side = _context.turn_into_waldo_var_if_was_var(other_side,True,_active_event,self._host_uuid,False)
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            weirdly_named = _context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(other_side,_active_event),"get_struct",init_val,)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(weirdly_named.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(weirdly_named.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(weirdly_named.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def get_partner_struct(self,init_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_partner_struct(_root_event,_ctx ,init_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_partner_struct(self,_active_event,_context,init_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                init_val = _context.turn_into_waldo_var_if_was_var(init_val,True,_active_event,self._host_uuid,False)

                pass

            s_struct = (self._partner_endpoint_msg_func_call_prefix__waldo__start_test(_active_event,_context,init_val,) if _context.set_msg_send_initialized_bit_false() else None)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(s_struct.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(s_struct.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(s_struct.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def test_struct_map(self,index,num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_struct_map(_root_event,_ctx ,index,num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_struct_map(self,_active_event,_context,index,num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                num = _context.turn_into_waldo_var_if_was_var(num,True,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                num = _context.turn_into_waldo_var_if_was_var(num,True,_active_event,self._host_uuid,False)

                pass

            ss = (self._partner_endpoint_msg_func_call_prefix__waldo__start_test(_active_event,_context,(_context.get_val_if_waldo(num,_active_event) + _context.get_val_if_waldo(23 ,_active_event)),) if _context.set_msg_send_initialized_bit_false() else None)

            _tmp0 = ss
            _context.assign_on_key(_context.global_store.get_var_if_exists("25__struct_map"),index,_tmp0, _active_event)

            (_context.get_val_if_waldo(0 ,_active_event) + _context.get_val_if_waldo(4 ,_active_event))
            _tmp0 = num
            _context.assign_on_key(_context.global_store.get_var_if_exists("25__struct_map").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),"a",_tmp0, _active_event)

            (_context.get_val_if_waldo(1 ,_active_event) + _context.get_val_if_waldo(2 ,_active_event))
            _tmp0 = _context.global_store.get_var_if_exists("25__struct_map").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event))
            if not _context.assign(ss,_tmp0,_active_event):
                ss = _tmp0

            (_context.get_val_if_waldo(3 ,_active_event) + _context.get_val_if_waldo(6 ,_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a") if 0 in _returning_to_public_ext_array else _context.de_waldoify(ss.get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(ss.get_val(_active_event).get_val_on_key(_active_event,"a"))




        def test_sequence_struct_map(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_sequence_struct_map(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_sequence_struct_map(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            ss = self._waldo_classes["WaldoUserStructVariable"]("47__ss",self._host_uuid,False,{"a": 0, })

            _tmp0 = 390 
            _context.assign_on_key(ss,"a",_tmp0, _active_event)

            mapper = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '48__mapper', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = ss
            _context.assign_on_key(mapper,'hi' ,_tmp0, _active_event)

            (self._partner_endpoint_msg_func_call_prefix__waldo__start_map_of_structs(_active_event,_context,mapper,'wow' ,) if _context.set_msg_send_initialized_bit_false() else None)

        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__start_test(self,_active_event,_context,num_to_load=None,_returning_to_public_ext_array=None):

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
                        "68__num_to_load", _context.convert_for_seq_local(num_to_load,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "68__num_to_load", _context.convert_for_seq_local(num_to_load,_active_event,self._host_uuid)
                    )

                    pass

                to_return = self._waldo_classes["WaldoUserStructVariable"]("69__to_return",self._host_uuid,False,{"a": 0, })

                _context.sequence_local_store.add_var(
                    "69__to_return",_context.convert_for_seq_local(to_return,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_test',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("69__to_return")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_input_struct(self,_active_event,_context,input_struct=None,inc1=None,inc2=None,_returning_to_public_ext_array=None):

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
                        "73__input_struct", _context.convert_for_seq_local(input_struct,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "74__inc1", _context.convert_for_seq_local(inc1,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "75__inc2", _context.convert_for_seq_local(inc2,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "73__input_struct", _context.convert_for_seq_local(input_struct,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "74__inc1", _context.convert_for_seq_local(inc1,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "75__inc2", _context.convert_for_seq_local(inc2,_active_event,self._host_uuid)
                    )

                    pass

                to_return = self._waldo_classes["WaldoUserStructVariable"]("76__to_return",self._host_uuid,False,{"a": 0, })

                _context.sequence_local_store.add_var(
                    "76__to_return",_context.convert_for_seq_local(to_return,_active_event,self._host_uuid))

                pass

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("73__input_struct").get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("74__inc1"),_active_event))
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("73__input_struct"),"a",_tmp0, _active_event)



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_input_struct',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("76__to_return")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_map_of_structs(self,_active_event,_context,mapper=None,index_to_insert=None,_returning_to_public_ext_array=None):

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
                        "79__mapper", _context.convert_for_seq_local(mapper,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "80__index_to_insert", _context.convert_for_seq_local(index_to_insert,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "79__mapper", _context.convert_for_seq_local(mapper,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "80__index_to_insert", _context.convert_for_seq_local(index_to_insert,_active_event,self._host_uuid)
                    )

                    pass

                returner = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                    '81__returner', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "81__returner",_context.convert_for_seq_local(returner,_active_event,self._host_uuid))

                pass

            strangely_named_struct = self._waldo_classes["WaldoUserStructVariable"]("82__strangely_named_struct",self._host_uuid,False,{"a": 0, })

            _tmp0 = strangely_named_struct
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("79__mapper"),_context.sequence_local_store.get_var_if_exists("80__index_to_insert"),_tmp0, _active_event)



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'recv_map_of_structs',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("81__returner")

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__recv_test(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = self._endpoint_func_call_prefix__waldo__get_struct(_active_event,_context,_context.sequence_local_store.get_var_if_exists("51__num_to_load"),)
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("52__to_return"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__recv_input_struct(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("56__input_struct").get_val(_active_event).get_val_on_key(_active_event,"a"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("58__inc2"),_active_event))
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("56__input_struct"),"a",_tmp0, _active_event)

            _tmp0 = _context.sequence_local_store.get_var_if_exists("56__input_struct")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("59__to_return"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__recv_map_of_structs(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.sequence_local_store.get_var_if_exists("62__mapper")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("64__returner"),_tmp0,_active_event):
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
