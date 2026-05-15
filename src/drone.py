from src.zone import Zone


class Drone:
    name: str
    current_zone: Zone
    action_log: list[str]

    def __init__(self, name: str, current_zone: Zone) -> None:
        self.name = name
        self.current_zone = current_zone
        self.action_log = []

    def move(self, target_zone: Zone) -> None:
        self.current_zone = target_zone
        self.action_log.append(f"Moved to {target_zone.name}")

    def wait(self) -> None:
        self.action_log.append("Waited")
