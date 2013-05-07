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

    
