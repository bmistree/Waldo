# Waldo emitted file


def SingleSide (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SingleSide (_waldo_classes["Endpoint"]):
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

            self._global_var_store.add_var(
                '1__map_',self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '1__map_', # variable's name
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

        def input_ext_num(self,input_num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__input_ext_num(_root_event,_ctx ,input_num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__input_ext_num(self,_active_event,_context,input_num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_num = _context.turn_into_waldo_var_if_was_var(input_num,False,_active_event,self._host_uuid,False)

                pass

            else:
                input_num = _context.turn_into_waldo_var_if_was_var(input_num,False,_active_event,self._host_uuid,False)

                pass

            _context.global_store.get_var_if_exists("0__num").write_val(_active_event,input_num.get_val(_active_event))


        def increment_ext_num(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__increment_ext_num(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__increment_ext_num(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            _context.global_store.get_var_if_exists("0__num").get_val(_active_event).write_val(_active_event,_context.get_val_if_waldo((_context.get_val_if_waldo(_context.global_store.get_var_if_exists("0__num"),_active_event) + _context.get_val_if_waldo(1 ,_active_event)),_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num"))




        def get_endpoint_ext_value(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_endpoint_ext_value(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_endpoint_ext_value(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num"))




        def get_endpoint_ext(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_endpoint_ext(_root_event,_ctx ,[0])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_endpoint_ext(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num"))




        def input_ext_num_to_map(self,input_num,index):

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
                _to_return = self._endpoint_func_call_prefix__waldo__input_ext_num_to_map(_root_event,_ctx ,input_num,index,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__input_ext_num_to_map(self,_active_event,_context,input_num,index,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                input_num = _context.turn_into_waldo_var_if_was_var(input_num,False,_active_event,self._host_uuid,False)
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)

                pass

            else:
                input_num = _context.turn_into_waldo_var_if_was_var(input_num,False,_active_event,self._host_uuid,False)
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)

                pass

            _context.global_store.get_var_if_exists("1__map_").get_val(_active_event).write_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event),input_num)


        def get_endpoint_map_ext_value(self,index):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_endpoint_map_ext_value(_root_event,_ctx ,index,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_endpoint_map_ext_value(self,_active_event,_context,index,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("1__map_").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__map_").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("1__map_").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)))




        def get_endpoint_map_index(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_endpoint_map_index(_root_event,_ctx ,[0])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_endpoint_map_index(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("1__map_") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__map_"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("1__map_"))




        def test_assign_from_map_index(self,index,to_assign):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_assign_from_map_index(_root_event,_ctx ,index,to_assign,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_assign_from_map_index(self,_active_event,_context,index,to_assign,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                to_assign = _context.turn_into_waldo_var_if_was_var(to_assign,False,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                to_assign = _context.turn_into_waldo_var_if_was_var(to_assign,False,_active_event,self._host_uuid,False)

                pass

            self._endpoint_func_call_prefix__waldo__get_endpoint_map_index(_active_event,_context,).get_val(_active_event).write_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event),to_assign)


        def test_assign_from_func_call(self,to_assign):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_assign_from_func_call(_root_event,_ctx ,to_assign,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_assign_from_func_call(self,_active_event,_context,to_assign,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_assign = _context.turn_into_waldo_var_if_was_var(to_assign,False,_active_event,self._host_uuid,False)

                pass

            else:
                to_assign = _context.turn_into_waldo_var_if_was_var(to_assign,False,_active_event,self._host_uuid,False)

                pass

            self._endpoint_func_call_prefix__waldo__get_endpoint_ext(_active_event,_context,).write_val(_active_event,to_assign)


        def test_ext_copy_dual_function_call(self,index,amt_to_add):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_ext_copy_dual_function_call(_root_event,_ctx ,index,amt_to_add,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_ext_copy_dual_function_call(self,_active_event,_context,index,amt_to_add,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                amt_to_add = _context.turn_into_waldo_var_if_was_var(amt_to_add,True,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                amt_to_add = _context.turn_into_waldo_var_if_was_var(amt_to_add,True,_active_event,self._host_uuid,False)

                pass

            self._endpoint_func_call_prefix__waldo__get_endpoint_map_index(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)).get_val(_active_event).write_val(_active_event,_context.get_val_if_waldo((_context.get_val_if_waldo(self._endpoint_func_call_prefix__waldo__get_endpoint_map_ext_value(_active_event,_context,index,),_active_event) + _context.get_val_if_waldo(amt_to_add,_active_event)),_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__get_endpoint_map_ext_value(_active_event,_context,index,) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__get_endpoint_map_ext_value(_active_event,_context,index,),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__get_endpoint_map_ext_value(_active_event,_context,index,))




        def test_ext_copy_single_function_call(self,to_copy_in):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_ext_copy_single_function_call(_root_event,_ctx ,to_copy_in,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_ext_copy_single_function_call(self,_active_event,_context,to_copy_in,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_copy_in = _context.turn_into_waldo_var_if_was_var(to_copy_in,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_copy_in = _context.turn_into_waldo_var_if_was_var(to_copy_in,True,_active_event,self._host_uuid,False)

                pass

            self._endpoint_func_call_prefix__waldo__get_endpoint_ext(_active_event,_context,).get_val(_active_event).write_val(_active_event,_context.get_val_if_waldo(to_copy_in,_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num"))




        def test_ext_copy_map(self,index,to_ext_copy_ind):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_ext_copy_map(_root_event,_ctx ,index,to_ext_copy_ind,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_ext_copy_map(self,_active_event,_context,index,to_ext_copy_ind,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                to_ext_copy_ind = _context.turn_into_waldo_var_if_was_var(to_ext_copy_ind,True,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                to_ext_copy_ind = _context.turn_into_waldo_var_if_was_var(to_ext_copy_ind,True,_active_event,self._host_uuid,False)

                pass

            _context.global_store.get_var_if_exists("1__map_").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)).get_val(_active_event).write_val(_active_event,_context.get_val_if_waldo(to_ext_copy_ind,_active_event))

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
