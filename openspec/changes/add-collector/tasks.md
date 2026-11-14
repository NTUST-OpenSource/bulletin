# Tasks: add-collector

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked
`xfail(strict=True)`, then implement it, remove the marker and commit with the gate green.

## 1. Scaffolding and the gate

- [x] 1.1 Create `pyproject.toml` for Python 3.14 with uv (FastAPI, psycopg 3, aiohttp; dev: pytest, coverage, ruff, pyright, prek) and `uv.lock`; verify `uv sync --locked` succeeds
- [x] 1.2 Configure ruff `select = ["ALL"]` with documented ignores, pyright strict and branch coverage of at least 85%, add `scripts/gate.sh` as in xincord and a smoke test importing the package; verify `scripts/gate.sh` passes
- [x] 1.3 Port `scripts/check_commit_msg.py` with its test from xincord and add `.pre-commit-config.yaml` (ruff, pyright, no CJK in `*.py`, commit-msg, the gate on pre-push); verify `uv run prek run --all-files` passes and a commit with a CJK subject is refused
- [x] 1.4 Add the Claude Code hooks from xincord (`.claude/settings.json`: ruff on edited `.py`, the gate on stop); verify editing a badly formatted file gets reformatted
- [x] 1.5 Add the CI workflow: pinned actions, `uv sync --locked`, a PGroonga service container, `BULLETIN_REQUIRE_DB=1`, the gate; verify it with `actionlint`

## 2. Database foundation

- [x] 2.1 Add the storage test fixture: a throwaway schema on `BULLETIN_TEST_DATABASE_URL`, skipped when unset, failing when `BULLETIN_REQUIRE_DB=1`; verify both paths with a test
- [ ] 2.2 Add the migration runner (numbered SQL files, `schema_migration`) and the first migration with the tables of design.md; verify a test applies it to an empty schema and a second run changes nothing
- [ ] 2.3 Record list and article pages as fixtures under `tests/fixtures/` (table and list layouts, a board without dates, a file link, a board listing another site's article, a withdrawn article's 302, an article with a `ptattach` module and body `/var/file/` links), one request at a time; verify every fixture names its source URL and date

## 3. Event log

- [ ] 3.1 Commit the xfail test for "Events" (event-log); verify it fails for the expected reason and the gate stays green
- [ ] 3.2 Implement "Events" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 3.3 Commit the xfail test for "Gap-free order" (event-log); verify it fails for the expected reason and the gate stays green
- [ ] 3.4 Implement "Gap-free order" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 3.5 Commit the xfail test for "Notify flag" (event-log); verify it fails for the expected reason and the gate stays green
- [ ] 3.6 Implement "Notify flag" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 3.7 Commit the xfail test for "Late discoveries are marked" (event-log); verify it fails for the expected reason and the gate stays green
- [ ] 3.8 Implement "Late discoveries are marked" and remove the marker; verify its scenarios pass and the gate is green

## 4. Board registry

- [ ] 4.1 Commit the xfail test for "Board identity" (board-registry); verify it fails for the expected reason and the gate stays green
- [ ] 4.2 Implement "Board identity" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.3 Commit the xfail test for "Seed import" (board-registry); verify it fails for the expected reason and the gate stays green
- [ ] 4.4 Implement "Seed import" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.5 Commit the xfail test for "Boards are kept" (board-registry); verify it fails for the expected reason and the gate stays green
- [ ] 4.6 Implement "Boards are kept" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.7 Commit the xfail test for "Board categories" (board-registry); verify it fails for the expected reason and the gate stays green
- [ ] 4.8 Implement "Board categories" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.9 Commit the xfail test for "Re-discovery" (board-registry); verify it fails for the expected reason and the gate stays green
- [ ] 4.10 Implement "Re-discovery" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.11 Commit the xfail test for "Category guess" (board-registry); verify it fails for the expected reason and the gate stays green
- [ ] 4.12 Implement "Category guess" and remove the marker; verify its scenarios pass and the gate is green

## 5. Polling

List parsing ports xincord's `ntust_announcements/pages.py` and `markup.py`; certificates port
`ntust_tls` with its TWCA certificate.

- [ ] 5.1 Commit the xfail test for "Tier intervals" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.2 Implement "Tier intervals" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.3 Commit the xfail test for "Request budget" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.4 Implement "Request budget" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.5 Commit the xfail test for "Queue order" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.6 Implement "Queue order" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.7 Commit the xfail test for "List page fetch" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.8 Implement "List page fetch" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.9 Commit the xfail test for "Unchanged pages" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.10 Implement "Unchanged pages" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.11 Commit the xfail test for "Paging on bursts" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.12 Implement "Paging on bursts" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.13 Commit the xfail test for "Failure backoff" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.14 Implement "Failure backoff" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.15 Commit the xfail test for "Poll log" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.16 Implement "Poll log" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.17 Commit the xfail test for "School certificates" (polling); verify it fails for the expected reason and the gate stays green
- [ ] 5.18 Implement "School certificates" and remove the marker; verify its scenarios pass and the gate is green

## 6. Detection

