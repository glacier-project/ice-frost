import csv
import logging
import os
import random
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import networkx as nx
from typing_extensions import override

SAVE_PUPDATES = os.getenv("SAVE_PUPDATES", "false").lower() == "true"

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

SEGMENT_1_TT = 17584
SEGMENT_2_TT = 22198
SEGMENT_3_TT = 18315
SEGMENT_4_TT = 8691
SEGMENT_5_TT = 10055
SEGMENT_6_TT = 17594
SEGMENT_7_TT = 21649
SEGMENT_8_TT = 13399
# Are these correct?
INTERCHANGE_TT = 7000
HALF_INTERCHANGE_TT = INTERCHANGE_TT // 2.5
BAY_TRANSFER_TT = 2000
BAY2_IO = 1272
BAY3_IO = 2833
BAY4_IO = 1585

BAY2_12 = 1766
BAY2_21 = 2077
BAY2_23 = 4413
BAY2_32 = 4857

BAY3_12 = 3925
BAY3_21 = 3779
BAY3_23 = 2061
BAY3_32 = 2173

BAY4_12 = 2809
BAY4_21 = 2603
BAY4_23 = 3492
BAY4_32 = 4292

class ConveyorPosition:
    """Represents a position on the conveyor system.

    Attributes:
        start_node (str): The starting node of the conveyor position.
        end_node (str | None): The ending node of the conveyor position. If None, it represents a single node.
        duration (int): The time duration to traverse from start_node to end_node.
    """

    def __init__(self, start_node: str, end_node: str | None = None, duration: int = 0):
        self.start_node = start_node
        self.end_node = end_node
        self.duration = duration

    def get_source_node(self) -> str:
        """Get the source node of the conveyor position.

        Returns:
            str: The source node.
        """
        return self.start_node

    def get_target_node(self) -> str:
        """Get the target node of the conveyor position.

        The target node is the end_node if it exists; otherwise, it is the
        start_node (it represents a single node position, e.g., a warehouse or
        quality control destination).

        Returns:
            str: The target node.
        """
        if self.end_node is not None:
            return self.end_node
        return self.start_node

    def get_remaining_time(self, timestamp: int, position_timestamp: int) -> int:
        """Calculate the remaining time to traverse the conveyor position.

        Args:
            timestamp (int): The current timestamp.
            position_timestamp (int): The timestamp at which the pallet reached this position.
        Returns:
            int: The remaining time to traverse the conveyor position.
        """
        assert (
            timestamp >= position_timestamp
        ), "Current timestamp must be greater than or equal to position timestamp"
        elapsed_time = timestamp - position_timestamp
        return self.duration - elapsed_time


class PalletPosition(Enum):
    """Enumeration of pallet positions on the conveyor system."""

    S1 = ConveyorPosition("M", "L", SEGMENT_1_TT)
    S2 = ConveyorPosition("L", "I", SEGMENT_2_TT)
    S3 = ConveyorPosition("I", "H", SEGMENT_3_TT)
    S4_1 = ConveyorPosition("H", "40", BAY_TRANSFER_TT)
    S4_2 = ConveyorPosition("40", "F", BAY_TRANSFER_TT)
    S5 = ConveyorPosition("A", "B", SEGMENT_5_TT)
    S6 = ConveyorPosition("B", "C", SEGMENT_6_TT)
    S7 = ConveyorPosition("C", "D", SEGMENT_7_TT)
    S8 = ConveyorPosition("D", "E", SEGMENT_8_TT)
    WH = ConveyorPosition("40")
    QC_1 = ConveyorPosition("34")
    QC_2 = ConveyorPosition("35")
    QC_3 = ConveyorPosition("36")
    RBTC_1 = ConveyorPosition("25")
    RBTC_2 = ConveyorPosition("26")
    RBTC_3 = ConveyorPosition("27")
    MILL_1 = ConveyorPosition("17")
    MILL_2 = ConveyorPosition("18")
    MILL_3 = ConveyorPosition("19")
    SPEA_1 = ConveyorPosition("9")
    UNDEFINED = ConveyorPosition("UNDEFINED")


