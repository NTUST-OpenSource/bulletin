# Proposal: add-not-found-and-icons

## Why

A mistyped address gets FastAPI's JSON `{"detail":"Not Found"}`, and the site has no icon, so
every browser's request for `/favicon.ico` is a 404 too (seen in production on 2026-11-16). The
owner approved both designs in the prototype on 2026-11-16.

## What Changes

- Any path the page does not know answers 404 with the page itself, which shows a not-found view:
  a large 4●4 whose ball, the accent ball of `bulletin.`, drops in and bounces, a heading and a
  link back to the stream. The view loads no announcements and shows no first-visit picker. The
  API and the built files keep their own 404 answers.
- The site's icon: the b of `bulletin.` with the accent ball in its counter, drawn from Bricolage
  Grotesque's own outline. An SVG follows the system's light or dark mode; a 32-pixel ICO and a
  180-pixel home-screen PNG cover browsers without SVG icons.

Out of scope: the header's load animation, which waits for its own approval.

## Capabilities

### Modified Capabilities

- `web-frontend`: adds "Unknown paths" and "The site's icon".

## Impact

- `src/bulletin/web/public.py` and `tests/test_web_page.py`.
- `web/src/main.ts`, a new `web/src/NotFound.svelte`, `web/src/lang/zh-TW.ts`, `web/index.html`,
  `web/public/` and a new `web/tests/not-found.spec.ts`.
