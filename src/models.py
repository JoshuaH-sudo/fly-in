"""Core data models for Fly-in."""

import enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ZoneType(enum.Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone(BaseModel):
    """Represents a single zone/hub in the map."""

    model_config = ConfigDict(frozen=True)

    name: str
    x: int
    y: int
    zone_type: ZoneType
    color: str | None = None
    max_drones: int = 1

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Zone name cannot be empty.")
        if " " in value or "-" in value:
            raise ValueError("Zone name cannot contain spaces or dashes.")
        return value

    @field_validator("max_drones")
    @classmethod
    def validate_max_drones(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_drones must be a positive integer.")
        return value

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is not None and (not value or " " in value):
            raise ValueError("color must be a single word when provided.")
        return value


class Connection(BaseModel):
    """Represents a bidirectional connection between two zones."""

    model_config = ConfigDict(frozen=True)

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

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
            raise ValueError(
                "max_link_capacity must be a positive integer."
            )
        return value


class Network(BaseModel):
    """Holds parsed map information."""

    model_config = ConfigDict(frozen=True)

    nb_drones: int = 0
    start_hub: str = ""
    end_hub: str = ""
    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)

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
