# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import util_pb2

DESCRIPTOR = descriptor.FileDescriptor(
  name='partnerRemovedSubscriber.proto',
  package='',
  serialized_pb='\n\x1epartnerRemovedSubscriber.proto\x1a\nutil.proto\"\x95\x01\n\x18PartnerRemovedSubscriber\x12\x19\n\nevent_uuid\x18\x01 \x02(\x0b\x32\x05.UUID\x12&\n\x17removed_subscriber_uuid\x18\x02 \x02(\x0b\x32\x05.UUID\x12\x18\n\thost_uuid\x18\x03 \x02(\x0b\x32\x05.UUID\x12\x1c\n\rresource_uuid\x18\x04 \x02(\x0b\x32\x05.UUID')




_PARTNERREMOVEDSUBSCRIBER = descriptor.Descriptor(
  name='PartnerRemovedSubscriber',
  full_name='PartnerRemovedSubscriber',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='event_uuid', full_name='PartnerRemovedSubscriber.event_uuid', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='removed_subscriber_uuid', full_name='PartnerRemovedSubscriber.removed_subscriber_uuid', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='host_uuid', full_name='PartnerRemovedSubscriber.host_uuid', index=2,
      number=3, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='resource_uuid', full_name='PartnerRemovedSubscriber.resource_uuid', index=3,
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
  serialized_start=47,
  serialized_end=196,
)

_PARTNERREMOVEDSUBSCRIBER.fields_by_name['event_uuid'].message_type = util_pb2._UUID
_PARTNERREMOVEDSUBSCRIBER.fields_by_name['removed_subscriber_uuid'].message_type = util_pb2._UUID
_PARTNERREMOVEDSUBSCRIBER.fields_by_name['host_uuid'].message_type = util_pb2._UUID
_PARTNERREMOVEDSUBSCRIBER.fields_by_name['resource_uuid'].message_type = util_pb2._UUID
DESCRIPTOR.message_types_by_name['PartnerRemovedSubscriber'] = _PARTNERREMOVEDSUBSCRIBER

class PartnerRemovedSubscriber(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PARTNERREMOVEDSUBSCRIBER
  
  # @@protoc_insertion_point(class_scope:PartnerRemovedSubscriber)

# @@protoc_insertion_point(module_scope)
