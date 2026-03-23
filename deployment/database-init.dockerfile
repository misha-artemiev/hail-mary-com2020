FROM python:3.14-slim
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
RUN apt-get update && apt-get install -y make netcat-openbsd
COPY backend/database ./backend/database
COPY backend/internal ./backend/internal
COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/README.md ./backend/README.md
COPY backend/Makefile ./backend/Makefile
COPY frontend/package.json ./frontend/package.json
WORKDIR /app/backend
RUN pip install --upgrade pip
RUN pip install --no-cache-dir ".[dev]"

CMD ["sh", "-c", "until nc -z database ${DATABASE_PORT}; do echo 'waiting for database'; sleep 1; done; make init-db-noninteractive && make upload-db"]
