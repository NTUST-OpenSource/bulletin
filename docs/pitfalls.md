# Pitfalls and verified facts

What the planning survey of 2026-11-13 to 2026-11-15 checked against the live sites and the tools.
Re-check a fact before relying on it for something new; the school changes its CMS without notice.

## The school's CMS (RPage)

- URL patterns:
  - `/p/403-{site}-{board}-{page}.php`: a board's list, page by page.
  - `/p/406-{site}-{article}.php`, optionally `/p/406-{site}-{article},r{board}.php`: an article.
  - `/p/404-{site}-{article}.php`: the same article; `404-1000-153631` and `406-1000-153631`
    served the same page on 2026-11-15. The secretariat's board lists news this way.
  - `/p/450-{site}-{article},c0.php`: a pointer to another site's article. The school-wide bulletin
    board lists cross-posts this way; `450-1045-152885,c0` answers 302 to
    `https://she.ntust.edu.tw/p/406-1068-152869,r1497.php`.
  - `/p/412-{site}-{n}.php`: a free-form page; `/p/17-{site}.php`: the site map.
  - `POST /app/index.php?Action=mobilercglist` with `Rcg`, `Op=getpartlist` and `Page`: the list as
    AJAX. It needs `X-Requested-With` and `Referer`.
- A list page past the last one answers 302 to `/`, like a withdrawn article
  (`403-1070-1626-50`, 2026-11-15). The pager states the page count: `共<span>385</span>頁`.
- The site map links free-form pages (`412`) and menus, not lists: student affairs' site map
  (`17-1053`) had 147 `412` links and no `403` link, and named one board only in a menu script.
- Menus are loaded by AJAX, so a site's home page does not link every board. Boards also show up
  as `name:'Rcg',value:` and `Type=mobile_rcg_mstr&Nbr=` in scripts, and as `,r{board}` in
  article links.
- The static list page 1 is cached by the CMS: about 0.1 s and 7-10 KB gzipped. Deeper pages take
  5-8 s, so they are generated on request. The AJAX list is never cached: the bulletin board's
  page 1 took 29 s.
- `Last-Modified` is the time the page's cache entry was built, and global cache purges change it
  too. HEAD responses carry none. The server never answers 304.
- Article ids are one global sequence across all sites (about 33 a day; near 153,700 in November
  2026). An id belongs to exactly one site. A cross-post on another site gets a new id.
- Board numbers are not unique: board 1927 exists on 8 sites. A board is (site, board number).
- A withdrawn article answers 302 to the site's home page. So does an article id requested under
  the wrong site: `406-1063-153625` redirects home although `406-1000-153625` exists. The three
  "withdrawn" articles of the survey's sample were all this wrong-site case. The first real
  withdrawals seen were 152457 (listed by board 1059-763) and 146159 (board 1017-1), which
  redirected home under their own site and under 1000 on 2026-11-15.
- A board can list another site's articles. The secretariat's board 1063-2211 links to
  `https://www.ntust.edu.tw/p/406-1000-153625,r167.php`. Take the article's host, site and board
  from the list item's href, never from the board being polled.
- A list item whose href is not a `406` page links straight to a file or another website.
- List order is not reliable:
  - 38 boards list old articles above the newest one, and the HTML has no pin marker.
  - 68 boards are not in time order at all.
  - 5 boards list old articles again under a new date (recycled articles), for example article
    91282 on board 1019-17, dated 2026-11-12.
