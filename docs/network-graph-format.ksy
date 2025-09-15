meta:
  id: network_graph
  title: Network Graph Format
  file-extension: eng
  endian: le
  encoding: utf-8
  ks-version: 0.9

doc: |
  Binary format representing a transport network graph.
  Version 2 of the format. All integers are little-endian.
  Strings are UTF-8, null terminated.

seq:
  - id: magic
    type: str
    size: 5
    encoding: ASCII
    doc: Magic string (must equal "emily")
  - id: version
    type: u1
    doc: File format version (must equal 2)
    valid:
      eq: 2
  - id: available_services_length
    type: u1
    doc: Number of bytes in service availability bitmask
  - id: nodes_start
    type: u4
    doc: Absolute offset of Nodes section
  - id: edges_start
    type: u4
    doc: Absolute offset of Edges section
  - id: penalty_multiplier
    type: f4
    doc: Multiplier for penalties
  - id: assumed_walking_seconds_per_kilometer
    type: u4
    doc: Assumed walking seconds per km
  - id: node_count
    type: u4
    doc: Number of nodes in file
  - id: node_length
    type: u1
    doc: Length of each node entry (bytes)
  - id: edge_length
    type: u1
    doc: Length of each edge entry (bytes)
  - id: mapping
    type: mapping_section

instances:
  nodes:
    pos: nodes_start
    type: node
    repeat: expr
    repeat-expr: node_count

  edges:
    pos: edges_start
    type: edge
    repeat: eos
    
  valid_magic:
    value: magic == "emily"

types:
  mapping_section:
    seq:
      - id: stop_count
        type: u4
      - id: route_count
        type: u4
      - id: heading_count
        type: u4
      - id: trip_count
        type: u4
      - id: service_count
        type: u4

      - id: stop_ids
        type: strz
        repeat: expr
        repeat-expr: stop_count
      - id: route_ids
        type: strz
        repeat: expr
        repeat-expr: route_count
      - id: headings
        type: strz
        repeat: expr
        repeat-expr: heading_count
      - id: trip_ids
        type: strz
        repeat: expr
        repeat-expr: trip_count
      - id: service_ids
        type: strz
        repeat: expr
        repeat-expr: service_count

  node:
    seq:
      - id: stop_index
        type: u4
      - id: latitude
        type: f4
        if: (flags & 1) == 0
      - id: longitude
        type: f4
        if: (flags & 1) == 0
      - id: route_index
        type: u4
        if: (flags & 1) == 1
      - id: heading_index
        type: u4
        if: (flags & 1) == 1
      - id: flags
        type: u1
        doc: |
          Bit 0 = Node type (0=Stop,1=Stop-Route)
          Bit 1 = Wheelchair accessible
      - id: edge_pointer
        type: u4
        doc: Offset in edges section
      - id: edge_count
        type: u4

    instances:
      node_type:
        value: flags & 1
      wheelchair_accessible:
        value: (flags >> 1) & 1

  edge:
    seq:
      - id: connected_node_index
        type: u4
      - id: cost
        type: u4
      - id: departure_time
        type: u4
        if: (flags & 3) == 0  # only for travel edges
      - id: trip_index
        type: u4
        if: (flags & 3) == 0  # only for travel edges
      - id: available_services
        size: _root.available_services_length
      - id: flags
        type: u1
        doc: |
          Bits 0-1 = Edge type
            00 = Travel
            01 = To Stop node
            10 = Transfer
            11 = To Stop-Route node
          Bit 2 = Wheelchair accessible
          Bit 3 = Bikes allowed

    instances:
      edge_type:
        value: flags & 3
      wheelchair_accessible:
        value: (flags >> 2) & 1
      bikes_allowed:
        value: (flags >> 3) & 1

