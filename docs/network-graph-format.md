# Network Graph Byte Format

# Basics
All numbers are little endian. All strings are null terminated UTF-8 encoded.

# Structure
| Part     | Composition       |
| -------- | ----------------- |
| Metadata | [Fixed, Metadata] |
| Mapping  | [Mapping]         |
| Nodes    | Node[]            |
| Edges    | Edge[]            |

# Fixed
| Field        | Value        |
| ------------ | ------------ |
| Magic Number | 0x656D696C79 |
| Version      | 2            |

# Metadata
| Field                             | Length | Type    | Description                                                 |
| --------------------------------- | ------ | ------- | ----------------------------------------------------------- |
| Available Services Length         | 1      | uint8   | The number of bytes used to represent available services.   |
| Nodes Start                       | 4      | uint32  | Points to the beginning of the nodes collection.            |
| Edges Start                       | 4      | uint32  | Points to the beginning of the edges collection.            |
| Penalty Multiplier                | 4      | float32 | The number to multiply the penalty value by.                |
| assumedWalkingSecondsPerKilometer | 4      | uint32  | Assumed number of seconds required to traverse a kilometer. |
| Node count                        | 4      | uint32  | Total number of nodes                                       |
| Node Length                       | 1      | uint8   | The number of bytes used to represent a node.               |
| Edge Length                       | 1      | uint8   | The number of bytes used to represent an edge.              |

# Mapping
| Field         | Length   | Type     | Description                                  |
| ------------- | -------- | -------- | -------------------------------------------- |
| Stop Count    | 4        | uint32   | The number of stops                          |
| Route Count   | 4        | uint32   | The number of routes                         |
| Heading Count | 4        | uint32   | The number of headings                       |
| Trip Count    | 4        | uint32   | The number of trips                          |
| Service Count | 4        | uint32   | The number of services                       |
| Stop IDs      | Variable | String[] | A list of null terminated stop ID strings    |
| Route IDs     | Variable | String[] | A list of null terminated route ID strings   |
| Headings      | Variable | String[] | A list of null terminated heading ID strings |
| Trip IDs      | Variable | String[] | A list of null terminated trip ID strings    |
| Service IDs   | Variable | String[] | A list of null terminated service ID strings |

# Node
All nodes are the same length (21 bytes), but differ depending on whether they are a route or stop node.

## Stop
| Field        | Offset | Length | Type      | Description                                                   |
| ------------ | ------ | ------ | --------- | ------------------------------------------------------------- |
| Stop Index   | 0x00   | 4      | uint32    | Represents an index into the stop ID array.                   |
| Latitude     | 0x04   | 4      | float     | The latitude of the stop.                                     |
| Longitude    | 0x08   | 4      | float     | The longitude of the stop.                                    |
| Flags        | 0x0C   | 1      | NODE_FLAG | Bit flags describing this node.                               |
| Edge Pointer | 0x0D   | 4      | uint32    | Pointer to where in the edge collection this node's edges are |
| Edge Count   | 0x11   | 4      | uint32    | The number of edges associated with this node                 |

## Stop Route
| Field         | Offset | Length | Type      | Description                                                                            |
| ------------- | ------ | ------ | --------- | -------------------------------------------------------------------------------------- |
| Stop Index    | 0x00   | 4      | uint32    | Represents an index into the stop ID array                                             |
| Route Index   | 0x04   | 4      | uint32    | Represents an index into the route ID array. Only applicable on ROUTE_STOP type nodes. |
| Heading Index | 0x08   | 4      | uint32    | Represents an index into the heading array. Only applicable on ROUTE_STOP type nodes.  |
| Flags         | 0x0C   | 1      | NODE_FLAG | Bit flags describing this node.                                                        |
| Edge Pointer  | 0x0D   | 4      | uint32    | Pointer to where in the edge collection this node's edges are                          |
| Edge Count    | 0x11   | 4      | uint32    | The number of edges associated with this node                                          |

## NODE_FLAG
| Bit(s) | Name                  | Description                                             |
| ------ | --------------------- | ------------------------------------------------------- |
| 0      | Node Type             | `0` = Stop Node, `1` = Stop Route Node                  |
| 1      | Wheelchair Accessible | Boolean indicating if the stop is wheelchair accessible |

# Edge
| Field                | Offset | Length   | Type       | Description                                                                                                                                                                              |
| -------------------- | ------ | -------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Connected Node Index | 0x00   | 4        | uint32     | Which node this edge connects to.                                                                                                                                                        |
| Cost                 | 0x04   | 4        | uint32     | The travel time of an edge.                                                                                                                                                              |
| Departure Time       | 0x08   | 4        | uint32     | How many seconds into the day a service departs (only relevant for travel nodes).                                                                                                        |
| Trip Index           | 0x0C   | 4        | uint32     | Represents an index into the trip array. Only applicable on Travel type nodes.                                                                                                           |
| Available Services   | 0x10   | Variable | byte[]     | Each bit represents whether the edge is active for that index in the service ID array (i.e. bit 3 set to 1 indicates that the edge is active for the service at index 3 in Service IDs). |
| Flags                |        | 1        | ROUTE_FLAG | Bit flags describing this edge.                                                                                                                                                          |

## ROUTE_FLAG
| Bit(s) | Name                  | Description                                                                     |
| ------ | --------------------- | ------------------------------------------------------------------------------- |
| 0-1    | Edge Type             | `00` = Travel, `10` = Transfer, `01` = To stop node, `11` = To stop-route node. |
| 2      | Wheelchair Accessible | Boolean indicating if the route is wheelchair accessible.                       |
| 3      | Bikes Allowed         | Boolean indicating if the route allows bikes.                                   |
