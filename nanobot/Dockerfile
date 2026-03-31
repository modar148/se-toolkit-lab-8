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

# Copy workspace dependency files first for better caching
# The 'workspace' additional_contexts makes the repo root available
COPY --from=workspace pyproject.toml uv.lock /app/

# Copy the nanobot project source
COPY --from=workspace nanobot/ /app/nanobot/

# Install the nanobot project and any editable dependencies
# Use --no-install-workspace to skip other workspace members
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM ${REGISTRY_PREFIX_DOCKER_HUB:-}python:3.14.2-slim-bookworm AS runtime

ARG APP_UID=1000
ARG APP_GID=1000

# Create non-root user (skip if running as root with UID 0)
RUN if [ "${APP_UID}" != "0" ]; then \
    groupadd --system --gid ${APP_GID} nonroot && \
    useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home nonroot; \
    fi

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv

# Copy nanobot project
COPY --chown=nonroot:nonroot --from=builder /app/nanobot /app/nanobot

# Set PATH to include uv venv
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user (skip if UID is 0)
USER nonroot

# Run the entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
