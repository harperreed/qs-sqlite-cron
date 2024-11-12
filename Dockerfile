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

RUN --mount=type=cache,target=/root/.cache <<EOT
    uv venv
EOT

WORKDIR /_project

# install deps
RUN --mount=type=cache,target=/root/.cache <<EOT
    uv sync --locked --no-dev --no-install-project
EOT

FROM uv AS project-builder
COPY --from=deps-builder /app /app
COPY scripts/ /src/
WORKDIR /src

# install project
RUN --mount=type=cache,target=/root/.cache <<EOT
    uv sync --locked --no-dev --no-editable
EOT

FROM base AS final
SHELL ["/bin/bash", "-exo", "pipefail",  "-c"]
ENV PATH=/app/bin:$PATH \
    PYTHONPATH=/app

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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Create necessary directories
RUN mkdir -p /app/data /app/logs \
    && chown -R app:app /app


# Copy the Python files to /app
COPY --from=project-builder --chown=app:app /src/*.py /app/

USER app
WORKDIR /app

# Modified entrypoint to run Python scripts
ENTRYPOINT ["python"]
CMD ["--help"]
