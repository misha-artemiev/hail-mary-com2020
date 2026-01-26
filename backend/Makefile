SRC = main.py internal routers database

.PHONY: default format lint

default: format spell typecheck lint

format:
	@echo "Running formatting"
	@ruff format $(SRC)

spell:
	@echo "Running spell check"
	@codespell $(SRC)

typecheck:
	@echo "Running type check"
	@mypy $(SRC)

lint:
	@echo "Running lint"
	@ruff check $(SRC)


lint:
	@echo "Running lint FIX"
	@ruff check --fix $(SRC)

run:
	@python -m main

init-db:
	@python -m database.init_db
