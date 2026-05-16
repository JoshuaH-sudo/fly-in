"""Simulation skeleton for Fly-in."""

from src.connection import Connection
from src.display import Display
from src.drone import Drone
from src.network import Network
from src.zone import Zone, ZoneType


def _snapshot_drone_positions(network: Network) -> dict[str, str]:
    """Capture each drone's current zone for history rendering."""
    return {drone.name: drone.current_pos.name for drone in network.drones}


def _next_step_towards_end(
    drone: Drone,
    network: Network,
    current_zone: Zone | Connection,
) -> Zone | Connection | None:
    """Return the next zone name on a shortest path to end_hub."""
    if current_zone.name == network.end_hub:
        return None

    neighbors = network.get_zone_neighbors(current_zone)
    for neighbor in sorted(neighbors, key=lambda zone: zone.name):
        if neighbor.name == network.end_hub:
            return neighbor
        if neighbor.zone_type == ZoneType.BLOCKED:
            continue
        if neighbor.name in drone.visited_zones:
            continue
        if neighbor.current_drones >= neighbor.max_drones:
            continue
        if neighbor.zone_type == ZoneType.RESTRICTED:
            # return connection to restricted zone to indicate waiting on it
            for connection in network.connections:
                if (
                    connection.zone_a == current_zone.name
                    and connection.zone_b == neighbor.name
                ) or (
                    connection.zone_b == current_zone.name
                    and connection.zone_a == neighbor.name
                ):
                    return connection
        return neighbor
    return None


def run_simulation(network: Network) -> list[dict[str, str]]:
    position_history: list[dict[str, str]] = [
        _snapshot_drone_positions(network)
    ]

    while not network.all_drones_at_end():
        moved_this_turn = False
        for drone in network.drones:
            next_zone = _next_step_towards_end(
                drone,
                network,
                drone.current_pos,
            )
            if next_zone is None:
                drone.wait()
                continue

            drone.move(next_zone)
            moved_this_turn = True

        if not moved_this_turn:
            raise RuntimeError(
                "Simulation stalled: no drone could move this turn. "
                "Check map connectivity and routing rules."
            )

        position_history.append(_snapshot_drone_positions(network))

    Display(network).show_history(position_history)
    return position_history
