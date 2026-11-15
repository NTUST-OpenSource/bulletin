# Design: add-rendering

## Context

See proposal.md for why. The collector stores each announcement's revisions with the raw body
HTML and text (`revision`), marks late discoveries (`announcement.late`) and records events in an
append-only log. Decisions E1-E4 fix the model (Gemini `gemini-4-hydrogen`, keys in turn), what
gets rendered, the tag taxonomy and Discord Markdown as the target. `docs/roadmap.md` section 2
settled the model input pipeline, measured on 59 cached pages. The xincord plugin
`ntust_announcements` already talks to Gemini and OpenAI-compatible APIs (`api.py`) and spreads
requests over several keys (`conversion.py`, `KeyRing`); this change ports both.

## Goals / Non-Goals

**Goals:**

- Every announcement of the last year rendered once per revision, checked before it is stored.
- A failure of the model or its quota delays renditions; it never touches the collector.
- Prompt changes are deliberate: editing the prompt cannot silently re-render a year of
  announcements.

**Non-Goals:**

- Parallel rendering. One request at a time is enough for about 33 new announcements a day, and
  the keys' rate limits, not concurrency, bound the backlog.
- Reading attachments' contents; the model sees their names only.

## Decisions

### A third loop in the service

`bulletin serve` gains a rendering loop beside the worker and the two listeners, in the same
event loop. It picks the next announcement to render, renders it and sleeps when nothing waits.
It sends nothing to the school, so it does not use the pacer, and its slow model calls (seconds
each) never delay a poll. Rendering as a job kind in the existing queue was considered: the queue
serializes every request behind the school's pacer, so a model call would hold up polls.

### What to render next

One query picks the next announcement: an article (not a link item) whose current revision has no
rendition for the current prompt version, first seen or listed within the last year, not resting
after an API error. Order: `late` false before true, then the list date or first-seen date, newest
first. A new first publication therefore goes before the backlog, which works through the last
year from the newest end, so the most useful renditions arrive first.
Resting announcements are kept in the loop's memory; a restart tries them again at once.

### Renditions and tags

- `rendition`: `id`, `revision_id`, `prompt_version`, `model`, `rendered_at`, `fallback`, `title`,
  `markdown`, `summary`, `deadline`; unique (`revision_id`, `prompt_version`). Earlier rows stay.
- `announcement.current_rendition` points at the newest, for the public API to read in one join.
- `tag`: (`announcement_id`, `dimension`, `tag`) primary key, `set_by` (`model` or `manual`);
  the column is not called `source` because `source` is also one of E3's dimensions.
  Storing a rendition deletes the announcement's model tags and inserts the new ones in the same
  transaction as the rendition and its `rendered` event.
- The ten-year prune deletes renditions and tags with their announcements.
- The taxonomy lives in `taxonomy.json`: dimension, stable English id, the approved label (E3).
  The JSON schema sent to the model lists the ids as enums, so labels never pass through it.

### Prompt version

The prompt is written for this service, not taken from the xincord bot's (owner, 2026-11-15). The
prompt template and the answer's JSON schema are files in the package. `PROMPT_VERSION` is an
integer next to them, and a test pins the files' SHA-256 to that version, so editing the prompt
fails the gate until the version is raised on purpose. Hashing the files into the version was
considered; it would re-render the whole last year after every wording fix.

### Model input

A reducer walks the parsed body (`bulletin.markup`) and keeps paragraphs, line breaks, lists,
tables, links, bold and images; headings become bold lines and everything else is unwrapped to its
text. It writes Markdown, pipe tables included, and replaces each link and image with `L<n>` or
`I<n>`, numbered in order of appearance and kept in a map. The attachment module follows as a list
of names with their placeholders. A converter of our own is enough for six element kinds and
avoids a dependency; the roadmap's numbers came from the same reduction.

### Model client and keys

