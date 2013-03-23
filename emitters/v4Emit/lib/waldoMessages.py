import util
from abc import abstractmethod


# FIXME: probably could do better from using a named tuple for messages.
class _Message(object):
    '''
    Endpoint pairs pass messages across the network to each other, for
    instance, to request a sequence block be executed or to forward a
    commit or backout request.  Each of these messages has a different
    structure, but they all subtype from this class.
    '''

    # indices are strings: the values that get put in the subtypes'
    # maps under the index MESSAGE_TYPE_FIELD when the message is
    # converted to a map in its map_to_msg method.  When module is
    # imported, add each subclass to the map.
    SUBTYPE_MAP = {}
    
    # Every single message has this field.  It tells us which _Message
    # subclass to call map_to_msg on to get back a message.
    MESSAGE_TYPE_FIELD = 'msg_type_field'
    EVENT_UUID_FIELD = 'event_uuid_field'
    
    def __init__(self,event_uuid):
        self.event_uuid = event_uuid

    @abstractmethod
    def msg_to_map(self):
        '''
        When ready to send message over the wire, we call msg_to_map
        on it and then pickle it.  msg_to_map returns a map with
        fields in it.  the other side can unpickle the map and then
        convert it into a proper message using map_to_msg.

        Note: each message must have a message type field so that when
        deserializing, we know which class to use.

        @returns {map}
        '''
        util.logger_assert(
            'serialize in _Message is purely virtual')

    @staticmethod
    def map_to_msg(msg_map):
        '''
        @returns {Subclass of _Message}
        '''
        #### DEBUG
        if _Message.MESSAGE_TYPE_FIELD not in msg_map:
            util.logger_assert(
                'Error: received a map that had no message type field.  '  +
                'Do not know which _Message subclass to use to convert it ' +
                'back into a message.')
        #### END DEBUG

        msg_type_field = msg_map[_Message.MESSAGE_TYPE_FIELD]
        msg_subtype = _Message.SUBTYPE_MAP[msg_type_field]
        return msg_subtype.map_to_msg(msg_map)


class _PartnerRequestSequenceBlockMessage(_Message):
    
    MSG_TYPE = 'partner_request_sequence_block_msg'

    NAME_OF_BLOCK_REQUESTING_FIELD = 'name_of_block_requesting_field'
    REPLY_WITH_UUID_FIELD = 'reply_with_uuid_field'
    REPLY_TO_UUID_FIELD = 'reply_to_uuid_field'
    SEQUENCE_LOCAL_VAR_STORE_DELTAS_FIELD = 'sequence_local_store_field'
    PEERED_VAR_STORE_DELTAS_FIELD = 'peered_var_store_field'
    
    def __init__(
        self,event_uuid,name_of_block_requesting,reply_with_uuid,reply_to_uuid,
        global_var_store_deltas,sequence_local_var_store_deltas):
        '''
        For params, @see
        waldoEndpoint._send_partner_message_sequence_block_request.

        +

        @param {dict} sequence_local_var_store_deltas --- For format
        of dict, @see waldoVariableStore.generate_deltas.  Should be
        able to put this dict directly into a _VariableStore
        object to update each of an event's sequnce local data.  @see
        waldoVariableStore._VariableStore.

        @param {dict} sequence_local_var_store_deltas --- For format
        of dict, @see waldoVariableStore.generate_deltas.  Should be
        able to put this dict directly into a _VariableStore
        object to update each of an event's pieces of peered data.
        @see wladoVariableStore._VariableStore.
        '''
        _Message.__init__(self,event_uuid)
        self.name_of_block_requesting = name_of_block_requesting
        self.reply_with_uuid = reply_with_uuid
        self.reply_to_uuid = reply_to_uuid
        self.sequence_local_var_store_deltas = sequence_local_var_store_deltas
        self.global_var_store_deltas = global_var_store_deltas

        
    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid,

            self.NAME_OF_BLOCK_REQUESTING_FIELD: self.name_of_block_requesting,
            self.REPLY_WITH_UUID_FIELD: self.reply_with_uuid,
            self.REPLY_TO_UUID_FIELD: self.reply_to_uuid,
            self.SEQUENCE_LOCAL_VAR_STORE_DELTAS_FIELD: self.sequence_local_var_store_deltas,
            self.PEERED_VAR_STORE_DELTAS_FIELD: self.global_var_store_deltas
            }

    @staticmethod
    def map_to_msg(msg_map):
        return _PartnerRequestSequenceBlockMessage(
            msg_map[_Message.EVENT_UUID_FIELD],
            msg_map[_PartnerRequestSequenceBlockMessage.NAME_OF_BLOCK_REQUESTING_FIELD],
            msg_map[_PartnerRequestSequenceBlockMessage.REPLY_WITH_UUID_FIELD],
            msg_map[_PartnerRequestSequenceBlockMessage.REPLY_TO_UUID_FIELD],
            msg_map[_PartnerRequestSequenceBlockMessage.PEERED_VAR_STORE_DELTAS_FIELD],
            msg_map[_PartnerRequestSequenceBlockMessage.SEQUENCE_LOCAL_VAR_STORE_DELTAS_FIELD])

    
