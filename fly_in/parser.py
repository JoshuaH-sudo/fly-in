"""Parsing skeleton for Fly-in map files."""

from fly_in.models import Network


def parse_map_file(path: str) -> Network:
    """Return an empty network placeholder for future parser work."""
    _ = path
    return Network()
