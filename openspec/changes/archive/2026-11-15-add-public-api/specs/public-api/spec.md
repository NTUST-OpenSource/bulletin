# public-api

## Purpose

Serves the archive read-only to the web frontend and to other clients under `/api/v1/` on
`bulletin.ntust.org`: the announcement stream, search, single announcements, the events feed,
sites, tags and stored files, cacheable by HTTP caches in front.

## ADDED Requirements

### Requirement: Read-only JSON under /api/v1
The public listener SHALL serve the API under `/api/v1/` as JSON, without authentication, and
SHALL answer only GET and CORS preflight requests there. Errors SHALL be JSON with a `detail`
message: 400 for a malformed parameter, 404 for something that does not exist, 405 for another
method, 429 when rate limited. The admin API SHALL stay unreachable from this listener.

#### Scenario: A write
- **WHEN** a client sends `POST /api/v1/announcements`
- **THEN** the answer is 405 and nothing changes

#### Scenario: The admin path
- **WHEN** a client asks the public listener for `/admin/boards`
- **THEN** the answer is 404

### Requirement: Announcement stream
`GET /api/v1/announcements` SHALL list announcements that are not cross-posts, by stream day,
newest first, then by id, highest first, `limit` per page (default 30, at most 100). Each page
SHALL carry a `next` cursor, null on the last page; passing it SHALL continue after the page's
last item in that order. A malformed cursor or a `limit` outside 1 to 100 SHALL be a 400.

#### Scenario: Two pages
- **WHEN** 45 announcements match and a client reads the first page, then the page after its
  `next` cursor
- **THEN** it has received all 45 once each, in order, and the second page's `next` is null

#### Scenario: A new announcement between pages
- **WHEN** an announcement is stored after a client read the first page
- **THEN** the page after the cursor neither repeats an item nor skips one

#### Scenario: A cross-post
- **WHEN** the school-wide bulletin board's copy is linked as a cross-post of an office's
  announcement
- **THEN** the stream lists the office's announcement only

#### Scenario: Bad paging values
- **WHEN** a client sends `cursor=xyz` or `limit=500`
- **THEN** the answer is 400

### Requirement: Stream filters
The stream SHALL take repeatable `site` ids and `board` keys (`<site>-<board>`); together they
select a set of boards, and an announcement matches when it or one of its cross-posts is placed
on one of them. Repeatable `tag` values (`<dimension>:<id>`) SHALL all have to match. `from` and
`to` SHALL bound the stream day, inclusive. Unknown tags and malformed values SHALL be a 400.

#### Scenario: Followed sites and a board
- **WHEN** a client asks for `site=1053&board=1045-1391`
- **THEN** it gets announcements placed on any board of site 1053 or on board 1045-1391

#### Scenario: Placed through a cross-post
- **WHEN** an office's announcement has a cross-post on board 1045-1391 and a client asks for that
  board
- **THEN** the office's announcement is listed

#### Scenario: Two tags
- **WHEN** a client asks for `tag=topic:scholarships&tag=audience:graduate-students`
- **THEN** only announcements carrying both tags are listed

#### Scenario: A range of days
- **WHEN** a client asks for `from=2026-11-01&to=2026-11-07`
- **THEN** only announcements whose stream day falls in that week are listed

#### Scenario: An unknown tag
- **WHEN** a client asks for `tag=topic:weather`
- **THEN** the answer is 400 naming the tag

### Requirement: Search
`q` SHALL search the titles and body texts of every retained announcement, alone or with the
filters, in stream order with the same pagination. Words separated by spaces SHALL all have to
match, each as plain text, so no character has a special meaning. `in=title` SHALL search titles
only. More than 10 words or 100 characters SHALL be a 400.

#### Scenario: A word in the body
- **WHEN** a client searches for a two-character term that appears only in an announcement's body
  from six years ago
- **THEN** that announcement is listed

#### Scenario: Titles only
- **WHEN** the same search adds `in=title`
- **THEN** that announcement is not listed

#### Scenario: Characters with meaning elsewhere
- **WHEN** a client searches for `113-1` or `(OR`
- **THEN** announcements containing that text are listed and the answer is not an error

#### Scenario: A long query
- **WHEN** a client searches for eleven words
- **THEN** the answer is 400

### Requirement: Stream items
Each stream item SHALL hold the id, site id, its site's unit or null, the URL, whether it is a
link item, the school's title, the publisher or null, the stream day, the list date or null, the
first-seen time, the withdrawal time or null, the boards it and its cross-posts are placed on,
its stored tags by dimension, and its rendition's title, summary and deadline, or null without a
rendition or with only a fallback.

#### Scenario: A rendered announcement
- **WHEN** an announcement has a rendition and tags
- **THEN** its item holds the rendition's title and summary and the tags by dimension

#### Scenario: A raw announcement
- **WHEN** an announcement has no rendition and no tags
- **THEN** its item holds the school's title, a null rendition and empty tag lists

#### Scenario: A fallback
- **WHEN** an announcement with model tags got a fallback rendition after a new revision
- **THEN** its item holds a null rendition and the tags as stored

#### Scenario: A link item
- **WHEN** an announcement is a link straight to a file
- **THEN** its item says it is a link item, with the link as its URL

### Requirement: One announcement
`GET /api/v1/announcements/{id}` SHALL return the stream item's fields plus the current
revision's raw body HTML, the rendition's Markdown, the attachments with name, URL, size and the
stored file's path, null unless the file is in the store, the revision times, the cross-posts,
and the announcement it copies or null. An unknown id SHALL be a 404.

