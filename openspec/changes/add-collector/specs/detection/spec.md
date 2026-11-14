# detection

## Purpose

Decides which items on a polled list are new announcements, and which new announcements are first
publications worth announcing, so that pinned, reordered, recycled and late-found posts never
reach people as news.

## ADDED Requirements

### Requirement: New announcement
A list item SHALL be a new announcement when its site and article id, or its site and URL for an
item without an article id, were never stored. Its position on the list, its list date and its
title SHALL NOT matter. A new announcement SHALL be stored with a placement on the board and
queued for its article fetch.

#### Scenario: An item moves up from page 2
- **WHEN** an announcement leaves page 1 and a known announcement from page 2 takes its place
- **THEN** no new announcement is stored

#### Scenario: A pinned old announcement
- **WHEN** page 1 lists a known two-year-old announcement above newer ones
- **THEN** no new announcement is stored

#### Scenario: A known announcement on a second board
- **WHEN** a stored announcement appears on another board of its site
- **THEN** it gains a placement on that board and is not new

### Requirement: Recycled articles
When a stored announcement appears again with a newer list date, the service SHALL update its
placement's list date and SHALL NOT treat it as new or record an event.

#### Scenario: Re-dated article
- **WHEN** a stored announcement with list date 2021-05-03 is listed again with 2026-11-12
- **THEN** its placement shows 2026-11-12 and no event is recorded

### Requirement: Frontier record
At least once an hour, the service SHALL record the highest article id it has seen on any site,
with the time. Records SHALL be kept for at least 7 days.

#### Scenario: Hourly record
- **WHEN** the highest stored article id is 153700 at 10:00
- **THEN** a frontier record of 153700 at 10:00 exists

### Requirement: Notify rule on backfilled boards
On a board whose backfill is complete, a new announcement is a first publication: its published
event SHALL be notify-worthy, even when its article id is old, as with a draft published late.

#### Scenario: A late-published draft
- **WHEN** a backfilled board lists an unknown article whose id is 2,000 below the frontier
- **THEN** its published event is notify-worthy

### Requirement: Frontier rule
On a board whose backfill is not complete, a new announcement's published event SHALL be
notify-worthy only when its article id is above the frontier recorded 72 hours earlier (the
oldest record when the service is younger), or its list date is at most 2 days before the poll.
Otherwise it is a late discovery. With no frontier recorded yet, none is notify-worthy.

#### Scenario: A board turned on
- **WHEN** a board turned on from off lists twenty unknown announcements from last year
- **THEN** all twenty are stored as late discoveries and none is notify-worthy

#### Scenario: A genuinely new one
- **WHEN** the same board lists an unknown announcement whose id is above the frontier of 72 hours
  ago
- **THEN** its published event is notify-worthy

#### Scenario: First start
- **WHEN** the service polls for the first time on an empty database
- **THEN** every announcement is stored and none is notify-worthy

### Requirement: Cross-posts
A new announcement whose normalized title, at least 8 characters long, matches an announcement of
another site first seen within the previous 14 days SHALL be linked to it as a cross-post, and its
published event SHALL NOT be notify-worthy. Normalizing drops bracketed prefixes, the words for
"forwarded" and "announcement", punctuation and spaces.

#### Scenario: The bulletin board's copy
- **WHEN** an office's announcement was first seen yesterday and the school-wide bulletin board
  lists an announcement with the same title under a different article id
- **THEN** the second is linked as a cross-post of the first and is not notify-worthy

#### Scenario: Short generic titles
- **WHEN** two sites post announcements titled with the same four characters
- **THEN** they are not linked
