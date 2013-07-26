# Waldo emitted file


def Test (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _Test (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,CA_pt):

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
                '0__CA',self._waldo_classes["WaldoEndpointVariable"](  # the type of waldo variable to create
                '0__CA', # variable's name
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
                try:
                    _to_return = self._onCreate(_root_event,_ctx ,CA_pt,[])
                except self._waldo_classes["BackoutException"]:
                    pass

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

        def _onCreate(self,_active_event,_context,CA_pt,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                CA_pt = _context.turn_into_waldo_var_if_was_var(CA_pt,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                CA_pt = _context.turn_into_waldo_var_if_was_var(CA_pt,True,_active_event,self._host_uuid,False,False)

                pass

            _tmp0 = CA_pt
            if not _context.assign(_context.global_store.get_var_if_exists("0__CA"),_tmp0,_active_event):
                pass

        ### USER DEFINED METHODS ###

        def print_cert(self,request):

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
                try:
                    _to_return = self._endpoint_func_call_prefix__waldo__print_cert(_root_event,_ctx ,request,[])
                except self._waldo_classes["BackoutException"]:
                    pass

                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return
                elif isinstance(_commit_resp,self._waldo_classes["StopRootCallResult"]):
                    raise self._waldo_classes["StoppedException"]()



        def _endpoint_func_call_prefix__waldo__print_cert(self,_active_event,_context,request,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                request = _context.turn_into_waldo_var_if_was_var(request,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                request = _context.turn_into_waldo_var_if_was_var(request,True,_active_event,self._host_uuid,False,False)

                pass

            cert = _context.get_val_if_waldo(_context.hide_endpoint_call(_active_event,_context,_context.get_val_if_waldo(_context.global_store.get_var_if_exists("0__CA"),_active_event),"req_to_cert",request,),_active_event)

            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple(cert if 0 in _returning_to_public_ext_array else _context.de_waldoify(cert,_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple(cert)



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

    return _Test(_waldo_classes,_host_uuid,_conn_obj,*args)
def _Test (_waldo_classes,_host_uuid,_conn_obj,*args):
    class __Test (_waldo_classes["Endpoint"]):
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

    return __Test(_waldo_classes,_host_uuid,_conn_obj,*args)
