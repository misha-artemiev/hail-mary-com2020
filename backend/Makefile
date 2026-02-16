SRC = main.py internal routers database testing

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: default format lint install typecheck lint-fix init-db run docs check check-apply sql

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

FILES = users admins sellers consumers bundles category allergens bundle_category bundle_allergens reservations seller_issue_reports admin_issue_reports inbox badges badges_acquired token
upload-db:
	@python -m database.data.dataGen
	@for file in $(FILES); do \
		csvsql --db "postgresql://$(DATABASE_USERNAME):$(DATABASE_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/$(DATABASE_DATABASE)" --insert --no-create --no-inference "synthetic_data/$$file.csv"; \
	done
	@rm -r ./synthetic_data
	@python -m database.data.fixSeq

docs:
	@mv .env .env.bak || true
	@pdoc --docformat google \
		--mermaid \
		--math \
		-o ./docs \
		main.py internal routers database
	@mv .env.bak .env || true

sql:
	@sqlc generate
