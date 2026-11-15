# Proposal: date-undated-articles

## Why

Some boards publish no dates in their lists (docs/pitfalls.md), so 836 of 2,449 stored articles
have no list date, all of them found by the backfill. Rendering dates them by the day they were
first seen, the day of the backfill: every one counts as new, goes first in the backlog and is
rendered however old it is, and its dates without a year are read against the wrong year (a
summer course's 8月16日 was stored as 2027-08-16). The owner paused rendering on 2026-11-15
until this is fixed.

## What Changes

- An article without a list date is dated by the list date of the dated article with the nearest
  article id; NTUST's article ids grow with time across every site. The day of first sight stays
  only for an article with no dated article at all.
- That day decides whether the article is rendered (the last year, E2), where it goes in the
  backlog, and the day the prompt and the date finder read dates against.
- A migration adds the index that finds the nearest dated article, and drops the renditions and
  model tags of the articles without a list date rendered so far, so they render again with the
  right day or stay raw.

Out of scope: storing the estimated day, showing it to readers (the public API decides what it
shows), and any change to the collector.

## Capabilities

### Modified Capabilities

- `rendering`: "What gets rendered" and "Deadlines from the text" use the estimated day.

## Impact

- `src/bulletin/renditions.py` (the pick query), a new migration `0005`, their tests.
- Production: about 404 of the 836 articles render; the other 432 stay raw.
