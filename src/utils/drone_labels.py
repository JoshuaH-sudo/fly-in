"""Helpers for formatting and ordering drone names."""


def drone_sort_key(drone_name: str) -> tuple[int, str]:
    """Build a stable sort key for drone names.

    Args:
        drone_name: Internal drone name (for example, ``drone_12``).

    Returns:
        Tuple used for sorting. Known numeric drone names are sorted first.
    """
    if drone_name.startswith("drone_"):
        suffix = drone_name.split("_", maxsplit=1)[1]
        if suffix.isdigit():
            return (int(suffix), drone_name)
    return (10**9, drone_name)


def drone_label(drone_name: str) -> str:
    """Convert a drone name to a display label.

    Args:
        drone_name: Internal drone name.

    Returns:
        Human-readable drone label (for example, ``D1``).
    """
    if drone_name.startswith("drone_"):
        suffix = drone_name.split("_", maxsplit=1)[1]
        return f"D{suffix}"
    return drone_name
