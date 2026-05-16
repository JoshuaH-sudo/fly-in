from enum import Enum

from pydantic.dataclasses import dataclass

from src.connection import Connection
from src.zone import Zone


class DroneState(Enum):
    """Enumerate possible drone states for simulation logic."""

    IN_FLIGHT = "in-flight"
    DELIVERED = "delivered"
    WAITING = "waiting"
    REVERSING = "reversing"


@dataclass
class DroneActions:
    position: Zone | Connection
    state: DroneState


class Drone:
    """Represent one drone moving through zones and connections."""

    name: str
    current_pos: Zone | Connection
    action_log: list[DroneActions]
    visited_positions: set[Zone | Connection]

    def __init__(self, name: str, current_zone: Zone) -> None:
        """Create a drone at the given starting zone.

        Args:
            name: Unique drone identifier.
            current_zone: Initial zone where the drone starts.
        """
        self.name = name
        self.current_pos = current_zone
        self.action_log = []
        self.visited_positions = {current_zone}

    def move(self, target_zone: Zone | Connection) -> None:
        """Move the drone to a zone or connection.

        Args:
            target_zone: Destination zone or in-flight connection.

        Returns:
            None.
        """
        self.current_pos.leave_drone()
        self.current_pos = target_zone
        target_zone.hold_drone()
        self.visited_positions.add(target_zone)

        if isinstance(target_zone, Zone):
            self.action_log.append(
                DroneActions(
                    position=target_zone,
                    state=DroneState.IN_FLIGHT,
                )
            )
        elif isinstance(target_zone, Connection):
            self.action_log.append(
                DroneActions(
                    position=target_zone,
                    state=DroneState.IN_FLIGHT,
                )
            )

    def deliver(self) -> None:
        """Record a successful delivery when the drone reaches the end hub.

        Returns:
            None.
        """
        self.action_log.append(
            DroneActions(
                position=self.current_pos,
                state=DroneState.DELIVERED,
            )
        )

    def reverse(self) -> None:
        """Record a reversal move when the drone needs to backtrack.

        Returns:
            None.
        """
        previous_position = (
            self.visited_positions.pop() if self.visited_positions else None
        )
        if previous_position is None:
            raise ValueError("No previous position to reverse to.")

        self.current_pos.leave_drone()
        self.current_pos = previous_position
        self.current_pos.hold_drone()
        self.action_log.append(
            DroneActions(
                position=previous_position,
                state=DroneState.REVERSING,
            )
        )

    def wait(self) -> None:
        """Record a no-op turn for this drone.

        Returns:
            None.
        """
        self.action_log.append(
            DroneActions(
                position=self.current_pos,
                state=DroneState.WAITING,
            )
        )
