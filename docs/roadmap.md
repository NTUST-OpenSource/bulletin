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
- Output: Markdown for Discord, a summary, a deadline date when the text states one, and tags
  from the fixed taxonomy (E3). Tags are stored per announcement with their source (model or
  manual).
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
- Rate limiting in the application per client IP, on uncacheable endpoints; internal clients on
  `proxy-net` exempt (F4).
- tigerduck reads the events feed over `proxy-net` (H1, tigerduck-app/tigerduck-backend#248).

## 4. `add-web-frontend`

Starts only after the owner approves the high-fidelity prototype (A5).

- Svelte 5 + Vite static SPA over the public API (F5).
- Tabs for announcements and news; regulations and forms reachable through search (B8).
- Browser settings: theme, rendition or raw, hidden boards; export as copied JSON, a JSON
  download, or a link carrying the settings after `#`, applied at once only when the viewer never
  changed their own settings, otherwise after asking to overwrite all of them.
- Checked in a headless browser at desktop width and at 375 px.

## Later

- Sites that do not run RPage (issue #1).
- A web page for the tier admin; the CLI and API come first (B5).
- The xincord `ntust_announcements` plugin reads the events feed instead of scraping (H2).
