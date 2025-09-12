import json
import math
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Set, Tuple

from .. import network_graph_pb2 as pb
from ..component.base import Writer
from ..component.intermediaries import StopCSV, RouteCSV, TripCSV, StopTimeCSV
from ..time_helper import TimeHelper

metadata_byte_format = "< 5s B B I I f I I"

mapping_count_byte_format = "< I I I I"

node_byte_format = "<I I I B I I"
# Assumes that all services can be fit into three bytes
edge_byte_format = "<I I I 5s B"


def set_bits(bits: Set[int], size: int) -> bytes:
    data = bytearray(size)
    for bit in bits:
        bit_index = bit % 8
        byte_index = bit // 8
        data[byte_index] = byte_index | (1 << bit_index)

    return bytes(data)


def str_to_bytes(s: str) -> bytes:
    return s.encode('utf-8') + b'\x00'


class Edge(ABC):
    @abstractmethod
    def build(self, from_node_index: int) -> bytes:
        pass


@dataclass
class StopRouteEdge(Edge):
    connected_route_node: int
    available_services: Set[int]

    def build(self, from_node_index: int) -> bytes:
        return struct.pack(
            edge_byte_format,
            self.connected_route_node,
            0,
            0,
            set_bits(self.available_services, 5),
            0b10
        )


@dataclass
class TravelEdge(Edge):
    connected_route_node: int
    departure_time: int
    travel_time: int
    available_services: Set[int]
    wheelchair_accessible: bool
    bikes_allowed: bool

    def build(self, from_node_index: int) -> bytes:
        return struct.pack(
            edge_byte_format,
            self.connected_route_node,
            self.travel_time,
            self.departure_time,
            set_bits(self.available_services, 5),
            0b00 | (int(self.wheelchair_accessible) << 2) | (int(self.bikes_allowed) << 3),
        )


@dataclass
class TransferEdge(Edge):
    connected_stop_node: int
    travel_time: int

    def build(self, from_node_index: int) -> bytes:
        return struct.pack(
            edge_byte_format,
            self.connected_stop_node,
            self.travel_time,
            0,
            bytes(bytearray(5)),
            0b11,
        )


class Node(ABC):
    @abstractmethod
    def build(self, edge_position: int, edge_count: int) -> bytes:
        pass


@dataclass
class StopNode(Node):
    stop_index: int
    wheelchair_accessible: bool

    def build(self, edge_position: int, edge_count: int) -> bytes:
        return struct.pack(
            node_byte_format,
            self.stop_index,
            0,
            0,
            0b0 | (int(self.wheelchair_accessible) << 1),
            edge_position,
            edge_count
        )


@dataclass
class RouteNode(Node):
    stop_index: int
    route_index: int
    heading_index: int

    def build(self, edge_position: int, edge_count: int) -> bytes:
        return struct.pack(
            node_byte_format,
            self.stop_index,
            self.route_index,
            self.heading_index,
            0b1,
            edge_position,
            edge_count
        )


@dataclass
class NodeAndIndex:
    node: Node
    index: int


