"""Output and formatting utilities for the Fly-in CLI."""

from src.connection import Connection
from src.network import Network
from src.zone import Zone


class OutputLogger:
    """Handles CLI output formatting and rendering."""

    def __init__(self, color_enabled: bool) -> None:
        self.color_enabled = color_enabled

    def _style(self, text: str, code: str) -> str:
        if not self.color_enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def _format_zone(self, zone: Zone, network: Network) -> str:
        role = "-"
        if zone.name == network.start_hub:
            role = "start"
        elif zone.name == network.end_hub:
            role = "end"
        color = zone.color if zone.color is not None else "-"
        return (
            f"{zone.name:<20} ({zone.x:>3},{zone.y:<3}) "
            f"{zone.zone_type.value:<10} cap={zone.max_drones:<3} "
            f"color={color:<10} role={role}"
        )

    def _format_connection(self, connection: Connection) -> str:
        return (
            f"{connection.zone_a:<20} <-> {connection.zone_b:<20} "
            f"cap={connection.max_link_capacity}"
        )

    def format_network(self, network: Network) -> str:
        lines: list[str] = []
        title = self._style("Network Summary", "1;36")
        lines.append(title)
        lines.append(
            f"  drones={network.nb_drones}  "
            f"start={network.start_hub}  end={network.end_hub}"
        )

        zones_header = self._style("Zones", "1;33")
        lines.append(f"  {zones_header} ({len(network.zones)}):")
        for zone in sorted(network.zones.values(), key=lambda z: z.name):
            lines.append(f"    {self._format_zone(zone, network)}")

        connections_header = self._style("Connections", "1;35")
        lines.append(f"  {connections_header} ({len(network.connections)}):")
        sorted_connections = sorted(
            network.connections,
            key=lambda c: (min(c.zone_a, c.zone_b), max(c.zone_a, c.zone_b)),
        )
        for connection in sorted_connections:
            lines.append(f"    {self._format_connection(connection)}")

        return "\n".join(lines)

    def print_map_title(self, map_title: str) -> None:
        pretty_title = self._style(f"=== {map_title} ===", "1;32")
        print(f"\n{pretty_title}")

    def print_map_error(self, map_path: str, error: Exception) -> None:
        print(f"Error parsing {map_path}: {error}")
