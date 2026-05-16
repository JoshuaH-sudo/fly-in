from src.connection import Connection
from src.zone import Zone


class Drone:
    """Represent one drone moving through zones and connections."""

    name: str
    current_pos: Zone | Connection
    action_log: list[str]
    visited_zones: set[str]

    def __init__(self, name: str, current_zone: Zone) -> None:
        """Create a drone at the given starting zone.

        Args:
            name: Unique drone identifier.
            current_zone: Initial zone where the drone starts.
        """
        self.name = name
        self.current_pos = current_zone
        self.action_log = []
        self.visited_zones = {current_zone.name}

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
        self.visited_zones.add(target_zone.name)

        if isinstance(target_zone, Zone):
            self.action_log.append(f"Moved to {target_zone.name}")
        elif isinstance(target_zone, Connection):
            self.action_log.append(
                "Moved to connection: "
                f"{target_zone.zone_a} <-> {target_zone.zone_b}"
            )

    def wait(self) -> None:
        """Record a no-op turn for this drone.

        Returns:
            None.
        """
        self.action_log.append(f"Waited on {self.current_pos.name}")
