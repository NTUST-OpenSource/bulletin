# rendering Specification

## Purpose
Rewrites announcements with a model into one clean version each, with a title, Discord Markdown, a
summary, a deadline and tags, kept next to the school's raw text and checked before it is stored.

## Requirements

### Requirement: What gets rendered
The service SHALL render every announcement with a revision whose stream day falls within the
last year. Link items, which have no article page, and older announcements SHALL stay raw.
Announcements that are not late discoveries SHALL be rendered before late ones, and within each
group the most recent stream day first.

#### Scenario: A new announcement during the backlog
- **WHEN** late discoveries from last spring wait for rendering and a first publication is stored
- **THEN** the first publication is rendered next

#### Scenario: An announcement from two years ago
- **WHEN** backfill stores an announcement listed two years ago
- **THEN** it gets no rendition

#### Scenario: An old article without a list date
- **WHEN** backfill stores an article without a list date whose nearest dated article was listed
  two years ago
- **THEN** it gets no rendition

#### Scenario: A recent article without a list date
- **WHEN** an article without a list date lies between articles listed last spring and last week
  and is nearest to last week's
- **THEN** it is rendered by last week's day, before last spring's

#### Scenario: A link item
- **WHEN** an announcement links straight to a file
- **THEN** it gets no rendition

### Requirement: Renditions follow revisions
A rendition SHALL belong to one revision and one prompt version. An announcement whose current
revision has no rendition for the current prompt version SHALL be rendered again. Earlier
renditions SHALL be kept.

#### Scenario: An edited announcement
- **WHEN** a rendered announcement gets a new revision
- **THEN** the new revision is rendered, and the earlier rendition stays stored

#### Scenario: A new prompt
- **WHEN** the prompt version changes
- **THEN** announcements within the last year are rendered again with it

### Requirement: Model input
The model SHALL receive the article's title and the article's body and attachment module, taken
by selector and reduced to paragraphs, lists, tables, links, bold and images, as Markdown. Each
link and image SHALL be replaced by a placeholder (`L1`, `I1`, ...), so the input holds no URL. A
target that repeats its scheme, such as `http:// https://host/`, SHALL name the URL after it; a
link whose host is not an ASCII host name SHALL keep its text only, and such an image SHALL be
left out.

#### Scenario: A recorded article
- **WHEN** the recorded article with an attachment module and a body file link is rendered
- **THEN** the input holds the body text, every attachment's name and a placeholder for each link
  and image, and no URL

#### Scenario: A scheme typed twice
- **WHEN** a link's target is `http://` and a space before `https://dca.moi.gov.tw/ris`
- **THEN** its placeholder stands for `https://dca.moi.gov.tw/ris`

#### Scenario: A host Discord cannot link
- **WHEN** a link's target is `http://name@mail.ntust.edu.tw%20/`, or `http://` before Chinese
  text
- **THEN** the input holds the link's text and no placeholder for it

### Requirement: Placeholders put back
After the model answers, each placeholder the input had SHALL be replaced by the URL it stands
for. An answer that holds, in a link or image target, a placeholder the input did not have SHALL
fail the attempt; elsewhere such text, as a masked ID number, SHALL stay as written. An answer MAY
leave out images: icons and decorations are left out (owner), images with content are kept.

#### Scenario: Links restored
- **WHEN** the answer uses `L1` and `I1`
- **THEN** the stored Markdown holds their URLs and no placeholder

#### Scenario: An invented placeholder
- **WHEN** the answer links to `L9` and the input had only `L1`
- **THEN** the attempt fails

#### Scenario: Text that looks like a placeholder
- **WHEN** the answer holds the masked ID number `L125***256` outside a link
- **THEN** the stored Markdown holds it as written

#### Scenario: An image left out
- **WHEN** the input had `I1` and the answer does not
- **THEN** the rendition is stored without it

### Requirement: Structured answer
The model SHALL be asked for JSON constrained by a schema: a title without bracketed tags, the
body as Discord Markdown, a summary, a deadline date or none, and tags. An answer that is not JSON
or does not match the schema SHALL fail the attempt.

#### Scenario: Not JSON
- **WHEN** the model answers with prose
- **THEN** the attempt fails