- Some boards publish no dates in the list.
- When an announcement on page 1 is withdrawn, the first item of page 2 moves up to page 1. It is
  not new (the owner's xincord plugin once notified for such an item).
- On the school-wide bulletin board (site 1045, board 1391), about 12% of items link straight to a
  file or another site instead of an article.
- The school-wide bulletin board's table has a publisher column, `data-th="發佈單位"`.
- The list's date is the date an office chose, not the publication time. Article ids appear to be
  assigned when a draft is created, so a draft published weeks later carries an old id and a fresh
  date.

## The network

- Every NTUST host resolves to 140.118.31.124, behind one WAF. A POST to
  `Action=mobileloadmod&Type=mobile_rcg_mstr` was blocked with HTTP 406 (`WAF` in the body).
- HEAD on attachment files answers 403. A GET with `Range: bytes=0-0` answers 206, and the total
  size is in `Content-Range`.
- The certificate covers `*.ntust.edu.tw`, one level of subdomain only. The servers speak HTTP/2.
- Python 3.13+ adds `VERIFY_X509_STRICT` to `ssl.create_default_context()`; NTUST hosts fail it
  with `Missing Subject Key Identifier`. Clear only that flag, only for them.
- `www.academic.ntust.edu.tw` leaves TWCA's intermediate out of its chain (`unable to get local
  issuer certificate`). xincord ships it as `twca-secure-ssl-ca.pem` (valid until 2030-10-16);
  tigerduck fetches it through the leaf's AIA URL instead.
- Cloudflare's Web Analytics, on by default for proxied sites, injects
  `static.cloudflareinsights.com/beacon.min.js` into HTML answers, which a strict CSP then blocks
  (seen on bulletin.ntust.org, 2026-11-16). `Cache-Control: no-transform` stops the injection.

## Attachments

- Most attachments sit in a module after the article body, not in the body:
  `<div class="module module-ptattach">` holds `<ul class="mptattach">`, whose links point at
  `/app/index.php?Action=downloadfile&file=<token>&fname=<token>`. The file name is the link text,
  and also in `Content-Disposition`.
- `downloadfile` ignores `Range`: it answers 200 with the whole file. Read the headers for
  `Content-Length`, then close the connection.
- Links in the body to `/var/file/{n}/{site}/img/...` honour `Range: bytes=0-0` (206 with
  `Content-Range`). Such files may sit on another school host than the article
  (`rd-r.ntust.edu.tw`).
- In 62 recent articles, 27 (44%) had attachments in the module: 42 files, median about 330 KB,
  34.3 MB in all, two over 5 MB (5.7 MB and 7.9 MB). Files under 5 MB come to about 330 KB per
  article. An earlier count of 14% looked only at the body and was wrong.

## Discord Markdown

Checked with the `@discord/markdown-wasm` 0.15.0 parser:

- A masked link whose text contains `http://` or `https://` renders literally.
- A bare URL followed directly by CJK text or full-width punctuation swallows that text into the
  link. Wrap bare URLs as `<url>`.
- Headings exist for `#` to `###` only; `-#` is small text. Lists use `- ` or `1. `, nested by two
  spaces. Tables and images do not exist.
- `__underline__` next to CJK characters does not parse.
- Never emit `@everyone`, `@here` or other mentions.
- A masked link after punctuation renders fine.
- A link whose host holds a `%` escape or non-ASCII text does not parse; userinfo, ports, IPs,
  underscores and punycode do. School pages link to such hosts (`http://` before Chinese text,
  `name@mail.ntust.edu.tw%20/`) and to `http:// https://host/` (2026-11-16).

## Gemini

Checked against Google's documentation and two recorded answers on 2026-11-15:

- `gemini-4-hydrogen` is a stable model id. Its context window is 1,048,576 tokens, input and
  output together; output defaults to at most 65,536 tokens.
- `thinkingLevel` takes `low`, `medium`, `high` (the default) or `xhigh`; `minimal` is an error
  and thinking cannot be turned off. Sending `thinkingBudget` with it is a 400. At `low`, a
  213-token prompt still used 243 thinking tokens (`usageMetadata.thoughtsTokenCount`), billed as
  output.
- REST `generateContent` takes the JSON schema as
  `generationConfig.responseFormat.text.{mimeType: "APPLICATION_JSON", schema}`; nullable fields
  as `"type": ["string", "null"]` are accepted. Google calls `generateContent` legacy next to the
  Interactions API, but supports it.
- A text part may carry a `thoughtSignature` beside its `text`; thought summaries come only with
  `includeThoughts` and are marked `thought: true`.
- The OpenAI-compatible endpoint is `https://generativelanguage.googleapis.com/v1beta/openai/`;
  it takes a strict `json_schema` `response_format` and `reasoning_effort`, which maps to the
  thinking level.
- The rate-limit page lists no limits for `gemini-4-hydrogen`; a 429 `RESOURCE_EXHAUSTED` comes
  with no documented `Retry-After`.
