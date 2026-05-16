from src.connection import Connection
from src.zone import Zone


class Drone:
    name: str
    current_pos: Zone | Connection
    action_log: list[str]

    def __init__(self, name: str, current_zone: Zone) -> None:
        self.name = name
        self.current_pos = current_zone
        self.action_log = []

    def move(self, target_zone: Zone) -> None:
        self.current_pos = target_zone
        self.action_log.append(f"Moved to {target_zone.name}")

    def wait_on_connection(self, connection: Connection) -> None:
        self.current_pos = connection
        self.action_log.append(f"Waiting on connection: \
                {connection.zone_a} <-> {connection.zone_b}")

    def wait(self) -> None:
        self.action_log.append(f"Waited on {self.current_pos.name}")
