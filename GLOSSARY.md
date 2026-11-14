# bulletin

The announcements that NTUST offices and departments publish on their own websites, collected
into one archive that outlives the school's own pages.

## Sources

**Site**:
One website of a school unit, identified by the school's numeric site id.
_Avoid_: website, unit, domain

**Unit**:
The office, college or department that owns a site or signs an announcement.
_Avoid_: department (when an office is meant), publisher

**Board**:
One list of announcements on a site, identified by the site and the school's board number
together, since the same board number recurs on different sites.
_Avoid_: page, category, rcg, channel

**Board category**:
What a board carries: announcements, news, regulations and forms, or content that is not
announcements at all (banners, albums, staff pages), which is excluded.
_Avoid_: type, kind

**Tier**:
How often a board is polled, from P1 (most often) to P4 (daily), or off.
_Avoid_: priority, weight, importance

## Announcements

**Announcement**:
One article as the school published it on one site, identified by that site and the school's
article id.
_Avoid_: post, bulletin, notice, news item

**Placement**:
An announcement appearing on a board; one announcement can be placed on several boards, also on
boards of other sites, which list it under its own site and article id.
_Avoid_: listing, entry

**Cross-post**:
A copy of an announcement that the school published on another site under a different article
id, such as the school-wide bulletin board's copy of an office's announcement.
_Avoid_: duplicate, repost

**Revision**:
The content of an announcement as fetched at one time; a new revision exists only when the
content changed.
_Avoid_: version, snapshot, edit

**Attachment**:
A file an announcement links to on a school host.
_Avoid_: file, document

**Withdrawn**:
The state of an announcement the school took down; bulletin keeps it and marks it.
_Avoid_: deleted, removed, hidden

**Recycled article**:
An old announcement that a board lists again with a new date, keeping its article id.
_Avoid_: bumped post, repost

**Pinned announcement**:
An older announcement that a board keeps above newer ones; the school's pages do not mark it.
_Avoid_: sticky

## Discovery

**First publication**:
The moment an announcement becomes public on the school's site for the first time, which can be
long after the school assigned its article id, for a draft published late.
_Avoid_: new post (ambiguous with first seen)

**Late discovery**:
An announcement bulletin first sees well after its first publication, such as one on a board that
was off; it does not count as news.
_Avoid_: old post, stale post

**Frontier**:
The highest article id bulletin had seen at a given moment; ids above an older frontier belong to
announcements published since then.
_Avoid_: watermark, cursor

**Backfill**:
Walking a board's older pages to record every announcement it has published, up to ten years
back.
_Avoid_: crawl, import, history sync

**Event**:
A recorded change to an announcement that clients can follow: published, revised, withdrawn or
restored.
_Avoid_: notification, update, message

**Notify-worthy**:
An event that clients should announce to people: the first publication of an announcement, not a
late discovery, a recycled article or a cross-post already announced.
_Avoid_: important, alert

## Presentation

**Rendition**:
A model-written version of a revision: the rewritten text, a summary, an extracted deadline and
tags.
_Avoid_: rewrite, LLM output, translation

**Tag**:
A label from one of four fixed dimensions: topic, audience, nature and source.
_Avoid_: label, category, importance
