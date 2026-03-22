FROM python:3.14-slim as builder
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
COPY backend/main.py ./backend/main.py
COPY backend/routers ./backend/routers
COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/internal ./backend/internal
COPY backend/README.md ./backend/README.md
COPY frontend/package.json ./frontend/package.json
WORKDIR /app/backend
RUN pip install --upgrade pip
RUN pip install -U build
RUN python -m build --wheel


FROM python:3.14-slim
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
COPY --from=builder /app/backend/dist/*.whl .
RUN pip install --no-cache-dir *.whl
RUN rm *.whl

EXPOSE 80
CMD ["python", "-m", "main"]