_position_map = {pos.name: pos for pos in PalletPosition}
_position_map["40"] = PalletPosition.WH
_position_map["34"] = PalletPosition.QC_1
_position_map["35"] = PalletPosition.QC_2
_position_map["36"] = PalletPosition.QC_3
_position_map["25"] = PalletPosition.RBTC_1
_position_map["26"] = PalletPosition.RBTC_2
_position_map["27"] = PalletPosition.RBTC_3
_position_map["17"] = PalletPosition.MILL_1
_position_map["18"] = PalletPosition.MILL_2
_position_map["19"] = PalletPosition.MILL_3
_position_map["9"] = PalletPosition.SPEA_1


def get_conveyor_position(position: str | int):
    """Get the PalletPosition enum member from a string or integer representation.

    Args:
        position (str | int): The string name or integer representation of the pallet position.
    Returns:
        PalletPosition: The corresponding PalletPosition enum member.
    """
    if isinstance(position, int):
        position = str(position)
    return _position_map.get(position, PalletPosition.UNDEFINED)


@dataclass
class PalletStatus:
    """Represents the status of a pallet on the conveyor system.

    Attributes:
        id (int): The unique identifier of the pallet.
        pallet_position (PalletPosition): The current position of the pallet on the conveyor.
        position_timestamp (int): The timestamp at which the pallet reached its current position.
    """

    id: int
    pallet_position: PalletPosition
    position_timestamp: int


def create_pallets(num_pallets: int = 10) -> list[PalletStatus]:
    """Create a list of PalletStatus objects with default values.

    Args:
        num_pallets (int): The number of pallets to create. Default is 10.
    Returns:
        list: A list of PalletStatus objects with default positions and timestamps.
    """
    return [
        PalletStatus(id=i, pallet_position=PalletPosition.UNDEFINED, position_timestamp=0)
        for i in range(1, num_pallets + 1)
    ]


def create_default_conveyor_graph(pallets: list[PalletStatus] | None = None) -> nx.DiGraph:
    """Create the default conveyor graph with predefined edge weights.
    Args:
        pallets (list | None): List of PalletStatus objects to add as nodes. If None, no pallet nodes are added.
    Returns:
        nx.DiGraph: The default conveyor graph.
    """
    if pallets is None:
        pallets = create_pallets()

    adjacency_dict = {
        "A": {
            "B": {"weight": SEGMENT_5_TT},
            "H": {"weight": SEGMENT_5_TT + INTERCHANGE_TT},
            "34": {"weight": SEGMENT_5_TT + BAY4_IO + INTERCHANGE_TT},
        },
        "34": {
            "35": {"weight": BAY4_12},
            "H": {"weight": BAY4_IO + HALF_INTERCHANGE_TT},
            "B": {"weight": BAY4_IO + INTERCHANGE_TT},
        },
        "35": {"36": {"weight": BAY4_23}, "34": {"weight": BAY4_21}},
        "36": {"35": {"weight": BAY4_32}},
        "B": {
            "C": {"weight": SEGMENT_6_TT},
            "I": {"weight": SEGMENT_6_TT + INTERCHANGE_TT},
            "25": {"weight": SEGMENT_6_TT + BAY3_IO + INTERCHANGE_TT},
        },
        "C": {
            "D": {"weight": SEGMENT_7_TT},
            "L": {"weight": SEGMENT_7_TT + INTERCHANGE_TT},
            "17": {"weight": SEGMENT_7_TT + BAY2_IO + INTERCHANGE_TT},
        },
        "D": {
            "M": {"weight": SEGMENT_8_TT + INTERCHANGE_TT},
            "9": {"weight": SEGMENT_8_TT + BAY_TRANSFER_TT + INTERCHANGE_TT},
        },
        "M": {
            "L": {"weight": SEGMENT_1_TT},
            "D": {"weight": SEGMENT_1_TT + INTERCHANGE_TT},
            "17": {"weight": SEGMENT_1_TT + BAY2_IO + HALF_INTERCHANGE_TT},
        },
        "9": {"M": {"weight": BAY_TRANSFER_TT}},
        "L": {
            "I": {"weight": SEGMENT_2_TT},
            "25": {"weight": SEGMENT_2_TT + BAY3_IO + HALF_INTERCHANGE_TT},
            "C": {"weight": SEGMENT_2_TT + INTERCHANGE_TT},
        },
        "17": {
            "18": {"weight": BAY2_12},
            "L": {"weight": BAY2_IO + HALF_INTERCHANGE_TT},
            "D": {"weight": BAY2_IO + INTERCHANGE_TT},
        },
        "18": {"19": {"weight": BAY2_23}, "17": {"weight": BAY2_21}},
        "19": {"18": {"weight": BAY2_32}},
        "I": {
            "H": {"weight": SEGMENT_3_TT},
            "34": {"weight": SEGMENT_3_TT + BAY4_IO + HALF_INTERCHANGE_TT},
            "B": {"weight": SEGMENT_3_TT + INTERCHANGE_TT},
        },
        "25": {
            "26": {"weight": BAY3_12},
            "I": {"weight": BAY3_IO + HALF_INTERCHANGE_TT},
            "C": {"weight": BAY3_IO + INTERCHANGE_TT},
        },
        "26": {"27": {"weight": BAY3_23}, "25": {"weight": BAY3_21}},
        "27": {"26": {"weight": BAY3_32}},
        "H": {
            "40": {"weight": SEGMENT_4_TT},
        },
        "40": {
            "A": {"weight": INTERCHANGE_TT + BAY_TRANSFER_TT},
        },
        "UNDEFINED": {
            "A": {"weight": 1e9},
        },
    }

    conveyor_graph = nx.DiGraph(adjacency_dict)
    return conveyor_graph


