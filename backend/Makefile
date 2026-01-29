SRC = main.py internal routers database

.PHONY: default format lint install typecheck lint-fix init-db run

default: check

check-apply: format spell typecheck lint-fix audit

check: format-check spell typecheck lint audit

install:
	@pip install -e ".[dev]"

format:
	@echo "Running formatting"
	@ruff format $(SRC)

format-check:
	@echo Running formatting checker
	@ruff format --check $(SRC)

spell:
	@echo "Running spell check"
	@codespell $(SRC)

typecheck:
	@echo "Running type check"
	@mypy $(SRC)

lint:
	@echo "Running lint"
	@ruff check $(SRC)

lint-fix:
	@echo "Running lint FIX"
	@ruff check --fix $(SRC)

audit:
	@pip-audit

run:
	@python -m main

init-db:
	@python -m database.init_db
