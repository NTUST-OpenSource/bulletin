# The 2026-11 board survey

`seeds/boards.json` is the board registry's starting point. It came from a one-off survey run
between 2026-11-13 and 2026-11-15, one request at a time, from scripts that were not kept.

## How it was produced

1. Sites: the unit lists on `www.ntust.edu.tw` (administrative and academic units) and the
   school-wide bulletin board's publishers, then each site's home page, site map
   (`/p/17-{site}.php`) and free-form pages.
2. Boards: every board number found in list links (`403-{site}-{board}`), article links
   (`406-...,r{board}`) and menu scripts (`name:'Rcg',value:`, `Type=mobile_rcg_mstr&Nbr=`).
3. Each board's page 1 was fetched once for its name, page count, article ids and dates. Busy
   boards were paged back one year through the AJAX list to measure their rate.
4. Categories come from the board name: banners, albums, videos, FAQs and staff or profile pages
   are `excluded`; regulations, forms and downloads are `regulation`; news, media coverage,
   honours and activity records are `news`; General Education's course areas are `course`; the
   rest are `announcement`.
5. Tiers are the owner's choices in the survey's review page on 2026-11-15. Boards the owner did
   not see, the excluded ones, are `off`.

## What it holds

445 boards on 64 sites:

| Tier | Boards |
| ---- | -----: |
| P1   |     10 |
| P2   |      9 |
| P3   |     19 |
| P4   |    226 |
| off  |    181 |

| Category     | Boards |
| ------------ | -----: |
| announcement |    226 |
| course       |      5 |
| news         |     44 |
| regulation   |     43 |
| excluded     |    127 |

Each entry: `site_id`, `rcg` (the school's board number), `host`, `unit` and `name` as the school
publishes them, `category` and `tier`. Categories are a first guess from the name. The owner set
the course boards (1076-1541 to 1076-1545) to P4, so they are polled despite decision B8.

Sites that do not run RPage are not in the seed; issue #1 tracks them.
