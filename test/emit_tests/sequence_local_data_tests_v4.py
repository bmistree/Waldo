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
                '3__endpoint_text',self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '3__endpoint_text', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo('sideA' ,_active_event)
            ))

            self._global_var_store.add_var(
                '0__peered_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '0__peered_num', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(22 ,_active_event)
            ))

            self._global_var_store.add_var(
                '1__peered_text',self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '1__peered_text', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                _context.get_val_if_waldo('a' ,_active_event)
            ))

            self._global_var_store.add_var(
                '2__peered_tf',self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                '2__peered_tf', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(True ,_active_event)
            ))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def read_peered_value_types(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__read_peered_value_types(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__read_peered_value_types(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__peered_num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__peered_num"),_active_event),_context.global_store.get_var_if_exists("1__peered_text") if 1 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__peered_text"),_active_event),_context.global_store.get_var_if_exists("2__peered_tf") if 2 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("2__peered_tf"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__peered_num"),_context.global_store.get_var_if_exists("1__peered_text"),_context.global_store.get_var_if_exists("2__peered_tf"))




        def arguments_check(self,arg_num,arg_text,arg_tf):

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
                _to_return = self._endpoint_func_call_prefix__waldo__arguments_check(_root_event,_ctx ,arg_num,arg_text,arg_tf,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__arguments_check(self,_active_event,_context,arg_num,arg_text,arg_tf,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                arg_num = _context.turn_into_waldo_var_if_was_var(arg_num,True,_active_event,self._host_uuid,False)
                arg_text = _context.turn_into_waldo_var_if_was_var(arg_text,True,_active_event,self._host_uuid,False)
                arg_tf = _context.turn_into_waldo_var_if_was_var(arg_tf,True,_active_event,self._host_uuid,False)

                pass

            else:
                arg_num = _context.turn_into_waldo_var_if_was_var(arg_num,True,_active_event,self._host_uuid,False)
                arg_text = _context.turn_into_waldo_var_if_was_var(arg_text,True,_active_event,self._host_uuid,False)
                arg_tf = _context.turn_into_waldo_var_if_was_var(arg_tf,True,_active_event,self._host_uuid,False)

                pass

            (self._partner_endpoint_msg_func_call_prefix__waldo__start_arguments_check_exchange(_active_event,_context,arg_num,arg_text,arg_tf,) if _context.set_msg_send_initialized_bit_false() else None)

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__read_peered_value_types(_active_event,_context,) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__read_peered_value_types(_active_event,_context,),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__read_peered_value_types(_active_event,_context,))




        def plus_equals_on_map_check(self,map_,to_increment_by):

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
                _to_return = self._endpoint_func_call_prefix__waldo__plus_equals_on_map_check(_root_event,_ctx ,map_,to_increment_by,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__plus_equals_on_map_check(self,_active_event,_context,map_,to_increment_by,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                map_ = _context.turn_into_waldo_var_if_was_var(map_,True,_active_event,self._host_uuid,False)
                to_increment_by = _context.turn_into_waldo_var_if_was_var(to_increment_by,True,_active_event,self._host_uuid,False)

                pass

            else:
                map_ = _context.turn_into_waldo_var_if_was_var(map_,False,_active_event,self._host_uuid,False)
                to_increment_by = _context.turn_into_waldo_var_if_was_var(to_increment_by,True,_active_event,self._host_uuid,False)

                pass

            total_plus_increment = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '13__total_plus_increment', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo((self._partner_endpoint_msg_func_call_prefix__waldo__start_plus_equals_on_map_exchange(_active_event,_context,map_,to_increment_by,) if _context.set_msg_send_initialized_bit_false() else None),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(total_plus_increment if 0 in _returning_to_public_ext_array else _context.de_waldoify(total_plus_increment,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(total_plus_increment)




        def returns_check(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__returns_check(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__returns_check(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_check_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None) if 0 in _returning_to_public_ext_array else _context.de_waldoify((self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_check_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_check_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None))




        def non_arg_return_seq_local_data_check(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__non_arg_return_seq_local_data_check(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__non_arg_return_seq_local_data_check(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__start_non_arg_return_seq_local_data_check_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None) if 0 in _returning_to_public_ext_array else _context.de_waldoify((self._partner_endpoint_msg_func_call_prefix__waldo__start_non_arg_return_seq_local_data_check_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__start_non_arg_return_seq_local_data_check_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None))




        def arguments_check_references(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__arguments_check_references(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__arguments_check_references(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            map_ = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '20__map_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(3 ,_active_event): _context.get_val_if_waldo(True ,_active_event),
            _context.get_val_if_waldo(5 ,_active_event): _context.get_val_if_waldo(False ,_active_event),
            }),_active_event)
            )

            list_ = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '21__list_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                ['m' ,'n' ,'o' ,]),_active_event)
            )

            sequence_checks_passed = self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                '22__sequence_checks_passed', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo((self._partner_endpoint_msg_func_call_prefix__waldo__start_arguments_check_references_exchange(_active_event,_context,map_,list_,) if _context.set_msg_send_initialized_bit_false() else None),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(sequence_checks_passed,_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(_context.handle_len(list_,_active_event),_active_event) == _context.get_val_if_waldo(3 ,_active_event)),_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(list_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)),_active_event) == _context.get_val_if_waldo('m' ,_active_event)),_active_event) and _context.get_val_if_waldo(( not ( _context.get_val_if_waldo(_context.handle_in_check(62 ,map_,_active_event),_active_event) )),_active_event)),_active_event)),_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(sequence_checks_passed,_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(_context.handle_len(list_,_active_event),_active_event) == _context.get_val_if_waldo(3 ,_active_event)),_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(list_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)),_active_event) == _context.get_val_if_waldo('m' ,_active_event)),_active_event) and _context.get_val_if_waldo(( not ( _context.get_val_if_waldo(_context.handle_in_check(62 ,map_,_active_event),_active_event) )),_active_event)),_active_event)),_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(sequence_checks_passed,_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(_context.handle_len(list_,_active_event),_active_event) == _context.get_val_if_waldo(3 ,_active_event)),_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(list_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)),_active_event) == _context.get_val_if_waldo('m' ,_active_event)),_active_event) and _context.get_val_if_waldo(( not ( _context.get_val_if_waldo(_context.handle_in_check(62 ,map_,_active_event),_active_event) )),_active_event)),_active_event)),_active_event)))




        def returns_check_references(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__returns_check_references(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__returns_check_references(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            map_ = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '25__map_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            list_ = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '26__list_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0,_tmp1 = (self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_check_references_exchange(_active_event,_context,) if _context.set_msg_send_initialized_bit_false() else None)
            if not _context.assign(map_,_tmp0,_active_event):
                map_ = _tmp0
            if not _context.assign(list_,_tmp1,_active_event):
                list_ = _tmp1

            other_map = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '28__other_map', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            other_list = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '29__other_list', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = map_
            if not _context.assign(other_map,_tmp0,_active_event):
                other_map = _tmp0

            _tmp0 = list_
            if not _context.assign(other_list,_tmp0,_active_event):
                other_list = _tmp0

            other_list.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo('20' ,_active_event))
            if _context.get_val_if_waldo((_context.get_val_if_waldo(_context.handle_len(other_list,_active_event),_active_event) != _context.get_val_if_waldo(_context.handle_len(list_,_active_event),_active_event)),_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(False  if 0 in _returning_to_public_ext_array else _context.de_waldoify(False ,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(False )



                pass


            _tmp0 = 25 
            _context.assign_on_key(map_,3 ,_tmp0, _active_event)

            if _context.get_val_if_waldo((_context.get_val_if_waldo(other_map.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(3 ,_active_event)),_active_event) != _context.get_val_if_waldo(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(3 ,_active_event)),_active_event)),_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(False  if 0 in _returning_to_public_ext_array else _context.de_waldoify(False ,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(False )



                pass



            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(True  if 0 in _returning_to_public_ext_array else _context.de_waldoify(True ,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(True )




        def return_reference_index(self,l,index):

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
                _to_return = self._endpoint_func_call_prefix__waldo__return_reference_index(_root_event,_ctx ,l,index,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__return_reference_index(self,_active_event,_context,l,index,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                l = _context.turn_into_waldo_var_if_was_var(l,True,_active_event,self._host_uuid,False)
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)

                pass

            else:
                l = _context.turn_into_waldo_var_if_was_var(l,False,_active_event,self._host_uuid,False)
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_single_reference_exchange(_active_event,_context,l,) if _context.set_msg_send_initialized_bit_false() else None).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_single_reference_exchange(_active_event,_context,l,) if _context.set_msg_send_initialized_bit_false() else None).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__start_returns_single_reference_exchange(_active_event,_context,l,) if _context.set_msg_send_initialized_bit_false() else None).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__start_arguments_check_exchange(self,_active_event,_context,some_number=None,some_text=None,some_tf=None,_returning_to_public_ext_array=None):

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
                        "39__some_number", _context.convert_for_seq_local(some_number,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "40__some_text", _context.convert_for_seq_local(some_text,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "41__some_tf", _context.convert_for_seq_local(some_tf,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "39__some_number", _context.convert_for_seq_local(some_number,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "40__some_text", _context.convert_for_seq_local(some_text,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "41__some_tf", _context.convert_for_seq_local(some_tf,_active_event,self._host_uuid)
                    )

                    pass


                pass

            _tmp0 = (_context.get_val_if_waldo(_context.global_store.get_var_if_exists("0__peered_num"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("39__some_number"),_active_event))
            if not _context.assign(_context.global_store.get_var_if_exists("0__peered_num"),_tmp0,_active_event):
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


            return 

        def _partner_endpoint_msg_func_call_prefix__waldo__start_returns_check_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

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

                ret_num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '46__ret_num', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "46__ret_num",_context.convert_for_seq_local(ret_num,_active_event,self._host_uuid))
                ret_text = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                    '47__ret_text', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "47__ret_text",_context.convert_for_seq_local(ret_text,_active_event,self._host_uuid))
                ret_tf = self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                    '48__ret_tf', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "48__ret_tf",_context.convert_for_seq_local(ret_tf,_active_event,self._host_uuid))

                pass

            _tmp0 = True 
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("48__ret_tf"),_tmp0,_active_event):
                pass

            _tmp0 = _context.global_store.get_var_if_exists("3__endpoint_text")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("47__ret_text"),_tmp0,_active_event):
                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_returns_check_exchange',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("46__ret_num"),_context.sequence_local_store.get_var_if_exists("47__ret_text"),_context.sequence_local_store.get_var_if_exists("48__ret_tf")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_non_arg_return_seq_local_data_check_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

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

                seq_local_num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '50__seq_local_num', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    _context.get_val_if_waldo(52 ,_active_event)
                )

                _context.sequence_local_store.add_var(
                    "50__seq_local_num",_context.convert_for_seq_local(seq_local_num,_active_event,self._host_uuid))
                seq_local_text = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                    '51__seq_local_text', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    _context.get_val_if_waldo('wow' ,_active_event)
                )

                _context.sequence_local_store.add_var(
                    "51__seq_local_text",_context.convert_for_seq_local(seq_local_text,_active_event,self._host_uuid))
                ret_num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '54__ret_num', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "54__ret_num",_context.convert_for_seq_local(ret_num,_active_event,self._host_uuid))
                ret_text = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                    '55__ret_text', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "55__ret_text",_context.convert_for_seq_local(ret_text,_active_event,self._host_uuid))

                pass

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("50__seq_local_num"),_active_event) + _context.get_val_if_waldo(10 ,_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("54__ret_num"),_tmp0,_active_event):
                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_non_arg_return_seq_local_data_check_exchange',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("54__ret_num"),_context.sequence_local_store.get_var_if_exists("55__ret_text")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_arguments_check_references_exchange(self,_active_event,_context,arg_map=None,arg_list=None,_returning_to_public_ext_array=None):

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
                        "58__arg_map", _context.convert_for_seq_local(arg_map,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "59__arg_list", _context.convert_for_seq_local(arg_list,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "58__arg_map", _context.convert_for_seq_local(arg_map,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "59__arg_list", _context.convert_for_seq_local(arg_list,_active_event,self._host_uuid)
                    )

                    pass

                expected_behavior = self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                    '60__expected_behavior', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "60__expected_behavior",_context.convert_for_seq_local(expected_behavior,_active_event,self._host_uuid))

                pass

            _tmp0 = True 
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("58__arg_map"),62 ,_tmp0, _active_event)

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("59__arg_list").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)),_active_event) == _context.get_val_if_waldo('m' ,_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("60__expected_behavior"),_tmp0,_active_event):
                pass

            _tmp0 = 'n' 
            _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("59__arg_list"),0 ,_tmp0, _active_event)



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_arguments_check_references_exchange',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("60__expected_behavior")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_returns_check_references_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

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

                map_ = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                    '64__map_', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "64__map_",_context.convert_for_seq_local(map_,_active_event,self._host_uuid))
                list_ = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                    '65__list_', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "65__list_",_context.convert_for_seq_local(list_,_active_event,self._host_uuid))

                pass

            _tmp0 = self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(1 ,_active_event): _context.get_val_if_waldo(2 ,_active_event),
            _context.get_val_if_waldo(3 ,_active_event): _context.get_val_if_waldo(4 ,_active_event),
            })
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("64__map_"),_tmp0,_active_event):
                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_returns_check_references_exchange',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("64__map_"),_context.sequence_local_store.get_var_if_exists("65__list_")

        def _partner_endpoint_msg_func_call_prefix__waldo__start_returns_single_reference_exchange(self,_active_event,_context,input=None,_returning_to_public_ext_array=None):

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
                        "68__input", _context.convert_for_seq_local(input,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "68__input", _context.convert_for_seq_local(input,_active_event,self._host_uuid)
                    )

                    pass

                to_return = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                    '69__to_return', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "69__to_return",_context.convert_for_seq_local(to_return,_active_event,self._host_uuid))

                pass

            _tmp0 = _context.sequence_local_store.get_var_if_exists("68__input")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("69__to_return"),_tmp0,_active_event):
                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_returns_single_reference_exchange',_threadsafe_queue, '_first_msg')
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

        def _partner_endpoint_msg_func_call_prefix__waldo__start_plus_equals_on_map_exchange(self,_active_event,_context,map_=None,to_increment_by=None,_returning_to_public_ext_array=None):

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
                        "72__map_", _context.convert_for_seq_local(map_,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "73__to_increment_by", _context.convert_for_seq_local(to_increment_by,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "72__map_", _context.convert_for_seq_local(map_,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "73__to_increment_by", _context.convert_for_seq_local(to_increment_by,_active_event,self._host_uuid)
                    )

                    pass

                total = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '74__total', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "74__total",_context.convert_for_seq_local(total,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'receive_plus_equals_on_map_exchange',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("74__total")

        ### User-defined message receive blocks ###

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
                '37__endpoint_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '37__endpoint_num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(55 ,_active_event)
            ))

            self._global_var_store.add_var(
                '0__peered_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '0__peered_num', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(22 ,_active_event)
            ))

            self._global_var_store.add_var(
                '1__peered_text',self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '1__peered_text', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                _context.get_val_if_waldo('a' ,_active_event)
            ))

            self._global_var_store.add_var(
                '2__peered_tf',self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                '2__peered_tf', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(True ,_active_event)
            ))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def read_peered_value_types(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__read_peered_value_types(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__read_peered_value_types(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__peered_num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__peered_num"),_active_event),_context.global_store.get_var_if_exists("1__peered_text") if 1 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__peered_text"),_active_event),_context.global_store.get_var_if_exists("2__peered_tf") if 2 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("2__peered_tf"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__peered_num"),_context.global_store.get_var_if_exists("1__peered_text"),_context.global_store.get_var_if_exists("2__peered_tf"))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__receive_arguments_check_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = (_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__peered_text"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("40__some_text"),_active_event))
            if not _context.assign(_context.global_store.get_var_if_exists("1__peered_text"),_tmp0,_active_event):
                pass

            _tmp0 = _context.sequence_local_store.get_var_if_exists("41__some_tf")
            if not _context.assign(_context.global_store.get_var_if_exists("2__peered_tf"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__receive_returns_check_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.global_store.get_var_if_exists("37__endpoint_num")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("46__ret_num"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__receive_non_arg_return_seq_local_data_check_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("51__seq_local_text"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("51__seq_local_text"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("51__seq_local_text"),_tmp0,_active_event):
                pass

            _tmp0 = _context.sequence_local_store.get_var_if_exists("51__seq_local_text")
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("55__ret_text"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__receive_arguments_check_references_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            _context.sequence_local_store.get_var_if_exists("59__arg_list").get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo('50' ,_active_event))
            _tmp0 = (_context.get_val_if_waldo((_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("59__arg_list").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)),_active_event) == _context.get_val_if_waldo('n' ,_active_event)),_active_event) and _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("60__expected_behavior"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("60__expected_behavior"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__receive_returns_check_references_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                ['5' ,'7' ,'9' ,])
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("65__list_"),_tmp0,_active_event):
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


        def _partner_endpoint_msg_func_call_prefix__waldo__receive_returns_single_reference_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

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


        def _partner_endpoint_msg_func_call_prefix__waldo__receive_plus_equals_on_map_exchange(self,_active_event,_context,_returning_to_public_ext_array=None):

            index = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '76__index', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____index in _context.get_for_iter(_context.sequence_local_store.get_var_if_exists("72__map_"),_active_event):
                index.write_val(_active_event,_secret_waldo_for_iter____index)
                _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("72__map_").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("73__to_increment_by"),_active_event))
                _context.assign_on_key(_context.sequence_local_store.get_var_if_exists("72__map_"),index,_tmp0, _active_event)

                _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("74__total"),_active_event) + _context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("72__map_").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),_active_event))
                if not _context.assign(_context.sequence_local_store.get_var_if_exists("74__total"),_tmp0,_active_event):
                    pass


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
