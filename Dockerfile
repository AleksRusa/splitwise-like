FROM python:3.12 as builder

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true

RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app .

COPY . .

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

EXPOSE 8000

# ENTRYPOINT ["uvicorn", "src.splitwise.main:app", "--host", "0.0.0.0", "--port", "8000"]

VOLUME /my_volume