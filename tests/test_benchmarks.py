"""Benchmark validation tests for provided Fly-in maps."""

from pathlib import Path
import os

import pytest

from src.parser import parse_map_file
from src.simulator import run_simulation

ROOT = Path(__file__).resolve().parents[1]

# Required benchmark targets from section VII.7.
REQUIRED_BENCHMARKS: list[tuple[str, int]] = [
    ("maps/easy/01_linear_path.txt", 6),
    ("maps/easy/02_simple_fork.txt", 8),
    ("maps/easy/03_basic_capacity.txt", 6),
    ("maps/medium/01_dead_end_trap.txt", 12),
    ("maps/medium/02_circular_loop.txt", 15),
    ("maps/medium/03_priority_puzzle.txt", 12),
    ("maps/hard/01_maze_nightmare.txt", 30),
    ("maps/hard/02_capacity_hell.txt", 35),
    ("maps/hard/03_ultimate_challenge.txt", 45),
]


@pytest.mark.parametrize("map_path,max_turns", REQUIRED_BENCHMARKS)
def test_required_benchmark_turn_targets(
    map_path: str,
    max_turns: int,
) -> None:
    """All required benchmark maps should meet their reference turn target."""
    network = parse_map_file(str(ROOT / map_path))
    history = run_simulation(network, render_history=False)

    # history includes step 0 (initial placement), so simulation turns are N-1.
    simulation_turns = len(history) - 1
    assert simulation_turns <= max_turns, (
        f"Benchmark failed for {map_path}: got {simulation_turns} turns, "
        f"expected <= {max_turns}."
    )


@pytest.mark.skipif(
    os.getenv("FLYIN_INCLUDE_CHALLENGER") != "1",
    reason="Optional challenger benchmark disabled by default.",
)
def test_optional_challenger_reference_target() -> None:
    """Optional challenger map reference target (enable with env var)."""
    map_path = ROOT / "maps/challenger/01_the_impossible_dream.txt"
    network = parse_map_file(str(map_path))
    history = run_simulation(network, render_history=False)
    simulation_turns = len(history) - 1

    assert simulation_turns <= 45, (
        "Optional challenger benchmark failed: "
        f"got {simulation_turns} turns, expected <= 45."
    )
