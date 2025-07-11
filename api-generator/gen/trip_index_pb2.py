# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: trip-index.proto
# Protobuf Python Version: 5.29.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    3,
    '',
    'trip-index.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10trip-index.proto\x12\ntrip_index\"\xd6\x02\n\tTripIndex\x12*\n\x05trips\x18\x01 \x03(\x0b\x32\x1b.trip_index.TripInformation\x12=\n\x0ctripsByRoute\x18\x02 \x03(\x0b\x32\'.trip_index.TripIndex.TripsByRouteEntry\x12;\n\x0btripsByStop\x18\x03 \x03(\x0b\x32&.trip_index.TripIndex.TripsByStopEntry\x1aP\n\x11TripsByRouteEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12*\n\x05value\x18\x02 \x01(\x0b\x32\x1b.trip_index.AssociatedTrips:\x02\x38\x01\x1aO\n\x10TripsByStopEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12*\n\x05value\x18\x02 \x01(\x0b\x32\x1b.trip_index.AssociatedTrips:\x02\x38\x01\"C\n\x0fTripInformation\x12\x0e\n\x06tripId\x18\x01 \x02(\t\x12\x0f\n\x07routeId\x18\x02 \x02(\t\x12\x0f\n\x07stopIds\x18\x03 \x03(\t\"!\n\x0f\x41ssociatedTrips\x12\x0e\n\x06tripId\x18\x01 \x03(\tB\x1a\n\x18\x63l.emilym.gtfs.tripindex')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'trip_index_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\030cl.emilym.gtfs.tripindex'
  _globals['_TRIPINDEX_TRIPSBYROUTEENTRY']._loaded_options = None
  _globals['_TRIPINDEX_TRIPSBYROUTEENTRY']._serialized_options = b'8\001'
  _globals['_TRIPINDEX_TRIPSBYSTOPENTRY']._loaded_options = None
  _globals['_TRIPINDEX_TRIPSBYSTOPENTRY']._serialized_options = b'8\001'
  _globals['_TRIPINDEX']._serialized_start=33
  _globals['_TRIPINDEX']._serialized_end=375
  _globals['_TRIPINDEX_TRIPSBYROUTEENTRY']._serialized_start=214
  _globals['_TRIPINDEX_TRIPSBYROUTEENTRY']._serialized_end=294
  _globals['_TRIPINDEX_TRIPSBYSTOPENTRY']._serialized_start=296
  _globals['_TRIPINDEX_TRIPSBYSTOPENTRY']._serialized_end=375
  _globals['_TRIPINFORMATION']._serialized_start=377
  _globals['_TRIPINFORMATION']._serialized_end=444
  _globals['_ASSOCIATEDTRIPS']._serialized_start=446
  _globals['_ASSOCIATEDTRIPS']._serialized_end=479
# @@protoc_insertion_point(module_scope)
