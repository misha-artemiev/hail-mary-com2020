PYTHON = .venv/bin/python
PIP = .venv/bin/pip

start:
	@$(PYTHON) main.py

init-db:
	@$(PYTHON) -m database.init_db

install:
	@$(PIP) install -r requirements.txt
