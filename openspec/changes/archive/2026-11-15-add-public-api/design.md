# Design: add-public-api

## Context

See proposal.md for why. The service runs one process with two uvicorn listeners: the public one
on `bulletin-internal:8000` (proxy-net, behind nginx-proxy-manager and Cloudflare, answering
`https://bulletin.ntust.org/health` since 2026-11-15), and the admin one on the internal
`bulletin-admin` network. Both share one psycopg pool of at most 4 connections with the worker
and the renderer. The schema is in migrations 0001-0005: `announcement` (with `publisher`,
`cross_post_of`, `withdrawn_at`, `current_revision`, `current_rendition` and PGroonga indexes on
`title` and `body_text`), `placement`, `revision`, `attachment` (with `sha256` for stored files,
kept after the file is pruned), `rendition`, `tag` and the append-only `event`.

Decisions F1-F4 fix the origin, the shape, caching and rate limiting; D4 makes search cover all ten
years; D6 keeps stored files only within a year and makes links point at the school.
`add-web-frontend` runs beside this change (A3) and codes against this spec.

Production on 2026-11-15 holds 2,567 announcements: 402 without a list date (sites whose lists
show no dates), 61 cross-posts, 338 announcements on two or more boards, 60 placements on a board
of another site, 118 link items without an article id, 1,733 stored files, and 148 renditions
so far.

## Goals / Non-Goals

**Goals:**

- One stream order that every client pages through without gaps, also while announcements
  arrive.
- Most requests answered by Cloudflare or with a 304 after an index lookup.
- The frontend's needs in as few requests as possible: one per stream page, one per article.

**Non-Goals:**

- Writes, accounts, per-user state on the server. Settings live in the browser (F5).
- Push (SSE, webhooks), F2.
- Faceted counts. The frontend shows every topic chip in the viewer's order.
- A docs page. `openapi.json` is enough for developers, and a Swagger page would load scripts
  from a CDN on this origin.

## Decisions

### A mounted sub-application

