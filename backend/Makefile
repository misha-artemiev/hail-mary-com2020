SRC = main.py internal routers database

.PHONY: default format lint

default: format spell typecheck lint

format:
	@ruff format $(SRC)

spell:
	@codespell $(SRC)

typecheck:
	@mypy $(SRC)

lint:
	@ruff check $(SRC)

run:
	@python -m main

init-db:
	@python -m database.init_db