The client ports xincord's `Api`: Gemini's `generateContent` with the key in `x-goog-api-key`, or
an OpenAI-compatible `chat/completions` with a bearer token. Gemini gets
`generationConfig.responseFormat.text` with `mimeType: APPLICATION_JSON` and the JSON schema, and
`thinkingConfig.thinkingLevel` (default `low`; the model's own default is `high`); the OpenAI
format gets a `json_schema` `response_format` with the same schema and `reasoning_effort`. Both
shapes were recorded from `gemini-4-hydrogen` (`tests/fixtures/model/`).

Keys come from `KeyRing`, ported: a sliding window per key, keys in turn, a wait when all are full.
A 429 rests that key until `Retry-After` or the end of its window. Error texts pass through the
port of xincord's `hide`, which removes keys and cuts URLs to their origin, before they are logged.
A 429, a 5xx, a timeout or a broken connection is an API error: the announcement rests for 10
minutes and no attempt is counted. Any other answer that fails a check counts as an attempt; the
three attempts run back to back, each on the next key with room.

### Answer checks, in order

1. JSON that matches the schema, tags from the taxonomy, one nature and one source.
2. Placeholders: none unknown, every image placeholder present; then each is replaced by its URL.
3. Deadline: kept only when the text holds the date in one of the forms the date finder knows
   (`2026-12-10`, `2026/12/10`, `115/12/10`, `115年12月10日`, `12月10日`, `12/10`,
   `December 10, 2026`, `10 Dec`; those without a year read in the list date's year and the
   next), after NFKC so that full-width digits count.
4. Discord fixes (E4): bare URLs wrapped as `<url>`, masked links whose text is a URL replaced by
   the URL.
5. The Discord Markdown check: a long-lived Node subprocess runs `@discord/markdown-wasm` and
   answers one JSON line per input; Python then rejects pipe tables, link targets that are not
   `http(s)` and text over 4,096 characters. A crashed subprocess is restarted and counts as an
   API error.

### Fallback

After three failed attempts the rendition is stored with `fallback` set, the announcement's title,
`[title](article URL)` as its Markdown, no summary, no deadline, and the tags left alone. It
records a `rendered` event like any rendition, so feed readers stop waiting.

### Settings

| Variable | Default | Meaning |
| --- | --- | --- |
| `BULLETIN_MODEL_KEYS` | none | Comma-separated API keys; without any, rendering is off. |
| `BULLETIN_MODEL_FORMAT` | `gemini` | `gemini` or `openai`. |
| `BULLETIN_MODEL_ENDPOINT` | `https://generativelanguage.googleapis.com/v1beta` | The API's base URL. |
| `BULLETIN_MODEL` | `gemini-4-hydrogen` | The model id. |
| `BULLETIN_MODEL_RATE` | `10` | Requests per key per minute, as the xincord bot uses. |
| `BULLETIN_THINKING_LEVEL` | `low` | Gemini's thinking level. |

### Image

A build stage runs `npm ci` for `tools/discord-markdown/` (its `package.json` and lock pin
`@discord/markdown-wasm`), and the runtime image copies the Node binary from the official
`node` slim image of the same Debian release, pinned by digest. CI installs the same Node version
for the tests that run the check.

### Measurement

`scripts/measure_rendering.py` renders 50 announcements of the corpus
(`~/IdeaProjects/bulletin-corpus`, not in the repository) with the configured model and reports
the check pass rate, tag agreement with a labelled set, deadline accuracy and requests and tokens
per article. The 50 labels are drafted first and the owner corrects them before the run.

### User-visible changes for review

- The rendition itself: the prompt's rules for titles, Markdown, summaries and deadlines, in
  Traditional Chinese.
- The fallback text: the announcement's title as a link.
- Tag ids, for example `topic/scholarships`, next to the approved labels of E3.
- The event kind `rendered` in the events feed.
- The settings above in `.env`.

## Risks / Trade-offs

- [Cost] → the owner accepts paid use without a daily cap (2026-11-15). At Google's listed paid
  price ($1.50 and $7.50 per million input and output tokens) a rendition of about 2,000 tokens in
  and 800 out costs about one cent, so a year's backlog of some 12,000 announcements would be
  about $120. 429s rest keys and never become fallbacks.
- [`low` thinking may lower quality] → the measurement compares `low` with the default before the
  backlog starts.
- [The model invents deadlines] → the date finder drops any date the text does not hold.
- [Dates the finder does not know, such as ranges written in words] → such deadlines are dropped,
  never invented; the measurement counts them.
- [Node in the image] → one pinned binary and one package; the check is a pure function, so its
  tests use recorded inputs.

## Migration Plan

1. Deploy as before; the migration adds the tables and the event kind. Without keys nothing else
   changes.
2. Put the keys of the xincord bot's configuration into the host's `.env` as `BULLETIN_MODEL_KEYS`
   and restart. New announcements render at once and the backlog follows.
3. Rollback: remove the keys and restart; renditions stay stored.

## Open Questions

- The rate per key, once the keys' limits for `gemini-4-hydrogen` are known; it is a setting.