- [ ] 6.1 Commit the xfail test for "New announcement" (detection); verify it fails for the expected reason and the gate stays green
- [ ] 6.2 Implement "New announcement" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 6.3 Commit the xfail test for "Recycled articles" (detection); verify it fails for the expected reason and the gate stays green
- [ ] 6.4 Implement "Recycled articles" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 6.5 Commit the xfail test for "Frontier record" (detection); verify it fails for the expected reason and the gate stays green
- [ ] 6.6 Implement "Frontier record" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 6.7 Commit the xfail test for "Notify rule on backfilled boards" (detection); verify it fails for the expected reason and the gate stays green
- [ ] 6.8 Implement "Notify rule on backfilled boards" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 6.9 Commit the xfail test for "Frontier rule" (detection); verify it fails for the expected reason and the gate stays green
- [ ] 6.10 Implement "Frontier rule" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 6.11 Commit the xfail test for "Cross-posts" (detection); verify it fails for the expected reason and the gate stays green
- [ ] 6.12 Implement "Cross-posts" and remove the marker; verify its scenarios pass and the gate is green

## 7. Archive

Article parsing ports the article half of xincord's `pages.py`.

- [ ] 7.1 Commit the xfail test for "Article fetch" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.2 Implement "Article fetch" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 7.3 Commit the xfail test for "Revisions" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.4 Implement "Revisions" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 7.5 Commit the xfail test for "Withdrawal" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.6 Implement "Withdrawal" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 7.7 Commit the xfail test for "Prompt withdrawal check" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.8 Implement "Prompt withdrawal check" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 7.9 Commit the xfail test for "Restored announcements" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.10 Implement "Restored announcements" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 7.11 Commit the xfail test for "Ten-year retention" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.12 Implement "Ten-year retention" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 7.13 Commit the xfail test for "Search indexes" (archive); verify it fails for the expected reason and the gate stays green
- [ ] 7.14 Implement "Search indexes" and remove the marker; verify its scenarios pass and the gate is green

## 8. Attachments

- [ ] 8.1 Commit the xfail test for "Attachment records" (attachments); verify it fails for the expected reason and the gate stays green
- [ ] 8.2 Implement "Attachment records" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 8.3 Commit the xfail test for "Stored copies" (attachments); verify it fails for the expected reason and the gate stays green
- [ ] 8.4 Implement "Stored copies" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 8.5 Commit the xfail test for "Size without HEAD" (attachments); verify it fails for the expected reason and the gate stays green
- [ ] 8.6 Implement "Size without HEAD" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 8.7 Commit the xfail test for "One-year file window" (attachments); verify it fails for the expected reason and the gate stays green
- [ ] 8.8 Implement "One-year file window" and remove the marker; verify its scenarios pass and the gate is green

## 9. Backfill

- [ ] 9.1 Commit the xfail test for "Ten-year walk" (backfill); verify it fails for the expected reason and the gate stays green
- [ ] 9.2 Implement "Ten-year walk" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 9.3 Commit the xfail test for "Backfill articles" (backfill); verify it fails for the expected reason and the gate stays green
- [ ] 9.4 Implement "Backfill articles" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 9.5 Commit the xfail test for "Resumable progress" (backfill); verify it fails for the expected reason and the gate stays green
- [ ] 9.6 Implement "Resumable progress" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 9.7 Commit the xfail test for "No announcements from backfill" (backfill); verify it fails for the expected reason and the gate stays green
- [ ] 9.8 Implement "No announcements from backfill" and remove the marker; verify its scenarios pass and the gate is green

## 10. Tier admin

- [ ] 10.1 Commit the xfail test for "Change a tier" (tier-admin); verify it fails for the expected reason and the gate stays green
- [ ] 10.2 Implement "Change a tier" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 10.3 Commit the xfail test for "Tier audit" (tier-admin); verify it fails for the expected reason and the gate stays green
- [ ] 10.4 Implement "Tier audit" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 10.5 Commit the xfail test for "Turning a board on" (tier-admin); verify it fails for the expected reason and the gate stays green
- [ ] 10.6 Implement "Turning a board on" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 10.7 Commit the xfail test for "Review new boards" (tier-admin); verify it fails for the expected reason and the gate stays green
- [ ] 10.8 Implement "Review new boards" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 10.9 Commit the xfail test for "Admin API access" (tier-admin); verify it fails for the expected reason and the gate stays green
- [ ] 10.10 Implement "Admin API access" and remove the marker; verify its scenarios pass and the gate is green

## 11. Deployment

- [ ] 11.1 Add the `Dockerfile` (uv, non-root user) and `/health` with its test; verify the image builds on the remote test host
- [ ] 11.2 Add `compose.yaml` and `.env.example` per design.md (no published ports, `bulletin-db` and `bulletin-admin` internal, `proxy-net` external, admin listener on its alias); verify on the remote test host that the app is healthy, the admin port does not answer on the `proxy-net` address and the database has no outbound route
- [ ] 11.3 Document deployment and the CLI in `README.md`; verify every command in it runs against the test host

## 12. Integration

- [ ] 12.1 Add an end-to-end test over fixtures and a fake transport: seed import, a first poll that announces nothing, a new article that is announced, a re-check that finds it withdrawn; verify the event log reads published (not notify-worthy), published (notify-worthy), withdrawn
- [ ] 12.2 List the user-visible changes of design.md for the owner and wait for approval before pushing
- [ ] 12.3 Run `scripts/gate.sh`; verify it passes

## Workflow follow-up

- Archive the change with `openspec archive add-collector --yes`, then run `openspec validate --all --strict`.
- Deploy to the owner's host only with the owner's approval.
