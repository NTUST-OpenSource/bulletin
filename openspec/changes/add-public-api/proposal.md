# Proposal: add-public-api

## Why

The collector keeps every announcement and the renderer rewrites them, but nothing outside the
database can read either. The web frontend, tigerduck (H1), the xincord plugin (H2) and anyone
else who wants NTUST's announcements need one read-only API on `bulletin.ntust.org`, cacheable
enough that a burst of readers never reaches the database.

## What Changes

- A read-only JSON API under `/api/v1/` on the public listener (F1, F2): the announcement
  stream with filters and search, one announcement with its raw text, rendition, tags,
  attachments and revisions, the events feed after a cursor, the sites with their units and
  boards, and the tag taxonomy.
- Cursor pagination over a stable order, newest day first. Each announcement has one stream day:
  the list date, else the day estimated from the nearest dated article, else the day it was first
  seen. The estimate rendering already uses becomes a stored date, kept by the collector, so the
  stream and the renderer share it.
- Cross-posts fold into the announcement they copy: the stream lists it once, with every board it
  appears on.
- HTTP caching (F3): `Cache-Control: max-age=60, stale-while-revalidate=600`, ETags from the
  release and the latest event and revision ids (lists) or the content (the rest), 304 answers,
  errors never cached, CORS `*` on reads.
- Stored attachment files by SHA-256 and recorded name, same origin, with a content type from an
  allow-list, `nosniff` and immutable caching.
- Search by plain words, titles and text or titles only, over all ten years (D4).
- Rate limiting per client IP on search (F4), internal clients on `proxy-net` exempt.
- The units' kind (school-wide, administrative, academic) and college, in the school's order,
  as package data, for the frontend's unit picker.
- An OpenAPI document at `/api/v1/openapi.json`.

Out of scope: the frontend itself (`add-web-frontend`), serving the frontend's files (that change
mounts them on the same listener), writes of any kind, authentication, SSE or webhooks (F2),
the Cloudflare cache rule (configured by the owner outside the repository), a docs page, and
moving tigerduck and xincord to the feed (H1, H2: their own repositories).

## Capabilities

### New Capabilities

- `public-api`: the read-only endpoints, their filters, pagination, response shapes, caching,
  CORS, stored files and rate limiting.

### Modified Capabilities

- `archive`: each announcement keeps a stream day, set when it is stored and re-estimated
  nightly while it has no list date.
- `rendering`: "What gets rendered" reads the stored stream day instead of estimating its own.

## Impact

- Code: `bulletin.web.public` grows the API; a query module for the stream and search; the
  rendering pick query shrinks to read the stored day.
- Database: migration 0006 adds `announcement.dated`, fills it, and indexes the stream order.
- Data: `src/bulletin/units.json`, the units' kind and college by site id, from the school's
  unit lists (`docs/survey.md`).
- Service: the public listener gets a database connection pool of its own, so readers cannot
  starve the worker and the renderer.
- Deployment: no new container. The DNS record and the nginx-proxy-manager host for
  `bulletin-internal:8000` exist since 2026-11-15; the owner adds the Cloudflare cache rule for
  `/api/*`.
- Traffic: none to the school. Images in announcements stay on the school's hosts, which allow
  other sites to show them.
