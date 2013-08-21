# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: partnerError.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import util_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='partnerError.proto',
  package='',
  serialized_pb='\n\x12partnerError.proto\x1a\nutil.proto\"\x95\x01\n\x0cPartnerError\x12\x19\n\nevent_uuid\x18\x01 \x02(\x0b\x32\x05.UUID\x12\x18\n\thost_uuid\x18\x02 \x02(\x0b\x32\x05.UUID\x12%\n\x04type\x18\x03 \x02(\x0e\x32\x17.PartnerError.ErrorType\")\n\tErrorType\x12\x0f\n\x0b\x41PPLICATION\x10\x01\x12\x0b\n\x07NETWORK\x10\x02')



_PARTNERERROR_ERRORTYPE = _descriptor.EnumDescriptor(
  name='ErrorType',
  full_name='PartnerError.ErrorType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='APPLICATION', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NETWORK', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=143,
  serialized_end=184,
)


_PARTNERERROR = _descriptor.Descriptor(
  name='PartnerError',
  full_name='PartnerError',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='event_uuid', full_name='PartnerError.event_uuid', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='host_uuid', full_name='PartnerError.host_uuid', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='PartnerError.type', index=2,
      number=3, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _PARTNERERROR_ERRORTYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=35,
  serialized_end=184,
)

_PARTNERERROR.fields_by_name['event_uuid'].message_type = util_pb2._UUID
_PARTNERERROR.fields_by_name['host_uuid'].message_type = util_pb2._UUID
_PARTNERERROR.fields_by_name['type'].enum_type = _PARTNERERROR_ERRORTYPE
_PARTNERERROR_ERRORTYPE.containing_type = _PARTNERERROR;
DESCRIPTOR.message_types_by_name['PartnerError'] = _PARTNERERROR

class PartnerError(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PARTNERERROR

  # @@protoc_insertion_point(class_scope:PartnerError)


# @@protoc_insertion_point(module_scope)
