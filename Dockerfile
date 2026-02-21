# Stage 1: Build the SQLite database from source data
FROM python:3.14-slim AS builder

WORKDIR /build

COPY IES2023.zip import_data.py ./

RUN apt-get update && apt-get install -y --no-install-recommends unzip \
    && unzip IES2023.zip -d csv_temp \
    && python import_data.py \
    && rm -rf csv_temp IES2023.zip \
    && apt-get purge -y unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Stage 2: Runtime image with the webapp
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY webapp/pyproject.toml webapp/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY webapp/app.py webapp/main.py ./
COPY webapp/templates/ templates/

COPY --from=builder /build/ies2023.db ./

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]
