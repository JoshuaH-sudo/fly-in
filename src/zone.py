"""Zone model for Fly-in."""

from pydantic import BaseModel, ConfigDict, field_validator
import enum


class ZoneType(enum.Enum):
    """Enumerate supported zone categories in Fly-in maps."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    START = "start"
    END = "end"

    @property
    def movement_cost(self) -> int:
        """Return movement cost in turns when entering this zone type.

        Returns:
            Number of turns required to enter this zone type.

        Raises:
            ValueError: If this zone type cannot be entered.
        """
        if self is ZoneType.RESTRICTED:
            return 2
        if self is ZoneType.BLOCKED:
            raise ValueError("Blocked zones cannot be entered.")
        return 1

    @property
    def default_max_drones(self) -> int:
        """Return default zone capacity for this zone type.

        Returns:
            Default occupancy limit used when metadata omits max_drones.
        """
        if self is ZoneType.BLOCKED:
            return 0
        if self is ZoneType.PRIORITY:
            return 2
        return 1


class Zone(BaseModel):
    """Represents a single zone/hub in the map."""

    model_config = ConfigDict(frozen=True)

    name: str
    x: int
    y: int
    zone_type: ZoneType
    color: str | None = None
    max_drones: int = ZoneType.NORMAL.default_max_drones
    current_drones: int = 0

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate zone identifier constraints.

        Args:
            value: Zone name to validate.

        Returns:
            Validated zone name.
        """
        if not value:
            raise ValueError("Zone name cannot be empty.")
        if " " in value or "-" in value:
            raise ValueError("Zone name cannot contain spaces or dashes.")
        return value

    @field_validator("max_drones")
    @classmethod
    def validate_max_drones(cls, value: int) -> int:
        """Validate that zone capacity is non-negative.

        Args:
            value: Zone capacity value.

        Returns:
            Validated capacity value.
        """
        if value < 0:
            raise ValueError("max_drones must be a non-negative integer.")
        return value

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        """Validate optional display color metadata.

        Args:
            value: Optional color token.

        Returns:
            Validated color token or ``None``.
        """
        if value is not None and (not value or " " in value):
            raise ValueError("color must be a single word when provided.")
        return value

    def hold_drone(self) -> None:
        """Reserve one occupancy slot in this zone.

        Returns:
            None.
        """
        if self.current_drones >= self.max_drones and self.zone_type not in {
            ZoneType.START,
            ZoneType.END,
        }:
            raise ValueError(f"Zone {self.name} is at full capacity.")
        object.__setattr__(self, "current_drones", self.current_drones + 1)

    def leave_drone(self) -> None:
        """Release one occupancy slot when at least one drone is present.

        Returns:
            None.
        """
        if self.current_drones > 0:
            object.__setattr__(self, "current_drones", self.current_drones - 1)
