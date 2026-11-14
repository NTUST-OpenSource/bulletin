# Decisions

Status: **accepted**. The owner made these between 2026-11-13 and 2026-11-15, while planning the
service from the xincord `ntust_announcements` plugin. Do not re-open a decision without asking
the owner. Code and docs cite the IDs, which stay stable: a retired decision leaves its number
unused.

Markers: **[rec]** the owner followed Claude's recommendation; **[owner]** the owner's own choice.

## A. Repository and process

- **A1 Pushing** [owner]: ask the owner before every push. Commits are GPG-signed.
- **A2 Language** [owner]: English in the repository; the owner reads replies in Traditional
  Chinese. Discussion happens in Chinese, the record in English.
- **A3 OpenSpec** [rec]: one active change at a time, in the order of `docs/roadmap.md`:
  collector, rendering, public API, web frontend.
- **A4 Quality gates** [rec]: adapted from xincord. ruff `select = ["ALL"]` with documented
  ignores, pyright strict, branch coverage of at least 85%, prek hooks (ruff, pyright, no CJK in
  `*.py`, ASCII Conventional Commits, the gate on pre-push), one `scripts/gate.sh`.
- **A5 Prototype first** [owner]: the web frontend change starts only after the owner approves a
  high-fidelity interactive prototype published as an Artifact.

## B. Sources and polling

- **B1 Scope** [owner]: every RPage board of NTUST units. The 2026-11-15 survey found 64 sites
  and 445 boards; `seeds/boards.json` holds them all (see `docs/survey.md`). Sites that do not run
  RPage wait in issue #1.
