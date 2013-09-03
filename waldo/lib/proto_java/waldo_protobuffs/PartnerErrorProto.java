// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: partnerError.proto

package waldo_protobuffs;

public final class PartnerErrorProto {
  private PartnerErrorProto() {}
  public static void registerAllExtensions(
      com.google.protobuf.ExtensionRegistry registry) {
  }
  public interface PartnerErrorOrBuilder
      extends com.google.protobuf.MessageOrBuilder {
    
    // required .UUID event_uuid = 1;
    boolean hasEventUuid();
    waldo_protobuffs.UtilProto.UUID getEventUuid();
    waldo_protobuffs.UtilProto.UUIDOrBuilder getEventUuidOrBuilder();
    
    // required .UUID host_uuid = 2;
    boolean hasHostUuid();
    waldo_protobuffs.UtilProto.UUID getHostUuid();
    waldo_protobuffs.UtilProto.UUIDOrBuilder getHostUuidOrBuilder();
    
    // required .PartnerError.ErrorType type = 3;
    boolean hasType();
    waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType getType();
    
    // optional string trace = 4;
    boolean hasTrace();
    String getTrace();
  }
  public static final class PartnerError extends
      com.google.protobuf.GeneratedMessage
      implements PartnerErrorOrBuilder {
    // Use PartnerError.newBuilder() to construct.
    private PartnerError(Builder builder) {
      super(builder);
    }
    private PartnerError(boolean noInit) {}
    
    private static final PartnerError defaultInstance;
    public static PartnerError getDefaultInstance() {
      return defaultInstance;
    }
    
    public PartnerError getDefaultInstanceForType() {
      return defaultInstance;
    }
    
    public static final com.google.protobuf.Descriptors.Descriptor
        getDescriptor() {
      return waldo_protobuffs.PartnerErrorProto.internal_static_PartnerError_descriptor;
    }
    
    protected com.google.protobuf.GeneratedMessage.FieldAccessorTable
        internalGetFieldAccessorTable() {
      return waldo_protobuffs.PartnerErrorProto.internal_static_PartnerError_fieldAccessorTable;
    }
    
    public enum ErrorType
        implements com.google.protobuf.ProtocolMessageEnum {
      APPLICATION(0, 1),
      NETWORK(1, 2),
      ;
      
      public static final int APPLICATION_VALUE = 1;
      public static final int NETWORK_VALUE = 2;
      
      
      public final int getNumber() { return value; }
      
      public static ErrorType valueOf(int value) {
        switch (value) {
          case 1: return APPLICATION;
          case 2: return NETWORK;
          default: return null;
        }
      }
      
      public static com.google.protobuf.Internal.EnumLiteMap<ErrorType>
          internalGetValueMap() {
        return internalValueMap;
      }
      private static com.google.protobuf.Internal.EnumLiteMap<ErrorType>
          internalValueMap =
            new com.google.protobuf.Internal.EnumLiteMap<ErrorType>() {
              public ErrorType findValueByNumber(int number) {
                return ErrorType.valueOf(number);
              }
            };
      
      public final com.google.protobuf.Descriptors.EnumValueDescriptor
          getValueDescriptor() {
        return getDescriptor().getValues().get(index);
      }
      public final com.google.protobuf.Descriptors.EnumDescriptor
          getDescriptorForType() {
        return getDescriptor();
      }
      public static final com.google.protobuf.Descriptors.EnumDescriptor
          getDescriptor() {
        return waldo_protobuffs.PartnerErrorProto.PartnerError.getDescriptor().getEnumTypes().get(0);
      }
      
      private static final ErrorType[] VALUES = {
        APPLICATION, NETWORK, 
      };
      
      public static ErrorType valueOf(
          com.google.protobuf.Descriptors.EnumValueDescriptor desc) {
        if (desc.getType() != getDescriptor()) {
          throw new java.lang.IllegalArgumentException(
            "EnumValueDescriptor is not for this type.");
        }
        return VALUES[desc.getIndex()];
      }
      
      private final int index;
      private final int value;
      
      private ErrorType(int index, int value) {
        this.index = index;
        this.value = value;
      }
      
      // @@protoc_insertion_point(enum_scope:PartnerError.ErrorType)
    }
    
    private int bitField0_;
    // required .UUID event_uuid = 1;
    public static final int EVENT_UUID_FIELD_NUMBER = 1;
    private waldo_protobuffs.UtilProto.UUID eventUuid_;
    public boolean hasEventUuid() {
      return ((bitField0_ & 0x00000001) == 0x00000001);
    }
    public waldo_protobuffs.UtilProto.UUID getEventUuid() {
      return eventUuid_;
    }
    public waldo_protobuffs.UtilProto.UUIDOrBuilder getEventUuidOrBuilder() {
      return eventUuid_;
    }
    
    // required .UUID host_uuid = 2;
    public static final int HOST_UUID_FIELD_NUMBER = 2;
    private waldo_protobuffs.UtilProto.UUID hostUuid_;
    public boolean hasHostUuid() {
      return ((bitField0_ & 0x00000002) == 0x00000002);
    }
    public waldo_protobuffs.UtilProto.UUID getHostUuid() {
      return hostUuid_;
    }
    public waldo_protobuffs.UtilProto.UUIDOrBuilder getHostUuidOrBuilder() {
      return hostUuid_;
    }
    
    // required .PartnerError.ErrorType type = 3;
    public static final int TYPE_FIELD_NUMBER = 3;
    private waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType type_;
    public boolean hasType() {
      return ((bitField0_ & 0x00000004) == 0x00000004);
    }
    public waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType getType() {
      return type_;
    }
    
    // optional string trace = 4;
    public static final int TRACE_FIELD_NUMBER = 4;
    private java.lang.Object trace_;
    public boolean hasTrace() {
      return ((bitField0_ & 0x00000008) == 0x00000008);
    }
    public String getTrace() {
      java.lang.Object ref = trace_;
      if (ref instanceof String) {
        return (String) ref;
      } else {
        com.google.protobuf.ByteString bs = 
            (com.google.protobuf.ByteString) ref;
        String s = bs.toStringUtf8();
        if (com.google.protobuf.Internal.isValidUtf8(bs)) {
          trace_ = s;
        }
        return s;
      }
    }
    private com.google.protobuf.ByteString getTraceBytes() {
      java.lang.Object ref = trace_;
      if (ref instanceof String) {
        com.google.protobuf.ByteString b = 
            com.google.protobuf.ByteString.copyFromUtf8((String) ref);
        trace_ = b;
        return b;
      } else {
        return (com.google.protobuf.ByteString) ref;
      }
    }
    
    private void initFields() {
      eventUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
      hostUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
      type_ = waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType.APPLICATION;
      trace_ = "";
    }
    private byte memoizedIsInitialized = -1;
    public final boolean isInitialized() {
      byte isInitialized = memoizedIsInitialized;
      if (isInitialized != -1) return isInitialized == 1;
      
      if (!hasEventUuid()) {
        memoizedIsInitialized = 0;
        return false;
      }
      if (!hasHostUuid()) {
        memoizedIsInitialized = 0;
        return false;
      }
      if (!hasType()) {
        memoizedIsInitialized = 0;
        return false;
      }
      if (!getEventUuid().isInitialized()) {
        memoizedIsInitialized = 0;
        return false;
      }
      if (!getHostUuid().isInitialized()) {
        memoizedIsInitialized = 0;
        return false;
      }
      memoizedIsInitialized = 1;
      return true;
    }
    
    public void writeTo(com.google.protobuf.CodedOutputStream output)
                        throws java.io.IOException {
      getSerializedSize();
      if (((bitField0_ & 0x00000001) == 0x00000001)) {
        output.writeMessage(1, eventUuid_);
      }
      if (((bitField0_ & 0x00000002) == 0x00000002)) {
        output.writeMessage(2, hostUuid_);
      }
      if (((bitField0_ & 0x00000004) == 0x00000004)) {
        output.writeEnum(3, type_.getNumber());
      }
      if (((bitField0_ & 0x00000008) == 0x00000008)) {
        output.writeBytes(4, getTraceBytes());
      }
      getUnknownFields().writeTo(output);
    }
    
    private int memoizedSerializedSize = -1;
    public int getSerializedSize() {
      int size = memoizedSerializedSize;
      if (size != -1) return size;
    
      size = 0;
      if (((bitField0_ & 0x00000001) == 0x00000001)) {
        size += com.google.protobuf.CodedOutputStream
          .computeMessageSize(1, eventUuid_);
      }
      if (((bitField0_ & 0x00000002) == 0x00000002)) {
        size += com.google.protobuf.CodedOutputStream
          .computeMessageSize(2, hostUuid_);
      }
      if (((bitField0_ & 0x00000004) == 0x00000004)) {
        size += com.google.protobuf.CodedOutputStream
          .computeEnumSize(3, type_.getNumber());
      }
      if (((bitField0_ & 0x00000008) == 0x00000008)) {
        size += com.google.protobuf.CodedOutputStream
          .computeBytesSize(4, getTraceBytes());
      }
      size += getUnknownFields().getSerializedSize();
      memoizedSerializedSize = size;
      return size;
    }
    
    private static final long serialVersionUID = 0L;
    @java.lang.Override
    protected java.lang.Object writeReplace()
        throws java.io.ObjectStreamException {
      return super.writeReplace();
    }
    
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(
        com.google.protobuf.ByteString data)
        throws com.google.protobuf.InvalidProtocolBufferException {
      return newBuilder().mergeFrom(data).buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(
        com.google.protobuf.ByteString data,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws com.google.protobuf.InvalidProtocolBufferException {
      return newBuilder().mergeFrom(data, extensionRegistry)
               .buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(byte[] data)
        throws com.google.protobuf.InvalidProtocolBufferException {
      return newBuilder().mergeFrom(data).buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(
        byte[] data,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws com.google.protobuf.InvalidProtocolBufferException {
      return newBuilder().mergeFrom(data, extensionRegistry)
               .buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(java.io.InputStream input)
        throws java.io.IOException {
      return newBuilder().mergeFrom(input).buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(
        java.io.InputStream input,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws java.io.IOException {
      return newBuilder().mergeFrom(input, extensionRegistry)
               .buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseDelimitedFrom(java.io.InputStream input)
        throws java.io.IOException {
      Builder builder = newBuilder();
      if (builder.mergeDelimitedFrom(input)) {
        return builder.buildParsed();
      } else {
        return null;
      }
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseDelimitedFrom(
        java.io.InputStream input,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws java.io.IOException {
      Builder builder = newBuilder();
      if (builder.mergeDelimitedFrom(input, extensionRegistry)) {
        return builder.buildParsed();
      } else {
        return null;
      }
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(
        com.google.protobuf.CodedInputStream input)
        throws java.io.IOException {
      return newBuilder().mergeFrom(input).buildParsed();
    }
    public static waldo_protobuffs.PartnerErrorProto.PartnerError parseFrom(
        com.google.protobuf.CodedInputStream input,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws java.io.IOException {
      return newBuilder().mergeFrom(input, extensionRegistry)
               .buildParsed();
    }
    
    public static Builder newBuilder() { return Builder.create(); }
    public Builder newBuilderForType() { return newBuilder(); }
    public static Builder newBuilder(waldo_protobuffs.PartnerErrorProto.PartnerError prototype) {
      return newBuilder().mergeFrom(prototype);
    }
    public Builder toBuilder() { return newBuilder(this); }
    
    @java.lang.Override
    protected Builder newBuilderForType(
        com.google.protobuf.GeneratedMessage.BuilderParent parent) {
      Builder builder = new Builder(parent);
      return builder;
    }
    public static final class Builder extends
        com.google.protobuf.GeneratedMessage.Builder<Builder>
       implements waldo_protobuffs.PartnerErrorProto.PartnerErrorOrBuilder {
      public static final com.google.protobuf.Descriptors.Descriptor
          getDescriptor() {
        return waldo_protobuffs.PartnerErrorProto.internal_static_PartnerError_descriptor;
      }
      
      protected com.google.protobuf.GeneratedMessage.FieldAccessorTable
          internalGetFieldAccessorTable() {
        return waldo_protobuffs.PartnerErrorProto.internal_static_PartnerError_fieldAccessorTable;
      }
      
      // Construct using waldo_protobuffs.PartnerErrorProto.PartnerError.newBuilder()
      private Builder() {
        maybeForceBuilderInitialization();
      }
      
      private Builder(BuilderParent parent) {
        super(parent);
        maybeForceBuilderInitialization();
      }
      private void maybeForceBuilderInitialization() {
        if (com.google.protobuf.GeneratedMessage.alwaysUseFieldBuilders) {
          getEventUuidFieldBuilder();
          getHostUuidFieldBuilder();
        }
      }
      private static Builder create() {
        return new Builder();
      }
      
      public Builder clear() {
        super.clear();
        if (eventUuidBuilder_ == null) {
          eventUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
        } else {
          eventUuidBuilder_.clear();
        }
        bitField0_ = (bitField0_ & ~0x00000001);
        if (hostUuidBuilder_ == null) {
          hostUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
        } else {
          hostUuidBuilder_.clear();
        }
        bitField0_ = (bitField0_ & ~0x00000002);
        type_ = waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType.APPLICATION;
        bitField0_ = (bitField0_ & ~0x00000004);
        trace_ = "";
        bitField0_ = (bitField0_ & ~0x00000008);
        return this;
      }
      
      public Builder clone() {
        return create().mergeFrom(buildPartial());
      }
      
      public com.google.protobuf.Descriptors.Descriptor
          getDescriptorForType() {
        return waldo_protobuffs.PartnerErrorProto.PartnerError.getDescriptor();
      }
      
      public waldo_protobuffs.PartnerErrorProto.PartnerError getDefaultInstanceForType() {
        return waldo_protobuffs.PartnerErrorProto.PartnerError.getDefaultInstance();
      }
      
      public waldo_protobuffs.PartnerErrorProto.PartnerError build() {
        waldo_protobuffs.PartnerErrorProto.PartnerError result = buildPartial();
        if (!result.isInitialized()) {
          throw newUninitializedMessageException(result);
        }
        return result;
      }
      
      private waldo_protobuffs.PartnerErrorProto.PartnerError buildParsed()
          throws com.google.protobuf.InvalidProtocolBufferException {
        waldo_protobuffs.PartnerErrorProto.PartnerError result = buildPartial();
        if (!result.isInitialized()) {
          throw newUninitializedMessageException(
            result).asInvalidProtocolBufferException();
        }
        return result;
      }
      
      public waldo_protobuffs.PartnerErrorProto.PartnerError buildPartial() {
        waldo_protobuffs.PartnerErrorProto.PartnerError result = new waldo_protobuffs.PartnerErrorProto.PartnerError(this);
        int from_bitField0_ = bitField0_;
        int to_bitField0_ = 0;
        if (((from_bitField0_ & 0x00000001) == 0x00000001)) {
          to_bitField0_ |= 0x00000001;
        }
        if (eventUuidBuilder_ == null) {
          result.eventUuid_ = eventUuid_;
        } else {
          result.eventUuid_ = eventUuidBuilder_.build();
        }
        if (((from_bitField0_ & 0x00000002) == 0x00000002)) {
          to_bitField0_ |= 0x00000002;
        }
        if (hostUuidBuilder_ == null) {
          result.hostUuid_ = hostUuid_;
        } else {
          result.hostUuid_ = hostUuidBuilder_.build();
        }
        if (((from_bitField0_ & 0x00000004) == 0x00000004)) {
          to_bitField0_ |= 0x00000004;
        }
        result.type_ = type_;
        if (((from_bitField0_ & 0x00000008) == 0x00000008)) {
          to_bitField0_ |= 0x00000008;
        }
        result.trace_ = trace_;
        result.bitField0_ = to_bitField0_;
        onBuilt();
        return result;
      }
      
      public Builder mergeFrom(com.google.protobuf.Message other) {
        if (other instanceof waldo_protobuffs.PartnerErrorProto.PartnerError) {
          return mergeFrom((waldo_protobuffs.PartnerErrorProto.PartnerError)other);
        } else {
          super.mergeFrom(other);
          return this;
        }
      }
      
      public Builder mergeFrom(waldo_protobuffs.PartnerErrorProto.PartnerError other) {
        if (other == waldo_protobuffs.PartnerErrorProto.PartnerError.getDefaultInstance()) return this;
        if (other.hasEventUuid()) {
          mergeEventUuid(other.getEventUuid());
        }
        if (other.hasHostUuid()) {
          mergeHostUuid(other.getHostUuid());
        }
        if (other.hasType()) {
          setType(other.getType());
        }
        if (other.hasTrace()) {
          setTrace(other.getTrace());
        }
        this.mergeUnknownFields(other.getUnknownFields());
        return this;
      }
      
      public final boolean isInitialized() {
        if (!hasEventUuid()) {
          
          return false;
        }
        if (!hasHostUuid()) {
          
          return false;
        }
        if (!hasType()) {
          
          return false;
        }
        if (!getEventUuid().isInitialized()) {
          
          return false;
        }
        if (!getHostUuid().isInitialized()) {
          
          return false;
        }
        return true;
      }
      
      public Builder mergeFrom(
          com.google.protobuf.CodedInputStream input,
          com.google.protobuf.ExtensionRegistryLite extensionRegistry)
          throws java.io.IOException {
        com.google.protobuf.UnknownFieldSet.Builder unknownFields =
          com.google.protobuf.UnknownFieldSet.newBuilder(
            this.getUnknownFields());
        while (true) {
          int tag = input.readTag();
          switch (tag) {
            case 0:
              this.setUnknownFields(unknownFields.build());
              onChanged();
              return this;
            default: {
              if (!parseUnknownField(input, unknownFields,
                                     extensionRegistry, tag)) {
                this.setUnknownFields(unknownFields.build());
                onChanged();
                return this;
              }
              break;
            }
            case 10: {
              waldo_protobuffs.UtilProto.UUID.Builder subBuilder = waldo_protobuffs.UtilProto.UUID.newBuilder();
              if (hasEventUuid()) {
                subBuilder.mergeFrom(getEventUuid());
              }
              input.readMessage(subBuilder, extensionRegistry);
              setEventUuid(subBuilder.buildPartial());
              break;
            }
            case 18: {
              waldo_protobuffs.UtilProto.UUID.Builder subBuilder = waldo_protobuffs.UtilProto.UUID.newBuilder();
              if (hasHostUuid()) {
                subBuilder.mergeFrom(getHostUuid());
              }
              input.readMessage(subBuilder, extensionRegistry);
              setHostUuid(subBuilder.buildPartial());
              break;
            }
            case 24: {
              int rawValue = input.readEnum();
              waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType value = waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType.valueOf(rawValue);
              if (value == null) {
                unknownFields.mergeVarintField(3, rawValue);
              } else {
                bitField0_ |= 0x00000004;
                type_ = value;
              }
              break;
            }
            case 34: {
              bitField0_ |= 0x00000008;
              trace_ = input.readBytes();
              break;
            }
          }
        }
      }
      
      private int bitField0_;
      
      // required .UUID event_uuid = 1;
      private waldo_protobuffs.UtilProto.UUID eventUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
      private com.google.protobuf.SingleFieldBuilder<
          waldo_protobuffs.UtilProto.UUID, waldo_protobuffs.UtilProto.UUID.Builder, waldo_protobuffs.UtilProto.UUIDOrBuilder> eventUuidBuilder_;
      public boolean hasEventUuid() {
        return ((bitField0_ & 0x00000001) == 0x00000001);
      }
      public waldo_protobuffs.UtilProto.UUID getEventUuid() {
        if (eventUuidBuilder_ == null) {
          return eventUuid_;
        } else {
          return eventUuidBuilder_.getMessage();
        }
      }
      public Builder setEventUuid(waldo_protobuffs.UtilProto.UUID value) {
        if (eventUuidBuilder_ == null) {
          if (value == null) {
            throw new NullPointerException();
          }
          eventUuid_ = value;
          onChanged();
        } else {
          eventUuidBuilder_.setMessage(value);
        }
        bitField0_ |= 0x00000001;
        return this;
      }
      public Builder setEventUuid(
          waldo_protobuffs.UtilProto.UUID.Builder builderForValue) {
        if (eventUuidBuilder_ == null) {
          eventUuid_ = builderForValue.build();
          onChanged();
        } else {
          eventUuidBuilder_.setMessage(builderForValue.build());
        }
        bitField0_ |= 0x00000001;
        return this;
      }
      public Builder mergeEventUuid(waldo_protobuffs.UtilProto.UUID value) {
        if (eventUuidBuilder_ == null) {
          if (((bitField0_ & 0x00000001) == 0x00000001) &&
              eventUuid_ != waldo_protobuffs.UtilProto.UUID.getDefaultInstance()) {
            eventUuid_ =
              waldo_protobuffs.UtilProto.UUID.newBuilder(eventUuid_).mergeFrom(value).buildPartial();
          } else {
            eventUuid_ = value;
          }
          onChanged();
        } else {
          eventUuidBuilder_.mergeFrom(value);
        }
        bitField0_ |= 0x00000001;
        return this;
      }
      public Builder clearEventUuid() {
        if (eventUuidBuilder_ == null) {
          eventUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
          onChanged();
        } else {
          eventUuidBuilder_.clear();
        }
        bitField0_ = (bitField0_ & ~0x00000001);
        return this;
      }
      public waldo_protobuffs.UtilProto.UUID.Builder getEventUuidBuilder() {
        bitField0_ |= 0x00000001;
        onChanged();
        return getEventUuidFieldBuilder().getBuilder();
      }
      public waldo_protobuffs.UtilProto.UUIDOrBuilder getEventUuidOrBuilder() {
        if (eventUuidBuilder_ != null) {
          return eventUuidBuilder_.getMessageOrBuilder();
        } else {
          return eventUuid_;
        }
      }
      private com.google.protobuf.SingleFieldBuilder<
          waldo_protobuffs.UtilProto.UUID, waldo_protobuffs.UtilProto.UUID.Builder, waldo_protobuffs.UtilProto.UUIDOrBuilder> 
          getEventUuidFieldBuilder() {
        if (eventUuidBuilder_ == null) {
          eventUuidBuilder_ = new com.google.protobuf.SingleFieldBuilder<
              waldo_protobuffs.UtilProto.UUID, waldo_protobuffs.UtilProto.UUID.Builder, waldo_protobuffs.UtilProto.UUIDOrBuilder>(
                  eventUuid_,
                  getParentForChildren(),
                  isClean());
          eventUuid_ = null;
        }
        return eventUuidBuilder_;
      }
      
      // required .UUID host_uuid = 2;
      private waldo_protobuffs.UtilProto.UUID hostUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
      private com.google.protobuf.SingleFieldBuilder<
          waldo_protobuffs.UtilProto.UUID, waldo_protobuffs.UtilProto.UUID.Builder, waldo_protobuffs.UtilProto.UUIDOrBuilder> hostUuidBuilder_;
      public boolean hasHostUuid() {
        return ((bitField0_ & 0x00000002) == 0x00000002);
      }
      public waldo_protobuffs.UtilProto.UUID getHostUuid() {
        if (hostUuidBuilder_ == null) {
          return hostUuid_;
        } else {
          return hostUuidBuilder_.getMessage();
        }
      }
      public Builder setHostUuid(waldo_protobuffs.UtilProto.UUID value) {
        if (hostUuidBuilder_ == null) {
          if (value == null) {
            throw new NullPointerException();
          }
          hostUuid_ = value;
          onChanged();
        } else {
          hostUuidBuilder_.setMessage(value);
        }
        bitField0_ |= 0x00000002;
        return this;
      }
      public Builder setHostUuid(
          waldo_protobuffs.UtilProto.UUID.Builder builderForValue) {
        if (hostUuidBuilder_ == null) {
          hostUuid_ = builderForValue.build();
          onChanged();
        } else {
          hostUuidBuilder_.setMessage(builderForValue.build());
        }
        bitField0_ |= 0x00000002;
        return this;
      }
      public Builder mergeHostUuid(waldo_protobuffs.UtilProto.UUID value) {
        if (hostUuidBuilder_ == null) {
          if (((bitField0_ & 0x00000002) == 0x00000002) &&
              hostUuid_ != waldo_protobuffs.UtilProto.UUID.getDefaultInstance()) {
            hostUuid_ =
              waldo_protobuffs.UtilProto.UUID.newBuilder(hostUuid_).mergeFrom(value).buildPartial();
          } else {
            hostUuid_ = value;
          }
          onChanged();
        } else {
          hostUuidBuilder_.mergeFrom(value);
        }
        bitField0_ |= 0x00000002;
        return this;
      }
      public Builder clearHostUuid() {
        if (hostUuidBuilder_ == null) {
          hostUuid_ = waldo_protobuffs.UtilProto.UUID.getDefaultInstance();
          onChanged();
        } else {
          hostUuidBuilder_.clear();
        }
        bitField0_ = (bitField0_ & ~0x00000002);
        return this;
      }
      public waldo_protobuffs.UtilProto.UUID.Builder getHostUuidBuilder() {
        bitField0_ |= 0x00000002;
        onChanged();
        return getHostUuidFieldBuilder().getBuilder();
      }
      public waldo_protobuffs.UtilProto.UUIDOrBuilder getHostUuidOrBuilder() {
        if (hostUuidBuilder_ != null) {
          return hostUuidBuilder_.getMessageOrBuilder();
        } else {
          return hostUuid_;
        }
      }
      private com.google.protobuf.SingleFieldBuilder<
          waldo_protobuffs.UtilProto.UUID, waldo_protobuffs.UtilProto.UUID.Builder, waldo_protobuffs.UtilProto.UUIDOrBuilder> 
          getHostUuidFieldBuilder() {
        if (hostUuidBuilder_ == null) {
          hostUuidBuilder_ = new com.google.protobuf.SingleFieldBuilder<
              waldo_protobuffs.UtilProto.UUID, waldo_protobuffs.UtilProto.UUID.Builder, waldo_protobuffs.UtilProto.UUIDOrBuilder>(
                  hostUuid_,
                  getParentForChildren(),
                  isClean());
          hostUuid_ = null;
        }
        return hostUuidBuilder_;
      }
      
      // required .PartnerError.ErrorType type = 3;
      private waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType type_ = waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType.APPLICATION;
      public boolean hasType() {
        return ((bitField0_ & 0x00000004) == 0x00000004);
      }
      public waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType getType() {
        return type_;
      }
      public Builder setType(waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType value) {
        if (value == null) {
          throw new NullPointerException();
        }
        bitField0_ |= 0x00000004;
        type_ = value;
        onChanged();
        return this;
      }
      public Builder clearType() {
        bitField0_ = (bitField0_ & ~0x00000004);
        type_ = waldo_protobuffs.PartnerErrorProto.PartnerError.ErrorType.APPLICATION;
        onChanged();
        return this;
      }
      
      // optional string trace = 4;
      private java.lang.Object trace_ = "";
      public boolean hasTrace() {
        return ((bitField0_ & 0x00000008) == 0x00000008);
      }
      public String getTrace() {
        java.lang.Object ref = trace_;
        if (!(ref instanceof String)) {
          String s = ((com.google.protobuf.ByteString) ref).toStringUtf8();
          trace_ = s;
          return s;
        } else {
          return (String) ref;
        }
      }
      public Builder setTrace(String value) {
        if (value == null) {
    throw new NullPointerException();
  }
  bitField0_ |= 0x00000008;
        trace_ = value;
        onChanged();
        return this;
      }
      public Builder clearTrace() {
        bitField0_ = (bitField0_ & ~0x00000008);
        trace_ = getDefaultInstance().getTrace();
        onChanged();
        return this;
      }
      void setTrace(com.google.protobuf.ByteString value) {
        bitField0_ |= 0x00000008;
        trace_ = value;
        onChanged();
      }
      
      // @@protoc_insertion_point(builder_scope:PartnerError)
    }
    
    static {
      defaultInstance = new PartnerError(true);
      defaultInstance.initFields();
    }
    
    // @@protoc_insertion_point(class_scope:PartnerError)
  }
  
  private static com.google.protobuf.Descriptors.Descriptor
    internal_static_PartnerError_descriptor;
  private static
    com.google.protobuf.GeneratedMessage.FieldAccessorTable
      internal_static_PartnerError_fieldAccessorTable;
  
  public static com.google.protobuf.Descriptors.FileDescriptor
      getDescriptor() {
    return descriptor;
  }
  private static com.google.protobuf.Descriptors.FileDescriptor
      descriptor;
  static {
    java.lang.String[] descriptorData = {
      "\n\022partnerError.proto\032\nutil.proto\"\244\001\n\014Par" +
      "tnerError\022\031\n\nevent_uuid\030\001 \002(\0132\005.UUID\022\030\n\t" +
      "host_uuid\030\002 \002(\0132\005.UUID\022%\n\004type\030\003 \002(\0162\027.P" +
      "artnerError.ErrorType\022\r\n\005trace\030\004 \001(\t\")\n\t" +
      "ErrorType\022\017\n\013APPLICATION\020\001\022\013\n\007NETWORK\020\002B" +
      "%\n\020waldo_protobuffsB\021PartnerErrorProto"
    };
    com.google.protobuf.Descriptors.FileDescriptor.InternalDescriptorAssigner assigner =
      new com.google.protobuf.Descriptors.FileDescriptor.InternalDescriptorAssigner() {
        public com.google.protobuf.ExtensionRegistry assignDescriptors(
            com.google.protobuf.Descriptors.FileDescriptor root) {
          descriptor = root;
          internal_static_PartnerError_descriptor =
            getDescriptor().getMessageTypes().get(0);
          internal_static_PartnerError_fieldAccessorTable = new
            com.google.protobuf.GeneratedMessage.FieldAccessorTable(
              internal_static_PartnerError_descriptor,
              new java.lang.String[] { "EventUuid", "HostUuid", "Type", "Trace", },
              waldo_protobuffs.PartnerErrorProto.PartnerError.class,
              waldo_protobuffs.PartnerErrorProto.PartnerError.Builder.class);
          return null;
        }
      };
    com.google.protobuf.Descriptors.FileDescriptor
      .internalBuildGeneratedFileFrom(descriptorData,
        new com.google.protobuf.Descriptors.FileDescriptor[] {
          waldo_protobuffs.UtilProto.getDescriptor(),
        }, assigner);
  }
  
  // @@protoc_insertion_point(outer_class_scope)
}
