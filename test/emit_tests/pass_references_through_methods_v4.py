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

        def create_map_return_literal(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__create_map_return_literal(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__create_map_return_literal(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(1 ,_active_event): _context.get_val_if_waldo(2 ,_active_event),
            _context.get_val_if_waldo(3 ,_active_event): _context.get_val_if_waldo(4 ,_active_event),
            }) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(1 ,_active_event): _context.get_val_if_waldo(2 ,_active_event),
            _context.get_val_if_waldo(3 ,_active_event): _context.get_val_if_waldo(4 ,_active_event),
            }),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(1 ,_active_event): _context.get_val_if_waldo(2 ,_active_event),
            _context.get_val_if_waldo(3 ,_active_event): _context.get_val_if_waldo(4 ,_active_event),
            }))




        def create_map_return_var(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__create_map_return_var(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__create_map_return_var(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            map_ = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '1__map_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._endpoint_func_call_prefix__waldo__create_map_return_literal(_active_event,_context,),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(map_ if 0 in _returning_to_public_ext_array else _context.de_waldoify(map_,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(map_)




        def get_element_from_map_call(self,index_to_get):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_element_from_map_call(_root_event,_ctx ,index_to_get,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_element_from_map_call(self,_active_event,_context,index_to_get,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            else:
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_map_return_var(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__create_map_return_var(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_map_return_var(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)))




        def get_element_from_map_literal_call(self,index_to_get):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_element_from_map_literal_call(_root_event,_ctx ,index_to_get,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_element_from_map_literal_call(self,_active_event,_context,index_to_get,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            else:
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_map_return_literal(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__create_map_return_literal(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_map_return_literal(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)))




        def get_element_from_map_var(self,index_to_get):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_element_from_map_var(_root_event,_ctx ,index_to_get,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_element_from_map_var(self,_active_event,_context,index_to_get,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            else:
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            map_ = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '11__map_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = self._endpoint_func_call_prefix__waldo__create_map_return_literal(_active_event,_context,)
            if not _context.assign(map_,_tmp0,_active_event):
                map_ = _tmp0


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)))




        def create_list_return_literal(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__create_list_return_literal(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__create_list_return_literal(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                [5 ,7 ,9 ,]) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                [5 ,7 ,9 ,]),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                [5 ,7 ,9 ,]))




        def create_list_return_var(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__create_list_return_var(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__create_list_return_var(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            list_ = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '15__list_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._endpoint_func_call_prefix__waldo__create_list_return_literal(_active_event,_context,),_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(list_ if 0 in _returning_to_public_ext_array else _context.de_waldoify(list_,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(list_)




        def get_element_from_list_call(self,index_to_get):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_element_from_list_call(_root_event,_ctx ,index_to_get,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_element_from_list_call(self,_active_event,_context,index_to_get,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            else:
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_list_return_var(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__create_list_return_var(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_list_return_var(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)))




        def get_element_from_list_literal_call(self,index_to_get):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_element_from_list_literal_call(_root_event,_ctx ,index_to_get,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_element_from_list_literal_call(self,_active_event,_context,index_to_get,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            else:
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_list_return_literal(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__create_list_return_literal(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__create_list_return_literal(_active_event,_context,).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)))




        def get_element_from_list_var(self,index_to_get):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_element_from_list_var(_root_event,_ctx ,index_to_get,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_element_from_list_var(self,_active_event,_context,index_to_get,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            else:
                index_to_get = _context.turn_into_waldo_var_if_was_var(index_to_get,True,_active_event,self._host_uuid,False)

                pass

            list_ = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '25__list_', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            _tmp0 = self._endpoint_func_call_prefix__waldo__create_list_return_literal(_active_event,_context,)
            if not _context.assign(list_,_tmp0,_active_event):
                list_ = _tmp0


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(list_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify(list_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(list_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index_to_get,_active_event)))



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
