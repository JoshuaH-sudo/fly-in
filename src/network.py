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
        """Build graph structures and initialize drones from parsed values.

        Args:
            **kwargs: Network field values passed to the base model.
        """
        super().__init__(**kwargs)
        zone_connections: dict[str, set[Zone]] = {
            name: set() for name in self.zones
        }
        for connection in self.connections:
            zone_a = self.get_position(connection.zone_a)
            zone_b = self.get_position(connection.zone_b)
            if not isinstance(zone_a, Zone) or not isinstance(zone_b, Zone):
                raise ValueError(
                    "Connections must reference existing zones."
                )
            zone_connections[zone_a.name].add(zone_b)
            zone_connections[zone_b.name].add(zone_a)
        object.__setattr__(self, "zone_connections", zone_connections)

        # Initialize drones based on nb_drones
        start_zone = self.get_position(self.start_hub)
        if not isinstance(start_zone, Zone):
            raise ValueError("start_hub must reference a valid zone.")
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
        """Ensure the number of drones is strictly positive.

        Args:
            value: Number of drones declared in the map.

        Returns:
            Validated positive drone count.
        """
        if value <= 0:
            raise ValueError("nb_drones must be a positive integer.")
        return value

    @field_validator("start_hub", "end_hub")
    @classmethod
    def validate_hub_name(cls, value: str) -> str:
        """Ensure start and end hub names are present.

        Args:
            value: Hub zone name.

        Returns:
            Validated non-empty hub name.
        """
        if not value:
            raise ValueError("start_hub and end_hub must be defined.")
        return value

    def get_zone_neighbors(self, position: Zone | Connection) -> set[Zone]:
        """Return zones directly connected to a position.

        Args:
            position: Current zone or connection where a drone is located.

        Returns:
            Adjacent zones available from the given position.
        """
        if isinstance(position, Connection):
            # For a connection, return the next zones on the other side
            zone_a = self.get_position(position.zone_a)
            zone_b = self.get_position(position.zone_b)
            if not isinstance(zone_a, Zone) or not isinstance(zone_b, Zone):
                raise ValueError(
                    "Connection endpoints must resolve to zones."
                )
            return {
                zone_a,
                zone_b,
            }
        # For a zone, return its directly connected neighbors
        return self.zone_connections.get(position.name, set())

    def get_position(
        self,
        position: str | Zone | Connection,
    ) -> Zone | Connection:
        """Return one position by name or pass through an existing position.

        Args:
            position: Zone/connection name or existing position object.

        Returns:
            Matching zone/connection object.
        """
        if isinstance(position, (Zone, Connection)):
            return position

        if position in self.zones:
            return self.zones[position]

        for connection in self.connections:
            if connection.name == position:
                return connection

        raise ValueError(
            f"Position '{position}' not found in the network."
        )

    def all_drones_at_end(self) -> bool:
        """Check if all drones have reached the end hub.

        Returns:
            ``True`` if every drone is currently at the end hub.
        """
        return all(
            drone.current_pos.name == self.end_hub for drone in self.drones
        )
