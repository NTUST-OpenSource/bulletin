# Tasks: rename-site-title

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked to fail,
then implement it, remove the marker and commit with the gate green.

## 1. The page

- [ ] 1.1 Commit the tab-title test expecting the new name, marked to fail; verify it fails for the expected reason and the gate stays green
- [ ] 1.2 Rename the site in `web/index.html` and `docs/roadmap.md`, and remove the marker; verify the test passes and the gate is green
