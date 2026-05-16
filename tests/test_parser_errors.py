"""Parser error-path tests for Fly-in map parsing."""

from pathlib import Path

import pytest

from src.parser import parse_map_file, parse_zone_definition


def _write_map(tmp_path: Path, content: str) -> Path:
    map_path = tmp_path / "invalid_map.txt"
    map_path.write_text(content)
    return map_path


def test_parse_zone_definition_rejects_non_bracket_metadata() -> None:
    with pytest.raises(
        ValueError,
        match="Metadata must be enclosed in brackets",
    ):
        parse_zone_definition("zone: a 0 0 type=normal")


def test_parse_zone_definition_rejects_malformed_metadata_item() -> None:
    with pytest.raises(ValueError, match="Invalid metadata item"):
        parse_zone_definition("zone: a 0 0 [type]")


def test_parse_zone_definition_rejects_unknown_zone_type() -> None:
    with pytest.raises(ValueError, match="Invalid zone type"):
        parse_zone_definition("zone: a 0 0 [type=teleport]")


def test_parse_zone_definition_rejects_unknown_metadata_key() -> None:
    with pytest.raises(ValueError, match="Unknown metadata key"):
        parse_zone_definition("zone: a 0 0 [speed=fast]")


def test_parse_map_file_requires_nb_drones_as_first_line(
    tmp_path: Path,
) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "start_hub: start 0 0",
                "nb_drones: 1",
                "end_hub: goal 1 0",
                "connection: start-goal",
            ]
        ),
    )

    with pytest.raises(ValueError, match="First line must define nb_drones"):
        parse_map_file(str(map_path))


def test_parse_map_file_requires_exactly_one_start_hub(tmp_path: Path) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "start_hub: start2 1 0",
                "end_hub: goal 2 0",
                "connection: start-goal",
            ]
        ),
    )

    with pytest.raises(
        ValueError,
        match="exactly one start_hub definition",
    ):
        parse_map_file(str(map_path))


def test_parse_map_file_rejects_connection_with_undefined_zone(
    tmp_path: Path,
) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: goal 1 0",
                "connection: start-missing_zone",
            ]
        ),
    )

    with pytest.raises(ValueError, match="undefined zone"):
        parse_map_file(str(map_path))


def test_parse_map_file_rejects_connection_unknown_metadata_key(
    tmp_path: Path,
) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: goal 1 0",
                "connection: start-goal [weight=5]",
            ]
        ),
    )

    with pytest.raises(ValueError, match="Unknown connection metadata key"):
        parse_map_file(str(map_path))


def test_parse_map_file_rejects_connection_without_dash(
    tmp_path: Path,
) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: goal 1 0",
                "connection: start_goal",
            ]
        ),
    )

    with pytest.raises(ValueError, match="Connection must use dash"):
        parse_map_file(str(map_path))
