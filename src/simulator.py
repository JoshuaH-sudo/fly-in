"""Simulation skeleton for Fly-in."""

from collections import deque
import sys

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


def _can_enter_position(
    neighbor: Zone | Connection,
) -> bool:
    """Return whether a position is enterable under hard constraints.

    Args:
        neighbor: Candidate neighboring position.

    Returns:
        ``True`` when no hard rule prevents entering the zone.
    """
    if isinstance(neighbor, Zone) and neighbor.zone_type == ZoneType.BLOCKED:
        return False

    if (
        not neighbor.allows_capacity_bypass()
        and neighbor.current_drones >= neighbor.capacity_limit
    ):
        return False

    return True


def _restricted_connection_for(
    current_zone: Zone | Connection,
    target_zone: Zone,
    network: Network,
) -> Connection | None:
    """Return the connection used to enter a restricted target zone.

    Args:
        current_zone: Drone's current zone or connection.
        target_zone: Restricted zone to be entered.
        network: Parsed network state.

    Returns:
        Matching connection when found, otherwise ``None``.
    """
    for connection in network.connections:
        if (
            connection.zone_a == current_zone.name
            and connection.zone_b == target_zone.name
        ) or (
            connection.zone_b == current_zone.name
            and connection.zone_a == target_zone.name
        ):
            return connection
    return None


def _previous_position(drone: Drone) -> Zone | Connection | None:
    """Return the drone position from the previous turn, if present.

    Args:
        drone: Drone whose history should be inspected.

    Returns:
        Previous position from action history, otherwise ``None``.
    """
    if len(drone.action_log) < 2:
        return None
    return drone.action_log[-2].position


def _zone_distance_to_end(network: Network, start_zone: Zone) -> int | None:
    """Compute shortest hop distance from one zone to the end hub.

    Args:
        network: Parsed network state.
        start_zone: Zone to start the distance search from.

    Returns:
        Number of zone hops to reach the end hub, or ``None`` if unreachable.
    """
    if start_zone.name == network.end_hub:
        return 0

    queue: deque[tuple[Zone, int]] = deque([(start_zone, 0)])
    visited: set[Zone] = {start_zone}

    while queue:
        zone, distance = queue.popleft()
        for neighbor in network.get_zone_neighbors(zone):
            if neighbor in visited:
                continue
            if neighbor.zone_type == ZoneType.BLOCKED:
                continue
            if neighbor.name == network.end_hub:
                return distance + 1
            visited.add(neighbor)
            queue.append((neighbor, distance + 1))

    return None


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
    if not neighbors:
        return None

    previous_position = _previous_position(drone)
    candidates: list[tuple[int, int, int, str, Zone]] = []
    for neighbor in neighbors:
        if not _can_enter_position(neighbor):
            continue

        if neighbor.name == network.end_hub:
            # Always prioritize direct delivery when reachable.
            return neighbor

        if neighbor.zone_type == ZoneType.RESTRICTED and isinstance(
            current_zone, Zone
        ):
            connection = _restricted_connection_for(
                current_zone,
                neighbor,
                network,
            )
            if connection is None or not _can_enter_position(connection):
                continue

        distance = _zone_distance_to_end(network, neighbor)
        if distance is None:
            continue

        revisit_penalty = 1 if neighbor in drone.visited_positions else 0
        backtrack_bonus = (
            0
            if previous_position is not None and neighbor == previous_position
            else 1
        )
        candidates.append(
            (
                distance,
                revisit_penalty,
                backtrack_bonus,
                neighbor.name,
                neighbor,
            )
        )

    if not candidates:
        return None

    chosen_neighbor = min(candidates)[-1]
    if chosen_neighbor.zone_type == ZoneType.RESTRICTED and isinstance(
        current_zone, Zone
    ):
        connection = _restricted_connection_for(
            current_zone,
            chosen_neighbor,
            network,
        )
        if connection is not None and _can_enter_position(connection):
            return connection
        return None

    return chosen_neighbor


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
            print(
                "Simulation stalled: no drone could move this turn. "
                "Check map connectivity and routing rules.",
                file=sys.stderr,
            )

        position_history.append(_snapshot_drone_positions(network))

    if render_history:
        Display(network).show_history(position_history)
    return position_history
