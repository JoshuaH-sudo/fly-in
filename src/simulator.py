"""Simulation skeleton for Fly-in."""

from src.connection import Connection
from src.display import Display
from src.drone import Drone
from src.network import Network
from src.types import DronePositions
from src.zone import Zone, ZoneType


def _snapshot_drone_positions(network: Network) -> DronePositions:
    """Capture each drone's current zone for history rendering.

    Args:
        network: Network with current drone states.

    Returns:
        Snapshot mapping drone names to zone names.
    """
    return {drone.name: drone.current_pos.name for drone in network.drones}


def _next_step_towards_end(
    drone: Drone,
    network: Network,
    current_zone: Zone | Connection,
) -> Zone | Connection | None:
    """Return the next valid move for one drone toward the end hub.

    Args:
        drone: Drone to route for this turn.
        network: Parsed network state.
        current_zone: Drone's current zone or connection.

    Returns:
        Next zone/connection to move to, or ``None`` if no move is possible.
    """
    if current_zone.name == network.end_hub:
        return None

    neighbors = network.get_zone_neighbors(current_zone)
    for neighbor in sorted(neighbors, key=lambda zone: zone.name):
        if neighbor.name == network.end_hub:
            return neighbor
        if (
            neighbor.zone_type == ZoneType.PRIORITY
            and neighbor.current_drones >= neighbor.max_drones
        ):
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


def run_simulation(
    network: Network,
    render_history: bool = True,
) -> list[DronePositions]:
    """Run the simulation until all drones arrive at the end hub.

    Args:
        network: Parsed network state.
        render_history: Whether to open the visual history browser.

    Returns:
        Ordered list of drone-position snapshots (including step 0).
    """
    position_history: list[DronePositions] = [
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

    if render_history:
        Display(network).show_history(position_history)
    return position_history
