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

# Copy workspace files from the 'workspace' additional_contexts
COPY --from=workspace pyproject.toml uv.lock ./
COPY --from=workspace nanobot/ ./nanobot/
COPY --from=workspace mcp/ ./mcp/
COPY --from=workspace nanobot-websocket-channel/ ./nanobot-websocket-channel/

# Install dependencies from uv.lock (skip workspace members)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --only-dev

# Install the packages we need as editable installs
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e ./mcp/mcp-lms

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e ./nanobot-websocket-channel/nanobot-channel-protocol

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e ./nanobot-websocket-channel/mcp-webchat

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e ./nanobot-websocket-channel/nanobot-webchat

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

# Copy nanobot project (config, entrypoint, workspace)
COPY --chown=nonroot:nonroot --from=builder /app/nanobot /app/nanobot

# Copy MCP servers and websocket channel (needed for runtime)
COPY --chown=nonroot:nonroot --from=builder /app/mcp /app/mcp
COPY --chown=nonroot:nonroot --from=builder /app/nanobot-websocket-channel /app/nanobot-websocket-channel

# Set PATH to include uv venv
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user (skip if UID is 0)
USER nonroot

# Run the entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