#### Scenario: Attachments
- **WHEN** an announcement has a stored PDF and a 7 MB file that was not stored
- **THEN** the PDF's attachment holds its file path and the other's holds null, both with their
  names and school URLs

#### Scenario: A pruned file
- **WHEN** the one-year window deleted an attachment's file and kept its digest
- **THEN** the attachment's file path is null

#### Scenario: A cross-post's own page
- **WHEN** a client asks for a cross-post by its id
- **THEN** it gets the cross-post, naming the announcement it copies

### Requirement: Events feed
`GET /api/v1/events` SHALL list events with ids above `after` (default 0), in id order, `limit`
per page (default 100, at most 500), each with its id, kind, notify and late flags, time and the
announcement as a stream item as it is now. The answer SHALL carry the last id it holds, or
`after` when it holds none.

#### Scenario: Resuming
- **WHEN** a client read events up to id 120 and asks with `after=120`
- **THEN** it gets the events from 121 on and none before

#### Scenario: Nothing new
- **WHEN** no event has an id above `after`
- **THEN** the list is empty and the last id is `after`

### Requirement: Sites and boards
`GET /api/v1/sites` SHALL list, in the school's order, each site with a board that is neither
excluded nor off: its id, host, unit, kind (`all`, `admin` or `academic`), its college for
academic units or null, and its boards that are not excluded, with key, name and category. A
site missing from the unit data SHALL be listed last, as `admin`.

#### Scenario: An academic unit
- **WHEN** the sites are listed
- **THEN** the electronic and computer engineering department is `academic` with the college of
  electrical engineering and computer science, after the college's own site

#### Scenario: An excluded board
- **WHEN** a site's banner board is excluded
- **THEN** the board is not listed

#### Scenario: A board turned off
- **WHEN** one of a site's boards is turned off and another still polls
- **THEN** the site lists both boards

### Requirement: Tag taxonomy
`GET /api/v1/tags` SHALL list the four dimensions in order, each with its id, whether several
tags are allowed (`several`), and its tags in order with id and label, as the taxonomy holds
them.

#### Scenario: The topics
- **WHEN** the tags are listed
- **THEN** the topic dimension allows several tags and holds 21, the library among them with its
  label

### Requirement: HTTP caching
Successful API answers other than files SHALL carry `Cache-Control: public, max-age=60,
stale-while-revalidate=600` and an ETag that changes with the release and, for the stream and
events, the latest event and revision, else the content; a request whose `If-None-Match` holds it
SHALL get a 304 without a body. Error answers SHALL carry
`Cache-Control: no-store`.

#### Scenario: Nothing changed
- **WHEN** a client repeats a stream request with the ETag it got and no event or revision was
  recorded since
- **THEN** the answer is 304

#### Scenario: A new event
- **WHEN** an event was recorded since
- **THEN** the answer is 200 with a new ETag

#### Scenario: Unchanged sites
- **WHEN** a client repeats a sites request with its ETag and the registry did not change
- **THEN** the answer is 304

#### Scenario: A refused search
- **WHEN** a search is answered with 429
- **THEN** the answer is not cacheable

### Requirement: CORS
Every API answer SHALL carry `Access-Control-Allow-Origin: *`, and preflight requests for GET
SHALL be allowed from any origin without credentials.

#### Scenario: Another site's page
- **WHEN** a page on another origin sends a GET with `Origin: https://example.org`
- **THEN** the answer allows any origin

#### Scenario: A preflight
- **WHEN** a page on another origin sends a preflight for a GET with an `If-None-Match` header
- **THEN** the preflight is allowed

### Requirement: Stored files
`GET /api/v1/files/{sha256}/{name}` SHALL return a stored file when an attachment records that
digest with that name and the file is in the store, else 404. The name SHALL be matched as
recorded, `/` included. The content type SHALL come from the name's extension through an
allow-list, inline, else `application/octet-stream` as an attachment; with `nosniff` and
immutable caching.

#### Scenario: A PDF
- **WHEN** a client asks for a stored PDF under its recorded name
- **THEN** it gets the file as `application/pdf`, inline, with the name and immutable caching

#### Scenario: An unexpected type
- **WHEN** the recorded name ends in `.html`
- **THEN** the file comes as `application/octet-stream`, as an attachment

#### Scenario: A pruned file
- **WHEN** the file was deleted by the one-year window
- **THEN** the answer is 404

#### Scenario: A name with a slash
- **WHEN** the recorded name is `113/1 schedule.pdf` and the path carries it percent-encoded
- **THEN** the file is returned

### Requirement: Search rate limit
Search requests SHALL be limited to 30 a minute per client, the client taken from the proxy
chain, IPv6 clients by their /64 network; more SHALL get a 429 with `Retry-After`. A request
without `X-Forwarded-For` from a private address, as on `proxy-net`, SHALL be exempt. Requests
without `q` SHALL never be limited.

#### Scenario: Too many searches
- **WHEN** one client sends its 31st search within a minute through the proxy
- **THEN** it gets a 429 with `Retry-After`

#### Scenario: A forged private address
- **WHEN** a client behind the proxy claims a private address in `X-Forwarded-For`
- **THEN** it is limited by its real address

#### Scenario: An internal client
- **WHEN** tigerduck searches 100 times a minute over `proxy-net`
- **THEN** none is limited

#### Scenario: Browsing
- **WHEN** one client reads 100 stream pages without `q` within a minute
- **THEN** none is limited

### Requirement: API description
The API SHALL describe itself as OpenAPI at `/api/v1/openapi.json`.

#### Scenario: The description
- **WHEN** a client reads `/api/v1/openapi.json`
- **THEN** it lists every endpoint of this capability with its parameters
