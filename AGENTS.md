# AGENTS.md

Rules for everyone who changes this repository, people and coding agents alike. There is no
CLAUDE.md on purpose: Claude Code reads this file when no CLAUDE.md exists.

bulletin collects the announcements that NTUST offices and departments post on their own websites,
keeps them for ten years, and serves them through a public API and a web frontend at
`bulletin.ntust.org`. Python 3.14, FastAPI, PostgreSQL 18 with PGroonga. Read these first:

- `docs/decisions.md`: accepted decisions. Do not re-open them without asking the owner.
- `docs/roadmap.md`: the planned changes in order, and what each one has already settled.
- `GLOSSARY.md`: the domain terms. Use them in code, specs and docs.
- `docs/pitfalls.md`: verified facts about the school's websites and the tools.
- `openspec/changes/`: the active change.

## Commands

```sh
uv sync                       # create or update .venv from uv.lock
uv run prek install           # install the git hooks once per clone
scripts/gate.sh               # the full gate: npm ci, ruff, pyright, pytest + coverage, openspec
npx --yes @fission-ai/openspec@1.14.1 <command>   # OpenSpec CLI (set OPENSPEC_TELEMETRY=0)
```

The Discord Markdown check (`tools/discord-markdown/`) needs Node.js 26; the gate installs its
package.

If your global git config sets `core.hooksPath`, run `git config --local core.hooksPath
.git/hooks` before `prek install`.

Storage tests need PostgreSQL with PGroonga: set `BULLETIN_TEST_DATABASE_URL` (for example
`postgresql://postgres:postgres@localhost:5432/postgres` against the `groonga/pgroonga` image
that CI uses). Without it they skip; with `BULLETIN_REQUIRE_DB=1`, as in CI, a skip fails.

## Language

- Everything in the repository is English: code, comments, docstrings, tests, docs, OpenSpec.
- Text the school publishes stays as published: board and unit names in `seeds/`, recorded pages
  and YAML under `tests/fixtures/`. The frontend's lang files are exempt too.
- No CJK characters in `*.py`, tests included; a prek hook enforces it. Assert Chinese text
  through fixtures or code points such as `chr(0x4E2D)`. Do not type `\u` escapes through agent
  tools: some decode them into the real characters when writing the file.
- Commit messages are ASCII.

## Commits

- Conventional Commits, `type(scope): subject`, optional bullet body. Types: feat, fix, test,
  refactor, docs, build, ci, chore. Scopes: `collector`, `render`, `api`, `web`, `deploy`; leave
  the scope out for changes that span the repository.
- GPG-sign every commit and tag.
- No `Co-Authored-By`, session links or tool attribution; the commit-msg hook rejects them.
- Small and frequent. Once `scripts/gate.sh` exists, every commit passes it.

## Test-driven development (xfail-first)

1. Write the test for one requirement. Run it and confirm it fails for the expected reason.
2. Commit it marked `@pytest.mark.xfail(strict=True, reason="<requirement name>")`, usually
   with `raises=NotImplementedError` against a stub. The gate stays green.
3. Implement, remove the marker, run the gate, commit.

- No product code without a failing test first. Scaffolding gets a smoke test.
- Test names or docstrings name the requirement.
- Pure logic (parsing, detection, scheduling) is tested without a network or a database. Parsers
  run against pages recorded under `tests/fixtures/`.
- Storage tests run against a real PostgreSQL with PGroonga, never SQLite: search behaviour
  differs.
- Before claiming something works, run the gate and show its output.

## OpenSpec

- One active change at a time, under `openspec/changes/<name>/`: proposal, spec deltas, design,
  tasks. Changes without a required order may run side by side (`docs/decisions.md`, A3).
- Every scenario maps to at least one test: pytest, or Vitest or Playwright for the frontend.
- Keep each requirement's description under 500 characters; `validate --strict` fails otherwise.
- Archive right after the change is implemented and verified (`openspec archive <name> --yes`),
  then run `openspec validate --all --strict`.

## The school's servers

- Every NTUST host sits behind one WAF. Respect the request budget in `docs/decisions.md`: one
  request at a time, on average no more than one every 2 seconds, with jitter. Do not run ad-hoc
  crawls in parallel.
- Tests never reach the network. Record a page once and keep it as a fixture.
- Send the bot's User-Agent on every request.

## Rules

- List every user-visible change (copy, API fields, interaction flow) for the owner to review
  before it is pushed.
- Never commit tokens, keys or personal data; use example values. School site, board and article
  ids are public and may appear in seeds and fixtures.
- An announcement the school withdraws is marked, never deleted.

## Pushing

- Ask the owner before every push, and before force pushes, deleting branches, tags, releases and
  repository settings.
- Do not create LICENSE; the owner adds it.
