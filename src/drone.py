from src.connection import Connection
from src.zone import Zone


class Drone:
    name: str
    current_pos: Zone | Connection
    action_log: list[str]
    visited_zones: set[str]

    def __init__(self, name: str, current_zone: Zone) -> None:
        self.name = name
        self.current_pos = current_zone
        self.action_log = []
        self.visited_zones = {current_zone.name}

    def move(self, target_zone: Zone | Connection) -> None:
        self.current_pos = target_zone
        if isinstance(target_zone, Zone):
            self.visited_zones.add(target_zone.name)
            self.action_log.append(f"Moved to {target_zone.name}")
        elif isinstance(target_zone, Connection):
            self.action_log.append(f"Moved to connection: {target_zone.zone_a} <-> {target_zone.zone_b}")

    def wait(self) -> None:
        self.action_log.append(f"Waited on {self.current_pos.name}")
