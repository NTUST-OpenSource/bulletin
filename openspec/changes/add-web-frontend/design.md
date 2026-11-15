# Design: add-web-frontend

## Context

See proposal.md for why. The approved prototype is the Artifact "bulletin 台科大公告"
(`https://claude.ai/artifact/2R23e2rDthvAqmog4xvkB9`), a single HTML file with the layout,
tokens, copy and interactions; `docs/roadmap.md` section 4 lists what its review decided. F5 fixes
Svelte 5 + Vite and browser-side settings, F6 the icons. The data comes from the public API of
`add-public-api`, active beside this change (A3); until it is deployed, tests and development use
fixtures in its specified shapes, recorded from production renditions.

The prototype keyed units by name and filtered a fixed list in the browser. The real stream is
ten years deep, so filtering moves to the API and units are keyed by site id. An announcement can
sit on several boards (338 in production), also through cross-posts and on other sites' boards,
so "its board" and "its unit" are sets in the frontend.

## Goals / Non-Goals

**Goals:**

- The prototype's look and behaviour on real data, at desktop width and at 375 px.
- A first page that works from Cloudflare's cache for readers with the default units.
- Settings that survive bad input: a stale board, a hand-edited file, an old link, an API outage.

**Non-Goals:**

- Server-side rendering, offline use, a service worker.
- Showing deadlines or filtering by action (roadmap section 4), showing revision history.
- Supporting browsers without `<dialog>`, `IntersectionObserver` or CSS `position: sticky`.

## Decisions

### Layout of `web/`

```
web/
  index.html
  package.json, bun.lock, vite.config.ts, tsconfig.json, playwright.config.ts
  src/
    main.ts, App.svelte
    lang/zh-TW.ts            all UI copy (exempt from the English rule, AGENTS.md)
    lib/                     pure TypeScript, tested with Vitest
      api.ts                 typed fetches of /api/v1, the stream query from settings
      settings.ts            defaults, reading, storage, export and import
      markdown.ts            the Discord Markdown subset to escaped HTML
      raw.ts                 the school's HTML through DOMPurify, links and images fixed
      stream.ts              day grouping, merging polled pages, cursor state
      csp.ts                 the page's policy, used by the build and by `vite preview`
    components/
      stream/                Stream, DaySection, Item, TopicChips, UnitMenu
      article/               Article, Attachments, Preview
      settings/              Settings, UnitPicker, Onboarding, ImportDialog
      ui/                    Dialog, Sheet, ContextMenu, Toast, Icon wrappers
    styles/tokens.css        the prototype's tokens, light and dark
  tests/                     Playwright specs and API fixtures
```

Svelte 5 runes hold the state: one settings store backed by `localStorage`, one stream store per
query. No router library: the app reads `location` on load and on `popstate`, and pushes
`/a/{id}` when an article opens.

### Package manager

Bun installs the frontend's packages from `bun.lock` and runs its scripts (the owner's choice on
2026-11-15; pnpm if Bun cannot). Vite, Vitest and Playwright keep their own runtimes: `bun run`
starts their binaries, which run on Node where Node is installed and on Bun in the image's build
stage. `tools/discord-markdown`, a checker run by the service rather than a frontend, keeps npm.

### Serving and the page's policy

The image builds `web/` in a Bun stage (`bun install --frozen-lockfile && bun run build`) and
copies `web/dist` to
`/app/web`. `public_app` mounts it at `/` after `/health` and `/api/v1`: files under `assets/`
(hashed by Vite) get `Cache-Control: public, max-age=31536000, immutable`; `index.html`, also
for `/` and `/a/{id}`, gets `no-cache`. Other unknown paths are 404.

