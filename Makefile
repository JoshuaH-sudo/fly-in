
UV := uv
VENV := .venv
VENV_BIN := $(VENV)/bin

.PHONY: install run debug clean lint lint-strict

install:
	$(UV) venv $(VENV)
	$(VENV_BIN)/uv pip install --upgrade pip
	$(VENV_BIN)/uv pip install -r requirements.txt -r requirements-dev.txt

run:
	$(VENV_BIN)/python -m fly_in

debug:
	$(VENV_BIN)/python -m pdb -m fly_in

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

lint:
	$(VENV_BIN)/flake8 .
	$(VENV_BIN)/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV_BIN)/flake8 .
	$(VENV_BIN)/mypy . --strict