`public_app` mounts a FastAPI app at `/api/v1` beside `/health` (and, in `add-web-frontend`, the
frontend's files at `/`). The sub-application has its own OpenAPI document at
`/api/v1/openapi.json`, no docs page, and the CORS middleware, which therefore never touches the
frontend's files. Routes declare GET only, so FastAPI answers 405 for other methods. Response
bodies are pydantic models, which also feed the OpenAPI document. An exception handler gives
every error `Cache-Control: no-store`.

The public app gets its own pool (`min_size=1`, `max_size=8`), so a burst of readers waits for
its own connections and never for the worker's or the renderer's.

### Stream day, stored

The stream sorts by day, and 402 announcements have no list date. Rendering already estimates
their day from the nearest dated article id (`date-undated-articles`), with a lateral join per
row. Sorting the whole stream that way would run it for every row on every page, so the day is
stored instead:

- An SQL function `stream_day(article_id, listed_on, first_seen_at)` holds the one definition:
  the list date, else the nearest dated neighbour's, else the first-seen day in Taipei.
- Migration 0006 adds `announcement.dated date NOT NULL`, filled by the function, and the index
  `announcement_stream (dated DESC, id DESC) WHERE cross_post_of IS NULL`. It also indexes
  `announcement (cross_post_of)` and `placement (announcement_id)`; the placement key starts with
  the board.
- A `BEFORE INSERT` trigger sets `dated` through the same function. `listed_on` is never updated
  after insert (detection changes only `placement`), so the collector's paths need no change.
- The nightly upkeep re-estimates rows without a list date (`UPDATE ... WHERE listed_on IS NULL
  AND dated IS DISTINCT FROM stream_day(...)`), so a neighbour stored later moves an estimate.
- `next_pending` reads `a.dated` and loses its lateral join; its scenarios keep passing.

A nightly move can shift an undated article between two pages a client reads, so it is seen
twice or not at all; clients de-duplicate by id. Only undated articles move, only overnight.

### Stream query

One function builds the query from the filters, driven by the boards when they are given:

```sql
WITH matched AS MATERIALIZED (                              -- only with q
  SELECT id FROM announcement
  WHERE (title &@ %(w1)s OR body_text &@ %(w1)s) AND ...  -- one condition per word
)
SELECT a.id ... FROM announcement a
WHERE a.cross_post_of IS NULL
  AND (a.dated, a.id) < (%(day)s, %(id)s)                   -- the cursor, when given
  AND a.id IN (SELECT COALESCE(c.cross_post_of, c.id)
               FROM placement p JOIN announcement c ON c.id = p.announcement_id
               WHERE p.site_id = ANY(%(sites)s)
                  OR (p.site_id, p.rcg) IN (SELECT * FROM unnest(%(board_sites)s, %(board_rcgs)s)))
  AND EXISTS (SELECT FROM tag t WHERE t.announcement_id = a.id
              AND t.dimension = %s AND t.tag = %s)          -- once per tag
  AND a.id IN (SELECT id FROM matched)
ORDER BY a.dated DESC, a.id DESC LIMIT %(limit)s + 1
```

The extra row says whether a next page exists. The page's tags, boards, renditions and units are
read in four queries over the page's ids, never one per item.

- The board subquery resolves to a set of ids first, so a small department or a rare topic
  costs a scan of its own placements, not of the whole stream index. Task 6.1 measures the
  default units, one small department, a rare topic chip and a rare search term.
- Search splits `q` on whitespace and matches each word with PGroonga's `&@`, a plain keyword
  match, so `-`, `OR` and parentheses have no meaning and no query can fail. `in=title` drops
  the `body_text` half. Materializing the matches keeps the planner from re-running the index
  scan per row.
- A cross-post's own text is searched only through its original; a copy rarely differs from it.

Measured on a copy of production (2,567 announcements, 2026-11-15) with `EXPLAIN ANALYZE`:
the default units' first page 1.8 ms, one small department 1.4 ms, a rare topic chip 1.2 ms, the
common word for "announcement" 35 ms, a rare word 1.4 ms. Through the SSH tunnel to the test
host, a stream page answered in 150 ms and a 304 in 26 ms.

The cursor is the last item's day and id, `YYYY-MM-DD.<id>` in URL-safe base64, opaque to
clients.

### Response shapes

Field names are snake case. A stream item:

```json
{
  "id": 2412,
  "site": 1017,
  "unit": "...",
  "url": "https://ece.ntust.edu.tw/p/406-1017-153702.php",
  "link_item": false,
  "title": "...",
  "publisher": null,
  "day": "2026-11-13",
  "listed_on": "2026-11-13",
  "first_seen_at": "2026-11-13T09:20:00Z",
  "withdrawn_at": null,
  "boards": ["1017-631"],
  "tags": {"topic": ["internships-and-jobs"], "audience": ["public", "staff"],
           "nature": ["action-required"], "source": ["on-campus"]},
  "rendition": {"title": "...", "summary": "...", "deadline": "2026-12-15"}
}
```

- `title` is always the school's; `rendition` is null without a rendition or with a fallback,
  whose title is the school's anyway. Clients choose which title to show.
- `unit` is the `site.unit` of the announcement's own site, null for a site outside the registry.
- `link_item` is true for announcements without an article id; their `url` is the link itself.
- `tags` are the stored tags, model and manual alike; every dimension is a list, so clients read
  all four alike. A fallback leaves earlier tags in place (tags spec).
- `boards` lists the boards of the announcement and of its cross-posts, own site's first.

One announcement adds:

```json
{
  "body_html": "<p>...</p>",
  "rendition": {"title": "...", "summary": "...", "deadline": null, "markdown": "..."},
  "attachments": [
    {"name": "schedule.pdf", "url": "https://...", "size": 122032,
     "file": "/api/v1/files/3f1c...e9/schedule.pdf"}
  ],
  "revisions": [{"fetched_at": "2026-11-13T09:21:04Z"}],
  "cross_posts": [{"id": 2419, "site": 1045, "url": "https://bulletin.ntust.edu.tw/p/..."}],
  "cross_post_of": null
}
```

`body_html` is raw, as stored, with the school's relative URLs and `data-src` images. `file` is a
relative URL with the name percent-encoded, present only while the file is in the store (one
`stat` per attachment).

A stream page is `{"items": [...], "next": "<cursor>" | null}`. An events page:

```json
{"events": [{"id": 121, "kind": "rendered", "notify": false, "late": false,
             "at": "2026-11-15T09:30:32Z", "announcement": {"id": 2412, "...": "..."}}],
 "last": 121}
```

Sites:

```json
[{"id": 1001, "host": "www.ceecs.ntust.edu.tw", "unit": "...", "kind": "academic",
  "college": "...", "boards": [{"key": "1001-1", "name": "...", "category": "announcement"}]}]
```

Tags:

```json
[{"id": "topic", "several": true, "tags": [{"id": "scholarships", "label": "..."}]},
 {"id": "nature", "several": false, "tags": [{"id": "action-required", "label": "..."}]}]
```

### Caching and ETags

Every ETag starts with the release, a token the service draws when it starts, so a deploy that
changes shapes never answers 304 for an old body; a restart costs each client one full answer.

- Stream and events: `W/"<release>.<max event id>.<max revision id>"`. A dependency reads both
  maxima (two index-only lookups) before the route runs and answers 304 at once on a match.
  The revision id covers the first revision, which records no event but sets the publisher.
- One announcement, sites and tags: a digest of the body. A single announcement is one primary-key
  read and its files change without events, so hashing the answer is both cheap and exact.

Stream answers can stay stale until the next event or revision after changes that record
neither: a new placement on another board, a tier change, the nightly re-estimates. Each is rare
or overnight, and events arrive every few minutes while the collector and renderer run.

Errors carry `no-store`, so Cloudflare never serves one reader's 429 or a passing 500 to others.
Cloudflare's cache rule for `/api/*` honours the origin's headers (F3), so popular stream pages,
such as the default units' first page, come from Cloudflare's edge.

### Stored files

The route is `/api/v1/files/{sha256}/{name:path}`, so a recorded name with `/` matches after
Starlette decodes `%2F`. It checks that the digest is 64 hex characters, that an attachment
records it under that name, and that `FileStore.path(digest)` exists, else 404; then it serves
the file with Starlette's `FileResponse`, which writes an RFC 6266 `filename*`. The type comes
from the name's extension; allow-listed types are inline, as roadmap section 3 says:

| Extensions | Type |
| --- | --- |
| pdf | application/pdf |
| png, jpg, jpeg, gif, webp | image/* |
| doc, docx, xls, xlsx, ppt, pptx, odt, ods, odp | the Office and OpenDocument types |
| zip, 7z, rar | the archive types |
| anything else | application/octet-stream, as an attachment |

Every file answer carries `X-Content-Type-Options: nosniff` and `Cache-Control: public,
max-age=31536000, immutable`; a digest's content never changes. No `Content-Security-Policy:
sandbox`: Chrome refuses to show a PDF under it, and nothing served inline runs script. Links in
the frontend still point at the school (D6); stored files serve previews and their download
button.

### Rate limiting

A dependency on the stream route applies when `q` is present: a sliding window of 30 searches per
60 seconds per client key, kept in memory (one process, D2), returning 429 with `Retry-After` in
whole seconds.

- The client is `request.client.host` after uvicorn's proxy-header handling, which walks
  `X-Forwarded-For` from the right and returns the first address outside `FORWARDED_ALLOW_IPS`,
  so addresses a client writes on the left are never taken. nginx-proxy-manager puts
  Cloudflare's `CF-Connecting-IP` rightmost, as compose.yaml already assumes.
- IPv6 clients are keyed by their /64, since one host can hold many addresses of its prefix.
- Exempt (F4): a request that carries no `X-Forwarded-For` and whose peer address is private.
  Everything that passes nginx-proxy-manager carries the header, so the exemption covers only
  clients on `proxy-net` talking to `bulletin-internal:8000` directly.
- The map holds at most 10,000 clients, dropping the least recently seen, so a flood of
  addresses cannot grow memory without bound.

The frontend debounces typing and waits for input methods to finish composing, so one search is
a few requests; 30 a minute leaves room for a person and stops a scraper.

### Unit data

`src/bulletin/units.json` lists sites in the order of the school's unit lists (`docs/survey.md`):
`{"site": 1045, "kind": "all"}`, `{"site": 1000, "kind": "admin"}`, `{"site": 1001, "kind":
"academic", "college": "..."}`. The unit names stay in the `site` table from the seed; this file
adds only kind, college and order. It is scaffolding, written once from the survey's topology and
reviewed by the owner; its test checks that every site with a polled board in
`seeds/boards.json` appears once.

### User-visible changes for review

- Paths: `/api/v1/announcements`, `/api/v1/announcements/{id}`, `/api/v1/events`,
  `/api/v1/sites`, `/api/v1/tags`, `/api/v1/files/{sha256}/{name}`, `/api/v1/openapi.json`.
- Parameters: `site`, `board`, `tag`, `from`, `to`, `q` (words, plain text, at most 10 words and
  100 characters), `in=title`, `cursor`, `limit`; `after` and `limit` on events.
- The fields under "Response shapes", the kind values `all`, `admin`, `academic`, the tag ids of
  `taxonomy.json` and the board keys `<site>-<board>`.
- Headers: the cache headers above, `no-store` on errors, CORS `*`, 304 answers.
- The search limit: 30 a minute per client, 429 with `Retry-After`.
- Error details in English: `invalid cursor`, `invalid limit`, `unknown tag <value>`, `query too
  long`, `no announcement <id>`, `no file`, `too many searches`.

## Risks / Trade-offs

- [The stored day drifts from the estimate between nights] -> Only undated articles move, and
  the nightly update runs in one statement over about 400 rows.
- [A trigger hides a write from the collector's code] -> The migration comment and the archive
  spec name it; the trigger only sets `dated`.
- [Search words that match much of the archive] -> PGroonga answers them in tens of milliseconds
  (D1); the rate limit bounds how many one client sends.
- [In-memory rate limits reset on restart] -> Acceptable for one process; a restart is rare and
  Cloudflare still caches repeated queries.
- [Plain-word search loses PGroonga's OR and exclusion] -> Nobody asked for operators; a
  `syntax` parameter can add them later without changing the default.

## Migration Plan

Migration 0006 runs on start like the others and fills `dated` for every row in one statement.
The deployment rebuilds the image. The DNS record and the nginx-proxy-manager host exist since
2026-11-15; the owner adds the Cloudflare cache rule for `/api/*` that respects origin headers.
Rolling back the code leaves the column and trigger, which the old code ignores.

## Open Questions

None.