class ByteNetworkGraphGenerator(Writer):
    distance_time_multiplier = 25 * 60 # 25 mins per kilometer
    distance_threshold_km = 2

    time_helper: TimeHelper

    def __init__(
            self,
            stops: List[StopCSV],
            route_index: Dict[str, RouteCSV],
            trips: List[TripCSV],
            stop_time_index_by_trip: Dict[str, List[StopTimeCSV]],
    ):
        self.stops = stops
        self.route_index = route_index
        self.trips = trips
        self.stop_time_index_by_trip = stop_time_index_by_trip

        self.node_id_counter = 0
        self.stop_ids = []
        self.stop_id_to_node_index = {}

        self.route_id_to_route_index = {}
        self.route_ids = []
        self.stop_id_route_id_to_node_index: Dict[Tuple[int, str, int], int] = {}

        self.service_ids = []
        self.service_id_to_service_index = {}

        self.headings = []
        self.heading_to_heading_index = {}

        self.edges: Dict[int, List[Edge]] = {}
        self.reverse_edges: Dict[int, List[Edge]] = {}
        self.trip_stop_to_route_edges: Dict[int, Dict[Tuple[int, int], StopRouteEdge]] = {}

        self.nodes = []

    def _compute_graph(self):
        self._compute_headings()
        self._generate_stop_nodes()
        self._connect_stops_by_transfer()
        self._generate_route_nodes()

    def _connect_graph(self, reverse=False) -> bytes:
        edges = self.edges if not reverse else self.reverse_edges

        mapping_bytes = bytearray()
        node_bytes = bytearray()
        edges_bytes = bytearray()

        mapping_bytes.extend(struct.pack(
            mapping_count_byte_format,
            len(self.stops),
            len(self.route_ids),
            len(self.headings),
            len(self.service_ids)
        ))

        for stop in self.stops:
            mapping_bytes.extend(str_to_bytes(stop.id))
        for route_id in self.route_ids:
            mapping_bytes.extend(str_to_bytes(route_id))
        for headings in self.headings:
            mapping_bytes.extend(str_to_bytes(headings))
        for service_id in self.service_ids:
            mapping_bytes.extend(str_to_bytes(service_id))

        for node_index, node in enumerate(self.nodes):
            associated_edges = edges[node_index] if node_index in edges else []
            connective_edges = self.trip_stop_to_route_edges[
                node_index] if node_index in self.trip_stop_to_route_edges else {}

            for k, vs in connective_edges.items():
                associated_edges.append(vs)

            node_bytes.extend(node.build(len(edges_bytes), len(associated_edges)))

            for edge in associated_edges:
                edges_bytes.extend(edge.build(node_index))

        metadata_size = struct.calcsize(metadata_byte_format)
        mapping_size = len(mapping_bytes)
        nodes_size = len(node_bytes)
        edges_size = len(edges_bytes)

        metadata_bytes = struct.pack(
            metadata_byte_format,
            'emily'.encode('ascii'),
            1,
            5,
            metadata_size + mapping_size,
            metadata_size + mapping_size + nodes_size,
            1.0,
            self.distance_time_multiplier,
            len(self.nodes)
        )

        return metadata_bytes + mapping_bytes + node_bytes + edges_bytes

    def generate(self, output_folder: Path):
        self._compute_graph()
        graph = self._connect_graph(reverse=False)
        # Legacy because I'm dumb
        self._write(graph, output_folder.joinpath("v1/network_graph.eng"))
        self._write(graph, output_folder.joinpath("v1/network-graph.eng"))

        reverse_graph = self._connect_graph(reverse=True)
        self._write(reverse_graph, output_folder.joinpath("v1/network-graph-reverse.eng"))

    def _compute_headings(self):
        for trip in self.trips:
            if trip.trip_headsign in self.heading_to_heading_index:
                continue

            self.heading_to_heading_index[trip.trip_headsign] = len(self.headings)
            self.headings.append(trip.trip_headsign)

    def _generate_stop_nodes(self):
        for stop in self.stops:
            stop_node = self._create_stop_node(stop)
            self.nodes.append(stop_node.node)

    def _generate_route_nodes(self):
        for trip in self.trips:
            stop_times = self.stop_time_index_by_trip[trip.id]
            for i, stop_time in enumerate(stop_times):
                stop_index = self.stop_id_to_node_index[stop_time.stop_id]
                route_id = trip.route_id
                heading_index = self.heading_to_heading_index[trip.trip_headsign]

                if (stop_index, route_id, heading_index) not in self.stop_id_route_id_to_node_index:
                    route_node = self._create_route_node(
                        self.route_index[route_id],
                        heading_index,
                        stop_index
                    )
                    node_index = len(self.nodes)
                    self.nodes.append(route_node)
                    self.stop_id_route_id_to_node_index[(stop_index, route_id, heading_index)] = node_index
                    route_node = NodeAndIndex(route_node, node_index)
                else:
                    index = self.stop_id_route_id_to_node_index[(stop_index, route_id, heading_index)]
                    route_node = NodeAndIndex(self.nodes[index], index)

                self._create_stop_to_route_edge(stop_index, route_node.index, heading_index, trip.service_id)

                if i - 1 >= 0 and stop_time.stop_sequence > 0:
                    previous_stop_time = stop_times[i - 1]
                    previous_route_index = self.stop_id_route_id_to_node_index[(
                        self.stop_id_to_node_index[previous_stop_time.stop_id],
                        route_id,
                        heading_index
                    )]
                    previous_departure_time = self.time_helper.output_time_seconds(previous_stop_time.departure_time)
                    if previous_route_index == route_node.index:
                        continue

                    self._create_trip_edge(
                        previous_route_index,
                        route_node.index,
                        previous_departure_time,
                        self.time_helper.output_time_seconds(stop_time.arrival_time) - previous_departure_time,
                        trip.service_id,
                        trip.wheelchair_accessible == 1,
                        trip.bikes_allowed == 1
                    )

            # UGLY!!! CLEAN UP LAter :/
            for i, stop_time in enumerate(stop_times):
                stop_index = self.stop_id_to_node_index[stop_time.stop_id]
                route_id = trip.route_id
                heading_index = self.heading_to_heading_index[trip.trip_headsign]

                index = self.stop_id_route_id_to_node_index[(stop_index, route_id, heading_index)]
                route_node = NodeAndIndex(self.nodes[index], index)

                if i + 1 < len(stop_times) and stop_time.stop_sequence > 0:
                    next_stop_time = stop_times[i + 1]
                    next_route_index = self.stop_id_route_id_to_node_index[(
                        self.stop_id_to_node_index[next_stop_time.stop_id],
                        route_id,
                        heading_index
                    )]
                    next_departure_time = self.time_helper.output_time_seconds(next_stop_time.departure_time)
                    if next_route_index == route_node.index:
                        continue

                    self._create_trip_edge(
                        next_route_index,
                        route_node.index,
                        next_departure_time,
                        next_departure_time - self.time_helper.output_time_seconds(stop_time.arrival_time),
                        trip.service_id,
                        trip.wheelchair_accessible == 1,
                        trip.bikes_allowed == 1,
                        reverse=True
                    )

    @staticmethod
    def _distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        lat1 = math.radians(lat1)
        lng1 = math.radians(lng1)
        lat2 = math.radians(lat2)
        lng2 = math.radians(lng2)

        parameters = ((math.sin(lat1) * math.sin(lat2)) +
                      (math.cos(lat1) * math.cos(lat2) * math.cos(lng2 - lng1)))
        if parameters < -1:
            parameters = -1
        if parameters > 1:
            parameters = 1
        return math.acos(parameters) * 6371.0

    def _connect_stops_by_transfer(self):
        visited_stops = {}
        for stop1 in self.stops:
            for stop2 in self.stops:
                if stop1.id == stop2.id:
                    continue
                if (stop2.id, stop1.id) in visited_stops:
                    continue

                distance = self._distance(stop1.location.lat, stop1.location.lng, stop2.location.lat,
                                          stop2.location.lng)

                if distance > self.distance_threshold_km:
                    continue

                # print(f"Connecting {stop1.id} to {stop2.id} (distance = {distance})")

                self._create_transfer_edge(stop1, stop2, distance)
                self._create_transfer_edge(stop2, stop1, distance)
                visited_stops[(stop1.id, stop2.id)] = True

    def _create_stop_node(
            self,
            stop: StopCSV,
    ) -> NodeAndIndex:
        stop_index = len(self.stop_ids)
        self.stop_ids.append(stop.id)
        self.stop_id_to_node_index[stop.id] = stop_index

        # print(f"Creating stop node {stop_index}")

        out = StopNode(
            stop_index,
            stop.accessibility.wheelchair == 2
        )

        return NodeAndIndex(out, stop_index)

    def _register_route(
            self,
            route_id: str
    ) -> int:
        if route_id in self.route_id_to_route_index:
            return self.route_id_to_route_index[route_id]

        route_index = len(self.route_ids)
        self.route_ids.append(route_id)
        self.route_id_to_route_index[route_id] = route_index

        return route_index

    def _create_route_node(
            self,
            route: RouteCSV,
            heading_index: int,
            stop_index: int
    ) -> RouteNode:
        route_index = self._register_route(route.id)

        out = RouteNode(
            stop_index,
            route_index,
            heading_index
        )

        return out

    def _register_service(
            self,
            service_id: str
    ) -> int:
        if service_id in self.service_id_to_service_index:
            return self.service_id_to_service_index[service_id]

        service_index = len(self.service_ids)
        self.service_ids.append(service_id)
        self.service_id_to_service_index[service_id] = service_index

        print(f"Registering service {service_id}")
        return service_index

    def add_edge(self, node: int, edge: Edge, reverse: bool = False):
        if not reverse:
            if node in self.edges:
                self.edges[node].append(edge)
            else:
                self.edges[node] = [edge]
        else:
            if node in self.reverse_edges:
                self.reverse_edges[node].append(edge)
            else:
                self.reverse_edges[node] = [edge]

    def _create_stop_to_route_edge(
            self,
            stop_index: int,
            route_index: int,
            heading_index: int,
            service_id: str,
    ):
        service_index = self._register_service(service_id)

        if stop_index in self.trip_stop_to_route_edges:
            stop_edges = self.trip_stop_to_route_edges[stop_index]
        else:
            stop_edges = {}
        k = (route_index, heading_index)
        if k in stop_edges:
            edge = stop_edges[k]
            edge.available_services.add(service_index)
        else:
            edge = StopRouteEdge(route_index, {service_index})

        stop_edges[k] = edge
        self.trip_stop_to_route_edges[stop_index] = stop_edges

    def _create_trip_edge(
            self,
            from_node_index: int,
            to_node_index: int,
            departure_time: int,
            travel_time_sec: int,
            service_id: str,
            wheelchair_accessible: bool,
            bikes_allowed: bool,
            reverse: bool = False
    ):
        service_index = self._register_service(service_id)

        out = TravelEdge(
            to_node_index,
            departure_time,
            travel_time_sec,
            {service_index},
            wheelchair_accessible,
            bikes_allowed
        )

        self.add_edge(from_node_index, out, reverse)

    def _create_transfer_edge(
            self,
            stop1: StopCSV,
            stop2: StopCSV,
            distance: float,
    ):
        stop1_node_index = self.stop_id_to_node_index[stop1.id]
        stop2_node_index = self.stop_id_to_node_index[stop2.id]

        out = TransferEdge(
            stop2_node_index,
            int(distance * self.distance_time_multiplier)
        )

        self.add_edge(stop1_node_index, out)
        self.add_edge(stop1_node_index, out, reverse=True)
