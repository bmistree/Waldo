# Waldo emitted file


def Manager (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _Manager (_waldo_classes["Endpoint"]):
        def __init__(self,_waldo_classes,_host_uuid,_conn_obj,outside_generate):

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
                '9__certificates',self._waldo_classes["WaldoMapVariable"](  # the type of waldo variable to create
                '9__certificates', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ))

            self._global_var_store.add_var(
                '10__generate',self._waldo_classes["WaldoFunctionVariable"](  # the type of waldo variable to create
                '10__generate', # variable's name
                _host_uuid, # host uuid var name
                False,  # if peered, True, otherwise, False
                
            ).set_external_args_array([]))

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
                _to_return = self._onCreate(_root_event,_ctx ,outside_generate,[])
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

        def _onCreate(self,_active_event,_context,outside_generate,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                outside_generate = _context.func_turn_into_waldo_var(outside_generate,True,_active_event,self._host_uuid,False,[],False)

                pass

            else:
                outside_generate = _context.func_turn_into_waldo_var(outside_generate,True,_active_event,self._host_uuid,False,[],False)

                pass

            _tmp0 = outside_generate
            if not _context.assign(_context.global_store.get_var_if_exists("10__generate"),_tmp0,_active_event):
                pass

        ### USER DEFINED METHODS ###
        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        ### User-defined message receive blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__give_key(self,_active_event,_context,_returning_to_public_ext_array=None):

            certificate = ""
            key = ""
            _tmp0,_tmp1 = _context.call_func_obj(_active_event,_context.global_store.get_var_if_exists("10__generate"),_context.sequence_local_store.get_var_if_exists("14__countryName"),_context.sequence_local_store.get_var_if_exists("15__stateOrProvinceName"),_context.sequence_local_store.get_var_if_exists("16__localityName"),_context.sequence_local_store.get_var_if_exists("17__organizationName"),_context.sequence_local_store.get_var_if_exists("18__organizationalUnitName"),_context.sequence_local_store.get_var_if_exists("19__commonName"))
            if not _context.assign(certificate,_tmp0,_active_event):
                certificate = _tmp0
            if not _context.assign(key,_tmp1,_active_event):
                key = _tmp1

            entry = self._waldo_classes["WaldoSingleThreadUserStructVariable"]("25__entry",self._host_uuid,False,{"certificate": "", "key": "", })
            _tmp0 = certificate
            _context.assign_on_key(entry,"certificate",_tmp0, _active_event)

            _tmp0 = key
            _context.assign_on_key(entry,"key",_tmp0, _active_event)

            _tmp0 = entry
            _context.assign_on_key(_context.global_store.get_var_if_exists("9__certificates"),_context.sequence_local_store.get_var_if_exists("13__uuid"),_tmp0, _active_event)

            _tmp0 = entry
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("20__cert_and_key"),_tmp0,_active_event):
                pass




            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out: 
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


        def _partner_endpoint_msg_func_call_prefix__waldo__send_key(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.global_store.get_var_if_exists("9__certificates").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("27__uuid"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("28__cert_and_key"),_tmp0,_active_event):
                pass




            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out: 
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


        def _partner_endpoint_msg_func_call_prefix__waldo__send_information(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.global_store.get_var_if_exists("9__certificates").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("31__uuid"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("32__cert_and_key"),_tmp0,_active_event):
                pass




            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out: 
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


        def _partner_endpoint_msg_func_call_prefix__waldo__exchange_key(self,_active_event,_context,_returning_to_public_ext_array=None):

            _tmp0 = _context.global_store.get_var_if_exists("9__certificates").get_val(_active_event).get_val_on_key(_active_event,_context.get_val_if_waldo(_context.sequence_local_store.get_var_if_exists("35__uuid"),_active_event))
            if not _context.assign(_context.sequence_local_store.get_var_if_exists("36__cert_and_key"),_tmp0,_active_event):
                pass




            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,None,_threadsafe_queue,False)
            # must wait on the result of the call before returning

            if None != None:
                # means that we have another sequence item to execute next

                _queue_elem = _threadsafe_queue.get()




                if isinstance(_queue_elem,self._waldo_classes["BackoutBeforeReceiveMessageResult"]):
                    # back everything out: 
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


    return _Manager(_waldo_classes,_host_uuid,_conn_obj,*args)
def Client (_waldo_classes,_host_uuid,_conn_obj,*args):
    class _Client (_waldo_classes["Endpoint"]):
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

        def get_new_key(self,uuid,countryName,stateOrProvinceName,localityName,organizationName,organizationalUnitName,commonName):

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
                _to_return = self._endpoint_func_call_prefix__waldo__get_new_key(_root_event,_ctx ,uuid,countryName,stateOrProvinceName,localityName,organizationName,organizationalUnitName,commonName,[])
                # try committing root event
                _root_event.request_commit()
                _commit_resp = _root_event.event_complete_queue.get()
                if isinstance(_commit_resp,self._waldo_classes["CompleteRootCallResult"]):
                    # means it isn't a backout message: we're done
                    return _to_return
                elif isinstance(_commit_resp,self._waldo_classes["StopRootCallResult"]):
                    raise self._waldo_classes["StoppedException"]()



        def _endpoint_func_call_prefix__waldo__get_new_key(self,_active_event,_context,uuid,countryName,stateOrProvinceName,localityName,organizationName,organizationalUnitName,commonName,_returning_to_public_ext_array=None):
            if _context.check_and_set_from_endpoint_call_false():
                uuid = _context.turn_into_waldo_var_if_was_var(uuid,True,_active_event,self._host_uuid,False,False)
                countryName = _context.turn_into_waldo_var_if_was_var(countryName,True,_active_event,self._host_uuid,False,False)
                stateOrProvinceName = _context.turn_into_waldo_var_if_was_var(stateOrProvinceName,True,_active_event,self._host_uuid,False,False)
                localityName = _context.turn_into_waldo_var_if_was_var(localityName,True,_active_event,self._host_uuid,False,False)
                organizationName = _context.turn_into_waldo_var_if_was_var(organizationName,True,_active_event,self._host_uuid,False,False)
                organizationalUnitName = _context.turn_into_waldo_var_if_was_var(organizationalUnitName,True,_active_event,self._host_uuid,False,False)
                commonName = _context.turn_into_waldo_var_if_was_var(commonName,True,_active_event,self._host_uuid,False,False)

                pass

            else:
                uuid = _context.turn_into_waldo_var_if_was_var(uuid,True,_active_event,self._host_uuid,False,False)
                countryName = _context.turn_into_waldo_var_if_was_var(countryName,True,_active_event,self._host_uuid,False,False)
                stateOrProvinceName = _context.turn_into_waldo_var_if_was_var(stateOrProvinceName,True,_active_event,self._host_uuid,False,False)
                localityName = _context.turn_into_waldo_var_if_was_var(localityName,True,_active_event,self._host_uuid,False,False)
                organizationName = _context.turn_into_waldo_var_if_was_var(organizationName,True,_active_event,self._host_uuid,False,False)
                organizationalUnitName = _context.turn_into_waldo_var_if_was_var(organizationalUnitName,True,_active_event,self._host_uuid,False,False)
                commonName = _context.turn_into_waldo_var_if_was_var(commonName,True,_active_event,self._host_uuid,False,False)

                pass


            if _returning_to_public_ext_array != None:
                # must de-waldo-ify objects before passing back
                return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__get_new_cert_and_key(_active_event,_context,uuid,countryName,stateOrProvinceName,localityName,organizationName,organizationalUnitName,commonName,) if _context.set_msg_send_initialized_bit_false() else None) if 0 in _returning_to_public_ext_array else _context.de_waldoify((self._partner_endpoint_msg_func_call_prefix__waldo__get_new_cert_and_key(_active_event,_context,uuid,countryName,stateOrProvinceName,localityName,organizationName,organizationalUnitName,commonName,) if _context.set_msg_send_initialized_bit_false() else None),_active_event))


            # otherwise, use regular return mechanism... do not de-waldo-ify
            return _context.flatten_into_single_return_tuple((self._partner_endpoint_msg_func_call_prefix__waldo__get_new_cert_and_key(_active_event,_context,uuid,countryName,stateOrProvinceName,localityName,organizationName,organizationalUnitName,commonName,) if _context.set_msg_send_initialized_bit_false() else None))



        ### USER DEFINED SEQUENCE BLOCKS ###

        ### User-defined message send blocks ###

        def _partner_endpoint_msg_func_call_prefix__waldo__get_new_cert_and_key(self,_active_event,_context,uuid=None,countryName=None,stateOrProvinceName=None,localityName=None,organizationName=None,organizationalUnitName=None,commonName=None,_returning_to_public_ext_array=None):

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
                        "13__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "14__countryName", _context.convert_for_seq_local(countryName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "15__stateOrProvinceName", _context.convert_for_seq_local(stateOrProvinceName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "16__localityName", _context.convert_for_seq_local(localityName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "17__organizationName", _context.convert_for_seq_local(organizationName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "18__organizationalUnitName", _context.convert_for_seq_local(organizationalUnitName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "19__commonName", _context.convert_for_seq_local(commonName,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "13__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "14__countryName", _context.convert_for_seq_local(countryName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "15__stateOrProvinceName", _context.convert_for_seq_local(stateOrProvinceName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "16__localityName", _context.convert_for_seq_local(localityName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "17__organizationName", _context.convert_for_seq_local(organizationName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "18__organizationalUnitName", _context.convert_for_seq_local(organizationalUnitName,_active_event,self._host_uuid)
                    )

                    _context.sequence_local_store.add_var(
                        "19__commonName", _context.convert_for_seq_local(commonName,_active_event,self._host_uuid)
                    )

                    pass

                cert_and_key = self._waldo_classes["WaldoSingleThreadUserStructVariable"]("20__cert_and_key",self._host_uuid,False,{"certificate": "", "key": "", })
                _context.sequence_local_store.add_var(
                    "20__cert_and_key",_context.convert_for_seq_local(cert_and_key,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'give_key',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("20__cert_and_key")

        def _partner_endpoint_msg_func_call_prefix__waldo__get_key(self,_active_event,_context,uuid=None,_returning_to_public_ext_array=None):

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
                        "27__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "27__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    pass

                cert_and_key = self._waldo_classes["WaldoSingleThreadUserStructVariable"]("28__cert_and_key",self._host_uuid,False,{"certificate": "", "key": "", })
                _context.sequence_local_store.add_var(
                    "28__cert_and_key",_context.convert_for_seq_local(cert_and_key,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'send_key',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("28__cert_and_key")

        def _partner_endpoint_msg_func_call_prefix__waldo__evaluate_key(self,_active_event,_context,uuid=None,_returning_to_public_ext_array=None):

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
                        "31__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "31__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    pass

                cert_and_key = self._waldo_classes["WaldoSingleThreadUserStructVariable"]("32__cert_and_key",self._host_uuid,False,{"certificate": "", "key": "", })
                _context.sequence_local_store.add_var(
                    "32__cert_and_key",_context.convert_for_seq_local(cert_and_key,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'send_information',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("32__cert_and_key")

        def _partner_endpoint_msg_func_call_prefix__waldo__revoke_key(self,_active_event,_context,uuid=None,_returning_to_public_ext_array=None):

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
                        "35__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    pass

                else:

                    _context.sequence_local_store.add_var(
                        "35__uuid", _context.convert_for_seq_local(uuid,_active_event,self._host_uuid)
                    )

                    pass

                cert_and_key = self._waldo_classes["WaldoSingleThreadUserStructVariable"]("36__cert_and_key",self._host_uuid,False,{"certificate": "", "key": "", })
                _context.sequence_local_store.add_var(
                    "36__cert_and_key",_context.convert_for_seq_local(cert_and_key,_active_event,self._host_uuid))

                pass



            _threadsafe_queue = self._waldo_classes["Queue"].Queue()
            _active_event.issue_partner_sequence_block_call(
                _context,'exchange_key',_threadsafe_queue, '_first_msg')
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


            return _context.sequence_local_store.get_var_if_exists("36__cert_and_key")

        ### User-defined message receive blocks ###

    return _Client(_waldo_classes,_host_uuid,_conn_obj,*args)
