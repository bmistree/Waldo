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

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def to_text_number(self,to_call_to_text_on):

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
                _to_return = self._endpoint_func_call_prefix__waldo__to_text_number(_root_event,_ctx ,to_call_to_text_on,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__to_text_number(self,_active_event,_context,to_call_to_text_on,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_call_to_text_on = _context.turn_into_waldo_var_if_was_var(to_call_to_text_on,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_call_to_text_on = _context.turn_into_waldo_var_if_was_var(to_call_to_text_on,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.to_text(to_call_to_text_on,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.to_text(to_call_to_text_on,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.to_text(to_call_to_text_on,_active_event))




        def to_text_text(self,to_call_to_text_on):

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
                _to_return = self._endpoint_func_call_prefix__waldo__to_text_text(_root_event,_ctx ,to_call_to_text_on,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__to_text_text(self,_active_event,_context,to_call_to_text_on,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_call_to_text_on = _context.turn_into_waldo_var_if_was_var(to_call_to_text_on,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_call_to_text_on = _context.turn_into_waldo_var_if_was_var(to_call_to_text_on,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.to_text(to_call_to_text_on,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.to_text(to_call_to_text_on,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.to_text(to_call_to_text_on,_active_event))




        def to_text_true_false(self,to_call_to_text_on):

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
                _to_return = self._endpoint_func_call_prefix__waldo__to_text_true_false(_root_event,_ctx ,to_call_to_text_on,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__to_text_true_false(self,_active_event,_context,to_call_to_text_on,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_call_to_text_on = _context.turn_into_waldo_var_if_was_var(to_call_to_text_on,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_call_to_text_on = _context.turn_into_waldo_var_if_was_var(to_call_to_text_on,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.to_text(to_call_to_text_on,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.to_text(to_call_to_text_on,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.to_text(to_call_to_text_on,_active_event))




        def nested_map(self,outer_index,inner_val_and_index):

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
                _to_return = self._endpoint_func_call_prefix__waldo__nested_map(_root_event,_ctx ,outer_index,inner_val_and_index,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__nested_map(self,_active_event,_context,outer_index,inner_val_and_index,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                outer_index = _context.turn_into_waldo_var_if_was_var(outer_index,True,_active_event,self._host_uuid,False)
                inner_val_and_index = _context.turn_into_waldo_var_if_was_var(inner_val_and_index,True,_active_event,self._host_uuid,False)

                pass

            else:
                outer_index = _context.turn_into_waldo_var_if_was_var(outer_index,True,_active_event,self._host_uuid,False)
                inner_val_and_index = _context.turn_into_waldo_var_if_was_var(inner_val_and_index,True,_active_event,self._host_uuid,False)

                pass

            outer_map = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '8__outer_map', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            inner_map = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '9__inner_map', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = inner_val_and_index
            _context.assign_on_key(inner_map,inner_val_and_index,_tmp0, _active_event)

            _tmp0 = inner_map
            _context.assign_on_key(outer_map,outer_index,_tmp0, _active_event)

            to_return = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '10__to_return', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = outer_map.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(outer_index,_active_event)).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(inner_val_and_index,_active_event))
            if not _context.assign(to_return,_tmp0,_active_event):
                to_return = _tmp0


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_return if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_return,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_return)




        def nested_list_append(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__nested_list_append(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__nested_list_append(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            double_list = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '12__double_list', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            l = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '13__l', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            l.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo(13 ,_active_event))
            double_list.get_val(_active_event).append_val(_active_event,l)
            double_list.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event))


        def test_list_remove(self,to_remove_from,index_to_remove):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_list_remove(_root_event,_ctx ,to_remove_from,index_to_remove,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_list_remove(self,_active_event,_context,to_remove_from,index_to_remove,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_remove_from = _context.turn_into_waldo_var_if_was_var(to_remove_from,True,_active_event,self._host_uuid,False)
                index_to_remove = _context.turn_into_waldo_var_if_was_var(index_to_remove,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_remove_from = _context.turn_into_waldo_var_if_was_var(to_remove_from,False,_active_event,self._host_uuid,False)
                index_to_remove = _context.turn_into_waldo_var_if_was_var(index_to_remove,True,_active_event,self._host_uuid,False)

                pass

            to_remove_from.get_val(_active_event).del_key_called(_active_event,_context.get_val_if_waldo(index_to_remove,_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_remove_from if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_remove_from,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_remove_from)




        def test_list_insert(self,to_insert_into,index_to_insert_into,what_to_insert):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_list_insert(_root_event,_ctx ,to_insert_into,index_to_insert_into,what_to_insert,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_list_insert(self,_active_event,_context,to_insert_into,index_to_insert_into,what_to_insert,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_insert_into = _context.turn_into_waldo_var_if_was_var(to_insert_into,True,_active_event,self._host_uuid,False)
                index_to_insert_into = _context.turn_into_waldo_var_if_was_var(index_to_insert_into,True,_active_event,self._host_uuid,False)
                what_to_insert = _context.turn_into_waldo_var_if_was_var(what_to_insert,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_insert_into = _context.turn_into_waldo_var_if_was_var(to_insert_into,False,_active_event,self._host_uuid,False)
                index_to_insert_into = _context.turn_into_waldo_var_if_was_var(index_to_insert_into,True,_active_event,self._host_uuid,False)
                what_to_insert = _context.turn_into_waldo_var_if_was_var(what_to_insert,True,_active_event,self._host_uuid,False)

                pass

            to_insert_into.get_val(_active_event).insert_into(_active_event,_context.get_val_if_waldo(index_to_insert_into,_active_event),_context.get_val_if_waldo(what_to_insert,_active_event))

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_insert_into if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_insert_into,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_insert_into)




        def test_return_nested_map(self,in_nested_map):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_return_nested_map(_root_event,_ctx ,in_nested_map,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_return_nested_map(self,_active_event,_context,in_nested_map,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                in_nested_map = _context.turn_into_waldo_var_if_was_var(in_nested_map,True,_active_event,self._host_uuid,False)

                pass

            else:
                in_nested_map = _context.turn_into_waldo_var_if_was_var(in_nested_map,False,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(in_nested_map if 0 in _returning_to_public_ext_array else _context.de_waldoify(in_nested_map,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(in_nested_map)




        def test_return_user_struct(self,fielda,fieldb):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_return_user_struct(_root_event,_ctx ,fielda,fieldb,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_return_user_struct(self,_active_event,_context,fielda,fieldb,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                fielda = _context.turn_into_waldo_var_if_was_var(fielda,True,_active_event,self._host_uuid,False)
                fieldb = _context.turn_into_waldo_var_if_was_var(fieldb,True,_active_event,self._host_uuid,False)

                pass

            else:
                fielda = _context.turn_into_waldo_var_if_was_var(fielda,True,_active_event,self._host_uuid,False)
                fieldb = _context.turn_into_waldo_var_if_was_var(fieldb,True,_active_event,self._host_uuid,False)

                pass

            ts = self._waldo_classes["WaldoUserStructVariable"]("25__ts",self._host_uuid,False,{"fieldb": "", "fielda": "", })

            _tmp0 = fielda
            _context.assign_on_key(ts,"fielda",_tmp0, _active_event)

            _tmp0 = fieldb
            _context.assign_on_key(ts,"fieldb",_tmp0, _active_event)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(ts if 0 in _returning_to_public_ext_array else _context.de_waldoify(ts,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(ts)




        def test_return_user_struct_in_map(self,map_index,user_struct_fielda,user_struct_fieldb):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_return_user_struct_in_map(_root_event,_ctx ,map_index,user_struct_fielda,user_struct_fieldb,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_return_user_struct_in_map(self,_active_event,_context,map_index,user_struct_fielda,user_struct_fieldb,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                map_index = _context.turn_into_waldo_var_if_was_var(map_index,True,_active_event,self._host_uuid,False)
                user_struct_fielda = _context.turn_into_waldo_var_if_was_var(user_struct_fielda,True,_active_event,self._host_uuid,False)
                user_struct_fieldb = _context.turn_into_waldo_var_if_was_var(user_struct_fieldb,True,_active_event,self._host_uuid,False)

                pass

            else:
                map_index = _context.turn_into_waldo_var_if_was_var(map_index,True,_active_event,self._host_uuid,False)
                user_struct_fielda = _context.turn_into_waldo_var_if_was_var(user_struct_fielda,True,_active_event,self._host_uuid,False)
                user_struct_fieldb = _context.turn_into_waldo_var_if_was_var(user_struct_fieldb,True,_active_event,self._host_uuid,False)

                pass

            map_ = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '30__map_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = self._endpoint_func_call_prefix__waldo__test_return_user_struct(_active_event,_context,user_struct_fielda,user_struct_fieldb,)
            _context.assign_on_key(map_,map_index,_tmp0, _active_event)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(map_ if 0 in _returning_to_public_ext_array else _context.de_waldoify(map_,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(map_)



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
