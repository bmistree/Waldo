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
                '0__global_txt',self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '0__global_txt', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo('a' ,_active_event)
            ))

            self._global_var_store.add_var(
                '1__global_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '1__global_num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(30 ,_active_event)
            ))

            self._global_var_store.add_var(
                '2__global_tf',self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                '2__global_tf', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(False ,_active_event)
            ))

            self._global_var_store.add_var(
                '3__global_list',self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '3__global_list', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                [2 ,4 ,6 ,]),_active_event)
            ))

            self._global_var_store.add_var(
                '4__global_map',self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '4__global_map', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(True ,_active_event): _context.get_val_if_waldo(100 ,_active_event),
            _context.get_val_if_waldo(False ,_active_event): _context.get_val_if_waldo(93 ,_active_event),
            }),_active_event)
            ))

            self._global_var_store.add_var(
                '5__global_other_num',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '5__global_other_num', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(_context.global_store.get_var_if_exists("1__global_num"),_active_event)
            ))

            self._global_var_store.add_var(
                '6__global_other_list',self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '6__global_other_list', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(_context.global_store.get_var_if_exists("3__global_list"),_active_event)
            ))

            self._waldo_classes["Endpoint"].__init__(self,_waldo_classes,_host_uuid,_conn_obj,self._global_var_store)



            # local endpoint's initialization has succeeded, tell other side that
            # we're done initializing.
            self._this_side_ready()


        ### OnCreate method

        # no oncreate defined to emit method for 
        ### USER DEFINED METHODS ###

        def return_global_vars(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__return_global_vars(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__return_global_vars(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__global_txt") if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("0__global_txt"),_active_event),_context.global_store.get_var_if_exists("1__global_num") if 1 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("1__global_num"),_active_event),_context.global_store.get_var_if_exists("2__global_tf") if 2 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("2__global_tf"),_active_event),_context.global_store.get_var_if_exists("3__global_list") if 3 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("3__global_list"),_active_event),_context.global_store.get_var_if_exists("4__global_map") if 4 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("4__global_map"),_active_event),_context.global_store.get_var_if_exists("5__global_other_num") if 5 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("5__global_other_num"),_active_event),_context.global_store.get_var_if_exists("6__global_other_list") if 6 in _returning_to_public_ext_array else _context.de_waldoify(_context.global_store.get_var_if_exists("6__global_other_list"),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.global_store.get_var_if_exists("0__global_txt"),_context.global_store.get_var_if_exists("1__global_num"),_context.global_store.get_var_if_exists("2__global_tf"),_context.global_store.get_var_if_exists("3__global_list"),_context.global_store.get_var_if_exists("4__global_map"),_context.global_store.get_var_if_exists("5__global_other_num"),_context.global_store.get_var_if_exists("6__global_other_list"))




        def return_local_vars(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__return_local_vars(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__return_local_vars(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            local_txt = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '8__local_txt', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo('a' ,_active_event)
            )

            local_num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '9__local_num', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(30 ,_active_event)
            )

            local_tf = self._waldo_classes["WaldoTrueFalseVariable"](  # the type of waldo variable to create
                '10__local_tf', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(False ,_active_event)
            )

            local_list = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '11__local_list', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._waldo_classes["WaldoListVariable"]("garbage_name",
                self._host_uuid,
                False,
                [2 ,4 ,6 ,]),_active_event)
            )

            local_map = self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '12__local_map', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(self._waldo_classes["WaldoMapVariable"]("garbage_name",
                self._host_uuid,
                False,
                {_context.get_val_if_waldo(True ,_active_event): _context.get_val_if_waldo(100 ,_active_event),
            _context.get_val_if_waldo(False ,_active_event): _context.get_val_if_waldo(93 ,_active_event),
            }),_active_event)
            )

            local_other_num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '13__local_other_num', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(local_num,_active_event)
            )

            local_other_list = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '14__local_other_list', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(local_list,_active_event)
            )


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(local_txt if 0 in _returning_to_public_ext_array else _context.de_waldoify(local_txt,_active_event),local_num if 1 in _returning_to_public_ext_array else _context.de_waldoify(local_num,_active_event),local_tf if 2 in _returning_to_public_ext_array else _context.de_waldoify(local_tf,_active_event),local_list if 3 in _returning_to_public_ext_array else _context.de_waldoify(local_list,_active_event),local_map if 4 in _returning_to_public_ext_array else _context.de_waldoify(local_map,_active_event),local_other_num if 5 in _returning_to_public_ext_array else _context.de_waldoify(local_other_num,_active_event),local_other_list if 6 in _returning_to_public_ext_array else _context.de_waldoify(local_other_list,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(local_txt,local_num,local_tf,local_list,local_map,local_other_num,local_other_list)



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
