# Waldo emitted file


def SingleSide (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SingleSide (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,in_text_identity,in_text_len,in_sum_list,in_no_return,in_sum_three_args,in_return_three_args):

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
                '0__text_identity',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '0__text_identity', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._global_var_store.add_var(
                '1__text_len',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '1__text_len', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._global_var_store.add_var(
                '2__sum_list',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '2__sum_list', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._global_var_store.add_var(
                '3__no_return',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '3__no_return', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._global_var_store.add_var(
                '4__sum_three_args',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '4__sum_three_args', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

            self._global_var_store.add_var(
                '5__return_three_args',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '5__return_three_args', # variable's name
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
                _to_return = self._onCreate(_root_event,_ctx ,in_text_identity,in_text_len,in_sum_list,in_no_return,in_sum_three_args,in_return_three_args,[])
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

        def _onCreate(self,_active_event,_context,in_text_identity,in_text_len,in_sum_list,in_no_return,in_sum_three_args,in_return_three_args,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                in_text_identity = _context.func_turn_into_waldo_var(in_text_identity,True,_active_event,self._host_uuid,False,[])
                in_text_len = _context.func_turn_into_waldo_var(in_text_len,True,_active_event,self._host_uuid,False,[])
                in_sum_list = _context.func_turn_into_waldo_var(in_sum_list,True,_active_event,self._host_uuid,False,[])
                in_no_return = _context.func_turn_into_waldo_var(in_no_return,True,_active_event,self._host_uuid,False,[])
                in_sum_three_args = _context.func_turn_into_waldo_var(in_sum_three_args,True,_active_event,self._host_uuid,False,[])
                in_return_three_args = _context.func_turn_into_waldo_var(in_return_three_args,True,_active_event,self._host_uuid,False,[])

                pass

            else:
                in_text_identity = _context.func_turn_into_waldo_var(in_text_identity,True,_active_event,self._host_uuid,False,[])
                in_text_len = _context.func_turn_into_waldo_var(in_text_len,True,_active_event,self._host_uuid,False,[])
                in_sum_list = _context.func_turn_into_waldo_var(in_sum_list,True,_active_event,self._host_uuid,False,[])
                in_no_return = _context.func_turn_into_waldo_var(in_no_return,True,_active_event,self._host_uuid,False,[])
                in_sum_three_args = _context.func_turn_into_waldo_var(in_sum_three_args,True,_active_event,self._host_uuid,False,[])
                in_return_three_args = _context.func_turn_into_waldo_var(in_return_three_args,True,_active_event,self._host_uuid,False,[])

                pass

            _tmp0 = in_text_identity
            if not _context.assign(_context.global_store.get_var_if_exists("0__text_identity"),_tmp0,_active_event):
                pass

            _tmp0 = in_text_len
            if not _context.assign(_context.global_store.get_var_if_exists("1__text_len"),_tmp0,_active_event):
                pass

            _tmp0 = in_sum_list
            if not _context.assign(_context.global_store.get_var_if_exists("2__sum_list"),_tmp0,_active_event):
                pass

            _tmp0 = in_no_return
            if not _context.assign(_context.global_store.get_var_if_exists("3__no_return"),_tmp0,_active_event):
                pass

            _tmp0 = in_sum_three_args
            if not _context.assign(_context.global_store.get_var_if_exists("4__sum_three_args"),_tmp0,_active_event):
                pass

            _tmp0 = in_return_three_args
            if not _context.assign(_context.global_store.get_var_if_exists("5__return_three_args"),_tmp0,_active_event):
                pass

        ### USER DEFINED METHODS ###

        def execute_identity_endpoint_func(self,input_text):

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
                _to_return = self._endpoint_func_call_prefix__waldo__execute_identity_endpoint_func(_root_event,_ctx ,input_text,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__execute_identity_endpoint_func(self,_active_event,_context,input_text,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_text = _context.turn_into_waldo_var_if_was_var(input_text,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_text = _context.turn_into_waldo_var_if_was_var(input_text,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__text_identity"),input_text),_active_event) == _context.get_val_if_waldo(input_text,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__text_identity"),input_text),_active_event) == _context.get_val_if_waldo(input_text,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__text_identity"),input_text),_active_event) == _context.get_val_if_waldo(input_text,_active_event)))




        def execute_len_endpoint_func(self,input_text):

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
                _to_return = self._endpoint_func_call_prefix__waldo__execute_len_endpoint_func(_root_event,_ctx ,input_text,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__execute_len_endpoint_func(self,_active_event,_context,input_text,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_text = _context.turn_into_waldo_var_if_was_var(input_text,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_text = _context.turn_into_waldo_var_if_was_var(input_text,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("1__text_len"),input_text),_active_event) == _context.get_val_if_waldo(_context.handle_len(input_text,_active_event),_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("1__text_len"),input_text),_active_event) == _context.get_val_if_waldo(_context.handle_len(input_text,_active_event),_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("1__text_len"),input_text),_active_event) == _context.get_val_if_waldo(_context.handle_len(input_text,_active_event),_active_event)))




        def execute_sum_list_endpoint_func(self,input_list):

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
                _to_return = self._endpoint_func_call_prefix__waldo__execute_sum_list_endpoint_func(_root_event,_ctx ,input_list,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__execute_sum_list_endpoint_func(self,_active_event,_context,input_list,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_list = _context.turn_into_waldo_var_if_was_var(input_list,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_list = _context.turn_into_waldo_var_if_was_var(input_list,False,_active_event,self._host_uuid,False)

                pass

            expected_sum = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '19__expected_sum', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '20__num', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____num in _context.get_for_iter(input_list,_active_event):
                num.write_val(_active_event,_secret_waldo_for_iter____num)
                _tmp0 = (_context.get_val_if_waldo(expected_sum,_active_event) + _context.get_val_if_waldo(num,_active_event))
                if not _context.assign(expected_sum,_tmp0,_active_event):
                    expected_sum = _tmp0


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("2__sum_list"),input_list),_active_event) == _context.get_val_if_waldo(expected_sum,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("2__sum_list"),input_list),_active_event) == _context.get_val_if_waldo(expected_sum,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("2__sum_list"),input_list),_active_event) == _context.get_val_if_waldo(expected_sum,_active_event)))




        def execute_no_return_endpoint_func(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__execute_no_return_endpoint_func(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__execute_no_return_endpoint_func(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            _context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("3__no_return"))


        def execute_sum_three_args_endpoint_func(self,a,b,c):

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
                _to_return = self._endpoint_func_call_prefix__waldo__execute_sum_three_args_endpoint_func(_root_event,_ctx ,a,b,c,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__execute_sum_three_args_endpoint_func(self,_active_event,_context,a,b,c,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False)
                b = _context.turn_into_waldo_var_if_was_var(b,True,_active_event,self._host_uuid,False)
                c = _context.turn_into_waldo_var_if_was_var(c,True,_active_event,self._host_uuid,False)

                pass

            else:
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False)
                b = _context.turn_into_waldo_var_if_was_var(b,True,_active_event,self._host_uuid,False)
                c = _context.turn_into_waldo_var_if_was_var(c,True,_active_event,self._host_uuid,False)

                pass

            expected_sum = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '27__expected_sum', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo((_context.get_val_if_waldo(a,_active_event) + _context.get_val_if_waldo((_context.get_val_if_waldo(b,_active_event) + _context.get_val_if_waldo(c,_active_event)),_active_event)),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("4__sum_three_args"),a,b,c),_active_event) == _context.get_val_if_waldo(expected_sum,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("4__sum_three_args"),a,b,c),_active_event) == _context.get_val_if_waldo(expected_sum,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("4__sum_three_args"),a,b,c),_active_event) == _context.get_val_if_waldo(expected_sum,_active_event)))




        def execute_return_three_args_endpoint_func(self,a,b,c):

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
                _to_return = self._endpoint_func_call_prefix__waldo__execute_return_three_args_endpoint_func(_root_event,_ctx ,a,b,c,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__execute_return_three_args_endpoint_func(self,_active_event,_context,a,b,c,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False)
                b = _context.turn_into_waldo_var_if_was_var(b,True,_active_event,self._host_uuid,False)
                c = _context.turn_into_waldo_var_if_was_var(c,True,_active_event,self._host_uuid,False)

                pass

            else:
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False)
                b = _context.turn_into_waldo_var_if_was_var(b,True,_active_event,self._host_uuid,False)
                c = _context.turn_into_waldo_var_if_was_var(c,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("5__return_three_args"),a,b,c) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("5__return_three_args"),a,b,c),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("5__return_three_args"),a,b,c))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

    return _SingleSide(_waldo_classes,_host_uuid,_conn_obj,*args)
def _SingleSide (_waldo_classes,_host_uuid,_conn_obj,*args):
    class __SingleSide (_waldo_classes["Endpoint"]):
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

        ### User-defined message receive blocks ###

    return __SingleSide(_waldo_classes,_host_uuid,_conn_obj,*args)
