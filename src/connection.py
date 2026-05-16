"""Connection model for Fly-in."""

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class Connection(BaseModel):
    """Represents a bidirectional connection between two zones."""

    model_config = ConfigDict(frozen=True)

    name: str = ""
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1
    current_drones: int = 0

    @field_validator("zone_a", "zone_b")
    @classmethod
    def validate_zone_name(cls, value: str) -> str:
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
        if value <= 0:
            raise ValueError("max_link_capacity must be a positive integer.")
        return value

    def __init__(
        self,
        **kwds: Any,
    ) -> None:
        super().__init__(**kwds)
        object.__setattr__(self, "name", f"{self.zone_a}<->{self.zone_b}")

    def hold_drone(self) -> None:
        if self.current_drones >= self.max_link_capacity:
            raise ValueError(f"Connection {self.name} is at full capacity.")
        object.__setattr__(self, "current_drones", self.current_drones + 1)

    def leave_drone(self) -> None:
        if self.current_drones > 0:
            object.__setattr__(self, "current_drones", self.current_drones - 1)
