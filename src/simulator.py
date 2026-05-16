"""Simulation skeleton for Fly-in."""

from collections import deque

from src.display import Display
from src.network import Network
from src.zone import ZoneType


def _snapshot_drone_positions(network: Network) -> dict[str, str]:
    """Capture each drone's current zone for history rendering."""
    return {
        drone.name: drone.current_zone.name for drone in network.drones
    }


def _next_step_towards_end(
    network: Network,
    current_zone_name: str,
) -> str | None:
    """Return the next zone name on a shortest path to end_hub."""
    if current_zone_name == network.end_hub:
        return None

    visited: set[str] = {current_zone_name}
    queue: deque[tuple[str, list[str]]] = deque([(current_zone_name, [])])

    while queue:
        zone_name, path = queue.popleft()
        if zone_name == network.end_hub:
            return path[0] if path else None

        neighbors = network.get_zone_connections(zone_name)
        for neighbor in sorted(neighbors, key=lambda zone: zone.name):
            if neighbor.zone_type == ZoneType.BLOCKED:
                continue
            if neighbor.name in visited:
                continue
            visited.add(neighbor.name)
            queue.append((neighbor.name, path + [neighbor.name]))

    return None


def run_simulation(network: Network) -> list[dict[str, str]]:
    position_history: list[dict[str, str]] = [
        _snapshot_drone_positions(network)
    ]

    while not network.all_drones_at_end():
        moved_this_turn = False
        for drone in network.drones:
            next_zone_name = _next_step_towards_end(
                network,
                drone.current_zone.name,
            )
            if next_zone_name is None:
                drone.wait()
                continue

            target_zone = network.get_zone(next_zone_name)
            drone.move(target_zone)
            moved_this_turn = True

        if not moved_this_turn:
            raise RuntimeError(
                "Simulation stalled: no drone could move this turn. "
                "Check map connectivity and routing rules."
            )

        position_history.append(_snapshot_drone_positions(network))

    Display(network).show_history(position_history)
    return position_history
