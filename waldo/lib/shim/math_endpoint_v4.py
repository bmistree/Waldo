# Waldo emitted file


def MathEndpoint (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _MathEndpoint (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,in_min_func,in_max_func,in_mod_func,in_rand_int_func):

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
                '0__math',self._waldo_classes["WaldoUserStructVariable"]("0__math",_host_uuid,False,{"min_func": self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                'min_func', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                None
            ).set_external_args_array([]), "max_func": self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                'max_func', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                None
            ).set_external_args_array([]), "mod_func": self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                'mod_func', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                None
            ).set_external_args_array([]), "rand_int_func": self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                'rand_int_func', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                None
            ).set_external_args_array([]), }))

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
                _to_return = self._onCreate(_root_event,_ctx ,in_min_func,in_max_func,in_mod_func,in_rand_int_func,[])
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

        def _onCreate(self,_active_event,_context,in_min_func,in_max_func,in_mod_func,in_rand_int_func,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                in_min_func = _context.func_turn_into_waldo_var(in_min_func,True,_active_event,self._host_uuid,False,[],False)
                in_max_func = _context.func_turn_into_waldo_var(in_max_func,True,_active_event,self._host_uuid,False,[],False)
                in_mod_func = _context.func_turn_into_waldo_var(in_mod_func,True,_active_event,self._host_uuid,False,[],False)
                in_rand_int_func = _context.func_turn_into_waldo_var(in_rand_int_func,True,_active_event,self._host_uuid,False,[],False)

                pass

            else:
                in_min_func = _context.func_turn_into_waldo_var(in_min_func,True,_active_event,self._host_uuid,False,[],False)
                in_max_func = _context.func_turn_into_waldo_var(in_max_func,True,_active_event,self._host_uuid,False,[],False)
                in_mod_func = _context.func_turn_into_waldo_var(in_mod_func,True,_active_event,self._host_uuid,False,[],False)
                in_rand_int_func = _context.func_turn_into_waldo_var(in_rand_int_func,True,_active_event,self._host_uuid,False,[],False)

                pass

            _tmp0 = in_min_func
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__math"),"min_func",_tmp0, _active_event)

            _tmp0 = in_max_func
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__math"),"max_func",_tmp0, _active_event)

            _tmp0 = in_mod_func
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__math"),"mod_func",_tmp0, _active_event)

            _tmp0 = in_rand_int_func
            _context.assign_on_key(_context.global_store.get_var_if_exists("0__math"),"rand_int_func",_tmp0, _active_event)

        ### USER DEFINED METHODS ###

        def min_func(self,in_nums):

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
                _to_return = self._endpoint_func_call_prefix__waldo__min_func(_root_event,_ctx ,in_nums,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__min_func(self,_active_event,_context,in_nums,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                in_nums = _context.turn_into_waldo_var_if_was_var(in_nums,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                in_nums = _context.turn_into_waldo_var_if_was_var(in_nums,False,_active_event,self._host_uuid,False,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"min_func"),in_nums) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"min_func"),in_nums),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"min_func"),in_nums))




        def max_func(self,in_nums):

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
                _to_return = self._endpoint_func_call_prefix__waldo__max_func(_root_event,_ctx ,in_nums,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__max_func(self,_active_event,_context,in_nums,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                in_nums = _context.turn_into_waldo_var_if_was_var(in_nums,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                in_nums = _context.turn_into_waldo_var_if_was_var(in_nums,False,_active_event,self._host_uuid,False,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"max_func"),in_nums) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"max_func"),in_nums),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"max_func"),in_nums))




        def mod_func(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__mod_func(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__mod_func(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"mod_func"),lhs,rhs) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"mod_func"),lhs,rhs),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"mod_func"),lhs,rhs))




        def rand_int_func(self,a,b):

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
                _to_return = self._endpoint_func_call_prefix__waldo__rand_int_func(_root_event,_ctx ,a,b,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__rand_int_func(self,_active_event,_context,a,b,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False,False)
                b = _context.turn_into_waldo_var_if_was_var(b,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                a = _context.turn_into_waldo_var_if_was_var(a,True,_active_event,self._host_uuid,False,False)
                b = _context.turn_into_waldo_var_if_was_var(b,True,_active_event,self._host_uuid,False,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"rand_int_func"),a,b) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"rand_int_func"),a,b),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("0__math").get_val(_active_event).get_val_on_key(_active_event,"rand_int_func"),a,b))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

    return _MathEndpoint(_waldo_classes,_host_uuid,_conn_obj,*args)
def _MathEndpoint (_waldo_classes,_host_uuid,_conn_obj,*args):
    class __MathEndpoint (_waldo_classes["Endpoint"]):
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

    return __MathEndpoint(_waldo_classes,_host_uuid,_conn_obj,*args)
