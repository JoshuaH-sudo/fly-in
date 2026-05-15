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


def _print_simulation_output(turns: list[str]) -> None:
    for turn_line in turns:
        print(turn_line)


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

    turns = run_simulation(network)
    if turns:
        _print_simulation_output(turns)
    else:
        print(logger.format_network(network))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
