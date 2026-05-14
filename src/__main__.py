"""CLI entry point for Fly-in skeleton."""

import argparse
import os
import sys

from src.models import Connection, Network, Zone
from src.parser import parse_map_file


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for the Fly-in command."""
    parser = argparse.ArgumentParser(
        description="Fly-in drone routing simulator",
    )
    parser.add_argument("map_file", nargs="?", help="Path to the map file")
    return parser


def _style(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def _format_zone(zone: Zone, network: Network) -> str:
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


def _format_connection(connection: Connection) -> str:
    return (
        f"{connection.zone_a:<20} <-> {connection.zone_b:<20} "
        f"cap={connection.max_link_capacity}"
    )


def format_network(network: Network, color_enabled: bool) -> str:
    lines: list[str] = []
    title = _style("Network Summary", "1;36", color_enabled)
    lines.append(title)
    lines.append(
        f"  drones={network.nb_drones}  "
        f"start={network.start_hub}  end={network.end_hub}"
    )

    zones_header = _style("Zones", "1;33", color_enabled)
    lines.append(f"  {zones_header} ({len(network.zones)}):")
    for zone in sorted(network.zones.values(), key=lambda z: z.name):
        lines.append(f"    {_format_zone(zone, network)}")

    connections_header = _style("Connections", "1;35", color_enabled)
    lines.append(f"  {connections_header} ({len(network.connections)}):")
    sorted_connections = sorted(
        network.connections,
        key=lambda c: (min(c.zone_a, c.zone_b), max(c.zone_a, c.zone_b)),
    )
    for connection in sorted_connections:
        lines.append(f"    {_format_connection(connection)}")

    return "\n".join(lines)


def _collect_map_files(maps_dir: str) -> list[str]:
    map_files: list[str] = []
    for subdir in ["easy", "medium", "hard", "challenger"]:
        subpath = os.path.join(maps_dir, subdir)
        if not os.path.isdir(subpath):
            continue
        for fname in sorted(os.listdir(subpath)):
            if fname.endswith(".txt"):
                map_files.append(os.path.join(subpath, fname))
    return map_files


def main() -> int:
    """Run the Fly-in skeleton application."""
    parser = build_parser()
    args = parser.parse_args()
    color_enabled = sys.stdout.isatty()

    # If a map_file is given, just parse and print it
    if args.map_file:
        network = parse_map_file(args.map_file)
        print(format_network(network, color_enabled))
        return 0

    # Otherwise, find all .txt map files in maps/*/*
    root = os.path.dirname(os.path.dirname(__file__))
    maps_dir = os.path.join(root, "maps")
    map_files = _collect_map_files(maps_dir)

    if not map_files:
        print("No map files found.")
        return 1

    for path in map_files:
        map_title = os.path.relpath(path, root)
        pretty_title = _style(f"=== {map_title} ===", "1;32", color_enabled)
        print(f"\n{pretty_title}")
        try:
            network = parse_map_file(path)
            print(format_network(network, color_enabled))
        except Exception as e:
            print(f"Error parsing {path}: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
