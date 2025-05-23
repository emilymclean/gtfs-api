# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: network-graph.proto
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
    'network-graph.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13network-graph.proto\x12\x0cnetworkgraph\"\x8b\x01\n\x05Graph\x12!\n\x05nodes\x18\x01 \x03(\x0b\x32\x12.networkgraph.Node\x12\x30\n\x06\x63onfig\x18\x02 \x02(\x0b\x32 .networkgraph.GraphConfiguration\x12-\n\x08mappings\x18\x03 \x02(\x0b\x32\x1b.networkgraph.GraphMappings\"\xc9\x01\n\rGraphMappings\x12=\n\tstopNodes\x18\x01 \x03(\x0b\x32*.networkgraph.GraphMappings.StopNodesEntry\x12\x0f\n\x07stopIds\x18\x02 \x03(\t\x12\x10\n\x08routeIds\x18\x03 \x03(\t\x12\x10\n\x08headings\x18\x05 \x03(\t\x12\x12\n\nserviceIds\x18\x04 \x03(\t\x1a\x30\n\x0eStopNodesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\r:\x02\x38\x01\"Z\n\x12GraphConfiguration\x12\x19\n\x11penaltyMultiplier\x18\x02 \x02(\x01\x12)\n!assumedWalkingSecondsPerKilometer\x18\x03 \x02(\x04\"\xa3\x01\n\x04\x45\x64ge\x12\x10\n\x08toNodeId\x18\x02 \x02(\r\x12\x15\n\rdepartureTime\x18\x03 \x01(\x04\x12\x0f\n\x07penalty\x18\x04 \x02(\x04\x12$\n\x04type\x18\x07 \x02(\x0e\x32\x16.networkgraph.EdgeType\x12\x19\n\x11\x61vailableServices\x18\x08 \x03(\r\x12\x1a\n\x12\x61\x63\x63\x65ssibilityFlags\x18\x06 \x01(\rJ\x04\x08\x01\x10\x02\"\xab\x01\n\x04Node\x12$\n\x04type\x18\x02 \x02(\x0e\x32\x16.networkgraph.NodeType\x12\x0e\n\x06stopId\x18\x03 \x02(\r\x12\x0f\n\x07routeId\x18\x04 \x01(\r\x12\x11\n\theadingId\x18\x07 \x01(\r\x12!\n\x05\x65\x64ges\x18\x05 \x03(\x0b\x32\x12.networkgraph.Edge\x12\x1a\n\x12\x61\x63\x63\x65ssibilityFlags\x18\x06 \x01(\rJ\x04\x08\x01\x10\x02J\x04\x08\x08\x10\x0b*y\n\x08\x45\x64geType\x12\x18\n\x14\x45\x44GE_TYPE_STOP_ROUTE\x10\x00\x12\x14\n\x10\x45\x44GE_TYPE_TRAVEL\x10\x01\x12\x16\n\x12\x45\x44GE_TYPE_TRANSFER\x10\x02\x12%\n!EDGE_TYPE_TRANSFER_NON_ADJUSTABLE\x10\x03*8\n\x08NodeType\x12\x12\n\x0eNODE_TYPE_STOP\x10\x00\x12\x18\n\x14NODE_TYPE_STOP_ROUTE\x10\x01\x42\x1d\n\x1b\x63l.emilym.gtfs.networkgraph')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'network_graph_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\033cl.emilym.gtfs.networkgraph'
  _globals['_GRAPHMAPPINGS_STOPNODESENTRY']._loaded_options = None
  _globals['_GRAPHMAPPINGS_STOPNODESENTRY']._serialized_options = b'8\001'
  _globals['_EDGETYPE']._serialized_start=815
  _globals['_EDGETYPE']._serialized_end=936
  _globals['_NODETYPE']._serialized_start=938
  _globals['_NODETYPE']._serialized_end=994
  _globals['_GRAPH']._serialized_start=38
  _globals['_GRAPH']._serialized_end=177
  _globals['_GRAPHMAPPINGS']._serialized_start=180
  _globals['_GRAPHMAPPINGS']._serialized_end=381
  _globals['_GRAPHMAPPINGS_STOPNODESENTRY']._serialized_start=333
  _globals['_GRAPHMAPPINGS_STOPNODESENTRY']._serialized_end=381
  _globals['_GRAPHCONFIGURATION']._serialized_start=383
  _globals['_GRAPHCONFIGURATION']._serialized_end=473
  _globals['_EDGE']._serialized_start=476
  _globals['_EDGE']._serialized_end=639
  _globals['_NODE']._serialized_start=642
  _globals['_NODE']._serialized_end=813
# @@protoc_insertion_point(module_scope)
