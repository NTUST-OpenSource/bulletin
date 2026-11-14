# archive

## Purpose

Keeps every announcement's content as the school published it, follows its edits and withdrawal,
and holds it for ten years, also after the school has taken it down.

## ADDED Requirements

### Requirement: Article fetch
For each new announcement with an article id, the service SHALL fetch its article page from the
host and site in its own link and store the first revision: title, publisher, the body as text and
as raw HTML, and the attachments. A link entry SHALL be stored with its URL and title only.

#### Scenario: A recorded article
- **WHEN** a new announcement's article page is fetched from a recorded fixture
- **THEN** its first revision holds the fixture's title, publisher, body text, body HTML and
  attachment links

#### Scenario: Another site's article
- **WHEN** board 1063-2211 lists site 1000's article 153625
- **THEN** the article page is requested at `https://www.ntust.edu.tw/p/406-1000-153625.php`

#### Scenario: A file link on the bulletin board
- **WHEN** a new item links straight to a PDF
- **THEN** the announcement is stored with the URL and title and no article page is requested

### Requirement: Revisions
The service SHALL re-check each announcement 1, 3, 7 and 30 days after it was first seen. When the
content hash of the title, body and attachment links differs from the latest revision, it SHALL
store a new revision and record a revised event; otherwise it SHALL store nothing.

#### Scenario: An edited deadline
- **WHEN** the 3-day re-check finds a changed body
- **THEN** a second revision is stored and a revised event is recorded

#### Scenario: No change
- **WHEN** the 7-day re-check finds the same content
- **THEN** no revision or event is added

### Requirement: Withdrawal
An article page requested at the announcement's own host, site and article id that answers with
a redirect to that site's home page SHALL mark the announcement withdrawn, with the time, and
record a withdrawn event; its revisions SHALL be kept. Leaving a board's page 1 SHALL NOT by itself
mark it withdrawn, nor SHALL a request built from the listing board's site.

#### Scenario: Taken down
- **WHEN** a re-check of an article answers 302 to the site's home page
- **THEN** the announcement is withdrawn, a withdrawn event is recorded and its content stays

#### Scenario: Pushed to page 2
- **WHEN** an announcement drops off page 1 while newer ones arrive
- **THEN** it is not withdrawn

#### Scenario: Re-checking another site's article
- **WHEN** site 1000's article 153625, listed by board 1063-2211, is re-checked
- **THEN** the request goes to `www.ntust.edu.tw` for `406-1000-153625`, never to the
  secretariat's host for `406-1063-153625`

### Requirement: Prompt withdrawal check
When an announcement leaves a board's page 1 and no new item took a place on that page, the service
SHALL re-check its article within an hour.

#### Scenario: One item gone, nothing new
- **WHEN** a poll finds page 1 without a known announcement and with no unknown item
- **THEN** that announcement's article is re-checked within an hour

### Requirement: Restored announcements
A withdrawn announcement whose article page answers again with content, at a re-check or because
it is listed again, SHALL lose its withdrawn mark and record a restored event.

#### Scenario: Back online
- **WHEN** a withdrawn announcement appears on a list again and its article page answers 200
- **THEN** it is no longer withdrawn and a restored event is recorded

### Requirement: Ten-year retention
Announcements SHALL be kept for ten years after they were first seen or listed, whichever is
earlier, withdrawn ones included. Nightly, older announcements SHALL be deleted with their
placements, revisions, attachments and events.

#### Scenario: The edge of ten years
- **WHEN** the nightly cleanup runs with announcements listed ten years and one day ago and nine
  years ago
- **THEN** only the older one is deleted

### Requirement: Search indexes
Titles and body texts of every stored announcement SHALL be indexed for full-text search that
matches two-character Chinese terms.

#### Scenario: A two-character term
- **WHEN** an announcement's body contains a two-character Chinese term and the index is queried
  for it
- **THEN** the announcement is found
