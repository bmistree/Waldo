# Waldo emitted file


def SideA (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SideA (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,number_to_load,index_to_load_self_into):

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
                '0__endpoint_list',self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '0__endpoint_list', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

            self._global_var_store.add_var(
                '1__endpoint_map',self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '1__endpoint_map', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

            self._global_var_store.add_var(
                '2__side_a_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '2__side_a_num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

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
                _to_return = self._onCreate(_root_event,_ctx ,number_to_load,index_to_load_self_into,[])
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

        def _onCreate(self,_active_event,_context,number_to_load,index_to_load_self_into,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                number_to_load = _context.turn_into_waldo_var_if_was_var(number_to_load,True,_active_event,self._host_uuid,False)
                index_to_load_self_into = _context.turn_into_waldo_var_if_was_var(index_to_load_self_into,True,_active_event,self._host_uuid,False)

                pass

            else:
                number_to_load = _context.turn_into_waldo_var_if_was_var(number_to_load,True,_active_event,self._host_uuid,False)
                index_to_load_self_into = _context.turn_into_waldo_var_if_was_var(index_to_load_self_into,True,_active_event,self._host_uuid,False)

                pass

            self._endpoint_func_call_prefix__waldo__set_side_number(_active_event,_context,number_to_load,)
            _context.global_store.get_var_if_exists("0__endpoint_list").get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo(self,_active_event))
            _tmp0 = self
            _context.assign_on_key(_context.global_store.get_var_if_exists("1__endpoint_map"),index_to_load_self_into,_tmp0, _active_event)

        ### USER DEFINED METHODS ###

        def get_self_holders(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_self_holders(_root_event,_ctx ,[0, 1])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_self_holders(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__endpoint_list") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__endpoint_list"),_active_event),_context.global_store.get_var_if_exists("1__endpoint_map") if 1 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__endpoint_map"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__endpoint_list"),_context.global_store.get_var_if_exists("1__endpoint_map"))




        def set_side_number(self,new_number):

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
                _to_return = self._endpoint_func_call_prefix__waldo__set_side_number(_root_event,_ctx ,new_number,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__set_side_number(self,_active_event,_context,new_number,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                new_number = _context.turn_into_waldo_var_if_was_var(new_number,True,_active_event,self._host_uuid,False)

                pass

            else:
                new_number = _context.turn_into_waldo_var_if_was_var(new_number,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = new_number
            if not _context.assign(_context.global_store.get_var_if_exists("2__side_a_num"),_tmp0,_active_event):
                pass



        def get_number(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_number(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_number(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("2__side_a_num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("2__side_a_num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("2__side_a_num"))




        def get_numbers_from_list(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_numbers_from_list(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_numbers_from_list(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            to_return = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '9__to_return', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            end = self._waldo_classes["WaldoEndpointVariable"](  # the type of waldo variable to create
                '10__end', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____end in _context.get_for_iter(_context.global_store.get_var_if_exists("0__endpoint_list"),_active_event):
                end.write_val(_active_event,_secret_waldo_for_iter____end)
                to_return.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo(_context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(end,_active_event),"get_number",),_active_event))

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_return if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_return,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_return)




        def get_numbers_from_map(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_numbers_from_map(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_numbers_from_map(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            to_return = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '12__to_return', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            index = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '13__index', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____index in _context.get_for_iter(_context.global_store.get_var_if_exists("1__endpoint_map"),_active_event):
                index.write_val(_active_event,_secret_waldo_for_iter____index)
                _tmp0 = _context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__endpoint_map").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(index,_active_event)),_active_event),"get_number",)
                _context.assign_on_key(to_return,index,_tmp0, _active_event)


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_return if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_return,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_return)



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

    return _SideA(_waldo_classes,_host_uuid,_conn_obj,*args)
def SideB (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _SideB (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,new_number):

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
                '15__side_b_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '15__side_b_num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

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
                _to_return = self._onCreate(_root_event,_ctx ,new_number,[])
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

        def _onCreate(self,_active_event,_context,new_number,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                new_number = _context.turn_into_waldo_var_if_was_var(new_number,True,_active_event,self._host_uuid,False)

                pass

            else:
                new_number = _context.turn_into_waldo_var_if_was_var(new_number,True,_active_event,self._host_uuid,False)

                pass

            self._endpoint_func_call_prefix__waldo__set_side_number(_active_event,_context,new_number,)
        ### USER DEFINED METHODS ###

        def set_side_number(self,new_number):

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
                _to_return = self._endpoint_func_call_prefix__waldo__set_side_number(_root_event,_ctx ,new_number,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__set_side_number(self,_active_event,_context,new_number,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                new_number = _context.turn_into_waldo_var_if_was_var(new_number,True,_active_event,self._host_uuid,False)

                pass

            else:
                new_number = _context.turn_into_waldo_var_if_was_var(new_number,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = new_number
            if not _context.assign(_context.global_store.get_var_if_exists("15__side_b_num"),_tmp0,_active_event):
                pass



        def get_number(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_number(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_number(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("15__side_b_num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("15__side_b_num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("15__side_b_num"))




        def append_self_to_list(self,list_):

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
                _to_return = self._endpoint_func_call_prefix__waldo__append_self_to_list(_root_event,_ctx ,list_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__append_self_to_list(self,_active_event,_context,list_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                list_ = _context.turn_into_waldo_var_if_was_var(list_,False,_active_event,self._host_uuid,False)

                pass

            else:
                list_ = _context.turn_into_waldo_var_if_was_var(list_,False,_active_event,self._host_uuid,False)

                pass

            list_.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo(self,_active_event))


        def append_self_to_map(self,index,map_):

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
                _to_return = self._endpoint_func_call_prefix__waldo__append_self_to_map(_root_event,_ctx ,index,map_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__append_self_to_map(self,_active_event,_context,index,map_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                map_ = _context.turn_into_waldo_var_if_was_var(map_,False,_active_event,self._host_uuid,False)

                pass

            else:
                index = _context.turn_into_waldo_var_if_was_var(index,True,_active_event,self._host_uuid,False)
                map_ = _context.turn_into_waldo_var_if_was_var(map_,False,_active_event,self._host_uuid,False)

                pass

            _tmp0 = self
            _context.assign_on_key(map_,index,_tmp0, _active_event)


        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

    return _SideB(_waldo_classes,_host_uuid,_conn_obj,*args)
