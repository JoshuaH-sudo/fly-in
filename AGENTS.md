# Agents

This file documents the agents used in this project, following both the Fly-in project and 42 school requirements.

## Agent Guidelines
- Agents must be modular and reusable.
- Each agent should have a clear responsibility (e.g., code generation, linting, testing, etc.).
- Agents must be documented with their purpose, expected inputs/outputs, and usage examples.
- All agents must adhere to the 42 school coding standards and project guidelines.

## Agent List

| Agent Name | Purpose | Entry Point | Description |
|------------|---------|-------------|-------------|
| PythonLintAgent | Lint Python code | Makefile/lint | Runs flake8 and mypy checks |
| PythonTestAgent | Run Python tests | tests/ | Executes all test cases in the tests/ directory |

## Adding New Agents
- Document new agents in this file.
- Ensure agents are discoverable and easy to invoke via Makefile or CLI.
- Update this file with any changes to agent responsibilities or structure.
