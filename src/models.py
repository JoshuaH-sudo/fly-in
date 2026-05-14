"""Core data models for Fly-in."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Zone:
    """Represents a single zone/hub in the map."""

    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1


@dataclass(slots=True)
class Connection:
    """Represents a bidirectional connection between two zones."""

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1


@dataclass(slots=True)
class Network:
    """Holds parsed map information."""

    nb_drones: int = 0
    start_hub: str = ""
    end_hub: str = ""
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
