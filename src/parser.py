"""Parsing skeleton for Fly-in map files."""

from pydantic import ValidationError

from src.models import Connection, Network, Zone, ZoneType


def parse_zone_definition(line: str) -> Zone:
    # Example line: "zone: A (1,2) [type=normal max_drones=5 color=red]"
    try:
        # Split the line into parts
        parts = line.split()
        if len(parts) < 3:
            raise ValueError("Invalid zone definition format.")

        # Extract zone name
        zone_name = parts[1]

        # Extract coordinates
        coords_part = parts[2]
        if not coords_part.startswith("(") or not coords_part.endswith(")"):
            raise ValueError("Coordinates must be enclosed in parentheses.")
        coords_str = coords_part[1:-1]  # Remove parentheses
        x_str, y_str = coords_str.split(",")
        x, y = int(x_str.strip()), int(y_str.strip())

        # Initialize default values for metadata
        zone_type = ZoneType.NORMAL
        max_drones = None
        color = None

        # Parse metadata if present
        if len(parts) > 3:
            metadata_part = " ".join(parts[3:])
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
        if line.startswith("start_hub:"):
            start_hub = line.split(":")[1].strip()
            continue
        if line.startswith("end_hub:"):
            end_hub = line.split(":")[1].strip()
            continue
        if line.startswith("zone:"):
            zone = parse_zone_definition(line)
            if zone.name in zones:
                raise ValueError(f"Parsing error at line {index}:\
                          Duplicate zone name '{zone.name}'.")
            zones[zone.name] = zone
            continue
        if line.startswith("connection:"):
            # Parse connection definition here
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
