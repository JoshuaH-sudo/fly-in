from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.connection import Connection
from src.drone import Drone
from src.zone import Zone


class Network(BaseModel):
    """Holds parsed map information."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    nb_drones: int = 0
    start_hub: str = ""
    end_hub: str = ""
    zones: dict[str, Zone] = Field(default_factory=dict)
    zone_connections: dict[str, set[Zone]] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)
    drones: list[Drone] = Field(default_factory=list)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        zone_connections: dict[str, set[Zone]] = {
            name: set() for name in self.zones
        }
        for connection in self.connections:
            zone_a = self.get_zone(connection.zone_a)
            zone_b = self.get_zone(connection.zone_b)
            zone_connections[zone_a.name].add(zone_b)
            zone_connections[zone_b.name].add(zone_a)
        object.__setattr__(self, "zone_connections", zone_connections)

        # Initialize drones based on nb_drones
        start_zone = self.get_zone(self.start_hub)
        object.__setattr__(
            self,
            "drones",
            [
                Drone(name=f"drone_{i+1}", current_zone=start_zone)
                for i in range(self.nb_drones)
            ],
        )

    @field_validator("nb_drones")
    @classmethod
    def validate_nb_drones(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("nb_drones must be a positive integer.")
        return value

    @field_validator("start_hub", "end_hub")
    @classmethod
    def validate_hub_name(cls, value: str) -> str:
        if not value:
            raise ValueError("start_hub and end_hub must be defined.")
        return value

    def get_zone_connections(self, zone_name: str) -> set[Zone]:
        return self.zone_connections.get(zone_name, set())

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise ValueError(f"Zone '{name}' not found in the network.")
        return self.zones[name]

    def all_drones_at_end(self) -> bool:
        """Check if all drones have reached the end hub."""
        return all(
            drone.current_pos.name == self.end_hub for drone in self.drones
        )
