# syntax=docker/dockerfile:1
# bulletin: the collector, the renderer, the admin API and the web page, installed from uv.lock, the
# Discord check's package-lock.json and the frontend's bun.lock. Run it with compose.yaml.

# The Discord Markdown check (tools/discord-markdown); CI runs the same Node version.
FROM node:26.13.0-trixie-slim@sha256:5adad64f9a1fca2d51972caa65983634c8a774eb300d72b20f7f2a0f60368072 AS node
WORKDIR /app/tools/discord-markdown
COPY tools/discord-markdown/package.json tools/discord-markdown/package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund
COPY tools/discord-markdown/check.mjs ./

# The frontend (web/); CI runs the same Bun version.
FROM oven/bun:1.4.4-slim@sha256:1846adf22496bd711036aae8be147e57bdebbaea2e5264e3e0b5af1db187d9a4 AS web
WORKDIR /app/web
COPY web/package.json web/bun.lock ./
RUN bun install --frozen-lockfile
COPY web/ ./
RUN bun run build

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
# Node needs libatomic, which the slim image lacks. /data/files is created here so a new named
# volume mounted there starts owned by bulletin.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 1000 --create-home bulletin \
    && mkdir -p /data/files \
    && chown -R bulletin:bulletin /data
COPY --from=builder /app/.venv /app/.venv
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /app/tools /app/tools
COPY --from=web /app/web/dist /app/web
COPY seeds /app/seeds
ENV PATH="/app/.venv/bin:${PATH}" PYTHONUNBUFFERED=1 BULLETIN_SEED=/app/seeds/boards.json \
    BULLETIN_DISCORD_CHECK=/app/tools/discord-markdown/check.mjs BULLETIN_WEB=/app/web
USER bulletin
WORKDIR /app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"]
ENTRYPOINT ["bulletin"]
CMD ["serve"]
