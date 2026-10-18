FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry==2.5.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

COPY alembic.ini ./
COPY alembic alembic
COPY shortener shortener

EXPOSE 8000

# In the form of a shell, so that it reads PORT, and with exec, so that uvicorn,
# and not the shell, gets the signals. See docs/service/running.md#the-processes
CMD exec uvicorn shortener.bootstrap.app:create_app --factory --host 0.0.0.0 --port "${PORT:-8000}"