The policy lives in the page, so `vite preview`, which Playwright drives, enforces exactly what
production does. A build-only Vite plugin writes it into `index.html` as a `<meta
http-equiv="Content-Security-Policy">` (development keeps Vite's inline client working):

```
default-src 'self'; img-src 'self' https: data: blob:; style-src 'self' 'unsafe-inline';
frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'
```

`frame-ancestors` has no effect in a meta tag, so `public_app` sends `Content-Security-Policy:
frame-ancestors 'none'` with `index.html` only, never with API answers or stored files, and
`vite preview` sends the same header. The PDF preview frames a same-origin file whose answer has
no policy, so it is unaffected.

- `img-src https:`: school pages also embed images from other hosts; the page shows what the
  school's page shows.
- `style-src 'unsafe-inline'`: Svelte's transitions write inline styles.
- Bricolage Grotesque comes from `@fontsource-variable/bricolage-grotesque`, the Latin subset
  only; CJK text uses the system's PingFang TC or Noto Sans TC, as in the prototype.

In development, `vite` proxies `/api` to a local `bulletin serve` or to `bulletin.ntust.org` once
the API is deployed.

### Stream queries from settings

The request is built from the settings and the current filters, each list sorted, so readers
with the same settings send the same URL and share Cloudflare's cache:

- `site=<id>` for each followed site with no hidden board among the sites list's boards,
  `board=<key>` for each visible board of a followed site with one;
- the unit menu narrows that to one site, by the same rule, so its hidden boards stay out;
- `tag=topic:<id>` for a selected chip;
- search drops the followed sites, keeps the chip and the unit menu, and adds `q` and `in`.

Units, boards and topics the API does not list are left out of the request. With no followed
unit left, no request is sent and the stream shows the prototype's empty state. The page's
query string holds `q`, `in`, `topic` and `unit`, replaced as they change.

### Day headings and items

Items are grouped by the API's `day`; a group continues across pages when the next page starts
on the same day. Headings are `position: sticky` and read as in the prototype (`11月13日 週五`,
the year added for other years). The column is 880 px wide, wider than the prototype's 760 px
(roadmap section 4). An item's source line is the publisher, else the name of the first board in
`boards` the reader follows and has not hidden, else the first board; the foot shows the unit and,
when withdrawn, 已刪除 muted at its bottom right, left of the unit.

### Polling and paging

- Every 5 minutes while `document.visibilityState` is `visible`, and once when the tab becomes
  visible after more than 5 minutes, the stream refetches its first page with
  `fetch(url, {cache: "no-cache"})`, which revalidates with the ETag (a 304 when nothing
  changed) instead of taking the browser's stale-while-revalidate copy. Opening an article does
  the same.
- Merging by the stream's order `(day, id)`: polled items already shown replace their shown
  copy, so a rewrite that arrived shows; unseen items are inserted where their `(day, id)`
  falls among the shown ones. When the polled page holds no shown item, the stream follows its
  cursor until a page overlaps (at most 5 pages), and otherwise starts over from the first page.
- Appended pages skip ids already shown, which covers an undated article moved overnight.
- Before inserting, the stream records the first item intersecting the viewport and its offset;
  after Svelte renders, it scrolls by the difference, so the reader's item stays put. CSS
  `overflow-anchor` would do this, but Safari does not implement it. New items get the
  prototype's `arrive` animation, which reduced motion turns off.
- A poll while an article or a search is open updates the stream underneath; closing returns to
  it with the same rule.

### Articles and their paths

- An item opens `/a/{id}` with `pushState`; Esc, the close button and back return. When the page
  was entered at `/a/{id}` with no earlier entry of this site in the history, the close button
  replaces the state with `/` (and the current filters) instead of going back off the site.
- A first visit through `/a/{id}` shows the article first and starts the unit picker when it
  closes.
- A cross-post's path loads it, then replaces the path with its original's and shows that.
- Link items (`link_item`) open their URL in a new tab from the stream; their path redirects
  there too.
- The article shows the source line, title, `11月13日 週五 · unit · 已刪除`, the summary, the body,
  attachments and the topic and audience tags as chips; a topic chip closes the article and filters
  the stream by it, as in the prototype. The article's menu toggles the rewrite and the school's
  version, copies the link and opens the school's page.

### Rendering article text

- The rewrite is Discord Markdown. `markdown.ts` ports the prototype's renderer, which covers what
  the prompt produces and the Discord check accepts: paragraphs, `- ` and `1. ` lists nested by
  two spaces, `# ` to `### ` headings, `-# ` subtext, `> ` quotes, `**bold**`, `*italic*`,
  `~~strike~~`, `` `code` ``, `[text](url)`, `<url>`, images and bare URLs. It escapes all text
  first and emits only those constructs, and links and images only for `http:` and `https:`
  URLs; anything else stays text. Vitest covers `javascript:`, `data:` and nested-bracket cases.
- The school's HTML goes through DOMPurify with `<style>`, `<link>`, `<form>` and the `style`,
  `class` and `id` attributes forbidden, so the school's CSS cannot restyle the page; hooks copy
  `data-src` to `src`, resolve relative `href` and `src` against the article's URL, keep only
  `http:`, `https:` and `mailto:` links, add `target="_blank" rel="noopener noreferrer"`, wrap
  tables for scrolling inside the article, and turn URLs in text nodes into links.
- Images load lazily and open the image preview on click.

### Attachments and previews

An attachment's name is an `<a href>` to the school's URL (D6), so the browser's save-link menu
saves the school's file. A left click on an attachment with a `file` path opens the preview
instead, for images, PDFs and DOCX only; other stored types follow the school's link:

- images with zoom (wheel, pinch, buttons) and arrows across all the article's images;
- PDFs in an `<iframe>` of the stored file, which the API serves inline; where
  `navigator.pdfViewerEnabled` is false (Android, iOS Safari), the stored file opens in a new tab;
- DOCX through `mammoth`, imported only when needed, then the same DOMPurify settings.

The preview's download button is an `<a download>` on the stored copy. A preview that fails
(a pruned file, a corrupt DOCX) says so and offers the school's link. When the attachments hold
exactly one image, it is shown after the text.

### Settings

```ts
type Settings = {
  version: 1;
  theme: "system" | "light" | "dark";
  prefer: "rendition" | "raw";
  sites: number[];            // followed, by site id
  hiddenBoards: string[];     // board keys
  topicOrder: string[];       // topic ids
};
```

- Saved as JSON under `localStorage["bulletin.settings"]`; its presence means the reader has
  saved settings. Every access is guarded, so a blocked storage gives a working page with default
  settings that are not kept.
- Reading checks types only: a wrong field falls back to its default. Ids are kept as they are;
  the request builder and the views ignore the ones the API does not list, and topics missing
  from `topicOrder` follow in the default order. Storage is written only when the reader changes
  settings or imports, so an outage of `/api/v1/sites` or a board that is off for a while
  changes nothing.
- The defaults follow site ids 1045, 1053, 1060, 1049, 1070 and 1051, the six P1 units, and order
  topics as the prototype did, with the library after IT systems.
- A settings link is `https://bulletin.ntust.org/#s=<base64url JSON>`, as in the prototype; the
  app removes the fragment after reading it, so a reload does not ask again.

### Context menu and long press

`contextmenu` events, a 500 ms touch hold without movement, and the menu key or Shift+F10 on a
focused item open the menu; at 640 px and below it is a bottom sheet. Its entries follow the
prototype: `隱藏「board」` for each board the item is shown through, `不再關注「unit」` for each
followed unit among those boards, `關注「unit」` for the item's own unit when it is not followed
(search results), then `複製連結` and `開啟原網頁`. Undo restores the settings from before that
change.

### Dragging topic chips

Pointer events move a chip within its row and drop it between neighbours; on a focused chip,
Alt+Left and Alt+Right move it by one. The new order saves at once. No library: the row is one
line of fixed items.

### Search input

The box searches 300 ms after the last `input` event, and not while `isComposing` is true; a
`compositionend` starts the wait, so zhuyin and pinyin send one search per committed word.
Enter searches at once. The box caps input at 100 characters and the request at the first 10
words, the API's limits, so a search never fails for its length.

### Tests

- Vitest covers `lib/`: settings reading, export and import round trips, the stream query from
  settings, day grouping, merging polled pages, the Markdown renderer and the raw HTML hooks (in
  jsdom).
- Playwright runs the scenarios that need a browser against `vite preview`, which serves the
  built page with its production policy, with `/api/v1` answered from fixtures by route
  interception, in Chromium at 1280 px and at 375 px. PDF tests use full Chromium
  (`channel: "chromium"`), since the default headless shell has no PDF viewer, and assert
  `navigator.pdfViewerEnabled` first. Fixtures hold recorded production items
  plus extreme ones: three-digit counts, a 200-character title without spaces, a 120-character
  file name, long URLs, an item on two followed boards, a cross-post, a link item.
- A pytest test checks that `public_app` serves `index.html` for `/` and `/a/{id}` with
  `frame-ancestors 'none'` and the cache headers, and the hashed assets as immutable.
- The gate runs `bun install --frozen-lockfile`, `svelte-check`, Vitest with coverage of `lib/`
  of at least 85% and `vite build`. CI adds a Playwright job with cached browsers; locally
  `bun run e2e`.

### User-visible changes for review

The copy, layout and interactions are the approved prototype's, with these changes:

- The column is 880 px wide (prototype 760 px; roadmap section 4 asked for wider).
- Units are keyed by site id; the defaults are the same six units.
- Every topic chip shows, in the reader's order; the prototype showed only topics present in its
  sample, and nearly every topic is present in ten years of announcements. The default order is
  the prototype's with 圖書館 after 資訊系統.
- Articles have their own address, `/a/{id}` (the prototype used `#a-<site>-<id>`), and the
  search, topic and unit filters live in the page's address.
- The context menu lists one hide and one unfollow entry per board and unit the item is shown
  through, so an item on two followed boards offers both.
- Link items open their link from the stream instead of an empty article.
- Search waits 300 ms (prototype 150 ms) and for input methods to finish.
- New copy, for failures the prototype did not have:
  - `無法載入公告` with a `重試` button
  - `搜尋太頻繁，請稍後再試`
  - `找不到這則公告`
  - `無法預覽` with a `開啟原檔` button

## Risks / Trade-offs

- [The API's shapes change while both changes are active] -> The frontend's types mirror the
  `public-api` spec; a change there updates the fixtures and types in the same commit.
- [School images are large (one measured 3.9 MB) and have no known dimensions] -> Lazy loading
  and a reserved aspect box once loaded; the stream shows no images.
- [Hotlinking may be refused by the school later] -> The school's version still shows text;
  images then show their alt text.
- [Mobile PDF behaviour is from documentation, not measured; iOS may report a PDF viewer and
  show only the first page in a frame] -> The owner opens a stored PDF on an iPhone and an Android
  phone (task 6.3); if iOS shows one page, iOS opens PDFs in a new tab too.
- [Playwright in CI is slow] -> It runs as its own job, not in the pre-push gate.

## Migration Plan

No data migration. The image gains `/app/web`; deploying it serves the page at `/` on the
existing proxy host. Rolling back the image removes the page; settings in readers' browsers stay
and load again later.

## Open Questions

None.
