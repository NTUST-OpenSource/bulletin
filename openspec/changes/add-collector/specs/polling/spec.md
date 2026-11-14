# polling

## Purpose

Fetches each board's first list page as often as its tier asks, through one queue that keeps the
load on the school's servers low and steady.

## ADDED Requirements

### Requirement: Tier intervals
A board's next poll SHALL be due one interval after its last poll. Intervals: P1 5 minutes on
weekdays from 08:00 to 18:00 Asia/Taipei and 20 minutes otherwise; P2 15 and 60; P3 60 and 240; P4
once a day. The window that holds the last poll decides the interval. Off boards SHALL never be
polled.

#### Scenario: Office hours
- **WHEN** a P1 board is polled at 10:00 on a Wednesday
- **THEN** its next poll is due at 10:05

#### Scenario: Weekend
- **WHEN** a P1 board is polled at 10:00 on a Saturday
- **THEN** its next poll is due at 10:20

#### Scenario: Off
- **WHEN** a board is off
- **THEN** no request for it is made

### Requirement: Request budget
Every request to a school host, from polls, article fetches, re-checks, backfill, attachments and
re-discovery alike, SHALL go through one queue that sends one request at a time. Each request
SHALL start at least 2 seconds after the previous one finished, plus a random delay of up to 1
second.

#### Scenario: Two polls due at once
- **WHEN** two polls are due at the same moment
- **THEN** the second request starts at least 2 seconds after the first one finished

### Requirement: Queue order
When several requests are due, the queue SHALL send them in this order: polls by tier from P1 to
P4, then article fetches and re-checks, then attachments, then re-discovery, then backfill.
Backfill SHALL only run from 01:00 to 06:00 Asia/Taipei.

#### Scenario: Backfill yields
- **WHEN** a backfill page and a P3 poll are both due at 02:00
- **THEN** the P3 poll is sent first

#### Scenario: Daytime
- **WHEN** a backfill is queued at 14:00
- **THEN** it waits until 01:00

### Requirement: List page fetch
A poll SHALL fetch the board's static list page 1, `/p/403-{site}-{board}-1.php` on the board's
host, with the bot's User-Agent, and read each item's article id or link, title, list date when the
board shows one, and publisher when the board lists one.

#### Scenario: A table board
- **WHEN** a recorded table-layout list page is polled
- **THEN** every item's article id, title and list date are read in page order

#### Scenario: A link to a file
- **WHEN** an item links straight to a file instead of an article
- **THEN** the item is read with its URL and title and no article id

### Requirement: Unchanged pages
After each poll, the service SHALL compare a fingerprint of the items read (article ids or links,
titles and list dates, in order) with the board's previous one. When they match, the poll SHALL be
recorded as unchanged and nothing else SHALL happen.

#### Scenario: Same page twice
- **WHEN** a board's page 1 is polled twice with the same items
- **THEN** the second poll is recorded as unchanged and detection does not run

### Requirement: Paging on bursts
When every item on a board's page 1 is unknown and the board has been polled before, the service
SHALL fetch pages 2, 3 and on until a page holds a known item, at most up to page 5.

#### Scenario: Six new announcements on a five-item page
- **WHEN** page 1 holds five unknown items and page 2 holds one unknown item followed by known ones
- **THEN** pages 1 and 2 are read, page 3 is not requested, and all six are detected

### Requirement: Failure backoff
A poll that fails with a network error, a timeout or an HTTP error SHALL be recorded with its
status, and the board's next poll SHALL be pushed back by its interval doubled for each consecutive
failure, up to one day. The first success SHALL reset it. A WAF block (HTTP 406) SHALL pause the
whole queue for 15 minutes.

#### Scenario: Three failures in a row
- **WHEN** a P2 board fails three polls in a row during office hours
- **THEN** its next poll is due 120 minutes after the third failure

#### Scenario: WAF block
- **WHEN** any request gets HTTP 406
- **THEN** no request to any school host starts within the next 15 minutes

### Requirement: Poll log
Every request to a school host SHALL be logged with its purpose, board when there is one, time,
HTTP status, bytes, duration, whether the list changed and the new ids. Entries older than 30 days
SHALL be deleted.

#### Scenario: Log retention
- **WHEN** the nightly cleanup runs with log entries 29 and 31 days old
- **THEN** the 31-day-old entry is deleted and the 29-day-old one stays

### Requirement: School certificates
Requests to `*.ntust.edu.tw` SHALL verify certificates against the system's trust store plus the
bundled TWCA intermediate, with only the strict X.509 flag cleared, because the school's
certificates lack a Subject Key Identifier. Requests to other hosts SHALL use the default strict
verification.

#### Scenario: School host without the intermediate
- **WHEN** a school host sends a chain without TWCA's intermediate and a leaf without a Subject Key
  Identifier
- **THEN** verification succeeds

#### Scenario: Other hosts stay strict
- **WHEN** a host outside the school sends a certificate that fails strict verification
- **THEN** the request fails
