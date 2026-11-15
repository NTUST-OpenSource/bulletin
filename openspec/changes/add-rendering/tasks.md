# Tasks: add-rendering

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked
`xfail(strict=True)`, then implement it, remove the marker and commit with the gate green. Tests
never reach the network: the model's answers are fixtures, and the Discord check runs locally.

## 1. Foundations

- [x] 1.1 Add migration 0004 per design.md: `rendition`, `tag`, `announcement.current_rendition`, and `rendered` in the event kind check; verify the migration test applies it to an empty schema
- [ ] 1.2 Add `tools/discord-markdown/` (`package.json`, lock file pinning `@discord/markdown-wasm`, the line-per-input check script) and a Node setup step in CI; verify `npm ci` and one check run locally and in CI
- [x] 1.3 Check in Google's documentation which schema field and thinking setting `gemini-4-hydrogen` takes, and record one Gemini answer and one OpenAI-format answer as fixtures from the documented shapes; verify each fixture names its source

## 2. Event log

- [x] 2.1 Commit the xfail test for "Events" (event-log, the rendered event); verify it fails for the expected reason and the gate stays green
- [x] 2.2 Implement "Events" and remove the marker; verify its scenarios pass and the gate is green
- [x] 2.3 Commit the xfail test for "Notify flag" (event-log, the rendered event); verify it fails for the expected reason and the gate stays green
- [x] 2.4 Implement "Notify flag" and remove the marker; verify its scenarios pass and the gate is green

## 3. Tags

- [x] 3.1 Commit the xfail test for "Fixed taxonomy" (tags); verify it fails for the expected reason and the gate stays green
- [x] 3.2 Implement "Fixed taxonomy" with `taxonomy.json` (E3 ids and labels) and remove the marker; verify its scenarios pass and the gate is green
- [x] 3.3 Commit the xfail test for "Tags with their source" (tags); verify it fails for the expected reason and the gate stays green
- [x] 3.4 Implement "Tags with their source" and remove the marker; verify its scenarios pass and the gate is green

## 4. Model input and answer checks

- [x] 4.1 Commit the xfail test for "Model input" (rendering) over the recorded article fixture; verify it fails for the expected reason and the gate stays green
- [x] 4.2 Implement "Model input" (the reducer, the Markdown converter, placeholders) and remove the marker; verify its scenarios pass and the gate is green
- [x] 4.3 Commit the xfail test for "Placeholders put back" (rendering); verify it fails for the expected reason and the gate stays green
- [x] 4.4 Implement "Placeholders put back" and remove the marker; verify its scenarios pass and the gate is green
- [x] 4.5 Commit the xfail test for "Structured answer" (rendering); verify it fails for the expected reason and the gate stays green
- [x] 4.6 Implement "Structured answer" (the prompt, its JSON schema, `PROMPT_VERSION` with the digest test) and remove the marker; verify its scenarios pass and the gate is green
- [x] 4.7 Commit the xfail test for "Deadlines from the text" (rendering); verify it fails for the expected reason and the gate stays green
- [x] 4.8 Implement "Deadlines from the text" (the date finder) and remove the marker; verify its scenarios pass and the gate is green
- [x] 4.9 Commit the xfail test for "Discord Markdown" (rendering); verify it fails for the expected reason and the gate stays green
- [x] 4.10 Implement "Discord Markdown" (the fixes and the Node subprocess) and remove the marker; verify its scenarios pass and the gate is green

## 5. Model client and the rendering loop

- [x] 5.1 Commit the xfail test for "Model configuration" (rendering); verify it fails for the expected reason and the gate stays green
- [x] 5.2 Implement "Model configuration" (settings, the Gemini and OpenAI-compatible client) and remove the marker; verify its scenarios pass and the gate is green
- [x] 5.3 Commit the xfail test for "Keys in turn" (rendering); verify it fails for the expected reason and the gate stays green
- [x] 5.4 Implement "Keys in turn" (the ported KeyRing, resting keys, hidden keys) and remove the marker; verify its scenarios pass and the gate is green
- [x] 5.5 Commit the xfail test for "Attempts and fallback" (rendering); verify it fails for the expected reason and the gate stays green
- [ ] 5.6 Implement "Attempts and fallback" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.7 Commit the xfail test for "What gets rendered" (rendering); verify it fails for the expected reason and the gate stays green
- [ ] 5.8 Implement "What gets rendered" (the pick query) and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.9 Commit the xfail test for "Renditions follow revisions" (rendering); verify it fails for the expected reason and the gate stays green
- [ ] 5.10 Implement "Renditions follow revisions" and remove the marker; verify its scenarios pass and the gate is green
- [ ] 5.11 Run the rendering loop in `bulletin serve` beside the worker, and make the ten-year prune delete renditions and tags; verify with the service test and a prune test

## 6. Image and measurement

- [ ] 6.1 Add the Node build stage and binary to the Dockerfile; verify on the remote test host that the image builds and the Discord check answers inside the container
- [ ] 6.2 Draft tags and deadlines for 50 corpus announcements and have the owner correct them; verify the labelled set is saved outside the repository with the corpus
- [ ] 6.3 Add `scripts/measure_rendering.py` and run it with thinking `low` and with the model's default; verify the report (pass rate, tag agreement, deadline accuracy, requests and tokens per article) is given to the owner

## 7. Verification

- [ ] 7.1 Add an end-to-end test: a stored announcement, a fake model answer, the rendition, its tags and the published then rendered events; verify it passes
- [ ] 7.2 Document the settings in `README.md` and list the user-visible changes of design.md for the owner; wait for approval before pushing
- [ ] 7.3 Run `scripts/gate.sh`; verify it passes

## Workflow follow-up

- Deploy to the owner's host with the keys of the xincord bot's configuration in `.env`, after the owner approves.
- Archive the change (`openspec archive add-rendering --yes`), then run `openspec validate --all --strict`.
