"""Parsing skeleton for Fly-in map files."""

from pydantic import ValidationError

from src.connection import Connection
from src.network import Network
from src.zone import Zone, ZoneType


def parse_zone_definition(line: str) -> Zone:
    # Example line: "zone: A (1,2) [type=normal max_drones=5 color=red]"
    try:
        # Split the line into parts
        parts = line.split()
        if len(parts) < 4:
            raise ValueError("Invalid zone definition format.")

        # Extract zone name
        zone_name = parts[1]

        # Extract coordinates (as two separate tokens)
        x = int(parts[2])
        y = int(parts[3])

        # Initialize default values for metadata
        zone_type = ZoneType.NORMAL
        max_drones = None
        color = None

        # Parse metadata if present
        if len(parts) > 4:
            metadata_part = " ".join(parts[4:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_str = metadata_part[1:-1]  # Remove brackets
                metadata_items = metadata_str.split()
                for item in metadata_items:
                    key, value = item.split("=")
                    key, value = key.strip(), value.strip()
                    if key in {"type", "zone"}:
                        if value not in {
                            "normal",
                            "blocked",
                            "restricted",
                            "priority",
                        }:
                            raise ValueError(f"Invalid zone type: {value}")
                        zone_type = ZoneType(value)
                    elif key == "max_drones":
                        max_drones = int(value)
                        if max_drones <= 0:
                            raise ValueError(
                                "max_drones must be a positive integer."
                            )
                    elif key == "color":
                        color = value
                    else:
                        raise ValueError(f"Unknown metadata key: {key}")
            else:
                raise ValueError("Metadata must be enclosed in brackets.")

        if max_drones is None:
            max_drones = 1  # Default value if not specified

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


def parse_map_file(path: str) -> Network:
    nb_drones = 0
    start_hub: str | None = None
    end_hub: str | None = None
    zones: dict[str, Zone] = {}
    connections: list[Connection] = []

    clean_lines = []
    with open(path, "r") as file:
        for line in file:
            if line.strip() == "":
                continue  # Skip empty lines
            if line.strip().startswith("#"):
                continue  # Skip comment lines
            clean_lines.append(line.strip())

    if not clean_lines[0].startswith("nb_drones:"):
        raise ValueError("Parsing error: First line must define nb_drones.")

    if sum(1 for line in clean_lines if line.startswith("start_hub:")) != 1:
        raise ValueError(
            "Parsing error: There must be exactly one start_hub definition."
        )

    if sum(1 for line in clean_lines if line.startswith("end_hub:")) != 1:
        raise ValueError(
            "Parsing error: There must be exactly one end_hub definition."
        )

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
            # Normalize all zone/hub/start_hub/end_hub to zone: for parsing
            # Format: <type>: <name> <x> <y> [metadata]
            parts = line.split(":", 1)
            kind = parts[0].strip()
            rest = parts[1].strip()
            # Rebuild as zone: <name> <x> <y> [metadata]
            # For start_hub/end_hub, set special names after parsing
            zone_line = f"zone: {rest}"
            zone = parse_zone_definition(zone_line)
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
            continue
        if line.startswith("connection:"):
            # Format: connection: <zone1>-<zone2> [metadata]
            conn_parts = line[len("connection:") :].strip().split()
            if not conn_parts:
                raise ValueError(
                    f"Parsing error at line {index}: "
                    "Empty connection definition."
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
                    f"Connection references undefined zone(s): "
                    f"{zone_a}, {zone_b}"
                )
            # Check for duplicate connections (a-b == b-a)
            if any(
                (c.zone_a == zone_a and c.zone_b == zone_b)
                or (c.zone_a == zone_b and c.zone_b == zone_a)
                for c in connections
            ):
                raise ValueError(
                    f"Parsing error at line {index}: "
                    f"Duplicate connection between {zone_a} and {zone_b}."
                )
            # Parse metadata if present
            max_link_capacity = 1
            if len(conn_parts) > 1:
                metadata_part = " ".join(conn_parts[1:])
                if metadata_part.startswith("[") and metadata_part.endswith(
                    "]"
                ):
                    metadata_str = metadata_part[1:-1]
                    metadata_items = metadata_str.split()
                    for item in metadata_items:
                        key, value = item.split("=")
                        key, value = key.strip(), value.strip()
                        if key == "max_link_capacity":
                            max_link_capacity = int(value)
                            if max_link_capacity <= 0:
                                raise ValueError(
                                    "max_link_capacity must be a "
                                    "positive integer."
                                )
                        else:
                            raise ValueError(
                                f"Unknown connection metadata key: {key}"
                            )
                else:
                    raise ValueError(
                        f"Parsing error at line {index}: "
                        "Connection metadata must be in brackets."
                    )
            connections.append(
                Connection(
                    zone_a=zone_a,
                    zone_b=zone_b,
                    max_link_capacity=max_link_capacity,
                )
            )
            continue
        # If we reach here, it's an unrecognized line format
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
