# Design: add-collector

## Context

See proposal.md for why. The repository holds docs and `seeds/boards.json` only; this change
creates the Python project. The constraints come from the school's CMS and network
(`docs/pitfalls.md`) and from decisions B1-B11, C1-C5, D1-D7, G1 and G2 in `docs/decisions.md`.
The xincord plugin `ntust_announcements` already parses RPage list and article pages
(`pages.py`, `markup.py`, stdlib `html.parser`) and builds the NTUST TLS context
(`ntust_tls`, with the TWCA intermediate); this change ports both instead of rewriting them.

## Goals / Non-Goals

**Goals:**

- A complete, correct archive: no announcement lost, none announced twice or late.
- A load on the school that is bounded by construction, not by convention.
- Every operator action possible from a shell in the container.

**Non-Goals:**

- More than one worker or host. The request budget is global and serial (B4), so parallelism buys
  nothing.
- Serving announcements to the public; this change only exposes `/health` publicly.
- Holiday calendars: office hours are weekdays 08:00-18:00 Asia/Taipei, holidays included.

## Decisions

### One process, two listeners

One Python process runs the FastAPI app and the worker loop in one event loop: the public listener
(`/health` now, `/api/v1/` in `add-public-api`) and the admin listener. A separate worker container
was considered; at one request every 2 seconds the loop is idle almost all the time, and one
process means one image, one health check and one place for configuration. Split it if the public
API's load ever delays polls.

### Scheduling in the database

`board.next_poll_at` holds when each board is due; `job.run_after` holds everything else. The worker
loop picks the single most urgent item in the queue order of the polling spec, sends it, records it
in `poll`, then sleeps `2 s + random(0, 1 s)` after the response. A WAF answer (406) sets a pause
time that the loop honours before anything else. Jobs are claimed with
`SELECT ... FOR UPDATE SKIP LOCKED` (D3), so a CLI command that runs a job by hand cannot double it.

A tier change writes `board.tier` and recomputes `next_poll_at` from `last_polled_at` and the new
interval in the same transaction, which is all "the next scheduling pass" needs.

### HTTP

aiohttp, as in the ported xincord code, with automatic redirects off: a withdrawal is a 302 the
service must see. The NTUST TLS context (`ntust_tls` ported with its certificate) is used for
`*.ntust.edu.tw` only. Attachment sizes come from a one-byte range GET for `/var/file/` links and
from the headers of a streamed GET for `downloadfile` links, which ignore `Range`; the connection
is closed before the body when the file is not stored. User-Agent: `bulletin/<version> (+https://bulletin.ntust.org)`. Tests use
recorded pages and a fake transport; nothing in the test suite reaches the network.

### Identity comes from the link

Boards list other sites' articles (`docs/pitfalls.md`), and an article id requested under the
wrong site redirects home exactly like a withdrawal. The list parser therefore returns each item's
host, site, article id and board from its href; an announcement is keyed by the href's site and
id, the polled board only gets a placement, and article fetches and re-checks use the stored host
and site. Items whose href is not a `406` page are link entries keyed by the polled board's site
and URL. The ported xincord parser builds article URLs from the board's site and must be changed.

### Detection state is per board

Decision C2 speaks of sites. This design keeps the backfilled state per board, because B6 turns
boards on one at a time and a board turned on must fall back to the frontier rule while its
siblings stay backfilled. The cost: an article listed for years on a never-backfilled board of a
site, then placed on a backfilled board, reads as a first publication. Placements across boards of
one site are rare, and cross-post linking catches the common case on another site.

### Event order

Events get their ids from a sequence, and each transaction that records events first takes a
transaction-scoped advisory lock (`pg_advisory_xact_lock`), so ids are taken and committed in the
same order and a reader resuming from its last id never skips a late-committing lower id. A
reader-side lag or `pg_snapshot_xmin` filtering would also work but pushes the problem onto every
client.

### Schema

PostgreSQL 18 with PGroonga; migrations are numbered SQL files applied at start in one transaction
each, recorded in `schema_migration`. No ORM: psycopg 3 with typed row factories. Alembic was
considered and rejected as weight without an ORM.

| Table | Key columns |
| ----- | ----------- |
| `site` | `site_id` PK, `host`, `unit` |
| `board` | (`site_id`, `rcg`) PK, `name`, `category`, `tier` (`P1`-`P4`, `off`), `pending_review`, `found_at`, `fingerprint`, `last_polled_at`, `next_poll_at`, `failures`, `backfill_page`, `backfilled_at` |
| `tier_change` | `id`, `site_id`, `rcg`, `old_tier`, `new_tier`, `by`, `at` |
| `announcement` | `id` identity, `site_id` and `host` (from the link), `article_id` (nullable), `link_url`, `title`, `publisher`, `listed_on`, `first_seen_at`, `late`, `cross_post_of`, `withdrawn_at`, `body_text` (latest revision, indexed), `current_revision`; unique (`site_id`, `article_id`) and (`site_id`, `link_url`) |
| `placement` | (`site_id`, `rcg`, `announcement_id`) PK, `listed_on`, `first_seen_at`, `last_seen_at`, `last_position` |
| `revision` | `id`, `announcement_id`, `fetched_at`, `title`, `body_html`, `body_text`, `content_hash` |
| `attachment` | `id`, `revision_id`, `name`, `url`, `origin` (`module`, `body`), `size`, `sha256` (set while a copy exists or existed) |
| `event` | `id` from a sequence, `announcement_id`, `kind`, `notify`, `late`, `at` |
| `job` | `id`, `kind` (`article`, `recheck`, `attachment`, `discovery`, `backfill`), `ref`, `run_after`, `attempts`, `last_error` |
| `poll` | `id`, `purpose`, `site_id`, `rcg`, `at`, `status`, `bytes`, `ms`, `changed`, `new_ids` |
| `frontier` | `at`, `max_article_id` |

