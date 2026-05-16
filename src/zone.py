"""Zone model for Fly-in."""

from pydantic import BaseModel, ConfigDict, field_validator
import enum


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
