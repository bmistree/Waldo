# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import util_pb2
import varStoreDeltas_pb2

DESCRIPTOR = descriptor.FileDescriptor(
  name='partnerNotifyOfPeeredModified.proto',
  package='',
  serialized_pb='\n#partnerNotifyOfPeeredModified.proto\x1a\nutil.proto\x1a\x14varStoreDeltas.proto\"\x9d\x01\n\x1dPartnerNotifyOfPeeredModified\x12\x19\n\nevent_uuid\x18\x01 \x02(\x0b\x32\x05.UUID\x12\x1b\n\x08priority\x18\x02 \x02(\x0b\x32\t.Priority\x12\x1e\n\x0freply_with_uuid\x18\x03 \x02(\x0b\x32\x05.UUID\x12$\n\x0bglob_deltas\x18\x04 \x02(\x0b\x32\x0f.VarStoreDeltas')




_PARTNERNOTIFYOFPEEREDMODIFIED = descriptor.Descriptor(
  name='PartnerNotifyOfPeeredModified',
  full_name='PartnerNotifyOfPeeredModified',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='event_uuid', full_name='PartnerNotifyOfPeeredModified.event_uuid', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='priority', full_name='PartnerNotifyOfPeeredModified.priority', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='reply_with_uuid', full_name='PartnerNotifyOfPeeredModified.reply_with_uuid', index=2,
      number=3, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='glob_deltas', full_name='PartnerNotifyOfPeeredModified.glob_deltas', index=3,
      number=4, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=74,
  serialized_end=231,
)

_PARTNERNOTIFYOFPEEREDMODIFIED.fields_by_name['event_uuid'].message_type = util_pb2._UUID
_PARTNERNOTIFYOFPEEREDMODIFIED.fields_by_name['priority'].message_type = util_pb2._PRIORITY
_PARTNERNOTIFYOFPEEREDMODIFIED.fields_by_name['reply_with_uuid'].message_type = util_pb2._UUID
_PARTNERNOTIFYOFPEEREDMODIFIED.fields_by_name['glob_deltas'].message_type = varStoreDeltas_pb2._VARSTOREDELTAS
DESCRIPTOR.message_types_by_name['PartnerNotifyOfPeeredModified'] = _PARTNERNOTIFYOFPEEREDMODIFIED

class PartnerNotifyOfPeeredModified(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PARTNERNOTIFYOFPEEREDMODIFIED
  
  # @@protoc_insertion_point(class_scope:PartnerNotifyOfPeeredModified)

# @@protoc_insertion_point(module_scope)
