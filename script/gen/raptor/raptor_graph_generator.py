from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict

from ..component import GeneratorComponent
from ..component.base import Writer
from ..component.intermediaries import StopCSV, RouteCSV, TripCSV, StopTimeCSV
from .. import network_graph_pb2 as pb


class SeparatedEdge(ABC):
    @abstractmethod
    def build(self, from_node_id: int) -> pb.Edge:
        pass

class LogicTreeNode(ABC):

    @abstractmethod
    def build(self) -> bytes:
        pass

@dataclass
class LeafLogicTreeNode(LogicTreeNode):
    service_index: int
    service_index_byte_width: int

    def build(self) -> bytes:
        return bytes(
            [0b1]
        ) + self.service_index.to_bytes(self.service_index_byte_width, byteorder='little')


@dataclass
class AndLogicTreeNode(LogicTreeNode):
    left: LogicTreeNode
    right: LogicTreeNode

    def build(self) -> bytes:
        return bytes([0b110]) + self.left.build() + self.right.build()


@dataclass
class OrLogicTreeNode(LogicTreeNode):
    left: LogicTreeNode
    right: LogicTreeNode

    def build(self) -> bytes:
        return bytes([0b010]) + self.left.build() + self.right.build()


@dataclass
class NotLogicTreeNode(LogicTreeNode):
    child: LogicTreeNode

    def build(self) -> bytes:
        return bytes([0b111]) + self.child.build()


@dataclass
class TripRouteEdge(SeparatedEdge):
    route_id: int
    condition: Optional[LogicTreeNode]

    def build(self, from_node_id: int) -> pb.Edge:
        out = pb.Edge()
        out.toNodeId = self.route_id
        out.penalty = 0
        if self.condition is not None:
            out.condition = self.condition.build()

        return out


@dataclass
class NodeAndIndex:
    node: pb.Node
    index: int


class NetworkGraphGenerator(Writer):

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

        self.route_ids = []
        self.stop_id_route_id_to_node_index = {}

        self.service_ids = []
        self.service_id_to_service_index = {}

        self.trip_stop_to_route_edges: Dict[int, Dict[int, TripRouteEdge]] = {}

        self.service_id_byte_width = 1

        self.nodes = []

    def generate(self, output_folder: Path):
        self._generate_stop_nodes()
        self._generate_route_nodes()
        self._add_all_edges()

        out = pb.Graph()

        for node in self.nodes:
            out.nodes.append(node)

        out.config.conditionLeafNodeWidth = self.service_id_byte_width
        out.config.penaltyMultiplier = 1

        for k, v in self.stop_id_to_node_index.items():
            out.mappings.stopNodes[k] = v

        for s in self.stop_ids:
            out.mappings.stopIds.append(s)

        for r in self.route_ids:
            out.mappings.routeIds.append(r)

        for s in self.service_ids:
            out.mappings.serviceIds.append(s)

        print(out.nodes[0])
        self._write(out.SerializeToString(), output_folder.joinpath("network_graph.pb"))

    def _add_all_edges(self):
        print("Adding all edges")
        for stop_index, v in self.trip_stop_to_route_edges.items():
            node = self.nodes[stop_index]
            print(f"Adding edges for node {stop_index}")
            for k, vs in v.items():
                node.edges.append(vs.build(stop_index))

    def _generate_stop_nodes(self):
        for stop in self.stops:
            stop_node = self._create_stop_node(stop)
            self.nodes.append(stop_node.node)

    def _generate_route_nodes(self):
        for trip in self.trips:
            stop_times = self.stop_time_index_by_trip[trip.id]
            for stop_time in stop_times:
                stop_index = self.stop_id_to_node_index[stop_time.stop_id]
                route_id = trip.route_id

                if (stop_index, route_id) not in self.stop_id_route_id_to_node_index:
                    route_node = self._create_route_node(
                        self.route_index[route_id],
                        stop_index
                    )
                    self.nodes.append(route_node.node)
                else:
                    index = self.stop_id_route_id_to_node_index[(stop_index, route_id)]
                    route_node = NodeAndIndex(index, self.route_ids[index])

                self._create_stop_to_route_edge(stop_index, route_node.index, trip.service_id)

    def _create_stop_node(
            self,
            stop: StopCSV,
    ) -> NodeAndIndex:
        stop_index = len(self.stop_ids)
        self.stop_ids.append(stop.id)
        self.stop_id_to_node_index[stop.id] = stop_index

        print(f"Creating stop node {stop_index}")

        out = pb.Node()
        out.type = pb.NodeType.NODE_TYPE_STOP
        out.stopId = stop_index
        out.accessibilityFlags = 0b1 if stop.accessibility.wheelchair == 2 else 0b0

        return NodeAndIndex(out, stop_index)

    def _create_route_node(
            self,
            route: RouteCSV,
            stop_index: int
    ) -> NodeAndIndex:
        route_index = len(self.route_ids)
        self.route_ids.append(route.id)

        print(f"Creating route node {route_index}")

        out = pb.Node()
        out.type = pb.NodeType.NODE_TYPE_STOP_ROUTE
        out.stopId = stop_index
        out.routeId = route_index

        return NodeAndIndex(out, route_index)

    def _register_service(
            self,
            service_id: str
    ) -> int:
        service_index = len(self.service_ids)
        self.service_ids.append(service_id)
        self.service_id_to_service_index[service_id] = service_index

        print(f"Registering service {service_id}")
        return service_index

    def _create_stop_to_route_edge(
            self,
            stop_index: int,
            route_index: int,
            service_id: str,
    ):
        if service_id not in self.service_id_to_service_index:
            service_index = self._register_service(service_id)
        else:
            service_index = self.service_id_to_service_index[service_id]

        condition = LeafLogicTreeNode(
            service_index=service_index,
            service_index_byte_width=self.service_id_byte_width,
        )

        if stop_index in self.trip_stop_to_route_edges:
            stop_edges = self.trip_stop_to_route_edges[stop_index]
        else:
            stop_edges = {}

        if route_index in stop_edges:
            edge = stop_edges[route_index]
            edge.condition = OrLogicTreeNode(edge.condition, condition)
        else:
            edge = TripRouteEdge(route_index, condition)

        stop_edges[route_index] = edge
        self.trip_stop_to_route_edges[stop_index] = stop_edges

