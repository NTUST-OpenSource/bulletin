# Roadmap

The service is built as four OpenSpec changes, one active at a time (decision A3). Each entry
lists what is already settled, so the change can start from it instead of re-deciding. Decision
IDs refer to `docs/decisions.md`.

## 1. `add-collector` (active)

The registry of sites and boards, tiered polling, new-announcement detection, revisions,
withdrawal checks, the ten-year backfill, attachments, the events table, the tier admin CLI and
API, and the Compose deployment of the database and the worker. See
`openspec/changes/add-collector/`.

## 2. `add-rendering`

- An OpenAI-compatible client; the model, base URL and key come from configuration (E1).
- Before fixing the default model, compare gemma-4-E4B with one or two other local models on 50
  announcements: Discord validation pass rate, tag agreement with a hand-labelled set, deadline
  accuracy, time per article on the host.
- Renders every new announcement and those from the last year; older ones stay raw (E2).
- A rendition is tied to a revision and a prompt version, so a new revision or prompt renders
  again.
- Model input, measured on 59 cached pages (trafilatura kept 7 of 42 attachment names and lost
  over 40% of the text on 10 pages; this pipeline kept 36 of 42 at a median of 786 characters
  against 1,942 for the raw container):
  1. Take `.mpgdetail` and the `mptattach` module by selector, not with a generic extractor.
  2. Reduce the HTML to paragraphs, lists, tables, links, bold and images, then convert it to
     Markdown. Tables stay as pipe tables in the input; only the output avoids them.
  3. Replace each link and image with a placeholder (`L1`, `I1`, ...) and substitute the real
     URLs after the model answers, so the model never copies a URL. An unknown placeholder fails
     the attempt, and so does a dropped image: the rewrite keeps each image where the source has
     it.
  4. Attachments reach the frontend from stored data, not through the model.
  5. Ask for JSON constrained by a JSON schema (llama-server `response_format`).
  6. Reject a deadline whose date does not appear in the source text.
- Output: a rewritten title without bracketed tags, Markdown for Discord, a summary, a deadline
  date when the text states one, and tags from the fixed taxonomy (E3). Tags are stored per
  announcement with their source (model or manual).
- Validation pipeline (E4): wrap bare URLs as `<url>`, replace masked links whose text is a URL,
  then check with `@discord/markdown-wasm` in a Node subprocess; retry up to 3 times, then fall
  back to the title and the link.
- Open: llama-server is shared with tigerduck on the same host (port 40001). Decide whether
  bulletin runs its own instance or queues against the shared one, after measuring contention.

## 3. `add-public-api`

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

## 4. `add-web-frontend`

The owner approved the third prototype on 2026-11-15 (A5), with the last round of changes below.

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
  - The tab title is `bulletin. | 臺科大公布欄`.
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
- The xincord `ntust_announcements` plugin reads the events feed instead of scraping (H2).
