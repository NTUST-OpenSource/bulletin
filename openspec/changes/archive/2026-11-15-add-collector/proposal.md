# Proposal: add-collector

## Why

NTUST units post announcements on 445 boards across 64 sites, and the school takes them down
without notice. Before anything can be rewritten, searched or served, bulletin needs its own
complete archive, fed by polling that stays gentle with the school's WAF and that tells first
publications from late discoveries, so clients never re-announce old posts.

## What Changes

- A board registry seeded from `seeds/boards.json`: every discovered board, off and excluded ones
  included, with its category and tier, and a monthly re-discovery that adds new boards as off
  and pending review.
- Tiered polling of each board's static list page 1 through one global, rate-limited queue, with
  unchanged-page skipping, paging on bursts, failure backoff and a poll log.
- Detection of new announcements by (site, article id), the notify rule (backfilled boards, the
  frontier rule otherwise) and cross-post linking.
- An archive of announcements, placements and revisions with raw HTML, re-checks at 1, 3, 7 and
  30 days, withdrawal confirmed by the article's redirect, and ten-year retention.
- An append-only event log (published, revised, withdrawn, restored) with a notify flag, for the
  public API and tigerduck to follow later.
- A nightly ten-year backfill per board.
- Attachments: name and URL always; files under 5 MB from school hosts stored for one year.
- Tier administration through a CLI and an admin API on an internal network, with an audit log.
- The repository scaffolding, the gate, and a Compose deployment of the database, the worker and
  the app.

Out of scope: model rendering and tags (`add-rendering`), the public read API and its caching and
rate limiting (`add-public-api`), the web frontend (`add-web-frontend`), sites that do not run
RPage (issue #1), the tigerduck switch (tigerduck-app/tigerduck-backend#248) and the xincord
plugin.

## Capabilities

### New Capabilities

- `board-registry`: the sites and boards bulletin knows, their categories and tiers, and
  re-discovery.
- `tier-admin`: changing tiers, reviewing new boards and the audit log, through the CLI and the
  admin API.
- `polling`: when and how boards are fetched, within the request budget.
- `detection`: deciding which list items are new announcements and which are notify-worthy.
- `archive`: announcements, placements, revisions, withdrawal and retention.
- `event-log`: the ordered record of changes to announcements that clients follow.
- `backfill`: recording every board's announcements of the last ten years.
- `attachments`: attachment records and the one-year file store.

### Modified Capabilities

None.

## Impact

- New Python 3.14 project (uv, FastAPI, psycopg 3) with a worker and an app process.
- PostgreSQL 18 with PGroonga (`groonga/pgroonga`, Alpine, PostgreSQL 18).
- A Docker Compose project `bulletin` on the owner's host, joining the external `proxy-net`.
- Outbound traffic to `*.ntust.edu.tw`: about 2,214 requests and 21 MB a day once running, plus
  about two weeks of nightly backfill.
