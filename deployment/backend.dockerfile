FROM python:3.14-alpine as builder
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
COPY backend ./backend
COPY frontend/package.json ./frontend/package.json
WORKDIR /app/backend
RUN pip install -U build
RUN python -m build --wheel

FROM python:3.14-alpine

WORKDIR /app
COPY --from=builder /app/backend/dist/*.whl .
RUN pip install --no-cache-dir *.whl
RUN rm *.whl

EXPOSE 80
CMD ["python", "-m", "main"]
