# Tasks: add-web-frontend

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked as an
expected failure (`test.fails` in Vitest, `test.fail()` in Playwright), then implement it, remove
the marker and commit with the gate green. Playwright answers `/api/v1` from fixtures in the
shapes of the `public-api` spec.

## 1. Foundations

- [x] 1.1 Scaffold `web/` (Svelte 5, TypeScript strict, Vite, Vitest, Playwright, `@jis3r/icons`, the font package) with a smoke test that the app mounts; verify `bun run check`, `bun run test` and `bun run build` pass
- [x] 1.2 Add the frontend to `scripts/gate.sh` (bun install --frozen-lockfile, svelte-check, Vitest with 85% coverage of `lib/`, build) and a Playwright job to CI; verify the gate passes locally and the CI job runs
- [x] 1.3 Record API fixtures from production renditions in the `public-api` shapes (stream pages, articles with stored and unstored files, sites, tags) plus the cases of design.md (extreme lengths, two followed boards, a cross-post, a link item); verify each fixture parses against the frontend's API types
- [x] 1.4 Port the prototype's tokens, light and dark, and its base layout into `styles/` and `App.svelte`; verify against the prototype's screenshots at 1280 px and 375 px

## 2. Serving

- [x] 2.1 Commit the xfail test for "The page" (web-frontend): pytest for the mount, cache headers, `frame-ancestors` and the `/a/{id}` fallback, Playwright for the tab title and a stored PDF under the built page's policy (full Chromium, `channel: "chromium"`); verify it fails for the expected reason and the gate stays green
- [x] 2.2 Implement "The page" (the static mount in `public_app` on top of add-public-api task 1.2, the build-time policy, the Bun stage in the Dockerfile) and remove the markers; verify its scenarios pass, the gate is green and the image builds on the remote test host

## 3. Settings

- [x] 3.1 Commit the xfail test for "Settings" (web-frontend); verify it fails for the expected reason and the gate stays green
- [x] 3.2 Implement "Settings" (`lib/settings.ts`, the settings sheet, themes) and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.3 Commit the xfail test for "Settings export and import" (web-frontend); verify it fails for the expected reason and the gate stays green
- [x] 3.4 Implement "Settings export and import" and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.5 Commit the xfail test for "First visit" (web-frontend); verify it fails for the expected reason and the gate stays green
- [x] 3.6 Implement "First visit" (the two-step unit picker) and remove the marker; verify its scenarios pass and the gate is green

## 4. Stream

- [x] 4.1 Commit the xfail test for "The stream" (web-frontend); verify it fails for the expected reason and the gate stays green
- [x] 4.2 Implement "The stream" (the query from settings, day sections, items) and remove the marker; verify its scenarios pass and the gate is green
- [x] 4.3 Commit the xfail test for "Topic chips and unit filter" (web-frontend); verify it fails for the expected reason and the gate stays green
- [x] 4.4 Implement "Topic chips and unit filter" (dragging and keyboard reordering) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.5 Commit the xfail test for "Paging and new announcements" (web-frontend); verify it fails for the expected reason and the gate stays green
- [ ] 4.6 Implement "Paging and new announcements" (the cursor, de-duplication, the uncached poll, merging by order, the scroll correction) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 4.7 Commit the xfail test for "Context menu" (web-frontend); verify it fails for the expected reason and the gate stays green
- [ ] 4.8 Implement "Context menu" (entries per board and unit, bottom sheet, long press, undo) and remove the marker; verify its scenarios pass and the gate is green

## 5. Articles and search

- [ ] 5.1 Commit the xfail test for "Article view" (web-frontend); verify it fails for the expected reason and the gate stays green
- [ ] 5.2 Implement "Article view" (`lib/markdown.ts`, `lib/raw.ts`, paths, cross-posts and link items, history and scroll position) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.3 Commit the xfail test for "Attachments" (web-frontend); verify it fails for the expected reason and the gate stays green
- [ ] 5.4 Implement "Attachments" (school links, image, PDF and DOCX previews, the new-tab PDF fallback) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.5 Commit the xfail test for "Search" (web-frontend); verify it fails for the expected reason and the gate stays green
- [ ] 5.6 Implement "Search" (the debounce, input methods, filters kept) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.7 Commit the xfail test for "Failures" (web-frontend); verify it fails for the expected reason and the gate stays green
- [ ] 5.8 Implement "Failures" and remove the marker; verify its scenarios pass and the gate is green

## 6. Verification

- [ ] 6.1 Commit the xfail test for "Narrow screens and long text" (web-frontend) over every view at 375 px and 1280 px; verify it fails for the expected reason and the gate stays green
- [ ] 6.2 Fix what it finds and remove the marker; verify its scenarios pass and the gate is green
- [ ] 6.3 Run the built page against the deployed API in headless Chromium at 1280 px and 375 px, light and dark, and compare it with the prototype; verify the screenshots are given to the owner, ask the owner to open a stored PDF on an iPhone and an Android phone, and close the browser and servers afterwards
- [ ] 6.4 List the user-visible changes of design.md for the owner; wait for approval before pushing
- [ ] 6.5 Run `scripts/gate.sh`; verify it passes

## Workflow follow-up

- Deploy to the owner's host after the owner approves, once `add-public-api` is deployed.
- Archive the change (`openspec archive add-web-frontend --yes`), then run `openspec validate --all --strict`.