def create_conveyor_graph(
    conveyor_graph: nx.DiGraph | str | None = None, pallets: list[PalletStatus] | None = None
) -> nx.DiGraph:
    """Create or load a conveyor graph and add pallet nodes.

    Args:
        conveyor_graph (nx.DiGraph | str | None): If None, create the default
        conveyor graph. If a string, load the graph from a GML file at the given
        path. If a nx.DiGraph, use it directly.
        pallets (list | None): List of PalletStatus objects to add as nodes.
        If None, create default pallets.
    Returns:
        nx.DiGraph: The conveyor graph with pallet nodes added.
    """
    if conveyor_graph is None:
        conveyor_graph = create_default_conveyor_graph(pallets)
    elif isinstance(conveyor_graph, str):
        conveyor_graph = create_default_conveyor_graph(nx.read_gml(conveyor_graph))
    assert isinstance(
        conveyor_graph, nx.DiGraph
    ), "conveyor_graph must be None, a file path string, or a networkx.DiGraph instance."

    if pallets is None:
        pallets = create_pallets()

    # Add pallet nodes
    for pallet in pallets:
        node_id = _get_pallet_node_id(pallet)
        conveyor_graph.add_node(node_id)
        conveyor_graph.add_edge(node_id, "UNDEFINED", weight=0)

    return conveyor_graph


def _shortest_path_length(graph: nx.DiGraph, source: str, target: str) -> float:
    """Compute the shortest path length between source and target nodes in the graph.

    Args:
        graph (nx.DiGraph): The conveyor graph.
        source (str): The source node ID.
        target (str): The target node ID.
    Returns:
        float: The shortest path length (total weight) from source to target.
    """
    if source == target:
        return 0.0

    try:
        return float(nx.shortest_path_length(graph, source=source, target=target, weight="weight"))
    except nx.NetworkXNoPath:
        logger.warning(f"No path found from {source} to {target} in conveyor graph.")
        return 1e9


