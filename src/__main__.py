"""CLI entry point for Fly-in skeleton."""

import argparse
import os
import sys

from src.map_menu import MapMenu
from src.output_logger import OutputLogger
from src.parser import parse_map_file
from src.simulator import run_simulation


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for the Fly-in command."""
    parser = argparse.ArgumentParser(
        description="Fly-in drone routing simulator",
    )
    parser.add_argument("map_file", nargs="?", help="Path to the map file")
    return parser


def _drone_sort_key(drone_name: str) -> tuple[int, str]:
    if drone_name.startswith("drone_"):
        suffix = drone_name.split("_", maxsplit=1)[1]
        if suffix.isdigit():
            return (int(suffix), drone_name)
    return (10**9, drone_name)


def _print_simulation_output(turns: list[dict[str, str]]) -> None:
    for step_index, turn_positions in enumerate(turns):
        items: list[str] = []
        for drone_name in sorted(turn_positions, key=_drone_sort_key):
            if drone_name.startswith("drone_"):
                suffix = drone_name.split("_", maxsplit=1)[1]
                drone_label = f"D{suffix}"
            else:
                drone_label = drone_name
            zone_name = turn_positions[drone_name]
            items.append(f"{drone_label}: {zone_name}")

        print(f"\n=== Step {step_index} ===\n")
        for item in items:
            print(f"{item}")


def main() -> int:
    """Run the Fly-in skeleton application."""
    parser = build_parser()
    args = parser.parse_args()
    logger = OutputLogger(color_enabled=sys.stdout.isatty())
    root = os.path.dirname(os.path.dirname(__file__))
    maps_dir = os.path.join(root, "maps")

    selected_map: str | None = args.map_file
    if args.map_file:
        selected_map = args.map_file
    else:
        menu = MapMenu(maps_dir)
        options = menu.discover_options()
        if not options:
            print("No map files found.")
            return 1
        selected_map = menu.choose_map(options)
        if selected_map is None:
            return 0

    map_title = os.path.relpath(selected_map, root)
    logger.print_map_title(map_title)

    try:
        network = parse_map_file(selected_map)
    except Exception as error:
        logger.print_map_error(selected_map, error)
        return 1

    print(logger.format_network(network))
    turns = run_simulation(network)
    _print_simulation_output(turns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
