# Multi-stage build for nanobot gateway
ARG REGISTRY_PREFIX_DOCKER_HUB=
ARG REGISTRY_PREFIX_GHCR=

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM ${REGISTRY_PREFIX_DOCKER_HUB:-}astral/uv:python3.14-bookworm-slim AS builder

ARG APP_UID=1000
ARG APP_GID=1000

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Sync dependencies (without installing the project itself yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the nanobot project source
COPY . /app/nanobot/

# Install the nanobot project and any editable dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM ${REGISTRY_PREFIX_DOCKER_HUB:-}python:3.14.2-slim-bookworm AS runtime

ARG APP_UID=1000
ARG APP_GID=1000

# Create non-root user
RUN groupadd --system --gid ${APP_GID} nonroot \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home nonroot

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

# Copy nanobot project
COPY --chown=nonroot:nonroot --from=builder /app/nanobot /app/nanobot

# Set PATH to include uv venv
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER nonroot

# Run the entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
