# syntax=docker/dockerfile:1.9
FROM python:3.11-slim-buster AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

FROM base AS uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11 \
    UV_PROJECT_ENVIRONMENT=/app

SHELL ["/bin/bash", "-exo", "pipefail",  "-c"]

RUN apt-get update -qy \
    && apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

FROM uv AS deps-builder
COPY scripts/pyproject.toml /_project/
COPY scripts/uv.lock /_project/

WORKDIR /_project

# Create and populate the venv that we'll copy to final image
RUN --mount=type=cache,target=/root/.cache <<EOT
    uv venv /app/venv
    UV_SYSTEM_PYTHON=/app/venv/bin/python \
    UV_PROJECT_ENVIRONMENT=/app/venv \
    uv sync
EOT

FROM uv AS project-builder
COPY --from=deps-builder /app/venv /app/venv
COPY scripts/ /src/
WORKDIR /src

# Install project into the venv
RUN --mount=type=cache,target=/root/.cache <<EOT
    UV_SYSTEM_PYTHON=/app/venv/bin/python \
    UV_PROJECT_ENVIRONMENT=/app/venv \
    uv sync
EOT

# Previous stages remain the same...

FROM base AS final
SHELL ["/bin/bash", "-exo", "pipefail",  "-c"]
ENV PATH=/app/venv/bin:$PATH \
    PYTHONPATH=/app \
    UV_SYSTEM_PYTHON=/app/venv/bin/python \
    UV_PROJECT_ENVIRONMENT=/app/venv

RUN <<EOT
    groupadd -r app
    useradd -r -d /app -g app -N app
EOT

STOPSIGNAL SIGINT

RUN <<EOT
    apt-get update -qy
    apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Create necessary directories
RUN mkdir -p /app/data /app/logs \
    && chown -R app:app /app

# Copy uv from the uv stage
COPY --from=uv /usr/local/bin/uv /usr/local/bin/uv

# Copy the venv and all project files
COPY --from=project-builder --chown=app:app /app/venv /app/venv
COPY --from=project-builder --chown=app:app /src/*.py /app/
COPY --from=project-builder --chown=app:app /src/uv.lock /app/
COPY --from=project-builder --chown=app:app /src/pyproject.toml /app/

USER app
WORKDIR /app

ENTRYPOINT ["uv", "run"]
