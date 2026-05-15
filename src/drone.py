from src.models import Zone
from src.network import Network


class Drone:
    name: str
    network: Network
    current_zone: Zone

    def __init__(self, name: str, network: Network):
        self.name = name
        self.network = network
        self.current_zone = self.network.get_zone(
            "start"
        )  # Start at the "start" zone

    def move(self, target_zone: Zone):
        if target_zone.name not in self.network.zones:
            raise ValueError(
                f"Target zone '{target_zone.name}' not found in the network."
            )
        self.current_zone = target_zone