def _get_pallet_node_id(pallet: PalletStatus) -> str:
    """Get the node ID for a pallet in the conveyor graph.
    Args:
        pallet (PalletStatus): The pallet status object.
    Returns:
        str: The node ID for the pallet.
    """
    return f"Pallet_{pallet.id}"


def _update_pallet_edges(graph: nx.DiGraph, pallet: PalletStatus, timestamp: int) -> None:
    """Update the edges of a pallet node in the conveyor graph based on its current position.
    Args:
        graph (nx.DiGraph): The conveyor graph.
        pallet (PalletStatus): The pallet status object.
        timestamp (int): The current timestamp.
    """
    # Remove existing edges from pallet node and add new edge to current position
    node_id = _get_pallet_node_id(pallet)
    current_edges = list(graph.edges(node_id))
    if current_edges:
        graph.remove_edges_from(current_edges)

    # Add edge from the pallet node to its current position in the conveyor graph
    pallet_target_node = pallet.pallet_position.value.get_target_node()
    weight = pallet.pallet_position.value.get_remaining_time(timestamp, pallet.position_timestamp)
    weight = max(0, weight)  # Ensure non-negative weight
    graph.add_edge(node_id, pallet_target_node, weight=weight)


class AbstractPalletMetric(ABC):
    """Abstract base class for pallet distance metrics.

    Attributes:
        _pallets (list): List of PalletStatus objects representing the pallets.
    """

    def __init__(self) -> None:
        self._pallets = create_pallets()
        if SAVE_PUPDATES:
            self._create_log_file()

    def set_pallet_position(self, pallet_id: int, position: PalletPosition, timestamp: int) -> None:
        """Update the position of a pallet to a new position at a given timestamp.

        Args:
            pallet_id (int): The ID of the pallet to update.
            position (PalletPosition): The new position of the pallet.
            timestamp (int): The timestamp of the position update.
        """
        pallet = self._pallets[pallet_id - 1]

        if pallet.pallet_position == position:
            return

        # Update pallet position and timestamp
        pallet.pallet_position = position
        pallet.position_timestamp = timestamp

        if SAVE_PUPDATES:
            logger.debug(
                f"Logging pallet position update: pallet_id={pallet_id}, position={position.name}, timestamp={timestamp}"
            )
            self._csv_writer.writerow([timestamp, pallet_id, position.name])

    @abstractmethod
    def get_pallets_to(self, destination: PalletPosition, timestamp: int) -> list[int]:
        """Get a list of pallet IDs sorted to a destination based on the metric.
        Args:
            destination (PalletPosition): The destination position.
            timestamp (int): The current timestamp.
        Returns:
            list: A list of pallet IDs sorted according to the metric.
        """
        pass

    def _create_log_file(self):
        filename = f"pallet_distance_metric_log_{uuid.uuid4()}.csv"
        logger.debug(f"Creating pallet distance metric log file: {filename}")
        self._log_file = open(filename, mode="w")  # noqa: SIM115
        self._csv_writer = csv.writer(self._log_file)
        self._csv_writer.writerow(["timestamp", "pallet_id", "pallet_position"])

    def close_log_file(self):
        if SAVE_PUPDATES:
            self._log_file.flush()
            self._log_file.close()


class DummyPalletMetric(AbstractPalletMetric):
    """A dummy pallet metric that returns pallet IDs in their natural order."""

    def __init__(self) -> None:
        super().__init__()

    @override
    def get_pallets_to(self, destination: PalletPosition, timestamp: int) -> list[int]:
        """Return pallet IDs in their natural order.
        Args:
            destination (PalletPosition): The destination position.
            timestamp (int): The current timestamp.
        Returns:
            list: A list of pallet IDs in natural order.
        """
        return list(range(1, 11))


class RandomPalletMetric(AbstractPalletMetric):
    """A random pallet metric that returns pallet IDs in a random order."""

    def __init__(self) -> None:
        super().__init__()

    @override
    def get_pallets_to(self, destination: PalletPosition, timestamp: int) -> list[int]:
        """Return pallet IDs in a random order.
        Args:
            destination (PalletPosition): The destination position.
            timestamp (int): The current timestamp.
        Returns:
            list: A list of pallet IDs in random order.
        """
        pallets = list(range(1, 11))
        random.shuffle(pallets)
        return pallets


