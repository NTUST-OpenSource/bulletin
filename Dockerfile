# syntax=docker/dockerfile:1
# bulletin: the collector and its admin API, installed from uv.lock. Run it with compose.yaml.

FROM python:3.14.8-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
# Dependencies first, so code changes reuse this layer until the lock file changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.14.8-slim-trixie
# /data/files is created here so a new named volume mounted there starts owned by bulletin.
RUN useradd --uid 1000 --create-home bulletin \
    && mkdir -p /data/files \
    && chown -R bulletin:bulletin /data
COPY --from=builder /app/.venv /app/.venv
COPY seeds /app/seeds
ENV PATH="/app/.venv/bin:${PATH}" PYTHONUNBUFFERED=1 BULLETIN_SEED=/app/seeds/boards.json
USER bulletin
WORKDIR /app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]
ENTRYPOINT ["bulletin"]
CMD ["serve"]
