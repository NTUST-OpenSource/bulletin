# Proposal: fix-rendering-fallbacks

## Why

By 2026-11-16, 14 of 1,338 renditions were fallbacks. Re-running them locally showed three causes
that failed all three attempts every time:

- **Text that looks like a placeholder** (5): admission lists mask ID numbers as `L125***256`, a
  venue is called `I8` and a table codes a category `I1`. `restore` read these as placeholders
  the input never had.
- **Malformed link targets** (4): school pages link to `http:// https://host/`, to
  `http://name@mail.ntust.edu.tw%20/` and to `http://` followed by Chinese text. Discord's parser
  takes no link whose host holds a space, a `%` escape or non-ASCII text.
- **Too long once the URLs are back** (5): lists of 28 to 110 links whose Markdown fits, but whose
  URLs push it past 4,096 characters.

The first two are faults of our own input and checks; the answers were good.

## What Changes

- Placeholders are put back where the input had them. An unknown placeholder fails the attempt
  only in a link or image target (`[text](L9)`, `![text](I9)`, `<L9>`); elsewhere it is text and
  stays as written.
- A link target that repeats its scheme (`http:// https://host/`) names the URL after it. A link
  whose host is not an ASCII host name keeps its text only; such an image is left out.
- Migration 0007 drops the fallback renditions, so those announcements render again.

Out of scope: the five that are too long. Fitting them needs the owner's call on decision E4
(a shorter prompt for long link lists, or renditions that hold more than Discord shows).

## Capabilities

### Modified Capabilities

- `rendering`: "Model input" repairs or drops malformed link targets; "Placeholders put back"
  fails only on unknown placeholders in link or image targets.

## Impact

- `src/bulletin/model_input.py`, `src/bulletin/answers.py`, a new
  `src/bulletin/migrations/0007_retry_fallbacks.sql`, and their tests.
- About 14 announcements render again after deploy; no prompt change, so no other re-rendering.
