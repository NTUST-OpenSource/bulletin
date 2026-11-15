#!/bin/sh
# The single quality gate. The pre-push hook, the Claude Code Stop hook and CI all run it.
set -eu
cd "$(dirname "$0")/.."

npm ci --prefix tools/discord-markdown --prefer-offline --no-audit --no-fund --silent
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pyright
uv run --locked coverage run -m pytest
uv run --locked coverage report
(
    cd web
    bun install --frozen-lockfile --silent
    bun run check
    bun run test
    bun run build
)
OPENSPEC_TELEMETRY=0 npx --yes --prefer-offline @fission-ai/openspec@1.14.1 validate --all --strict </dev/null
