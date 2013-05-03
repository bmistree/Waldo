# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import partnerNotifyReady_pb2
import partnerNotifyOfPeeredModifiedResponse_pb2
import partnerRequestSequenceBlock_pb2
import partnerNotifyOfPeeredModified_pb2

DESCRIPTOR = descriptor.FileDescriptor(
  name='generalMessage.proto',
  package='',
  serialized_pb='\n\x14generalMessage.proto\x1a\x18partnerNotifyReady.proto\x1a+partnerNotifyOfPeeredModifiedResponse.proto\x1a!partnerRequestSequenceBlock.proto\x1a#partnerNotifyOfPeeredModified.proto\"\xe4\x03\n\x0eGeneralMessage\x12\x31\n\x0cmessage_type\x18\x01 \x02(\x0e\x32\x1b.GeneralMessage.MessageType\x12)\n\x0cnotify_ready\x18\x02 \x01(\x0b\x32\x13.PartnerNotifyReady\x12N\n\x1enotify_of_peered_modified_resp\x18\x03 \x01(\x0b\x32&.PartnerNotifyOfPeeredModifiedResponse\x12<\n\x16request_sequence_block\x18\x04 \x01(\x0b\x32\x1c.PartnerRequestSequenceBlock\x12\x41\n\x19notify_of_peered_modified\x18\x05 \x01(\x0b\x32\x1e.PartnerNotifyOfPeeredModified\"\xa2\x01\n\x0bMessageType\x12\x18\n\x14PARTNER_NOTIFY_READY\x10\x00\x12.\n*PARTNER_NOTIFY_OF_PEERED_MODIFIED_RESPONSE\x10\x01\x12\"\n\x1ePARTNER_REQUEST_SEQUENCE_BLOCK\x10\x02\x12%\n!PARTNER_NOTIFY_OF_PEERED_MODIFIED\x10\x03')



_GENERALMESSAGE_MESSAGETYPE = descriptor.EnumDescriptor(
  name='MessageType',
  full_name='GeneralMessage.MessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='PARTNER_NOTIFY_READY', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='PARTNER_NOTIFY_OF_PEERED_MODIFIED_RESPONSE', index=1, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='PARTNER_REQUEST_SEQUENCE_BLOCK', index=2, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='PARTNER_NOTIFY_OF_PEERED_MODIFIED', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=490,
  serialized_end=652,
)


_GENERALMESSAGE = descriptor.Descriptor(
  name='GeneralMessage',
  full_name='GeneralMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='message_type', full_name='GeneralMessage.message_type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='notify_ready', full_name='GeneralMessage.notify_ready', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='notify_of_peered_modified_resp', full_name='GeneralMessage.notify_of_peered_modified_resp', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='request_sequence_block', full_name='GeneralMessage.request_sequence_block', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='notify_of_peered_modified', full_name='GeneralMessage.notify_of_peered_modified', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _GENERALMESSAGE_MESSAGETYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=168,
  serialized_end=652,
)

_GENERALMESSAGE.fields_by_name['message_type'].enum_type = _GENERALMESSAGE_MESSAGETYPE
_GENERALMESSAGE.fields_by_name['notify_ready'].message_type = partnerNotifyReady_pb2._PARTNERNOTIFYREADY
_GENERALMESSAGE.fields_by_name['notify_of_peered_modified_resp'].message_type = partnerNotifyOfPeeredModifiedResponse_pb2._PARTNERNOTIFYOFPEEREDMODIFIEDRESPONSE
_GENERALMESSAGE.fields_by_name['request_sequence_block'].message_type = partnerRequestSequenceBlock_pb2._PARTNERREQUESTSEQUENCEBLOCK
_GENERALMESSAGE.fields_by_name['notify_of_peered_modified'].message_type = partnerNotifyOfPeeredModified_pb2._PARTNERNOTIFYOFPEEREDMODIFIED
_GENERALMESSAGE_MESSAGETYPE.containing_type = _GENERALMESSAGE;
DESCRIPTOR.message_types_by_name['GeneralMessage'] = _GENERALMESSAGE

class GeneralMessage(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _GENERALMESSAGE
  
  # @@protoc_insertion_point(class_scope:GeneralMessage)

# @@protoc_insertion_point(module_scope)