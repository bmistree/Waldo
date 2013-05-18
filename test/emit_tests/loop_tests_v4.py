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

        def range_test(self,base,limit,increment):

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
                _to_return = self._endpoint_func_call_prefix__waldo__range_test(_root_event,_ctx ,base,limit,increment,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__range_test(self,_active_event,_context,base,limit,increment,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                base = _context.turn_into_waldo_var_if_was_var(base,True,_active_event,self._host_uuid,False)
                limit = _context.turn_into_waldo_var_if_was_var(limit,True,_active_event,self._host_uuid,False)
                increment = _context.turn_into_waldo_var_if_was_var(increment,True,_active_event,self._host_uuid,False)

                pass

            else:
                base = _context.turn_into_waldo_var_if_was_var(base,True,_active_event,self._host_uuid,False)
                limit = _context.turn_into_waldo_var_if_was_var(limit,True,_active_event,self._host_uuid,False)
                increment = _context.turn_into_waldo_var_if_was_var(increment,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(base,_active_event),_context.get_val_if_waldo(limit,_active_event),_context.get_val_if_waldo(increment,_active_event)))) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(base,_active_event),_context.get_val_if_waldo(limit,_active_event),_context.get_val_if_waldo(increment,_active_event)))),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(base,_active_event),_context.get_val_if_waldo(limit,_active_event),_context.get_val_if_waldo(increment,_active_event)))))




        def no_increment_range_test(self,base,limit):

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
                _to_return = self._endpoint_func_call_prefix__waldo__no_increment_range_test(_root_event,_ctx ,base,limit,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__no_increment_range_test(self,_active_event,_context,base,limit,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                base = _context.turn_into_waldo_var_if_was_var(base,True,_active_event,self._host_uuid,False)
                limit = _context.turn_into_waldo_var_if_was_var(limit,True,_active_event,self._host_uuid,False)

                pass

            else:
                base = _context.turn_into_waldo_var_if_was_var(base,True,_active_event,self._host_uuid,False)
                limit = _context.turn_into_waldo_var_if_was_var(limit,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(base,_active_event),_context.get_val_if_waldo(limit,_active_event),_context.get_val_if_waldo(1 ,_active_event)))) if 0 in _returning_to_public_ext_array else _context.de_waldoify(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(base,_active_event),_context.get_val_if_waldo(limit,_active_event),_context.get_val_if_waldo(1 ,_active_event)))),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(base,_active_event),_context.get_val_if_waldo(limit,_active_event),_context.get_val_if_waldo(1 ,_active_event)))))




        def test_while_less_than(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_while_less_than(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_while_less_than(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            times_in_loop = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '9__times_in_loop', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            while _context.get_val_if_waldo((_context.get_val_if_waldo(lhs,_active_event) < _context.get_val_if_waldo(rhs,_active_event)),_active_event): 
                _tmp0 = (_context.get_val_if_waldo(times_in_loop,_active_event) + _context.get_val_if_waldo(1 ,_active_event))
                if not _context.assign(times_in_loop,_tmp0,_active_event):
                    times_in_loop = _tmp0

                _tmp0 = (_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(1 ,_active_event))
                if not _context.assign(lhs,_tmp0,_active_event):
                    lhs = _tmp0


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(times_in_loop if 0 in _returning_to_public_ext_array else _context.de_waldoify(times_in_loop,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(times_in_loop)




        def test_empty_while(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_empty_while(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_empty_while(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            while _context.get_val_if_waldo(False ,_active_event): 

                pass



        def range_for_test(self,num_iterations):

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
                _to_return = self._endpoint_func_call_prefix__waldo__range_for_test(_root_event,_ctx ,num_iterations,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__range_for_test(self,_active_event,_context,num_iterations,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                num_iterations = _context.turn_into_waldo_var_if_was_var(num_iterations,True,_active_event,self._host_uuid,False)

                pass

            else:
                num_iterations = _context.turn_into_waldo_var_if_was_var(num_iterations,True,_active_event,self._host_uuid,False)

                pass

            counter = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '12__counter', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            i = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '13__i', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____i in _context.get_for_iter(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(0 ,_active_event),_context.get_val_if_waldo(num_iterations,_active_event),_context.get_val_if_waldo(1 ,_active_event)))),_active_event):
                i.write_val(_active_event,_secret_waldo_for_iter____i)
                _tmp0 = (_context.get_val_if_waldo(counter,_active_event) + _context.get_val_if_waldo(1 ,_active_event))
                if not _context.assign(counter,_tmp0,_active_event):
                    counter = _tmp0


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(counter if 0 in _returning_to_public_ext_array else _context.de_waldoify(counter,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(counter)




        def empty_for_test(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__empty_for_test(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__empty_for_test(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            i = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '15__i', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____i in _context.get_for_iter(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(0 ,_active_event),_context.get_val_if_waldo(2 ,_active_event),_context.get_val_if_waldo(1 ,_active_event)))),_active_event):
                i.write_val(_active_event,_secret_waldo_for_iter____i)

                pass



        def list_iter_for_test(self,list_):

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
                _to_return = self._endpoint_func_call_prefix__waldo__list_iter_for_test(_root_event,_ctx ,list_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__list_iter_for_test(self,_active_event,_context,list_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                list_ = _context.turn_into_waldo_var_if_was_var(list_,True,_active_event,self._host_uuid,False)

                pass

            else:
                list_ = _context.turn_into_waldo_var_if_was_var(list_,False,_active_event,self._host_uuid,False)

                pass

            to_return = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '17__to_return', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            t = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '18__t', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____t in _context.get_for_iter(list_,_active_event):
                t.write_val(_active_event,_secret_waldo_for_iter____t)
                to_return.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo(t,_active_event))

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_return if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_return,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_return)




        def map_iter_for_test(self,map_):

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
                _to_return = self._endpoint_func_call_prefix__waldo__map_iter_for_test(_root_event,_ctx ,map_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__map_iter_for_test(self,_active_event,_context,map_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                map_ = _context.turn_into_waldo_var_if_was_var(map_,True,_active_event,self._host_uuid,False)

                pass

            else:
                map_ = _context.turn_into_waldo_var_if_was_var(map_,False,_active_event,self._host_uuid,False)

                pass

            to_return = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '21__to_return', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            t = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '22__t', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____t in _context.get_for_iter(map_,_active_event):
                t.write_val(_active_event,_secret_waldo_for_iter____t)
                to_return.get_val(_active_event).append_val(_active_event,_context.get_val_if_waldo(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(t,_active_event)),_active_event))

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(to_return if 0 in _returning_to_public_ext_array else _context.de_waldoify(to_return,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(to_return)




        def nested_list_iter_test(self,nested_list):

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
                _to_return = self._endpoint_func_call_prefix__waldo__nested_list_iter_test(_root_event,_ctx ,nested_list,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__nested_list_iter_test(self,_active_event,_context,nested_list,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                nested_list = _context.turn_into_waldo_var_if_was_var(nested_list,True,_active_event,self._host_uuid,False)

                pass

            else:
                nested_list = _context.turn_into_waldo_var_if_was_var(nested_list,False,_active_event,self._host_uuid,False)

                pass

            return_val = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '25__return_val', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            it = self._waldo_classes["WaldoListVariable"](  # the type of waldo variable to create
                '26__it', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____it in _context.get_for_iter(nested_list,_active_event):
                it.write_val(_active_event,_secret_waldo_for_iter____it)
                i = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '27__i', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                for _secret_waldo_for_iter____i in _context.get_for_iter(it,_active_event):
                    i.write_val(_active_event,_secret_waldo_for_iter____i)
                    _tmp0 = (_context.get_val_if_waldo(return_val,_active_event) + _context.get_val_if_waldo(i,_active_event))
                    if not _context.assign(return_val,_tmp0,_active_event):
                        return_val = _tmp0


                    pass


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(return_val if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_val,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(return_val)




        def nested_map_iter_test(self,map_):

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
                _to_return = self._endpoint_func_call_prefix__waldo__nested_map_iter_test(_root_event,_ctx ,map_,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__nested_map_iter_test(self,_active_event,_context,map_,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                map_ = _context.turn_into_waldo_var_if_was_var(map_,True,_active_event,self._host_uuid,False)

                pass

            else:
                map_ = _context.turn_into_waldo_var_if_was_var(map_,False,_active_event,self._host_uuid,False)

                pass

            counter = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '30__counter', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            t1 = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                '31__t1', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____t1 in _context.get_for_iter(map_,_active_event):
                t1.write_val(_active_event,_secret_waldo_for_iter____t1)
                t2 = self._waldo_classes["WaldoTextVariable"](  # the type of waldo variable to create
                    '32__t2', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                for _secret_waldo_for_iter____t2 in _context.get_for_iter(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(t1,_active_event)),_active_event):
                    t2.write_val(_active_event,_secret_waldo_for_iter____t2)
                    map_elem = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                        '33__map_elem', # variable's name
                        self._host_uuid, # host uuid var name
                        False,  # if peered, True, otherwise, False
                        _context.get_val_if_waldo(map_.get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(t1,_active_event)).get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(t2,_active_event)),_active_event)
                    )

                    _tmp0 = (_context.get_val_if_waldo(counter,_active_event) + _context.get_val_if_waldo(map_elem,_active_event))
                    if not _context.assign(counter,_tmp0,_active_event):
                        counter = _tmp0


                    pass


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(counter if 0 in _returning_to_public_ext_array else _context.de_waldoify(counter,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(counter)




        def test_break(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_break(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_break(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            i = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '35__i', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____i in _context.get_for_iter(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(0 ,_active_event),_context.get_val_if_waldo(10 ,_active_event),_context.get_val_if_waldo(1 ,_active_event)))),_active_event):
                i.write_val(_active_event,_secret_waldo_for_iter____i)
                if _context.get_val_if_waldo((_context.get_val_if_waldo(i,_active_event) == _context.get_val_if_waldo(5 ,_active_event)),_active_event):
                    break

                    pass



                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(i,_active_event) == _context.get_val_if_waldo(5 ,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(i,_active_event) == _context.get_val_if_waldo(5 ,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(i,_active_event) == _context.get_val_if_waldo(5 ,_active_event)))




        def test_continue(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_continue(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_continue(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            counter = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '37__counter', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            i = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '38__i', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            )

            for _secret_waldo_for_iter____i in _context.get_for_iter(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(0 ,_active_event),_context.get_val_if_waldo(10 ,_active_event),_context.get_val_if_waldo(1 ,_active_event)))),_active_event):
                i.write_val(_active_event,_secret_waldo_for_iter____i)
                if _context.get_val_if_waldo(_context.handle_in_check(i,self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(0 ,_active_event),_context.get_val_if_waldo(10 ,_active_event),_context.get_val_if_waldo(2 ,_active_event)))),_active_event),_active_event):
                    continue

                    pass


                _tmp0 = (_context.get_val_if_waldo(counter,_active_event) + _context.get_val_if_waldo(i,_active_event))
                if not _context.assign(counter,_tmp0,_active_event):
                    counter = _tmp0


                pass

            expected_num = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '39__expected_num', # variable's name
                self._host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                _context.get_val_if_waldo(0 ,_active_event)
            )

            for _secret_waldo_for_iter____i in _context.get_for_iter(self._waldo_classes["WaldoListVariable"]("garbage",self._host_uuid,False,list(range(_context.get_val_if_waldo(1 ,_active_event),_context.get_val_if_waldo(10 ,_active_event),_context.get_val_if_waldo(2 ,_active_event)))),_active_event):
                i.write_val(_active_event,_secret_waldo_for_iter____i)
                _tmp0 = (_context.get_val_if_waldo(expected_num,_active_event) + _context.get_val_if_waldo(i,_active_event))
                if not _context.assign(expected_num,_tmp0,_active_event):
                    expected_num = _tmp0


                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(expected_num,_active_event) == _context.get_val_if_waldo(counter,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(expected_num,_active_event) == _context.get_val_if_waldo(counter,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(expected_num,_active_event) == _context.get_val_if_waldo(counter,_active_event)))



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
