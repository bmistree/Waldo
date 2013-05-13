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
                '1__end',self._waldo_classes["WaldoEndpointVariable"](  # the type of waldo variable to create
                '1__end', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

            self._global_var_store.add_var(
                '2__ext_num',self._waldo_classes["WaldoExtNumVariable"](  # the type of waldo variable to create
                '2__ext_num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

            self._global_var_store.add_var(
                '0__peered_list',self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '0__peered_list', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                
            ))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def assign_endpoint(self,ept):

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
                _to_return = self._endpoint_func_call_prefix__waldo__assign_endpoint(_root_event,_ctx ,ept,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__assign_endpoint(self,_active_event,_context,ept,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                ept = _context.turn_into_waldo_var_if_was_var(ept,True,_active_event,self._host_uuid,False)

                pass

            else:
                ept = _context.turn_into_waldo_var_if_was_var(ept,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = ept
            if not _context.assign(_context.global_store.get_var_if_exists("1__end"),_tmp0,_active_event):
                pass



        def assign_external_number(self,e_num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__assign_external_number(_root_event,_ctx ,e_num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__assign_external_number(self,_active_event,_context,e_num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                e_num = _context.turn_into_waldo_var_if_was_var(e_num,False,_active_event,self._host_uuid,False)

                pass

            else:
                e_num = _context.turn_into_waldo_var_if_was_var(e_num,False,_active_event,self._host_uuid,False)

                pass

            _context.global_store.get_var_if_exists("2__ext_num").write_val(_active_event,e_num.get_val(_active_event))


        def test_assigned_number(self,input_number,increment_num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_assigned_number(_root_event,_ctx ,input_number,increment_num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_assigned_number(self,_active_event,_context,input_number,increment_num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_number = _context.turn_into_waldo_var_if_was_var(input_number,True,_active_event,self._host_uuid,False)
                increment_num = _context.turn_into_waldo_var_if_was_var(increment_num,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_number = _context.turn_into_waldo_var_if_was_var(input_number,True,_active_event,self._host_uuid,False)
                increment_num = _context.turn_into_waldo_var_if_was_var(increment_num,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__end"),_active_event),"get_val",input_number,increment_num,) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__end"),_active_event),"get_val",input_number,increment_num,),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__end"),_active_event),"get_val",input_number,increment_num,))




        def check_value_type_argument(self,input_number,increment_by):

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
                _to_return = self._endpoint_func_call_prefix__waldo__check_value_type_argument(_root_event,_ctx ,input_number,increment_by,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__check_value_type_argument(self,_active_event,_context,input_number,increment_by,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_number = _context.turn_into_waldo_var_if_was_var(input_number,True,_active_event,self._host_uuid,False)
                increment_by = _context.turn_into_waldo_var_if_was_var(increment_by,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_number = _context.turn_into_waldo_var_if_was_var(input_number,True,_active_event,self._host_uuid,False)
                increment_by = _context.turn_into_waldo_var_if_was_var(increment_by,True,_active_event,self._host_uuid,False)

                pass

            result = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '10__result', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(_context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__end"),_active_event),"get_val",input_number,increment_by,),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(input_number if 0 in _returning_to_public_ext_array else _context.de_waldoify(input_number,_active_event),result if 1 in _returning_to_public_ext_array else _context.de_waldoify(result,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(input_number,result)




        def test_updated_val(self,new_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_updated_val(_root_event,_ctx ,new_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_updated_val(self,_active_event,_context,new_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                new_val = _context.turn_into_waldo_var_if_was_var(new_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                new_val = _context.turn_into_waldo_var_if_was_var(new_val,True,_active_event,self._host_uuid,False)

                pass

            _context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__end"),_active_event),"external_changer",_context.global_store.get_var_if_exists("2__ext_num"),new_val,)

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("2__ext_num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("2__ext_num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("2__ext_num"))




        def hide_list(self,text_list):

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
                _to_return = self._endpoint_func_call_prefix__waldo__hide_list(_root_event,_ctx ,text_list,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__hide_list(self,_active_event,_context,text_list,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                text_list = _context.turn_into_waldo_var_if_was_var(text_list,True,_active_event,self._host_uuid,False)

                pass

            else:
                text_list = _context.turn_into_waldo_var_if_was_var(text_list,False,_active_event,self._host_uuid,False)

                pass

            _tmp0 = text_list
            if not _context.assign(_context.global_store.get_var_if_exists("0__peered_list"),_tmp0,_active_event):
                pass

            _context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__end"),_active_event),"append_to_list",_context.global_store.get_var_if_exists("0__peered_list"),)

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.handle_len(_context.global_store.get_var_if_exists("0__peered_list"),_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.handle_len(_context.global_store.get_var_if_exists("0__peered_list"),_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.handle_len(_context.global_store.get_var_if_exists("0__peered_list"),_active_event))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

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
                '0__peered_list',self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '0__peered_list', # variable's name
                _host_uuid, # host uuid var name
                True,  # if peered, True, otherwise, False
                
            ))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def get_val(self,input_number,increment_by):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_val(_root_event,_ctx ,input_number,increment_by,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_val(self,_active_event,_context,input_number,increment_by,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_number = _context.turn_into_waldo_var_if_was_var(input_number,True,_active_event,self._host_uuid,False)
                increment_by = _context.turn_into_waldo_var_if_was_var(increment_by,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_number = _context.turn_into_waldo_var_if_was_var(input_number,True,_active_event,self._host_uuid,False)
                increment_by = _context.turn_into_waldo_var_if_was_var(increment_by,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = (_context.get_val_if_waldo(input_number,_active_event) + _context.get_val_if_waldo(increment_by,_active_event))
            if not _context.assign(input_number,_tmp0,_active_event):
                input_number = _tmp0


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(input_number if 0 in _returning_to_public_ext_array else _context.de_waldoify(input_number,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(input_number)




        def external_changer(self,to_change,new_val):

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
                _to_return = self._endpoint_func_call_prefix__waldo__external_changer(_root_event,_ctx ,to_change,new_val,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__external_changer(self,_active_event,_context,to_change,new_val,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_change = _context.turn_into_waldo_var_if_was_var(to_change,False,_active_event,self._host_uuid,False)
                new_val = _context.turn_into_waldo_var_if_was_var(new_val,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_change = _context.turn_into_waldo_var_if_was_var(to_change,False,_active_event,self._host_uuid,False)
                new_val = _context.turn_into_waldo_var_if_was_var(new_val,True,_active_event,self._host_uuid,False)

                pass

            to_change.get_val(_active_event).write_val(_active_event,_context.get_val_if_waldo(new_val,_active_event))


        def append_to_list(self,text_list):

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
                _to_return = self._endpoint_func_call_prefix__waldo__append_to_list(_root_event,_ctx ,text_list,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__append_to_list(self,_active_event,_context,text_list,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                text_list = _context.turn_into_waldo_var_if_was_var(text_list,True,_active_event,self._host_uuid,False)

                pass

            else:
                text_list = _context.turn_into_waldo_var_if_was_var(text_list,False,_active_event,self._host_uuid,False)

                pass

            text_list.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo('hioe' ,_active_event))

        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

    return _SideB(_waldo_classes,_host_uuid,_conn_obj,*args)
