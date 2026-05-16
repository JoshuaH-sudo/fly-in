"""Connection model for Fly-in."""

from typing import Any

from pydantic import ConfigDict, field_validator

from src.drone_occupancy import DroneOccupancy


class Connection(DroneOccupancy):
    """Represents a bidirectional connection between two zones."""

    model_config = ConfigDict(frozen=True)

    name: str = ""
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    @field_validator("zone_a", "zone_b")
    @classmethod
    def validate_zone_name(cls, value: str) -> str:
        """Validate endpoint zone names for connection declarations.

        Args:
            value: Zone name to validate.

        Returns:
            The validated zone name.
        """
        if not value:
            raise ValueError("Connection zone names cannot be empty.")
        if " " in value or "-" in value:
            raise ValueError(
                "Connection zone names cannot contain spaces or dashes."
            )
        return value

    @field_validator("max_link_capacity")
    @classmethod
    def validate_max_link_capacity(cls, value: int) -> int:
        """Validate that link capacity is positive.

        Args:
            value: Link capacity value.

        Returns:
            The validated capacity value.
        """
        if value <= 0:
            raise ValueError("max_link_capacity must be a positive integer.")
        return value

    def __init__(
        self,
        **kwds: Any,
    ) -> None:
        """Initialize the connection and derive its display name.

        Args:
            **kwds: Connection field values.
        """
        super().__init__(**kwds)
        object.__setattr__(self, "name", f"{self.zone_a}<->{self.zone_b}")

    @property
    def capacity_limit(self) -> int:
        """Return this connection traversal capacity.

        Returns:
            Maximum drones allowed on the connection simultaneously.
        """
        return self.max_link_capacity

    @property
    def occupancy_label(self) -> str:
        """Return label used in occupancy capacity errors.

        Returns:
            Human-readable connection label.
        """
        return f"Connection {self.name}"

    def leave_drone(self) -> None:
        """Release one traversal slot when at least one drone is present.

        Returns:
            None.
        """
        super().leave_drone()