class _PartnerCommitRequestMessage(_Message):
    MSG_TYPE = 'partner_commit_request_message'
    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid
            }

    @staticmethod
    def map_to_msg(msg_map):
        return _PartnerCommitRequestMessage(msg_map[_Message.EVENT_UUID_FIELD])


class _PartnerCompleteCommitRequestMessage(_Message):
    MSG_TYPE = 'partner_complete_commit_request_message'
    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid
            }

    @staticmethod
    def map_to_msg(msg_map):
        return _PartnerCompleteCommitRequestMessage(
            msg_map[_Message.EVENT_UUID_FIELD])


class _PartnerBackoutCommitRequestMessage(_Message):
    MSG_TYPE = 'partner_backout_commit_request_message'
    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid
            }

    @staticmethod
    def map_to_msg(msg_map):
        return _PartnerBackoutCommitRequestMessage(
            msg_map[_Message.EVENT_UUID_FIELD])

    

class _PartnerRemovedSubscriberMessage(_Message):
    MSG_TYPE = 'partner_removed_subscriber_message'
    REMOVED_SUBSCRIBER_UUID_FIELD = 'removed_subscriber_uuid_field'
    HOST_UUID_FIELD = 'host_uuid_field'    
    RESOURCE_UUID_FIELD = 'resource_uuid_field'
    
    def __init__(
        self,event_uuid,removed_subscriber_uuid,host_uuid,resource_uuid):
        _Message.__init__(self,event_uuid)
        self.removed_subscriber_uuid = removed_subscriber_uuid
        self.host_uuid = host_uuid
        self.resource_uuid = resource_uuid
        
    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid,

            self.REMOVED_SUBSCRIBER_UUID_FIELD: self.removed_subscriber_uuid,
            self.HOST_UUID_FIELD: self.host_uuid,            
            self.RESOURCE_UUID_FIELD: self.resource_uuid,
            }

    @staticmethod
    def map_to_msg(msg_map):
        return _PartnerRemovedSubscriberMessage(
            msg_map[_Message.EVENT_UUID_FIELD],
            msg_map[_PartnerRemovedSubscriberMessage.REMOVED_SUBSCRIBER_UUID_FIELD],
            msg_map[_PartnerAdditionalSubscriberMessage.HOST_UUID_FIELD],            
            msg_map[_PartnerRemovedSubscriberMessage.RESOURCE_UUID_FIELD]
            )

class _PartnerAdditionalSubscriberMessage(_Message):
    MSG_TYPE = 'partner_additional_subscriber_message'
    ADDITIONAL_SUBSCRIBER_UUID_FIELD = 'additional_subscriber_uuid_field'
    HOST_UUID_FIELD = 'host_uuid_field'
    RESOURCE_UUID_FIELD = 'resource_uuid_field'
    
    def __init__(
        self,event_uuid,additional_subscriber_uuid,host_uuid,resource_uuid):
        _Message.__init__(self,event_uuid)
        self.additional_subscriber_uuid = additional_subscriber_uuid
        self.host_uuid = host_uuid
        self.resource_uuid = resource_uuid
        
    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid,

            self.ADDITIONAL_SUBSCRIBER_UUID_FIELD: self.additional_subscriber_uuid,
            self.HOST_UUID_FIELD: self.host_uuid,
            self.RESOURCE_UUID_FIELD: self.resource_uuid
            }

    @staticmethod
    def map_to_msg(msg_map):
        return _PartnerAdditionalSubscriberMessage(
            msg_map[_Message.EVENT_UUID_FIELD],
            msg_map[_PartnerAdditionalSubscriberMessage.ADDITIONAL_SUBSCRIBER_UUID_FIELD],
            msg_map[_PartnerAdditionalSubscriberMessage.HOST_UUID_FIELD],
            msg_map[_PartnerAdditionalSubscriberMessage.RESOURCE_UUID_FIELD]
            )
    
