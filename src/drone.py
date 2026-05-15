from src.zone import Zone


class Drone:
    name: str
    current_zone: Zone
    action_log: list[str] = []

    def __init__(self, name: str, current_zone: Zone):
        self.name = name
        self.current_zone = current_zone

    def move(self, target_zone: Zone):
        self.current_zone = target_zone
        self.action_log.append(f"Moved to {target_zone.name}")

    def wait(self):
        self.action_log.append("Waited")