- **B2 What to fetch** [rec]: the static list page 1, `/p/403-{site}-{board}-1.php`. The CMS
  caches it (about 0.1 s, 7-10 KB gzipped). The AJAX list endpoint is not cached (29 s for the
  bulletin board's page 1) and the embedded-board POST tripped the WAF.
- **B3 Tiers** [owner]: P1 weekdays 08-18 every 5 minutes, otherwise every 20; P2 15 and 60;
  P3 60 and 240; P4 daily; off. The owner's choice on 2026-11-15: P1 10 boards, P2 9, P3 19,
  P4 226, off 54, plus 127 excluded boards also off. About 2,214 requests and 21 MB a day.
- **B4 Request budget** [owner]: one global queue, one request at a time, on average no more than
  one every 2 seconds, with jitter. Hard ceiling 5 GB a day; the plan uses under 0.5% of it.
- **B5 Tiers stay editable** [owner]: the owner changes any board's tier at any time through the
  admin CLI or admin API, without a redeploy; the change applies at the next scheduling pass and
  is audited. Every discovered board stays in the registry, excluded ones included, so any of them
  can be turned on.
- **B6 Re-enabling a board** [rec]: a board turned on from off counts as not backfilled: its
  notifications follow the frontier rule (C2) and it is queued for backfill.
- **B7 Re-discovery** [rec]: once a month, walk each site's sitemap; new boards join as off and
  pending review.
- **B8 Board categories** [rec]: announcements (in the feed), news (polled, its own tab),
  regulations and forms (P4, searchable, not in the feed), course descriptions (not polled),
  excluded (banners, albums, videos, staff pages; not polled).
- **B9 Unchanged pages** [rec]: hash the parsed page 1 (ids and titles) and skip processing when
  it matches the previous poll. `Last-Modified` is useless and the server never answers 304.
- **B10 Backfill** [owner]: ten years back, at night, through static list pages, one request at a
  time.
- **B11 No browser contributions** [rec]: the school's sites send no CORS headers, so browsers
  cannot poll for the service.

## C. Detection

- **C1 Identity** [rec]: an announcement is new when its (site, article id) was never seen; its
  position on the list is ignored. Site and article id come from the list item's link, never from
  the board, because boards list other sites' articles; the board only gets a placement.
- **C2 Notify rule** [rec]: on a site whose backfill is complete, a never-seen id is a first
  publication and notify-worthy, which also covers drafts published late. Before that, and for
  ids older than ten years, notify only when the id is above the frontier of 72 hours ago or the
  list date is within 2 days.
- **C3 Paging on bursts** [rec]: when every id on page 1 is new, read further pages until a known
  id appears, at most 5 pages.
- **C4 Withdrawal** [rec]: dropping off page 1 does not mean withdrawn. Withdrawal is confirmed by
  fetching the article at its own link: a 302 to the site's home page. Articles are re-checked 1, 3, 7 and 30 days
  after they were first seen.
- **C5 Revisions** [rec]: a new revision is stored only when the content hash changes.

## D. Storage

- **D1 PostgreSQL 18 with PGroonga** [rec]: measured on 1 CPU and 1 GB, 100k documents, worst
  CJK query: pg_trgm 1,531 ms (two-character terms fall back to a sequential scan), SQLite FTS5
  trigram 416 ms, PGroonga 81 ms. Image `groonga/pgroonga:latest-alpine-18`, pinned by digest.
- **D2 No Redis** [rec]: a primary-key read takes 0.61 ms and the latest 30 announcements
  0.82 ms; HTTP caching in front covers the rest.
- **D3 Job queue in PostgreSQL** [rec]: `SELECT ... FOR UPDATE SKIP LOCKED`; no broker.
- **D4 Retention** [owner]: ten years, kept when the school withdraws an announcement. Full-text
  and title search cover all of it.
- **D5 Raw pages** [rec]: each revision keeps the raw HTML of the article body.
- **D6 Attachments** [owner]: name and URL always, from the attachment module and from links in
  the body. Files under 5 MB on a school host are stored, content-addressed by SHA-256, only while
  their announcement is within the last 365 days; a nightly job deletes older files. Stored files
  are a fallback; links point at the school.
- **D7 Capacity** [rec]: about 60,000 announcements in ten years; the database stays near 2 GB
  with the PGroonga indexes. A 62-article sample had attachments on 44% of articles and about
  330 KB of files under 5 MB per article, so the one-year file store stays near 2 GB.

## E. Rendering

- **E1 Model** [owner]: any OpenAI-compatible endpoint; the default is gemma-4-E4B on
  llama-server running natively on the host. The rendering change compares 2-3 models on 50
  articles before fixing the default.
- **E2 What gets rendered** [owner]: announcements from the last year, and every new one. Older
  backfilled announcements stay raw.
- **E3 Tags** [owner]: four dimensions plus an extracted deadline. The Chinese labels are the
  approved UI text.
  - Topic, several allowed: scholarships, competitions and calls, talks and events, courses,
    enrolment and grades, exams and certification, fees, housing, internships and jobs,
    international exchange, research projects, admissions, venue and service changes, safety
    and health, IT systems, military service, clubs and volunteering, rules and policy, honours,
    free food.
    Labels: 獎助學金, 競賽徵件, 講座活動, 課程選課, 學籍成績, 考試檢定, 繳費, 住宿, 實習就業, 國際交流,
    研究計畫, 招生, 場地與服務異動, 安全健康, 資訊系統, 兵役, 社團志工, 法規制度, 榮譽賀訊, 免費餐點.
  - Audience, several allowed: all students, undergraduates, graduate students, new students,
    graduating students, international students, staff, the public.
    Labels: 全體學生, 大學部, 研究生, 新生, 畢業生, 國際生, 教職員, 校外.
  - Nature, one: action required, lists and results, information, news and records.
    Labels: 需要行動, 名單結果, 資訊宣導, 新聞紀錄.
  - Source, one: on campus, forwarded from outside. Labels: 校內, 轉知校外.
- **E4 Discord Markdown first** [owner]: the rewrite targets Discord's Markdown. Output passes
  deterministic fixes, then the `@discord/markdown-wasm` parser in a Node subprocess; failures
  retry the model up to 3 times, then fall back to the title and the link.

## F. Public API and frontend

- **F1 Domain** [owner]: `bulletin.ntust.org`; the frontend at `/`, the API under `/api/v1/`.
- **F2 API shape** [rec]: read-only JSON, no authentication, cursor pagination, ETag, CORS `*`
  on reads. Endpoints: announcements (filters: site, board, tag, query, time), one announcement
  (raw and rendition), events after a cursor, boards, tags. No SSE or webhooks for now.
- **F3 Caching** [rec]: `Cache-Control: max-age=60, stale-while-revalidate=600`, ETag from the
  latest event id, and a Cloudflare cache rule for `/api/*`.
- **F4 Rate limiting** [rec]: in the application, per client IP taken from the proxy chain, on
  the endpoints a cache cannot answer (search). It is versioned and tested with the code, and
  internal clients on `proxy-net` are exempt; a Cloudflare rule would live outside the repository.
- **F5 Frontend** [rec]: a Svelte 5 + Vite static SPA over the public API. Settings live in the
  browser: theme, rendition or raw, hidden boards. Export copies JSON, downloads it, or copies a
  link carrying the settings after `#`; opening such a link applies them at once when the viewer
  never changed theirs, and otherwise asks before overwriting all of them.

## G. Deployment

- **G1 Host** [owner]: the owner's machine, Docker Compose project `bulletin`, following
  `~/selfhost/Docker/tigerduck-backend` on that host. Cloudflare and nginx-proxy-manager terminate
  TLS; no Caddy. No host ports: the API container `bulletin-internal` joins the external
  `proxy-net`; PostgreSQL sits on an internal bridge.
- **G2 Egress** [owner]: the host polls the school from a Chunghwa Telecom address. Every request
  names the bot in its User-Agent.

## H. Integrations

- **H1 tigerduck** [rec]: tigerduck keeps its bulletin tables and `/v3` API and replaces its
  scraper with bulletin's events feed, read over `proxy-net`
  (tigerduck-app/tigerduck-backend#248).
- **H2 xincord** [rec]: the `ntust_announcements` plugin moves to the events feed once it exists;
  a separate xincord issue tracks it then.
