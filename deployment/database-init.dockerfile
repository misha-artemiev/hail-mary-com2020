FROM python:3.14-alpine
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
RUN apk add --no-cache make
COPY backend/database ./backend/database
COPY backend/internal ./backend/internal
COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/README.md ./backend/README.md
COPY backend/Makefile ./backend/Makefile
COPY frontend/package.json ./frontend/package.json
WORKDIR /app/backend
RUN apk add --no-cache gcc musl-dev g++ libgomp
ENV CC=gcc CXX=g++ CMAKE_BUILD_PARALLEL_LEVEL=1 
RUN pip install --upgrade pip
RUN pip install ".[dev]"

CMD ["sh", "-c", "until nc -z database ${DATABASE_PORT}; do echo 'waiting for database'; sleep 1; done; make init-db-noninteractive && make upload-db"]