### Requirement: Deadlines from the text
A deadline SHALL be kept only when its date appears in the source text, in any of the school's
date forms: Gregorian or ROC years, numeric, Chinese or with English month names, with or without
the year. A deadline that does not appear SHALL be dropped; the rendition is stored without one.
Dates without a year SHALL be read against the announcement's day, the one that decides whether
it is rendered. The prompt SHALL give that day and today's date.

#### Scenario: An ROC date
- **WHEN** the text says the deadline is 115年12月10日 and the answer gives 2026-12-10
- **THEN** the rendition's deadline is 2026-12-10

#### Scenario: An invented date
- **WHEN** the answer gives a deadline whose date the text does not hold
- **THEN** the rendition has no deadline

#### Scenario: Both days in the prompt
- **WHEN** an announcement listed on 2026-11-03 is rendered on 2026-11-15
- **THEN** its prompt gives both days

#### Scenario: An announcement without a list date
- **WHEN** an article without a list date is rendered and its nearest dated article was listed
  on 2026-07-20
- **THEN** its prompt gives 2026-07-20

#### Scenario: No dated article at all
- **WHEN** an article without a list date is rendered and no article has a list date
- **THEN** its prompt gives the day it was first seen, in Taipei

### Requirement: Discord Markdown
Before a rendition is stored, its Markdown SHALL have bare URLs wrapped as `<url>` and masked
links whose text is a URL or empty replaced by the URL, images without a description given one,
and SHALL then pass the Discord Markdown check: the `@discord/markdown-wasm` parser accepts it, it
holds no table, and it fits 4,096 characters. A failed check SHALL fail the attempt.

#### Scenario: A bare URL
- **WHEN** the restored Markdown holds a bare URL
- **THEN** the stored Markdown holds it as `<url>`

#### Scenario: An image without a description
- **WHEN** the restored Markdown holds an image whose description is empty
- **THEN** the stored Markdown describes it as 圖片, or Image in a text without Chinese

#### Scenario: A table in the answer
- **WHEN** the answer's Markdown holds a pipe table
- **THEN** the attempt fails

### Requirement: No emoji
Renditions SHALL hold no emoji (owner). Emoji SHALL be removed from the model's input and from the
answer's title, Markdown and summary, and from a fallback's title; a keycap keeps its digit.
Symbols that are text, such as reference marks, stars and circled numbers, SHALL stay.

#### Scenario: Emoji in the source
- **WHEN** an article's title, body and image descriptions hold emoji
- **THEN** neither the model input nor the rendition holds any

### Requirement: Attempts and fallback
A rendering SHALL make at most three attempts whose answers fail the checks. After the third, the
announcement SHALL get a fallback rendition, marked as such, holding its title and link. Errors of
the model's API, such as rate limits, server errors and timeouts, SHALL NOT count as attempts:
the announcement is tried again later.

#### Scenario: Three bad answers
- **WHEN** three answers in a row fail the checks
- **THEN** the announcement gets a fallback rendition with its title and link

#### Scenario: A rate limit
- **WHEN** the API answers HTTP 429
- **THEN** no attempt is counted, no fallback is stored, and the announcement is tried again later

### Requirement: Keys in turn
The service SHALL use the configured API keys in turn, each within its own limit of requests per
minute. A key the API answers with a rate limit SHALL rest until its window ends while the others
carry on; when every key rests, rendering SHALL wait. No key SHALL appear in a log line or in a
stored error.

#### Scenario: Two keys
- **WHEN** two keys are configured and three announcements are rendered
- **THEN** the requests use the first, the second and the first key

#### Scenario: A resting key
- **WHEN** the first key gets HTTP 429
- **THEN** the next requests use the second key until the first key's window ends

#### Scenario: An error that quotes a key
- **WHEN** the API's error text holds the key
- **THEN** the logged and stored text shows the key hidden

### Requirement: Model configuration
The model's endpoint, API format (Gemini's generateContent or an OpenAI-compatible chat
completions API), model id, keys and thinking level SHALL come from configuration, with Gemini's
API and `gemini-4-hydrogen` as the defaults. Without keys the service SHALL run without rendering
and the collector SHALL be unaffected.

#### Scenario: An OpenAI-compatible endpoint
- **WHEN** the format is set to OpenAI-compatible
- **THEN** requests go to the endpoint's chat completions with the key as a bearer token

#### Scenario: No keys
- **WHEN** the service starts without model keys
- **THEN** polls and jobs run as before and no rendering request is sent
