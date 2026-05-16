"""Abstract occupancy behavior shared by zones and connections."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class DroneOccupancy(BaseModel, ABC):
    """Provide common occupancy bookkeeping for drone containers.

    Subclasses define their capacity rules and display label.
    """

    current_drones: int = 0

    @property
    @abstractmethod
    def capacity_limit(self) -> int:
        """Return the maximum number of drones this object can hold.

        Returns:
            Capacity limit used for occupancy checks.
        """

    @property
    @abstractmethod
    def occupancy_label(self) -> str:
        """Return object label used in occupancy errors.

        Returns:
            Human-readable label (for example, ``Zone start``).
        """

    def allows_capacity_bypass(self) -> bool:
        """Return whether this object can exceed capacity checks.

        Returns:
            ``True`` when capacity limit should be ignored.
        """
        return False

    def hold_drone(self) -> None:
        """Reserve one occupancy slot.

        Returns:
            None.

        Raises:
            ValueError: If capacity is full and bypass is not allowed.
        """
        if (
            not self.allows_capacity_bypass()
            and self.current_drones >= self.capacity_limit
        ):
            raise ValueError(f"{self.occupancy_label} is at full capacity.")
        object.__setattr__(self, "current_drones", self.current_drones + 1)

    def leave_drone(self) -> None:
        """Release one occupancy slot when at least one drone is present.

        Returns:
            None.
        """
        if self.current_drones > 0:
            object.__setattr__(self, "current_drones", self.current_drones - 1)
