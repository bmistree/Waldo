import util
from abc import abstractmethod

_Message.SUBTYPE_MAP[
    _PartnerRequestSequenceBlockMessage.MSG_TYPE] = _PartnertnerRequestSequenceBlockMessage


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
    def map_to_msg(self,msg_map):
        '''
        @returns {Subclass of _Message}
        '''

        #### DEBUG
        if MESSAGE_TYPE_FIELD not in msg_map:
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
        sequence_local_var_store_deltas,global_var_store_deltas):
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
            _Message.EVENT_UUID_FIELD: self.event,

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
            msg_map[_PartnerRequestSequenceBlockMessage.SEQUENCE_LOCAL_VAR_STORE_DELTAS_FIELD],
            msg_map[_PartnerRequestSequenceBlockMessage.PEERED_VAR_STORE_DELTAS_FIELD])

    
