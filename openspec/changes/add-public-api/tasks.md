# Tasks: add-public-api

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked
`xfail(strict=True)`, then implement it, remove the marker and commit with the gate green. API
tests call the app in process with httpx's ASGI transport against the PGroonga test database.

## 1. Foundations

- [x] 1.1 Scaffolding: write `src/bulletin/units.json` from the survey's unit lists (kind, college, order by site id) with a test that every site with a polled board in `seeds/boards.json` appears exactly once; verify the test passes and list the units by kind and college for the owner
- [x] 1.2 Scaffolding: mount the `/api/v1` sub-application on the public app with its own pool, keep `/health`, and wire `serve` to pass the pool, the file store and the release; verify with the service test that `/health` still answers and `/api/v1/openapi.json` exists (add-web-frontend task 2.2 builds on this)

## 2. Stream day

- [x] 2.1 Commit the xfail test for "Stream day" (archive): migration 0006, the trigger on insert and the nightly re-estimate; verify it fails for the expected reason and the gate stays green
- [x] 2.2 Implement "Stream day" (migration 0006 with `stream_day`, the trigger, the indexes, the nightly update) and remove the marker; verify its scenarios and the migration test pass and the gate is green
- [x] 2.3 Make `next_pending` read `announcement.dated` for "What gets rendered" (rendering); verify the existing scenarios still pass and the gate is green

## 3. Stream and search

- [x] 3.1 Commit the xfail test for "Read-only JSON under /api/v1" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 3.2 Implement "Read-only JSON under /api/v1" (JSON errors, 405, no admin routes) and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.3 Commit the xfail test for "Announcement stream" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 3.4 Implement "Announcement stream" (the query driven by boards, the cursor, cross-posts folded) and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.5 Commit the xfail test for "Stream items" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 3.6 Implement "Stream items" (tags, boards and renditions read per page) and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.7 Commit the xfail test for "Stream filters" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 3.8 Implement "Stream filters" and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.9 Commit the xfail test for "Search" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 3.10 Implement "Search" (plain words with `&@`, the materialized matches) and remove the marker; verify its scenarios pass and the gate is green

## 4. Single announcements, events, sites and tags

- [ ] 4.1 Commit the xfail test for "One announcement" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 4.2 Implement "One announcement" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.3 Commit the xfail test for "Events feed" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 4.4 Implement "Events feed" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.5 Commit the xfail test for "Sites and boards" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 4.6 Implement "Sites and boards" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.7 Commit the xfail test for "Tag taxonomy" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 4.8 Implement "Tag taxonomy" and remove the marker; verify its scenarios pass and the gate is green

## 5. HTTP behaviour

- [ ] 5.1 Commit the xfail test for "HTTP caching" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 5.2 Implement "HTTP caching" (the release and event-id ETag dependency, content ETags, 304, `no-store` on errors) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.3 Commit the xfail test for "CORS" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 5.4 Implement "CORS" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.5 Commit the xfail test for "Stored files" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 5.6 Implement "Stored files" (the store check, names with `/`, the allow-list, immutable caching) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.7 Commit the xfail test for "Search rate limit" (public-api), with the app wrapped in uvicorn's proxy-header middleware as `serve` runs it; verify it fails for the expected reason and the gate stays green
- [ ] 5.8 Implement "Search rate limit" (IPv6 by /64, the exemption without `X-Forwarded-For`, the bounded map) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.9 Commit the xfail test for "API description" (public-api); verify it fails for the expected reason and the gate stays green
- [ ] 5.10 Implement "API description" and remove the marker; verify its scenarios pass and the gate is green

## 6. Verification

- [ ] 6.1 Load a dump of the production database into a scratch database on the remote test host and run the public app against it; verify the default units' first page, one small department, a rare topic chip, a common and a rare search word, and an article answer correctly, and time each query with `EXPLAIN ANALYZE`
- [ ] 6.2 Document the API, its limits and the owner's proxy, DNS and Cloudflare steps in `README.md`, and list the user-visible changes of design.md for the owner; wait for approval before pushing
- [ ] 6.3 Run `scripts/gate.sh`; verify it passes

## Workflow follow-up

- Deploy to the owner's host after the owner approves; the owner adds the DNS record, the proxy host and the cache rule.
- Archive the change (`openspec archive add-public-api --yes`), then run `openspec validate --all --strict`.
