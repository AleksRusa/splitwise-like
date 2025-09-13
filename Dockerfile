FROM python:3.12 as builder

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app ./

COPY . .

EXPOSE 8000

ENTRYPOINT ['uvicorn', 'src.splitwise.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000']

VOLUME /my_volume