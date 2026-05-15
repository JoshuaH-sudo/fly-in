"""Simulation skeleton for Fly-in."""

from collections import Counter

from src.display import Display
from src.network import Network


def _snapshot_drone_counts(network: Network) -> Counter[str]:
    """Capture how many drones are currently in each zone."""
    return Counter(drone.current_zone.name for drone in network.drones)


def run_simulation(network: Network) -> list[str]:
    history: list[Counter[str]] = [_snapshot_drone_counts(network)]

    while not network.all_drones_at_end():
        for drone in network.drones:
            connections = network.get_zone_connections(drone.current_zone.name)
            if connections:
                target_zone = min(connections, key=lambda zone: zone.name)
                drone.move(target_zone)
            else:
                drone.wait()

        history.append(_snapshot_drone_counts(network))

    Display(network).show_history(history)
    return []
