# Tasks: add-not-found-and-icons

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing tests marked
`xfail(strict=True)` or to fail, then implement it, remove the markers and commit with the gate
green.

## 1. Unknown paths

- [x] 1.1 Commit the server tests (an unknown path answers 404 with the page; the API and built files keep theirs) and the page test (the not-found view, no announcements, no picker, the link back), marked to fail; verify they fail for the expected reason and the gate stays green
- [x] 1.2 Answer unknown paths with the page in `public.py`, mount `NotFound.svelte` for them in `main.ts`, and remove the markers; verify the tests pass at both widths and the gate is green

## 2. The site's icon

- [x] 2.1 Commit the server test (the three icons served and cached for a day) and the page test (the page links them), marked to fail; verify they fail for the expected reason and the gate stays green
- [x] 2.2 Add the icons under `web/public/`, link them in `index.html`, serve them in `public.py`, and remove the markers; verify the tests pass and the gate is green