class _PartnerFirstPhaseResultMessage(_Message):
    '''
    We use a two-phase commit process when committing events.  A root
    event initiates the first phase of the commit.  When the
    corresponding _ActiveEvents running on hosts throughout the
    network attempt to perform the first phase of the commit, we must
    send their results back to the root.  (So that the root can
    determine when to backout or move on to the second phase of the
    commit.)  

    This message type is used to send the results of attempting the
    first phase of the commit back to a partner.  The partner will
    forward the message to its subscriber, which forwards to its
    subscriber, etc., up until it gets all the way back to the root.

    The first phase was either successful or not successful.
    
    If it was successful, we also pass back a list of endpoint uuids.
    Each of these correspond to endpoints that the root must wait on
    before transitioning to second phase of commit.
    '''

    MSG_TYPE = 'partner_first_phase_resutl_message'

    SENDING_ENDPOINT_UUID_FIELD = 'sending_endpoint'
    SUCCESSFUL_FIELD = 'successful'
    CHILDREN_EVENT_ENDPOINT_UUIDS_FIELD = 'children_endpoint_uuids'
    
    def __init__(
        self,event_uuid,sending_endpoint_uuid,successful,
        children_event_endpoint_uuids=None):
        '''
        @param {uuid} event_uuid ---

        @pararm {uuid} sending_endpoint_uuid --- The uuid of the
        endpoint that originated the response message.
        
        @param {bool} successful --- True if the message was
        successful, False otherwise.
        
        @param {list or None} --- If None, means that the event was
        not successful.
        '''
        self.event_uuid = event_uuid
        self.sending_endpoint_uuid = sending_endpoint_uuid
        self.successful = successful
        self.children_event_endpoint_uuids = children_event_endpoint_uuids
        

    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid,

            self.SENDING_ENDPOINT_UUID_FIELD: self.sending_endpoint_uuid,
            self.SUCCESSFUL_FIELD: self.successful,
            
            self.CHILDREN_EVENT_ENDPOINT_UUIDS_FIELD:
                self.children_event_endpoint_uuids
            }

    @staticmethod
    def map_to_msg(msg):
        return _PartnerFirstPhaseResultMessage(
            msg[_Message.EVENT_UUID_FIELD],
            msg[_PartnerFirstPhaseResultMessage.SENDING_ENDPOINT_UUID_FIELD],
            msg[_PartnerFirstPhaseResultMessage.SUCCESSFUL_FIELD],
            msg[_PartnerFirstPhaseResultMessage.CHILDREN_EVENT_ENDPOINT_UUIDS_FIELD])
        

class _PartnerNotifyOfPeeredModified(_Message):
    '''
    @see waldoActiveEvent.wait_if_modified_peered    
    '''
    MSG_TYPE = 'partner_notify_of_peered_modified'

    REPLY_WITH_UUID_FIELD = 'reply_with_uuid'
    PEERED_DELTAS_FIELD = 'peered_deltas'

    def __init__(
        self,event_uuid,reply_with_uuid,peered_deltas):
        self.event_uuid = event_uuid
        self.reply_with_uuid = reply_with_uuid
        self.peered_deltas = peered_deltas

    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid,

            self.REPLY_WITH_UUID_FIELD: self.reply_with_uuid,
            self.PEERED_DELTAS_FIELD: self.peered_deltas,
            }

    @staticmethod
    def map_to_msg(msg):
        return _PartnerNotifyOfPeeredModified(
            msg[_Message.EVENT_UUID_FIELD],
            msg[_PartnerNotifyOfPeeredModified.REPLY_WITH_UUID_FIELD],
            msg[_PartnerNotifyOfPeeredModified.PEERED_DELTAS_FIELD])

    
