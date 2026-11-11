FROM python:3.14-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

ENV UV_PYTHON=3.14
ENV UV_PYTHON_DOWNLOADS=never

RUN uv sync --frozen --no-install-project

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

ENV PYTHONPATH=/app/src

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000"]
