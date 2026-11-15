# Proposal: add-web-frontend

## Why

Students and staff read NTUST's announcements on dozens of unit websites, each with its own
layout and quality. bulletin now keeps and rewrites all of them; a web page at
`bulletin.ntust.org` turns that into one stream a reader follows by unit, reads in a consistent
form, and searches across ten years. The owner approved the third high-fidelity prototype on
2026-11-15 (A5); this change builds it on the public API.

## What Changes

- A Svelte 5 + Vite static single-page app under `web/` (F5), served by the public listener at
  `/` beside `/api/v1/`, and built into the image.
- One stream of the followed units' announcements, newest day first, with pinned day headings,
  topic chips in the viewer's order (draggable), a unit filter, infinite scroll by cursor, and a
  poll every 5 minutes while the tab is visible that animates new items in without moving what
  the viewer is reading.
- The article view: the rewrite by default and the school's version from its menu, images where
  the school placed them, every URL a link, attachments with in-page preview of stored files
  (images, PDF, DOCX), the withdrawal and tags shown; closing it keeps the stream's position.
- Search across every unit, titles and text or titles only, from the header.
- A first-visit picker for the viewer's department and other units, with six units preselected;
  a context menu (right click, long press, the menu key) to hide a board or unfollow a unit, with
  undo.
- Settings kept in the browser: theme, rewrite or raw, followed units, hidden boards, topic
  order; export as copied JSON, a JSON download or a link, and import from any of them (F5).
- Animated icons from `@jis3r/icons` (F6).
- Frontend checks in the gate (type check, unit tests, build) and headless-browser tests at
  desktop width and 375 px in CI.

Out of scope: accounts and server-side settings, notifications and push, deadline display and
action filters (roadmap section 4), offline use, languages other than Traditional Chinese, the
tier admin page (B5), and the API itself (`add-public-api`).

## Capabilities

### New Capabilities

- `web-frontend`: the stream, article view, search, unit picker, context menu, settings and
  their export and import, as the reader sees them.

### Modified Capabilities

None. The frontend reads the `public-api` capability of `add-public-api` as specified there.

## Impact

- Code: `web/` (Svelte 5, TypeScript, Vite, Vitest, Playwright) with its own `package.json` and
  lock file; the public app mounts the built files with a fallback to `index.html` for article
  paths.
- Image: a Node build stage for `web/`; the runtime image gains the static files only.
- Gate and CI: `scripts/gate.sh` runs the frontend's type check, unit tests and build; CI adds a
  Playwright job.
- Dependencies (installed with Bun): `svelte`, `vite`, `@sveltejs/vite-plugin-svelte`, `typescript`,
  `svelte-check`, `@jis3r/icons`, `dompurify`, `mammoth` (loaded only for a DOCX preview),
  `@fontsource-variable/bricolage-grotesque`, `vitest`, `@playwright/test`.
- Data: the reader's settings stay in `localStorage`; nothing about readers reaches the server
  beyond the API requests.
