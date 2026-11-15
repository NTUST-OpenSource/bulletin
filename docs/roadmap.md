# Roadmap

The service is built as four OpenSpec changes, one active at a time (decision A3). Each entry
lists what is already settled, so the change can start from it instead of re-deciding. Decision
IDs refer to `docs/decisions.md`.

## 1. `add-collector` (archived 2026-11-15)

The registry of sites and boards, tiered polling, new-announcement detection, revisions,
withdrawal checks, the ten-year backfill, attachments, the events table, the tier admin CLI and
API, and the Compose deployment of the database and the worker. Specs under `openspec/specs/`, the
change under `openspec/changes/archive/2026-11-15-add-collector/`.

## 2. `add-rendering` (archived 2026-11-15)

Renditions of every new announcement and those of the last year with `gemini-4-hydrogen` (or an
OpenAI-compatible API), keys in turn, the model input reduced by selector with placeholders for
links and images, a versioned prompt and JSON schema, the deadline finder, the Discord Markdown
fixes and check in a Node subprocess, three attempts then a fallback, tags with their source and
the `rendered` event. Measured on 50 hand-labelled announcements: with `low` thinking all 50 pass,
at about 1.3 cents and 7 seconds each. Specs under `openspec/specs/`, the change under
`openspec/changes/archive/2026-11-15-add-rendering/`.

## 3. `add-public-api` (archived 2026-11-15)

- Same origin as the frontend, under `/api/v1/` on `bulletin.ntust.org` (F1).
- Read-only JSON, no authentication, cursor pagination, CORS `*` on reads (F2).
- Endpoints: announcements with filters (site, board, tag, query, time range), one announcement
  with its raw text and rendition, events after a cursor, boards, tags.
- `Cache-Control: max-age=60, stale-while-revalidate=600`; ETag from the latest event id; a
  Cloudflare cache rule for `/api/*` (F3).
- Stored attachment files by SHA-256, same origin so the frontend can preview them: inline
  `Content-Disposition` with the file's name, a sniffing-safe content type, immutable caching.
- Rate limiting in the application per client IP, on uncacheable endpoints; internal clients on
  `proxy-net` exempt (F4).
- tigerduck reads the events feed over `proxy-net` (H1, tigerduck-app/tigerduck-backend#248).

## 4. `add-web-frontend` (archived 2026-11-15)

The owner approved the third prototype on 2026-11-15 (A5), with the last round of changes below.
Specs under `openspec/specs/web-frontend/`, the change under
`openspec/changes/archive/2026-11-15-add-web-frontend/`.

- Svelte 5 + Vite static SPA over the public API (F5).
- Decided while reviewing the prototype:
  - A wider column than the prototype's 760 px.
  - The search box closes when focus leaves it; a query stays applied until cleared.
  - Every URL in an article is a link, also where the school's page shows it as plain text.
  - 已刪除 sits at the item's bottom right, muted, left of the main source.
  - Topic chips can be dragged into a new order on the home page as well as in the settings.
  - Closing an article (Esc, the close button, back) keeps the stream's scroll position.
  - Images stay where the school's page places them, in the rewrite too. When the attachments
    hold exactly one image, it is shown at the end of the article; the other attachments are
    listed as usual.
  - Attachments preview in the page, as club-aio's `FilePreview` does: a left click opens images
    (zoom, and arrows across the article's images), PDF in the browser's viewer and DOCX
    converted to sanitized HTML; the preview has a download button. A file name is a real link,
    so a right click offers the browser's save-link menu. Only stored files preview (the school
    sends no CORS headers); the others open the school's link.
  - The tab title is `bulletin. | 臺科公布欄`.
  - One stream for every category, no tabs; day headings stay pinned while scrolling.
  - A first visit asks for the viewer's department, then other units; the six P1 units are
    preselected. The stream shows followed units only; search covers every unit.
  - Hiding a board or unfollowing a unit is a context-menu action (right click, long press, the
    menu key), with undo.
  - Rewritten titles and summaries by default; the raw version sits in the article's menu.
    Images in the body are shown.
  - No deadline display and no action filter; topic chips whose order the viewer can change.
  - Infinite scroll with cursor pages; a poll every 5 minutes while the tab is visible, new items
    animate in without moving what the viewer is reading.
  - The settings end with: 內容轉寫自國立臺灣科技大學各單位網站，以原網頁內容為準
- Browser settings: theme, rendition or raw, followed units, hidden boards, topic order; export
  as copied JSON, a JSON download, or a link carrying the settings after `#`, applied at once only
  when the viewer never saved settings, otherwise after asking to overwrite all of them.
- Checked in a headless browser at desktop width and at 375 px.
- Icons: `@jis3r/icons` (movingicons.dev), the Svelte 5 port of lucide-animated, which is React
  only (F6).

## Later

- Sites that do not run RPage (issue #1).
- A web page for the tier admin; the CLI and API come first (B5).
- ~~The xincord `ntust_announcements` plugin reads the events feed instead of scraping (H2).~~
  Done in xincord on 2026-11-15 (`18b2f21`).
