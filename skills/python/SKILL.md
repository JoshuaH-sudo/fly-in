---
name: Python Core Skills
description: Guidelines and best practices for Python development in the Fly-in project, following 42 school standards.
---

# Python Core Skills

## Overview
This skill provides standardized instructions for writing, testing, and maintaining Python code in this repository. It ensures code quality, maintainability, and compliance with 42 school and Fly-in project requirements.

## Guidelines
- Write idiomatic, readable Python code (PEP8).
- Use type annotations and static typing (mypy enforced).
- Use `flake8` for linting and code style.
- Write tests for all public functions and classes.
- Prefer built-in modules and standard library over external dependencies.
- Document all public APIs with docstrings.
- Use virtual environments (uv/venv) for dependency management.
- Follow 42 school project guidelines for submission and structure.

## Usage Example
- Run `make lint` to check code style and types.
- Run `make install` to set up the environment.
- Add new skills in this folder as needed.

## References
- [PEP8](https://peps.python.org/pep-0008/)
- [mypy](http://mypy-lang.org/)
- [flake8](https://flake8.pycqa.org/)
