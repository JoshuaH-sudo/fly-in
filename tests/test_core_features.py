"""Additional core behavior tests for parser, simulator, and menu."""

from pathlib import Path
import sys

import pytest

from src.map_menu import MapMenu, MapOption
from src.parser import parse_map_file, parse_zone_definition
import src.simulator as simulator_module
from src.zone import ZoneType

ROOT = Path(__file__).resolve().parents[1]


def _write_map(tmp_path: Path, content: str) -> Path:
    map_path = tmp_path / "map.txt"
    map_path.write_text(content)
    return map_path


@pytest.mark.parametrize(
    "zone_line,expected_type,expected_capacity",
    [
        ("zone: p 1 1 [type=priority]", ZoneType.PRIORITY, 2),
        ("zone: b 2 2 [type=blocked]", ZoneType.BLOCKED, 0),
        ("zone: n 3 3 [type=normal]", ZoneType.NORMAL, 1),
    ],
)
def test_zone_defaults_follow_zone_type(
    zone_line: str,
    expected_type: ZoneType,
    expected_capacity: int,
) -> None:
    zone = parse_zone_definition(zone_line)
    assert zone.zone_type == expected_type
    assert zone.max_drones == expected_capacity


def test_start_and_end_hubs_are_assigned_special_zone_types(
    tmp_path: Path,
) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0 [color=green]",
                "end_hub: goal 1 0 [color=red]",
                "connection: start-goal",
            ]
        ),
    )

    network = parse_map_file(str(map_path))

    start = network.get_position("start")
    goal = network.get_position("goal")

    assert start.zone_type == ZoneType.START
    assert goal.zone_type == ZoneType.END


def test_duplicate_connections_are_rejected(tmp_path: Path) -> None:
    map_path = _write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: goal 1 0",
                "connection: start-goal",
                "connection: goal-start",
            ]
        ),
    )

    with pytest.raises(ValueError, match="Duplicate connection"):
        parse_map_file(str(map_path))


def test_map_menu_non_tty_returns_first_option(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    menu = MapMenu(str(ROOT / "maps"))
    options = [
        MapOption(label="easy/01_linear_path.txt", path="/tmp/map1.txt"),
        MapOption(label="medium/01_dead_end_trap.txt", path="/tmp/map2.txt"),
    ]

    class DummyStdin:
        def isatty(self) -> bool:
            return False

    monkeypatch.setattr(sys, "stdin", DummyStdin())
    selected = menu.choose_map(options)
    assert selected == "/tmp/map1.txt"


def test_run_simulation_headless_does_not_render(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = {"value": False}

    class DummyDisplay:
        def __init__(self, _network: object) -> None:
            called["value"] = True

        def show_history(self, _history: list[dict[str, str]]) -> None:
            called["value"] = True

    monkeypatch.setattr(simulator_module, "Display", DummyDisplay)
    network = parse_map_file(str(ROOT / "maps/easy/01_linear_path.txt"))

    history = simulator_module.run_simulation(network, render_history=False)

    assert called["value"] is False
    assert history[-1]
    assert all(zone == network.end_hub for zone in history[-1].values())


def test_run_simulation_render_mode_calls_display(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"count": 0}

    class DummyDisplay:
        def __init__(self, _network: object) -> None:
            pass

        def show_history(self, _history: list[dict[str, str]]) -> None:
            calls["count"] += 1

    monkeypatch.setattr(simulator_module, "Display", DummyDisplay)
    network = parse_map_file(str(ROOT / "maps/easy/01_linear_path.txt"))

    simulator_module.run_simulation(network, render_history=True)

    assert calls["count"] == 1
