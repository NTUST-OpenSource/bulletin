# Proposal: add-rendering

## Why

The collector now keeps every announcement as the school wrote it: uneven HTML, bracketed tags in
titles, deadlines buried in the text, no way to filter by topic. Readers, the frontend and Discord
need one clean, consistent version of each announcement with a summary and tags, made once and
kept next to the raw text.

## What Changes

- A rendering loop in the service that rewrites announcements with a model: a title without
  bracketed tags, Discord Markdown, a summary, a deadline when the text states one, and tags from
  the fixed taxonomy (E3). It renders every new announcement and those from the last year (E2);
  older ones stay raw.
- A model client for Gemini's API and for an OpenAI-compatible one, with `gemini-4-hydrogen` as
  the default model and several API keys used in turn (E1).
- Model input built from the article's body and attachment module by selector, reduced to
  Markdown, with links and images replaced by placeholders that are put back after the model
  answers, so the model never copies a URL and every image stays in place.
- Output checks: JSON constrained by a schema, deadlines that must appear in the source text, and
  Discord Markdown fixed and validated with `@discord/markdown-wasm`; three failed attempts fall
  back to the title and the link (E4).
- Renditions tied to a revision and a prompt version, so a new revision or a new prompt renders
  again; tags stored per announcement with their source.
- A `rendered` event in the event log, so feed readers know when an announcement's rendition is
  ready.

Out of scope: serving renditions and tags (`add-public-api`), the frontend (`add-web-frontend`),
posting to Discord (xincord, H2), editing tags by hand (the schema keeps the `manual` source for
it), rendering attachments' contents, and announcements older than a year.

## Capabilities

### New Capabilities

- `rendering`: which announcements are rendered and in what order, the model input, the model
  client and its keys, output checks, fallback, and renditions tied to revisions and prompt
  versions.
- `tags`: the fixed taxonomy of four dimensions and how tags are stored per announcement with
  their source.

### Modified Capabilities

- `event-log`: a new `rendered` event kind, which is never notify-worthy.

## Impact

- Code: a model client, the input reducer and Markdown converter, the Discord Markdown checks, the
  rendering loop beside the worker in `bulletin serve`, and the taxonomy as data.
- Database: a migration adding `rendition` and `tag` tables and the `rendered` event kind.
- Dependencies: Node.js and a pinned `@discord/markdown-wasm` in the image for the validator
  subprocess; no new Python dependency for HTTP (aiohttp is there).
- Configuration: model keys, endpoint, format, model, rate limit and thinking level from the
  environment; without keys the service runs the collector only. The deployment on the owner's
  host gets the keys of the xincord bot's configuration in its `.env`.
- Traffic: requests go to Google's API, not to the school, so the school's request budget (B4)
  is untouched.
