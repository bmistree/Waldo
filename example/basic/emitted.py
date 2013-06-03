# Waldo emitted file


def Requester (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _Requester (_waldo_classes["Endpoint"]):
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

        def increment(self,to_increment):

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
                _to_return = self._endpoint_func_call_prefix__waldo__increment(_root_event,_ctx ,to_increment,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return


        def _endpoint_func_call_prefix__waldo__increment(self,_active_event,_context,to_increment,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                to_increment = _context.turn_into_waldo_var_if_was_var(to_increment,True,_active_event,self._host_uuid,False)

                pass

            else:
                to_increment = _context.turn_into_waldo_var_if_was_var(to_increment,True,_active_event,self._host_uuid,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__other_side_increment(_active_event,_context,to_increment,) if _context.set_msg_send_initialized_bit_false() else None) if 0 in _returning_to_public_ext_array else _context.de_waldoify((self._partner_endpoint_msg_func_call_prefix__waldo__other_side_increment(_active_event,_context,to_increment,) if _context.set_msg_send_initialized_bit_false() else None),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__other_side_increment(_active_event,_context,to_increment,) if _context.set_msg_send_initialized_bit_false() else None))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__other_side_increment(self,_active_event,_context,what_to_increment=None,_returning_to_public_ext_array=None):

            _first_msg = False
            if not _context.set_msg_send_initialized_bit_true():
                # we must load all arguments into sequence local data and perform
                # initialization on sequence local data....start by loading
                # arguments into sequence local data
                # below tells the message send that it must serialize and
                # send all sequence local data.
                _first_msg = True
                if _context.check_and_set_from_endpoint_call_false():

                    _context.sequence_local_store.add_var(
                        "6__what_to_increment", _context.convert_for_seq_local(what_to_increment,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "6__what_to_increment", _context.convert_for_seq_local(what_to_increment,_active_event,self._host_uuid)
                    )

                    pass

                result = self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                    '7__result', # variable's name
                    self._host_uuid, # host uuid var name
                    False,  # if peered, True, otherwise, False
                    
                )

                _context.sequence_local_store.add_var(
                    "7__result",_context.convert_for_seq_local(result,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'perform_increment',_threadsafe_queue, '_first_msg')
            _queue_elem = _threadsafe_queue.get()

            if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                raise self._waldo_classes["BackoutException"]()

            _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

            # apply changes to sequence variables.  (There shouldn't
            # be any, but it's worth getting in practice.)  Note: that
            # the system has already applied deltas for global data.
            _context.sequence_local_store.incorporate_deltas(
                _active_event,_queue_elem.sequence_local_var_store_deltas)

            # send more messages
            _to_exec_next = _queue_elem.to_exec_next_name_msg_field
            if _to_exec_next != None:
                # means that we do not have any additional functions to exec
                _to_exec = getattr(self,_to_exec_next)
                _to_exec(_active_event,_context)
            else:
                # end of sequence: reset to_reply_with_uuid in context.  we do
                # this so that if we go on to execute another message sequence
                # following this one, then the message sequence will be viewed as
                # a new message sequence, rather than the continuation of a
                # previous one.
                _context.reset_to_reply_with()


            return _context.sequence_local_store.get_var_if_exists("7__result")

        ### User-defined message receive blocks ###

    return _Requester(_waldo_classes,_host_uuid,_conn_obj,*args)
def Incrementer (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _Incrementer (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,amt):

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
                '3__amt_to_increment_by',self._waldo_classes["WaldoNumVariable"](  # the type of waldo variable to create
                '3__amt_to_increment_by', # variable's name
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
                _to_return = self._onCreate(_root_event,_ctx ,amt,[])
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

        def _onCreate(self,_active_event,_context,amt,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                amt = _context.turn_into_waldo_var_if_was_var(amt,True,_active_event,self._host_uuid,False)

                pass

            else:
                amt = _context.turn_into_waldo_var_if_was_var(amt,True,_active_event,self._host_uuid,False)

                pass

            _tmp0 = amt
            if not _context.assign(_context.global_store.get_var_if_exists("3__amt_to_increment_by"),_tmp0,_active_event):
                pass

        ### USER DEFINED METHODS ###
        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__perform_increment(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = (_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("6__what_to_increment"),_active_event) + _context.get_val_if_waldo(_context.global_store.get_var_if_exists("3__amt_to_increment_by"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("7__result"),_tmp0,_active_event):
                pass




            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out
                    raise self._waldo_classes["BackoutException"]()

                _context.set_to_reply_with(_queue_elem.reply_with_msg_field)

                # apply changes to sequence variables.  Note: that
                # the system has already applied deltas for global data.
                _context.sequence_local_store.incorporate_deltas(
                    _active_event,_queue_elem.sequence_local_var_store_deltas)

                # send more messages
                _to_exec_next = _queue_elem.to_exec_next_name_msg_field
                if _to_exec_next != None:
                    # means that we do not have any additional functions to exec
                    _to_exec = getattr(self,_to_exec_next)
                    _to_exec(_active_event,_context)


    return _Incrementer(_waldo_classes,_host_uuid,_conn_obj,*args)
