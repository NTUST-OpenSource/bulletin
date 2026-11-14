# detection

## Purpose

Decides which items on a polled list are new announcements, and which new announcements are first
publications worth announcing, so that pinned, reordered, recycled and late-found posts never
reach people as news.

## ADDED Requirements

### Requirement: New announcement
An item linking to an article page SHALL be identified by the site and article id in its link,
whichever board lists it; any other item is a link entry, identified by the polled board's site
and the URL. An item SHALL be a new announcement when its identity was never stored; position,
list date and title SHALL NOT matter. It SHALL be stored with a placement on the polled board.

#### Scenario: An item moves up from page 2
- **WHEN** an announcement leaves page 1 and a known announcement from page 2 takes its place
- **THEN** no new announcement is stored

#### Scenario: A pinned old announcement
- **WHEN** page 1 lists a known two-year-old announcement above newer ones
- **THEN** no new announcement is stored

#### Scenario: A known announcement on a second board
- **WHEN** a stored announcement appears on another board, of its own site or another
- **THEN** it gains a placement on that board and is not new

#### Scenario: Another site's article
- **WHEN** board 1063-2211 lists `https://www.ntust.edu.tw/p/406-1000-153625,r167.php`
- **THEN** the announcement is site 1000's article 153625, with a placement on board 1063-2211

#### Scenario: A link entry
- **WHEN** a board of site 1045 lists an item linking to a PDF
- **THEN** it is stored as a link entry of site 1045 identified by the PDF's URL

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