class PalletDistanceMetric(AbstractPalletMetric):
    """A pallet distance metric that sorts pallets based on their distance to a destination.

    Attributes:
        _conveyor_graph (nx.DiGraph): The conveyor graph used for distance calculations.
    """

    def __init__(self, conveyor_graph: nx.DiGraph | str | None = None) -> None:
        super().__init__()
        conveyor_graph = create_conveyor_graph(conveyor_graph, self._pallets)

        assert isinstance(
            conveyor_graph, nx.DiGraph
        ), "Cannot initialize PalletDistanceMetric: conveyor_graph must be None, a file path string, or a networkx.DiGraph instance."
        self._conveyor_graph = conveyor_graph

    @override
    def get_pallets_to(self, destination: PalletPosition, timestamp: int) -> list[int]:
        """Get a list of pallet IDs sorted by their distance to the destination.
        Args:
            destination (PalletPosition): The destination position.
            timestamp (int): The current timestamp.
        Returns:
            list: A list of pallet IDs sorted by distance to the destination.
        """
        pallet_distances: list[tuple[float, int, PalletStatus]] = []

        for pallet in self._pallets:
            _update_pallet_edges(self._conveyor_graph, pallet, timestamp)
            distance = _shortest_path_length(
                self._conveyor_graph, _get_pallet_node_id(pallet), destination.value.start_node
            )

            remaining_time = pallet.pallet_position.value.get_remaining_time(
                timestamp, pallet.position_timestamp
            )
            pallet_distances.append((distance, remaining_time, pallet))

        # Sort by distance, then by pallet ID
        # print("Pallet distances:", [(p.id, dist) for p, dist in pallet_distances])
        logger.debug(
            f"Pallet distances to {destination.name} at time {timestamp}: {pallet_distances}"
        )
        pallet_distances.sort(key=lambda x: (x[0], x[1], x[2].id))
        ret = [pallet.id for _, _, pallet in pallet_distances]
        logger.debug(
            f"Pallets sorted by distance to {destination.name} at time {timestamp}: {[pallet for _, _, pallet in pallet_distances]}"
        )
        return ret


class PalletMetricType(Enum):
    """Enumeration of pallet metric types."""

    ID = "ID"
    RANDOM = "RANDOM"
    DISTANCE = "DISTANCE"


def _get_pallet_metric(
    metric_type: PalletMetricType | str, conveyor_graph: nx.DiGraph | str | None = None
) -> AbstractPalletMetric:
    """Factory function to create a pallet metric instance based on the specified type.

    Args:
        metric_type (PalletMetricType | str): The type of pallet metric to create.
        conveyor_graph (nx.DiGraph | str | None): The conveyor graph to use for distance metrics.
    Returns:
        AbstractPalletMetric: An instance of the specified pallet metric.
    """
    if isinstance(metric_type, str):
        metric_type = PalletMetricType(metric_type)

    if metric_type == PalletMetricType.ID:
        return DummyPalletMetric()
    elif metric_type == PalletMetricType.RANDOM:
        return RandomPalletMetric()
    elif metric_type == PalletMetricType.DISTANCE:
        return PalletDistanceMetric(conveyor_graph=conveyor_graph)
    else:
        raise ValueError(f"Unknown PalletMetricType: {metric_type}")


if __name__ == "__main__":
    metric = PalletDistanceMetric()
    conveyor_graph = metric._conveyor_graph

    metric.set_pallet_position(1, PalletPosition.S1, timestamp=10)
    metric.set_pallet_position(2, PalletPosition.S3, timestamp=20)
    metric.set_pallet_position(3, PalletPosition.QC_1, timestamp=15)

    print("Pallets for MILL_1:", metric.get_pallets_to(PalletPosition.MILL_1, timestamp=30))
