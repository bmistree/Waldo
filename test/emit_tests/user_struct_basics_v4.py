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
                '0__num_struct',self._waldo_classes["WaldoUserStructVariable"]("0__num_struct",_host_uuid,False,{"num": 0, }))

            self._global_var_store.add_var(
                '1__nested_struct',self._waldo_classes["WaldoUserStructVariable"]("1__nested_struct",_host_uuid,False,{"additional_structs": self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                'additional_structs', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                None
            ), "num": 0, }))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def assign_num_to_number_struct(self,new_num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__assign_num_to_number_struct(_root_event,_ctx ,new_num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__assign_num_to_number_struct(self,_active_event,_context,new_num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                new_num = _context.turn_into_waldo_var_if_was_var(new_num,True,_active_event,self._host_uuid,False)

                pass

            else:
                new_num = _context.turn_into_waldo_var_if_was_var(new_num,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = new_num
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__num_struct"),"num",_tmp0, _active_event)



        def read_num_from_number_struct(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__read_num_from_number_struct(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__read_num_from_number_struct(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num_struct").get_val(_active_event).get_val_on_key(_active_event,"num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__num_struct").get_val(_active_event).get_val_on_key(_active_event,"num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__num_struct").get_val(_active_event).get_val_on_key(_active_event,"num"))




        def assign_num_to_nested_struct(self,outer_num,inner_num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__assign_num_to_nested_struct(_root_event,_ctx ,outer_num,inner_num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__assign_num_to_nested_struct(self,_active_event,_context,outer_num,inner_num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                outer_num = _context.turn_into_waldo_var_if_was_var(outer_num,True,_active_event,self._host_uuid,False)
                inner_num = _context.turn_into_waldo_var_if_was_var(inner_num,True,_active_event,self._host_uuid,False)

                pass

            else:
                outer_num = _context.turn_into_waldo_var_if_was_var(outer_num,True,_active_event,self._host_uuid,False)
                inner_num = _context.turn_into_waldo_var_if_was_var(inner_num,True,_active_event,self._host_uuid,False)

                pass

            inner_struct = self._waldo_classes["WaldoUserStructVariable"]("6__inner_struct",self._host_uuid,False,{"additional_structs": self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                'additional_structs', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                None
            ), "num": 0, })

            _tmp0 = outer_num
            _context.assign_on_key(_context.global_store.get_var_if_exists("1__nested_struct"),"num",_tmp0, _active_event)

            _context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"additional_structs").get_val(_active_event).append_val(_active_event,inner_struct)
            _tmp0 = inner_num
            _context.assign_on_key(_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"additional_structs").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)),"num",_tmp0, _active_event)



        def get_outer_and_inner_nested_nums(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_outer_and_inner_nested_nums(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_outer_and_inner_nested_nums(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"num"),_active_event),_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"additional_structs").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)).get_val(_active_event).get_val_on_key(_active_event,"num") if 1 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"additional_structs").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)).get_val(_active_event).get_val_on_key(_active_event,"num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"num"),_context.global_store.get_var_if_exists("1__nested_struct").get_val(_active_event).get_val_on_key(_active_event,"additional_structs").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(0 ,_active_event)).get_val(_active_event).get_val_on_key(_active_event,"num"))




        def get_nested_struct_num(self,ns):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_nested_struct_num(_root_event,_ctx ,ns,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_nested_struct_num(self,_active_event,_context,ns,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                ns = _context.turn_into_waldo_var_if_was_var(ns,True,_active_event,self._host_uuid,False)

                pass

            else:
                ns = _context.turn_into_waldo_var_if_was_var(ns,False,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(ns.get_val(_active_event).get_val_on_key(_active_event,"num") if 0 in _returning_to_public_ext_array else _context.de_waldoify(ns.get_val(_active_event).get_val_on_key(_active_event,"num"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(ns.get_val(_active_event).get_val_on_key(_active_event,"num"))




        def get_endpoint_nested_struct_num(self,new_num):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_endpoint_nested_struct_num(_root_event,_ctx ,new_num,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__get_endpoint_nested_struct_num(self,_active_event,_context,new_num,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                new_num = _context.turn_into_waldo_var_if_was_var(new_num,True,_active_event,self._host_uuid,False)

                pass

            else:
                new_num = _context.turn_into_waldo_var_if_was_var(new_num,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = new_num
            _context.assign_on_key(_context.global_store.get_var_if_exists("1__nested_struct"),"num",_tmp0, _active_event)


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__get_nested_struct_num(_active_event,_context,_context.global_store.get_var_if_exists("1__nested_struct"),) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._endpoint_func_call_prefix__waldo__get_nested_struct_num(_active_event,_context,_context.global_store.get_var_if_exists("1__nested_struct"),),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._endpoint_func_call_prefix__waldo__get_nested_struct_num(_active_event,_context,_context.global_store.get_var_if_exists("1__nested_struct"),))



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
