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

        def less_than(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__less_than(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__less_than(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) < _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) < _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) < _context.get_val_if_waldo(rhs,_active_event)))




        def less_than_eq(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__less_than_eq(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__less_than_eq(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) <= _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) <= _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) <= _context.get_val_if_waldo(rhs,_active_event)))




        def greater_than(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__greater_than(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__greater_than(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) > _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) > _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) > _context.get_val_if_waldo(rhs,_active_event)))




        def greater_than_eq(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__greater_than_eq(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__greater_than_eq(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) >= _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) >= _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) >= _context.get_val_if_waldo(rhs,_active_event)))




        def not_equal(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__not_equal(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__not_equal(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) != _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) != _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) != _context.get_val_if_waldo(rhs,_active_event)))




        def equal(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__equal(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__equal(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) == _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) == _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) == _context.get_val_if_waldo(rhs,_active_event)))




        def plus_num(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__plus_num(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__plus_num(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(rhs,_active_event)))




        def plus_text(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__plus_text(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__plus_text(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) + _context.get_val_if_waldo(rhs,_active_event)))




        def minus(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__minus(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__minus(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) - _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) - _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) - _context.get_val_if_waldo(rhs,_active_event)))




        def mult(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__mult(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__mult(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) * _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) * _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) * _context.get_val_if_waldo(rhs,_active_event)))




        def div(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__div(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__div(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) / _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) / _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) / _context.get_val_if_waldo(rhs,_active_event)))




        def or_(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__or_(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__or_(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) or _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) or _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) or _context.get_val_if_waldo(rhs,_active_event)))




        def and_(self,lhs,rhs):

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
                _to_return = self._endpoint_func_call_prefix__waldo__and_(_root_event,_ctx ,lhs,rhs,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__and_(self,_active_event,_context,lhs,rhs,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass

            else:
                lhs = _context.turn_into_waldo_var_if_was_var(lhs,True,_active_event,self._host_uuid,False)
                rhs = _context.turn_into_waldo_var_if_was_var(rhs,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) and _context.get_val_if_waldo(rhs,_active_event)) if 0 in _returning_to_public_ext_array else _context.de_waldoify((_context.get_val_if_waldo(lhs,_active_event) and _context.get_val_if_waldo(rhs,_active_event)),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((_context.get_val_if_waldo(lhs,_active_event) and _context.get_val_if_waldo(rhs,_active_event)))




        def in_map(self,map_,key):

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
                _to_return = self._endpoint_func_call_prefix__waldo__in_map(_root_event,_ctx ,map_,key,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__in_map(self,_active_event,_context,map_,key,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                map_ = _context.turn_into_waldo_var_if_was_var(map_,True,_active_event,self._host_uuid,False)
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass

            else:
                map_ = _context.turn_into_waldo_var_if_was_var(map_,False,_active_event,self._host_uuid,False)
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,map_,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.handle_in_check(key,map_,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,map_,_active_event))




        def in_list(self,list_,key):

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
                _to_return = self._endpoint_func_call_prefix__waldo__in_list(_root_event,_ctx ,list_,key,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__in_list(self,_active_event,_context,list_,key,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                list_ = _context.turn_into_waldo_var_if_was_var(list_,True,_active_event,self._host_uuid,False)
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass

            else:
                list_ = _context.turn_into_waldo_var_if_was_var(list_,False,_active_event,self._host_uuid,False)
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,list_,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.handle_in_check(key,list_,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,list_,_active_event))




        def in_waldo_text(self,text,key):

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
                _to_return = self._endpoint_func_call_prefix__waldo__in_waldo_text(_root_event,_ctx ,text,key,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__in_waldo_text(self,_active_event,_context,text,key,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                text = _context.turn_into_waldo_var_if_was_var(text,True,_active_event,self._host_uuid,False)
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass

            else:
                text = _context.turn_into_waldo_var_if_was_var(text,True,_active_event,self._host_uuid,False)
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,text,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.handle_in_check(key,text,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,text,_active_event))




        def in_static_text(self,key):

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
                _to_return = self._endpoint_func_call_prefix__waldo__in_static_text(_root_event,_ctx ,key,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__in_static_text(self,_active_event,_context,key,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass

            else:
                key = _context.turn_into_waldo_var_if_was_var(key,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,'static text' ,_active_event) if 0 in _returning_to_public_ext_array else _context.de_waldoify(_context.handle_in_check(key,'static text' ,_active_event),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(_context.handle_in_check(key,'static text' ,_active_event))



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
