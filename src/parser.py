"""Parsing skeleton for Fly-in map files."""

from pydantic import ValidationError

from src.connection import Connection
from src.network import Network
from src.zone import Zone, ZoneType


def _clean_non_comment_lines(path: str) -> list[str]:
    """Load map file lines while dropping empty lines and comments."""
    clean_lines: list[str] = []
    with open(path, "r") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            clean_lines.append(line)
    return clean_lines


def _parse_metadata_items(metadata_str: str) -> dict[str, str]:
    """Parse key=value tokens from bracket metadata."""
    metadata: dict[str, str] = {}
    for item in metadata_str.split():
        if "=" not in item:
            raise ValueError(f"Invalid metadata item: {item}")
        key, value = item.split("=", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def _extract_bracket_metadata(metadata_part: str) -> dict[str, str]:
    """Return parsed metadata if wrapped with [ and ]."""
    if not metadata_part.startswith("[") or not metadata_part.endswith("]"):
        raise ValueError("Metadata must be enclosed in brackets.")
    metadata_str = metadata_part[1:-1]
    return _parse_metadata_items(metadata_str)


def _parse_zone_metadata(
    metadata: dict[str, str],
) -> tuple[ZoneType, int | None, str | None]:
    """Parse zone metadata entries into validated values."""
    zone_type = ZoneType.NORMAL
    max_drones: int | None = None
    color: str | None = None

    for key, value in metadata.items():
        if key in {"type", "zone"}:
            if value not in {"normal", "blocked", "restricted", "priority"}:
                raise ValueError(f"Invalid zone type: {value}")
            zone_type = ZoneType(value)
        elif key == "max_drones":
            max_drones = int(value)
            if max_drones < 0:
                raise ValueError("max_drones must be a non-negative integer.")
        elif key == "color":
            color = value
        else:
            raise ValueError(f"Unknown metadata key: {key}")

    return zone_type, max_drones, color


def parse_zone_definition(line: str) -> Zone:
    """Parse a zone definition line into a Zone model."""
    try:
        # Expected shape: zone: <name> <x> <y> [optional metadata]
        parts = line.split()
        if len(parts) < 4:
            raise ValueError("Invalid zone definition format.")

        zone_name = parts[1]
        x = int(parts[2])
        y = int(parts[3])

        zone_type = ZoneType.NORMAL
        max_drones: int | None = None
        color: str | None = None

        if len(parts) > 4:
            metadata_part = " ".join(parts[4:])
            metadata = _extract_bracket_metadata(metadata_part)
            zone_type, max_drones, color = _parse_zone_metadata(metadata)

        if max_drones is None:
            max_drones = zone_type.default_max_drones

        return Zone(
            name=zone_name,
            x=x,
            y=y,
            zone_type=zone_type,
            max_drones=max_drones,
            color=color,
        )

    except ValidationError as e:
        raise ValueError(f"Error parsing zone definition: {e}") from e
    except Exception as e:
        raise ValueError(f"Error parsing zone definition: {e}")


def _parse_connection_definition(
    line: str,
    index: int,
    zones: dict[str, Zone],
    existing_connections: list[Connection],
) -> Connection:
    """Parse and validate one connection definition line."""
    conn_parts = line[len("connection:"):].strip().split()
    if not conn_parts:
        raise ValueError(
            f"Parsing error at line {index}: Empty connection definition."
        )

    zones_part = conn_parts[0]
    if "-" not in zones_part:
        raise ValueError(
            f"Parsing error at line {index}: "
            "Connection must use dash between zones."
        )

    zone_a, zone_b = zones_part.split("-", 1)
    zone_a = zone_a.strip()
    zone_b = zone_b.strip()

    if zone_a not in zones or zone_b not in zones:
        raise ValueError(
            f"Parsing error at line {index}: "
            f"Connection references undefined zone(s): {zone_a}, {zone_b}"
        )

    if any(
        (c.zone_a == zone_a and c.zone_b == zone_b)
        or (c.zone_a == zone_b and c.zone_b == zone_a)
        for c in existing_connections
    ):
        raise ValueError(
            f"Parsing error at line {index}: "
            f"Duplicate connection between {zone_a} and {zone_b}."
        )

    max_link_capacity = 1
    if len(conn_parts) > 1:
        metadata_part = " ".join(conn_parts[1:])
        if (
            not metadata_part.startswith("[")
            or not metadata_part.endswith("]")
        ):
            raise ValueError(
                f"Parsing error at line {index}: "
                "Connection metadata must be in brackets."
            )

        metadata = _extract_bracket_metadata(metadata_part)
        for key, value in metadata.items():
            if key == "max_link_capacity":
                max_link_capacity = int(value)
                if max_link_capacity <= 0:
                    raise ValueError(
                        "max_link_capacity must be a positive integer."
                    )
            else:
                raise ValueError(f"Unknown connection metadata key: {key}")

    return Connection(
        zone_a=zone_a,
        zone_b=zone_b,
        max_link_capacity=max_link_capacity,
    )


def _parse_zone_like_line(
    line: str,
    index: int,
    zones: dict[str, Zone],
    start_hub: str | None,
    end_hub: str | None,
) -> tuple[str | None, str | None]:
    """Parse zone/hub/start_hub/end_hub declarations into a Zone."""
    parts = line.split(":", 1)
    kind = parts[0].strip()
    rest = parts[1].strip()

    # Normalize all variants to the same zone parser.
    zone = parse_zone_definition(f"zone: {rest}")
    if kind == "start_hub":
        zone = zone.model_copy(update={"zone_type": ZoneType.START})
    elif kind == "end_hub":
        zone = zone.model_copy(update={"zone_type": ZoneType.END})

    if zone.name in zones:
        raise ValueError(
            f"Parsing error at line {index}: "
            f"Duplicate zone name '{zone.name}'."
        )

    zones[zone.name] = zone
    if kind == "start_hub":
        start_hub = zone.name
    elif kind == "end_hub":
        end_hub = zone.name

    return start_hub, end_hub


def _validate_required_headers(clean_lines: list[str]) -> None:
    """Validate required top-level directives before line parsing."""
    if not clean_lines or not clean_lines[0].startswith("nb_drones:"):
        raise ValueError("Parsing error: First line must define nb_drones.")

    if sum(1 for line in clean_lines if line.startswith("start_hub:")) != 1:
        raise ValueError(
            "Parsing error: There must be exactly one start_hub definition."
        )

    if sum(1 for line in clean_lines if line.startswith("end_hub:")) != 1:
        raise ValueError(
            "Parsing error: There must be exactly one end_hub definition."
        )


def parse_map_file(path: str) -> Network:
    """Parse a map file into a validated Network model."""
    nb_drones = 0
    start_hub: str | None = None
    end_hub: str | None = None
    zones: dict[str, Zone] = {}
    connections: list[Connection] = []

    clean_lines = _clean_non_comment_lines(path)
    _validate_required_headers(clean_lines)

    for index, line in enumerate(clean_lines):
        if line.startswith("nb_drones:"):
            nb_drones = int(line.split(":")[1].strip())
            continue

        if (
            line.startswith("start_hub:")
            or line.startswith("end_hub:")
            or line.startswith("hub:")
            or line.startswith("zone:")
        ):
            start_hub, end_hub = _parse_zone_like_line(
                line,
                index,
                zones,
                start_hub,
                end_hub,
            )
            continue

        if line.startswith("connection:"):
            connections.append(
                _parse_connection_definition(
                    line,
                    index,
                    zones,
                    connections,
                )
            )
            continue

        raise ValueError(
            f"Parsing error at line {index}: Unrecognized line format."
        )

    if not start_hub:
        raise ValueError("Parsing error: Missing start_hub definition.")
    if not end_hub:
        raise ValueError("Parsing error: Missing end_hub definition.")

    try:
        return Network(
            nb_drones=nb_drones,
            start_hub=start_hub,
            end_hub=end_hub,
            zones=zones,
            connections=connections,
        )
    except ValidationError as e:
        raise ValueError(f"Parsing error: {e}") from e