class _PartnerNotifyOfPeeredModifiedResponse(_Message):
    '''
    This is a response message to _PartnerNotifyOfPeeredModified
    
    @see waldoActiveEvent.wait_if_modified_peered
    '''
    MSG_TYPE = 'partner_notify_of_peered_modified_resp'

    REPLY_TO_UUID_FIELD = 'reply_to_uuid'
    INVALIDATED_FIELD = 'invalidated'

    
    def __init__(self,event_uuid,reply_to_uuid,invalidated):
        '''
        @param {uuid} event_uuid

        @param {uuid} reply_to_uuid --- Matches reply_with_uuid from
        _PartnerNotifyOfPeeredModified.
        
        @param {bool} invalidated --- True if when notifying other
        side of the changes to peered data, the other side cannot
        apply changes because they have already been invalidated.
        (Early exit condition.)
        '''
        self.event_uuid = event_uuid
        self.reply_to_uuid = reply_to_uuid
        self.invalidated = invalidated

    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _Message.EVENT_UUID_FIELD: self.event_uuid,

            self.REPLY_TO_UUID_FIELD: self.reply_to_uuid,
            self.INVALIDATED_FIELD: self.invalidated
            }

    @staticmethod
    def map_to_msg(msg):
        return _PartnerNotifyOfPeeredModifiedResponse(
            msg[_Message.EVENT_UUID_FIELD],
            msg[_PartnerNotifyOfPeeredModifiedResponse.REPLY_TO_UUID_FIELD],
            msg[_PartnerNotifyOfPeeredModifiedResponse.INVALIDATED_FIELD])
    

class _PartnerNotifyReady(_Message):
    '''
    The endpoint that sent this message has completed its on_ready
    method
    '''
    MSG_TYPE = 'partner_notify_ready_msg'
    ENDPOINT_UUID_FIELD = 'endpoint_uuid'

    def __init__(self,endpoint_uuid):
        self.endpoint_uuid = endpoint_uuid

    def msg_to_map(self):
        return {
            _Message.MESSAGE_TYPE_FIELD: self.MSG_TYPE,
            _PartnerNotifyReady.ENDPOINT_UUID_FIELD: self.endpoint_uuid,
            }

    @staticmethod
    def map_to_msg(msg):
        return _PartnerNotifyReady(
            msg[_PartnerNotifyReady.ENDPOINT_UUID_FIELD])

    
_Message.SUBTYPE_MAP[
    _PartnerRequestSequenceBlockMessage.MSG_TYPE] = _PartnerRequestSequenceBlockMessage
_Message.SUBTYPE_MAP[
    _PartnerCommitRequestMessage.MSG_TYPE] = _PartnerCommitRequestMessage
_Message.SUBTYPE_MAP[
    _PartnerCompleteCommitRequestMessage.MSG_TYPE] = _PartnerCompleteCommitRequestMessage
_Message.SUBTYPE_MAP[
    _PartnerBackoutCommitRequestMessage.MSG_TYPE] = _PartnerBackoutCommitRequestMessage
_Message.SUBTYPE_MAP[
    _PartnerRemovedSubscriberMessage.MSG_TYPE] = _PartnerRemovedSubscriberMessage
_Message.SUBTYPE_MAP[
    _PartnerAdditionalSubscriberMessage.MSG_TYPE] = _PartnerAdditionalSubscriberMessage
_Message.SUBTYPE_MAP[
    _PartnerFirstPhaseResultMessage.MSG_TYPE] = _PartnerFirstPhaseResultMessage
_Message.SUBTYPE_MAP[
    _PartnerNotifyOfPeeredModified.MSG_TYPE] = _PartnerNotifyOfPeeredModified
_Message.SUBTYPE_MAP[
    _PartnerNotifyOfPeeredModifiedResponse.MSG_TYPE] = _PartnerNotifyOfPeeredModifiedResponse
_Message.SUBTYPE_MAP[
    _PartnerNotifyReady.MSG_TYPE] = _PartnerNotifyReady
