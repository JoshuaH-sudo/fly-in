*This project has been created as part of the 42 curriculum by JoshuaH-sudo.*

# fly-in

## Description
Fly-in is a graph-routing project where a fleet of drones must move from a single start hub to a single end hub in the fewest simulation turns while respecting:
- zone types (`normal`, `blocked`, `restricted`, `priority`),
- zone occupancy capacities (`max_drones`),
- connection capacities (`max_link_capacity`),
- and per-turn collision/conflict constraints.

This repository currently provides a clean Python skeleton (parser/simulator templates, CLI entry point, lint/type-check setup, and starter tests) so implementation can begin quickly.

## Instructions
### 1) Environment setup
```bash
make install
```
This creates `.venv` and installs dependencies.

### 2) Run the app
```bash
make run
```

### 3) Debug the app
```bash
make debug
```

### 4) Lint and type-check
```bash
make lint
# optional strict mode
make lint-strict
```

### 5) Clean caches
```bash
make clean
```

### 6) Tests
A starter `unittest` smoke test is available:
```bash
.venv/bin/python -m unittest discover -q
```

## Algorithm choices and implementation strategy
Planned implementation strategy:
1. **Parser-first validation pipeline**: Parse line-by-line with strict grammar checks and explicit error messages containing line number + cause.
2. **Graph model with metadata-aware weights**: Build adjacency structures carrying zone/link capacities and weighted move costs (restricted = 2 turns, blocked disallowed, priority preferred).
3. **Routing + scheduling separation**:
   - Routing computes candidate paths (possibly multiple) with weighted costs and tie-breaking that favors priority zones.
   - Scheduling executes turn-by-turn movement while enforcing zone/link capacity constraints and no-conflict rules.
4. **Throughput optimization**: Distribute drones across compatible paths and insert strategic waits only when constraints force them.
5. **Performance approach**: Cache reusable path computations and avoid full recomputation each turn when topology is unchanged.

## Visual representation
The skeleton is CLI-ready. Planned visualization includes:
- colored terminal output for zone states and drone movements,
- turn-by-turn movement lines in required format (`D<ID>-<zone>` / `D<ID>-<connection>`),
- optional future graphical view if needed.

This visual output will make congestion points, waiting turns, and path allocation decisions easier to inspect.

## Resources
- 42 subject and peer-evaluation documentation
- Python docs:
  - argparse: https://docs.python.org/3/library/argparse.html
  - dataclasses: https://docs.python.org/3/library/dataclasses.html
  - unittest: https://docs.python.org/3/library/unittest.html
- Type-checking and linting:
  - mypy: https://mypy.readthedocs.io/
  - flake8: https://flake8.pycqa.org/

### AI usage
AI assistance was used to scaffold this initial project structure, generate starter Makefile targets, and draft documentation sections. Core parser, algorithm, scheduling logic, and optimization decisions remain to be implemented and validated by the project author.
