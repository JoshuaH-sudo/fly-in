"""CLI entry point for Fly-in skeleton."""

import argparse

from src.parser import parse_map_file
from src.simulator import run_simulation


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for the Fly-in command."""
    parser = argparse.ArgumentParser(
        description="Fly-in drone routing simulator",
    )
    parser.add_argument("map_file", nargs="?", help="Path to the map file")
    return parser


def main() -> int:
    """Run the Fly-in skeleton application."""
    parser = build_parser()
    args = parser.parse_args()

    if args.map_file:
        network = parse_map_file(args.map_file)
        turns = run_simulation(network)
        for line in turns:
            print(line)
    else:
        print(
            "Fly-in skeleton ready. Provide a map file to start implementing "
            "parser/simulator.",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
