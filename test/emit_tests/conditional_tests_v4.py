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

        def test_if(self,cond_if,if_true,if_false):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_if(_root_event,_ctx ,cond_if,if_true,if_false,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_if(self,_active_event,_context,cond_if,if_true,if_false,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                cond_if = _context.turn_into_waldo_var_if_was_var(cond_if,True,_active_event,self._host_uuid,False)
                if_true = _context.turn_into_waldo_var_if_was_var(if_true,True,_active_event,self._host_uuid,False)
                if_false = _context.turn_into_waldo_var_if_was_var(if_false,True,_active_event,self._host_uuid,False)

                pass

            else:
                cond_if = _context.turn_into_waldo_var_if_was_var(cond_if,True,_active_event,self._host_uuid,False)
                if_true = _context.turn_into_waldo_var_if_was_var(if_true,True,_active_event,self._host_uuid,False)
                if_false = _context.turn_into_waldo_var_if_was_var(if_false,True,_active_event,self._host_uuid,False)

                pass

            if _context.get_val_if_waldo(cond_if,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(if_true if 0 in _returning_to_public_ext_array else _context.de_waldoify(if_true,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(if_true)



                pass



            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(if_false if 0 in _returning_to_public_ext_array else _context.de_waldoify(if_false,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(if_false)




        def test_else_if(self,cond_if,return_if,cond_else_if_a,return_else_if_a,cond_else_if_b,return_else_if_b,cond_else_if_c,return_else_if_c,cond_else_if_d,return_else_if_d,cond_else_if_e,return_else_if_e,cond_else_if_f,return_else_if_f,return_else,incorrect_return):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_else_if(_root_event,_ctx ,cond_if,return_if,cond_else_if_a,return_else_if_a,cond_else_if_b,return_else_if_b,cond_else_if_c,return_else_if_c,cond_else_if_d,return_else_if_d,cond_else_if_e,return_else_if_e,cond_else_if_f,return_else_if_f,return_else,incorrect_return,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_else_if(self,_active_event,_context,cond_if,return_if,cond_else_if_a,return_else_if_a,cond_else_if_b,return_else_if_b,cond_else_if_c,return_else_if_c,cond_else_if_d,return_else_if_d,cond_else_if_e,return_else_if_e,cond_else_if_f,return_else_if_f,return_else,incorrect_return,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                cond_if = _context.turn_into_waldo_var_if_was_var(cond_if,True,_active_event,self._host_uuid,False)
                return_if = _context.turn_into_waldo_var_if_was_var(return_if,True,_active_event,self._host_uuid,False)
                cond_else_if_a = _context.turn_into_waldo_var_if_was_var(cond_else_if_a,True,_active_event,self._host_uuid,False)
                return_else_if_a = _context.turn_into_waldo_var_if_was_var(return_else_if_a,True,_active_event,self._host_uuid,False)
                cond_else_if_b = _context.turn_into_waldo_var_if_was_var(cond_else_if_b,True,_active_event,self._host_uuid,False)
                return_else_if_b = _context.turn_into_waldo_var_if_was_var(return_else_if_b,True,_active_event,self._host_uuid,False)
                cond_else_if_c = _context.turn_into_waldo_var_if_was_var(cond_else_if_c,True,_active_event,self._host_uuid,False)
                return_else_if_c = _context.turn_into_waldo_var_if_was_var(return_else_if_c,True,_active_event,self._host_uuid,False)
                cond_else_if_d = _context.turn_into_waldo_var_if_was_var(cond_else_if_d,True,_active_event,self._host_uuid,False)
                return_else_if_d = _context.turn_into_waldo_var_if_was_var(return_else_if_d,True,_active_event,self._host_uuid,False)
                cond_else_if_e = _context.turn_into_waldo_var_if_was_var(cond_else_if_e,True,_active_event,self._host_uuid,False)
                return_else_if_e = _context.turn_into_waldo_var_if_was_var(return_else_if_e,True,_active_event,self._host_uuid,False)
                cond_else_if_f = _context.turn_into_waldo_var_if_was_var(cond_else_if_f,True,_active_event,self._host_uuid,False)
                return_else_if_f = _context.turn_into_waldo_var_if_was_var(return_else_if_f,True,_active_event,self._host_uuid,False)
                return_else = _context.turn_into_waldo_var_if_was_var(return_else,True,_active_event,self._host_uuid,False)
                incorrect_return = _context.turn_into_waldo_var_if_was_var(incorrect_return,True,_active_event,self._host_uuid,False)

                pass

            else:
                cond_if = _context.turn_into_waldo_var_if_was_var(cond_if,True,_active_event,self._host_uuid,False)
                return_if = _context.turn_into_waldo_var_if_was_var(return_if,True,_active_event,self._host_uuid,False)
                cond_else_if_a = _context.turn_into_waldo_var_if_was_var(cond_else_if_a,True,_active_event,self._host_uuid,False)
                return_else_if_a = _context.turn_into_waldo_var_if_was_var(return_else_if_a,True,_active_event,self._host_uuid,False)
                cond_else_if_b = _context.turn_into_waldo_var_if_was_var(cond_else_if_b,True,_active_event,self._host_uuid,False)
                return_else_if_b = _context.turn_into_waldo_var_if_was_var(return_else_if_b,True,_active_event,self._host_uuid,False)
                cond_else_if_c = _context.turn_into_waldo_var_if_was_var(cond_else_if_c,True,_active_event,self._host_uuid,False)
                return_else_if_c = _context.turn_into_waldo_var_if_was_var(return_else_if_c,True,_active_event,self._host_uuid,False)
                cond_else_if_d = _context.turn_into_waldo_var_if_was_var(cond_else_if_d,True,_active_event,self._host_uuid,False)
                return_else_if_d = _context.turn_into_waldo_var_if_was_var(return_else_if_d,True,_active_event,self._host_uuid,False)
                cond_else_if_e = _context.turn_into_waldo_var_if_was_var(cond_else_if_e,True,_active_event,self._host_uuid,False)
                return_else_if_e = _context.turn_into_waldo_var_if_was_var(return_else_if_e,True,_active_event,self._host_uuid,False)
                cond_else_if_f = _context.turn_into_waldo_var_if_was_var(cond_else_if_f,True,_active_event,self._host_uuid,False)
                return_else_if_f = _context.turn_into_waldo_var_if_was_var(return_else_if_f,True,_active_event,self._host_uuid,False)
                return_else = _context.turn_into_waldo_var_if_was_var(return_else,True,_active_event,self._host_uuid,False)
                incorrect_return = _context.turn_into_waldo_var_if_was_var(incorrect_return,True,_active_event,self._host_uuid,False)

                pass

            if _context.get_val_if_waldo(cond_if,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_if if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_if,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_if)



                pass

            elif _context.get_val_if_waldo(cond_else_if_a,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else_if_a if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else_if_a,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else_if_a)



                pass

            elif _context.get_val_if_waldo(cond_else_if_b,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else_if_b if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else_if_b,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else_if_b)



                pass

            elif _context.get_val_if_waldo(cond_else_if_c,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else_if_c if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else_if_c,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else_if_c)



                pass

            elif _context.get_val_if_waldo(cond_else_if_d,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else_if_d if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else_if_d,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else_if_d)



                pass

            elif _context.get_val_if_waldo(cond_else_if_e,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else_if_e if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else_if_e,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else_if_e)



                pass

            elif _context.get_val_if_waldo(cond_else_if_f,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else_if_f if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else_if_f,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else_if_f)



                pass

            else:

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else)



                pass



            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(incorrect_return if 0 in _returning_to_public_ext_array else _context.de_waldoify(incorrect_return,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(incorrect_return)




        def test_if_else(self,cond_if,return_if,return_else,incorrect_number):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_if_else(_root_event,_ctx ,cond_if,return_if,return_else,incorrect_number,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_if_else(self,_active_event,_context,cond_if,return_if,return_else,incorrect_number,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                cond_if = _context.turn_into_waldo_var_if_was_var(cond_if,True,_active_event,self._host_uuid,False)
                return_if = _context.turn_into_waldo_var_if_was_var(return_if,True,_active_event,self._host_uuid,False)
                return_else = _context.turn_into_waldo_var_if_was_var(return_else,True,_active_event,self._host_uuid,False)
                incorrect_number = _context.turn_into_waldo_var_if_was_var(incorrect_number,True,_active_event,self._host_uuid,False)

                pass

            else:
                cond_if = _context.turn_into_waldo_var_if_was_var(cond_if,True,_active_event,self._host_uuid,False)
                return_if = _context.turn_into_waldo_var_if_was_var(return_if,True,_active_event,self._host_uuid,False)
                return_else = _context.turn_into_waldo_var_if_was_var(return_else,True,_active_event,self._host_uuid,False)
                incorrect_number = _context.turn_into_waldo_var_if_was_var(incorrect_number,True,_active_event,self._host_uuid,False)

                pass

            if _context.get_val_if_waldo(cond_if,_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_if if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_if,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_if)



                pass

            else:

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_else if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_else)



                pass



            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(incorrect_number if 0 in _returning_to_public_ext_array else _context.de_waldoify(incorrect_number,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(incorrect_number)




        def test_boolean_logic(self,a_or1,a_or2,b_and1,b_and2,return_if,return_else):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_boolean_logic(_root_event,_ctx ,a_or1,a_or2,b_and1,b_and2,return_if,return_else,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_boolean_logic(self,_active_event,_context,a_or1,a_or2,b_and1,b_and2,return_if,return_else,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                a_or1 = _context.turn_into_waldo_var_if_was_var(a_or1,True,_active_event,self._host_uuid,False)
                a_or2 = _context.turn_into_waldo_var_if_was_var(a_or2,True,_active_event,self._host_uuid,False)
                b_and1 = _context.turn_into_waldo_var_if_was_var(b_and1,True,_active_event,self._host_uuid,False)
                b_and2 = _context.turn_into_waldo_var_if_was_var(b_and2,True,_active_event,self._host_uuid,False)
                return_if = _context.turn_into_waldo_var_if_was_var(return_if,True,_active_event,self._host_uuid,False)
                return_else = _context.turn_into_waldo_var_if_was_var(return_else,True,_active_event,self._host_uuid,False)

                pass

            else:
                a_or1 = _context.turn_into_waldo_var_if_was_var(a_or1,True,_active_event,self._host_uuid,False)
                a_or2 = _context.turn_into_waldo_var_if_was_var(a_or2,True,_active_event,self._host_uuid,False)
                b_and1 = _context.turn_into_waldo_var_if_was_var(b_and1,True,_active_event,self._host_uuid,False)
                b_and2 = _context.turn_into_waldo_var_if_was_var(b_and2,True,_active_event,self._host_uuid,False)
                return_if = _context.turn_into_waldo_var_if_was_var(return_if,True,_active_event,self._host_uuid,False)
                return_else = _context.turn_into_waldo_var_if_was_var(return_else,True,_active_event,self._host_uuid,False)

                pass

            if _context.get_val_if_waldo((_context.get_val_if_waldo((_context.get_val_if_waldo(a_or1,_active_event) or _context.get_val_if_waldo(a_or2,_active_event)),_active_event) and _context.get_val_if_waldo((_context.get_val_if_waldo(b_and1,_active_event) and _context.get_val_if_waldo(b_and2,_active_event)),_active_event)),_active_event):

                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(return_if if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_if,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(return_if)



                pass



            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(return_else if 0 in _returning_to_public_ext_array else _context.de_waldoify(return_else,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(return_else)




        def many_statements_in_if_else_if_else(self,if_cond,else_if_cond,if_base,else_if_base,else_base,incorrect_number):

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
                _to_return = self._endpoint_func_call_prefix__waldo__many_statements_in_if_else_if_else(_root_event,_ctx ,if_cond,else_if_cond,if_base,else_if_base,else_base,incorrect_number,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__many_statements_in_if_else_if_else(self,_active_event,_context,if_cond,else_if_cond,if_base,else_if_base,else_base,incorrect_number,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                if_cond = _context.turn_into_waldo_var_if_was_var(if_cond,True,_active_event,self._host_uuid,False)
                else_if_cond = _context.turn_into_waldo_var_if_was_var(else_if_cond,True,_active_event,self._host_uuid,False)
                if_base = _context.turn_into_waldo_var_if_was_var(if_base,True,_active_event,self._host_uuid,False)
                else_if_base = _context.turn_into_waldo_var_if_was_var(else_if_base,True,_active_event,self._host_uuid,False)
                else_base = _context.turn_into_waldo_var_if_was_var(else_base,True,_active_event,self._host_uuid,False)
                incorrect_number = _context.turn_into_waldo_var_if_was_var(incorrect_number,True,_active_event,self._host_uuid,False)

                pass

            else:
                if_cond = _context.turn_into_waldo_var_if_was_var(if_cond,True,_active_event,self._host_uuid,False)
                else_if_cond = _context.turn_into_waldo_var_if_was_var(else_if_cond,True,_active_event,self._host_uuid,False)
                if_base = _context.turn_into_waldo_var_if_was_var(if_base,True,_active_event,self._host_uuid,False)
                else_if_base = _context.turn_into_waldo_var_if_was_var(else_if_base,True,_active_event,self._host_uuid,False)
                else_base = _context.turn_into_waldo_var_if_was_var(else_base,True,_active_event,self._host_uuid,False)
                incorrect_number = _context.turn_into_waldo_var_if_was_var(incorrect_number,True,_active_event,self._host_uuid,False)

                pass

            if _context.get_val_if_waldo(if_cond,_active_event):
                _tmp0 = (_context.get_val_if_waldo(if_base,_active_event) + _context.get_val_if_waldo(1 ,_active_event))
                if not _context.assign(if_base,_tmp0,_active_event):
                    if_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo(if_base,_active_event) + _context.get_val_if_waldo(2 ,_active_event))
                if not _context.assign(if_base,_tmp0,_active_event):
                    if_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo(if_base,_active_event) + _context.get_val_if_waldo(5 ,_active_event))
                if not _context.assign(if_base,_tmp0,_active_event):
                    if_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo((_context.get_val_if_waldo(3 ,_active_event) * _context.get_val_if_waldo(4 ,_active_event)),_active_event) + _context.get_val_if_waldo(if_base,_active_event))
                if not _context.assign(if_base,_tmp0,_active_event):
                    if_base = _tmp0


                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(if_base if 0 in _returning_to_public_ext_array else _context.de_waldoify(if_base,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(if_base)



                pass

            elif _context.get_val_if_waldo(else_if_cond,_active_event):
                _tmp0 = (_context.get_val_if_waldo(else_if_base,_active_event) + _context.get_val_if_waldo(1 ,_active_event))
                if not _context.assign(else_if_base,_tmp0,_active_event):
                    else_if_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo(else_if_base,_active_event) + _context.get_val_if_waldo(2 ,_active_event))
                if not _context.assign(else_if_base,_tmp0,_active_event):
                    else_if_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo(else_if_base,_active_event) + _context.get_val_if_waldo(5 ,_active_event))
                if not _context.assign(else_if_base,_tmp0,_active_event):
                    else_if_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo((_context.get_val_if_waldo(3 ,_active_event) * _context.get_val_if_waldo(4 ,_active_event)),_active_event) + _context.get_val_if_waldo(else_if_base,_active_event))
                if not _context.assign(else_if_base,_tmp0,_active_event):
                    else_if_base = _tmp0


                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(else_if_base if 0 in _returning_to_public_ext_array else _context.de_waldoify(else_if_base,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(else_if_base)



                pass

            else:
                _tmp0 = (_context.get_val_if_waldo(else_base,_active_event) + _context.get_val_if_waldo(1 ,_active_event))
                if not _context.assign(else_base,_tmp0,_active_event):
                    else_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo(else_base,_active_event) + _context.get_val_if_waldo(2 ,_active_event))
                if not _context.assign(else_base,_tmp0,_active_event):
                    else_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo(else_base,_active_event) + _context.get_val_if_waldo(5 ,_active_event))
                if not _context.assign(else_base,_tmp0,_active_event):
                    else_base = _tmp0

                _tmp0 = (_context.get_val_if_waldo((_context.get_val_if_waldo(3 ,_active_event) * _context.get_val_if_waldo(4 ,_active_event)),_active_event) + _context.get_val_if_waldo(else_base,_active_event))
                if not _context.assign(else_base,_tmp0,_active_event):
                    else_base = _tmp0


                if _returning_to_public_ext_array != None:
                    # must de-waldo-ify objects before passing back
                    return _context.flatten_into_single_return_tuple(else_base if 0 in _returning_to_public_ext_array else _context.de_waldoify(else_base,_active_event))


                # otherwise, use regular return mechanism... do not de-waldo-ify
                return _context.flatten_into_single_return_tuple(else_base)



                pass



            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(incorrect_number if 0 in _returning_to_public_ext_array else _context.de_waldoify(incorrect_number,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(incorrect_number)




        def test_empty_if_body(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_empty_if_body(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_empty_if_body(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            if _context.get_val_if_waldo(True ,_active_event):

                pass




        def test_empty_else_if_body(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_empty_else_if_body(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_empty_else_if_body(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            if _context.get_val_if_waldo(False ,_active_event):

                pass

            elif _context.get_val_if_waldo(True ,_active_event):

                pass




        def test_empty_else_body(self):

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
                _to_return = self._endpoint_func_call_prefix__waldo__test_empty_else_body(_root_event,_ctx ,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__test_empty_else_body(self,_active_event,_context,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():

                pass

            else:

                pass

            if _context.get_val_if_waldo(False ,_active_event):

                pass

            elif _context.get_val_if_waldo(False ,_active_event):

                pass

            else:

                pass



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
