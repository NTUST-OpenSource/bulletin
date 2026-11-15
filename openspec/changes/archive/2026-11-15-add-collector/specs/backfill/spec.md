# backfill

## Purpose

Records every announcement a board published in the last ten years, so that the archive is
complete and an unseen id on a backfilled board can only be a first publication.

## ADDED Requirements

### Requirement: Ten-year walk
For every board with a tier other than off and a backfill not complete, the service SHALL read the
board's static list pages from page 2 onward, storing each item like a poll would, until a page
holds only items listed more than ten years ago or the last page is read. The board's backfill is
then complete.

#### Scenario: A board with three pages
- **WHEN** a board's backfill reads pages 2 and 3 and page 3 is the last
- **THEN** every item of both pages is stored and the board's backfill is complete

#### Scenario: Ten years reached
- **WHEN** page 40 holds only items listed eleven years ago
- **THEN** none of them is stored, page 41 is not requested and the backfill is complete

### Requirement: Backfill articles
Every announcement backfill stores within the ten years SHALL get its article fetch, through the
backfill's place in the queue, so that its body is searchable.

#### Scenario: Article bodies
- **WHEN** backfill stores an announcement from 2019
- **THEN** its article page is fetched during the backfill window and its first revision stored

### Requirement: Resumable progress
Backfill progress SHALL be stored per board, so that a restart continues at the next unread page.
A board whose backfill is complete SHALL not be walked again unless it is turned on from off.

#### Scenario: Restart in the middle
- **WHEN** the service restarts after page 12 of a board's backfill
- **THEN** the backfill continues at page 13

### Requirement: No announcements from backfill
Announcements stored by backfill SHALL be late discoveries: their published events SHALL NOT be
notify-worthy.

#### Scenario: Backfill finds an unseen announcement
- **WHEN** backfill stores an announcement that no poll has seen
- **THEN** its published event is marked late and not notify-worthy