Indexes: PGroonga on `announcement.title` and `announcement.body_text` (default bigram tokenizer,
`NormalizerAuto`); B-tree on `announcement(listed_on)`, `event(id)` and `board(next_poll_at)`.

Stored attachment files live on a volume at `files/<first two hex>/<sha256>`; the nightly prune
deletes files that no attachment of an announcement from the last 365 days references (D6).

### Tests and the database

Storage tests need PostgreSQL with PGroonga (AGENTS.md). They read `BULLETIN_TEST_DATABASE_URL`
and create a throwaway schema per test session. The owner's laptop runs no Docker, so locally the
URL points at a PGroonga container on the remote test host; CI runs one as a service container.
When the variable is unset the storage tests skip, and the gate fails on any skip when
`BULLETIN_REQUIRE_DB=1`, which CI sets.

### Deployment

Compose project `bulletin` on the owner's host, following `~/selfhost/Docker/tigerduck-backend`
(G1):

- `db`: `groonga/pgroonga` Alpine PostgreSQL 18 image, pinned by digest, on `bulletin-db`
  (`internal: true`, no outbound NAT); data in a named volume.
- `app`: `container_name: bulletin-internal`, on `bulletin-db`, the external `proxy-net` (public
  listener; also the egress to the school) and `bulletin-admin` (`internal: true`) with the alias
  `bulletin-internal-admin`, to which the admin listener binds, so nothing on `proxy-net` reaches
  it. No published ports. `env_file: .env` (database URL, admin tokens), the files volume,
  `extra_hosts: host.docker.internal:host-gateway` for the model server later, and
  `FORWARDED_ALLOW_IPS: 172.16.0.0/12,192.168.0.0/16`. Health check on `/health`.
- nginx-proxy-manager routes `bulletin.ntust.org` to `bulletin-internal` once `add-public-api`
  serves something; Cloudflare and NPM terminate TLS, so there is no proxy in this project.
- The CLI runs as `docker compose exec app bulletin <command>` and works on the database directly
  through the same service functions as the admin API.

Rate limiting (F4) and the Cloudflare cache rule (F3) belong to `add-public-api`.

### Capacity

- Polling: about 2,214 requests and 21 MB a day with the seeded tiers.
- Articles: about 33 new a day across the school; with re-checks, about 170 article requests a
  day.
- Backfill: about 60,000 announcements over ten years, so about 60,000 article pages and some 6,000
  list pages, the deep ones taking 5-8 s each on the server. At one request every 2.5 s inside a
  five-hour night, about 6,700 requests a night: roughly two weeks.
- Storage: database near 2 GB after ten years including the PGroonga indexes (25,000 documents
  with 56 MB of text grew the database by 233 MB); stored files near 2 GB, bounded by the one-year
  window: 44% of articles carry attachments, about 330 KB of files under 5 MB per article.
- Attachments: about 25 downloads a day for new articles; backfilling the last year's files adds
  about 4,000 requests.

### User-visible changes for review

- CLI: `bulletin boards [--tier T] [--pending]`, `bulletin tier set <site>-<board> <P1|P2|P3|P4|off>
  [--by NAME]`, `bulletin tier history <site>-<board>`, `bulletin review accept <site>-<board>
  [--tier T] [--category C]`, `bulletin discover` (queue a re-discovery now).
- Admin API on the admin listener: `GET /admin/boards`, `PUT /admin/boards/{site}-{board}/tier`,
  `GET /admin/boards/{site}-{board}/tier-changes`, `POST /admin/boards/{site}-{board}/review`.
- The User-Agent the school sees: `bulletin/<version> (+https://bulletin.ntust.org)`.
- `bulletin serve`, the container's command: the public listener on `:8000`, the admin listener
  on `bulletin-internal-admin:8001` and the worker in one process.
- Settings: `POSTGRES_PASSWORD` and `BULLETIN_ADMIN_TOKENS` (comma-separated `name:token` pairs,
  tokens of 32 or more characters) in `.env`; `BULLETIN_DATABASE_URL`, `BULLETIN_ADMIN_HOST`,
  `BULLETIN_FILES` and `BULLETIN_SEED` with defaults from the image and `compose.yaml`.

## Risks / Trade-offs

- [A withdrawal during a backfill walk shifts later items one place forward, so one item can be
  skipped] → the skipped id, if a poll ever lists it again, reads as a first publication: at
  worst one wrong notification per withdrawal during a walk.
- [The WAF blocks the host's address] → the queue pauses on 406, the User-Agent names the service,
  and the budget keeps the load near one request every 40 seconds outside backfill.
- [The school changes its page markup] → parsing failures surface as polls with zero items; a
  board whose page 1 parses to nothing three times in a row is logged as an error.
- [The PGroonga image tag moves] → pinned by digest; Renovate proposes updates.
- [Boards without list dates] → the frontier rule falls back to ids alone; such boards are P4 or
  off today.
- [The TWCA intermediate expires on 2030-10-16] → a test fails once it is less than a year from
  expiry.

## Migration Plan

1. Create `.env` from `.env.example` on the host, then `docker compose up -d`.
2. The first start applies migrations and imports the seed; the first polls record frontiers and
   announce nothing (detection, first start).
3. Backfill runs nightly from the first night; boards switch to the backfilled rule one by one.
4. Rollback: `docker compose down`; the volumes keep the archive.

## Open Questions

- Whether the office-hours window should skip school holidays. Deferrable: it only changes the
  interval table.
