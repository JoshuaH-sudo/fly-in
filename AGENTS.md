# Fly-in Agent Guide

This file provides operational instructions for coding agents working on this repository.
It is distilled from the project subject and formatted for implementation tasks.

## Mission
Build a Python simulation that routes drones from a single start hub to a single end hub in the fewest turns while respecting all movement, occupancy, and capacity constraints.

## Required Deliverables
- Parser for map files
- Simulation engine with turn-by-turn scheduling
- Pathfinding/routing strategy that minimizes total turns
- Visual representation (colored terminal output, GUI, or both)
- Output format exactly matching the specification

## Technical Constraints
- Python: 3.10+
- Style: flake8 compliant
- Typing: mypy compliant, typed functions and relevant variables
- Architecture: object-oriented
- Forbidden: graph helper libraries (for example networkx, graphlib)

## Build and Tooling Rules
Use the Make targets in this repository:
- install
- run
- debug
- clean
- lint
- lint-strict (optional)

## Input Format Rules
Map files use these declarations:
- nb_drones: <positive_integer>
- start_hub: <name> <x> <y> [metadata]
- end_hub: <name> <x> <y> [metadata]
- hub: <name> <x> <y> [metadata]
- connection: <zone1>-<zone2> [metadata]

Metadata:
- For hubs/zones:
  - zone=<normal|blocked|restricted|priority> (default normal)
  - color=<single_word> (default none)
  - max_drones=<positive_integer> (default 1)
- For connections:
  - max_link_capacity=<positive_integer> (default 1)

Additional parser constraints:
- Exactly one start_hub and one end_hub
- Zone names must be unique
- Zone names cannot contain dashes or spaces
- Connections must reference previously defined zones
- Duplicate connections are forbidden (a-b equals b-a)
- Invalid metadata or invalid types must raise parsing errors
- Any syntax/semantic parsing error must report line and cause clearly

## Movement and Simulation Rules
Simulation runs in discrete turns.

At each turn, a drone can:
- Move to an adjacent connected zone
- Start/continue a restricted-zone traversal (2-turn movement)
- Wait in place

Destination zone type cost:
- normal: 1 turn
- priority: 1 turn (prefer during pathfinding)
- restricted: 2 turns
- blocked: cannot be entered

Occupancy and capacity:
- Default zone capacity is 1 drone
- Zone capacity can be increased via max_drones
- Start and end hubs are special and can host multiple drones
- A move into a zone is valid only if capacity remains after departures in that same turn
- Connection traversal also obeys max_link_capacity
- Restricted traversal occupies the connection during transit and must complete on schedule (no extra waiting on edge)

Conflict prevention:
- No capacity overflow on zones or connections
- No invalid concurrent movements
- Avoid deadlocks and path conflicts

## Output Format Rules
- Output one line per simulation turn
- Line contains all movements that occurred during that turn, space-separated
- Movement token format:
  - D<ID>-<zone>
  - D<ID>-<connection> when in-flight to restricted destination
- Drones that do not move in a turn are omitted from that line
- Delivered drones (arrived at end_hub) are no longer tracked
- End simulation when all drones are delivered

Example:
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal

## Optimization Expectations
Target overall objective: minimize total simulation turns.

Reference targets:
- Easy maps: typically under 10 turns
- Medium maps: typically 10-30 turns
- Hard maps: typically under 60 turns
- Challenger map: aim to beat 45 turns (optional)

Secondary quality indicators:
- Throughput per turn
- Average turns per drone
- Total weighted path cost
- Clarity and usefulness of visual representation

## Implementation Guidance for Agents
When modifying code, follow this order:
1. Parse and validate input strictly.
2. Build internal graph/state model with capacities and zone types.
3. Implement a scheduler that resolves moves per turn with conflict checks.
4. Integrate pathfinding that supports multi-path distribution and waiting strategies.
5. Enforce restricted traversal lifecycle across turns.
6. Emit exact output format.
7. Add tests for parser errors, capacity conflicts, restricted traversal, and benchmark maps.

## Definition of Done
A change is complete when:
- make install succeeds
- make lint succeeds
- make test succeeds
- Parser and simulation respect all mandatory rules
- Output format matches spec exactly
- Agent can explain algorithm choices during review
