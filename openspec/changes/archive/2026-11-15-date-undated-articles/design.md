# Design: date-undated-articles

## Context

See proposal.md. `next_pending` dates an article by `COALESCE(listed_on, first_seen_at)` in the
one-year filter and the order, and `Pending.dated` by the list date or the day of first sight in
Taipei. The backfill stores old articles today, so their first sight says nothing about their age.

## Decisions

### The nearest dated article

Article ids are one sequence across NTUST's sites and grow with time; an id is given when a
draft is created, so a draft published weeks later carries an older id (docs/pitfalls.md).
Measured on production on 2026-11-15, estimating each of the 1,613 dated articles from its
nearest other dated article: median error 0 days, 90th percentile 30 days, 8% off by more than
60 days. Most of the tail is recycled articles, old ids listed again under a new date, which is an
error of the measured article rather than of the estimate. The median of the five nearest did
barely better (7.7% over 60 days), so the nearest one is used.

The day is computed in the pick query, not stored: a later poll can add dated neighbours, and the
query stays the one place that decides. For each undated candidate a lateral subquery takes the
nearest dated article above and below by `article_id`, through a partial index on
`announcement (article_id) WHERE listed_on IS NOT NULL`, and keeps the closer one. The day of
first sight is read in Taipei, as `Pending.dated` already was.

Storing an estimated day at insert time was considered: the backfill stores undated articles
before their dated neighbours, so the estimate would be stale.

### Renditions made with the wrong day

Migration `0005` creates the index and, once, clears the current rendition of every article
without a list date, deletes its model tags and its renditions. The next pick renders the recent
ones again and leaves the old ones raw. Their `rendered` events stay: the log is append-only, and
a new `rendered` event follows when they render again. On an empty database the migration only
creates the index.

## Risks / Trade-offs

- [A draft created long before it was published] → its estimate is too old, by weeks; the
  two-month rule of the prompt absorbs most of it, and the date finder still drops a date the text
  does not hold.
- [An undated article whose neighbours are recycled articles] → it may count as recent and render;
  the cost is one rendition, and its dates are still read from its text.

## Migration Plan

Deploy; the migration runs at start. Then uncomment `BULLETIN_MODEL_KEYS` in the host's `.env`
and restart: rendering resumes. Rollback: comment the keys out again.
