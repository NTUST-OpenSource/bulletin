# web-frontend Specification

## Purpose
The web page at `bulletin.ntust.org`: one stream of the announcements of the units a reader
follows, the rewritten or the school's version of each, search across the archive, and settings
kept in the reader's browser.

## Requirements

### Requirement: The page
The public listener SHALL serve the frontend at `/` and at article paths `/a/{id}`, with the tab
title `bulletin. | 臺科大公布欄`. Built files with a content hash in their names SHALL be cached as
immutable, the page itself revalidated on every load. The page SHALL load no script, style or
font from another origin, and SHALL not be framed by other sites.

#### Scenario: An article link
- **WHEN** a reader opens `/a/2412` directly
- **THEN** the page loads with that article open over the stream

#### Scenario: A new release
- **WHEN** a new build is deployed and a reader reloads
- **THEN** the page references the new built files

#### Scenario: A stored PDF under the page's policy
- **WHEN** the built page, served with its production policy, previews a stored PDF
- **THEN** the PDF shows, and the browser reports no policy violation

### Requirement: First visit
A reader without saved settings and without a settings link SHALL first pick their department
from the academic units, grouped by college, then other units from the school-wide and
administrative ones, where six are preselected: the school-wide bulletin board, student affairs,
international affairs, the library, the language center and the center for teaching and learning
development. Finishing SHALL save the settings. An article link SHALL open its article first.

#### Scenario: Picking a department
- **WHEN** a new reader picks the electronic and computer engineering department, keeps the six
  preselected units and finishes
- **THEN** the stream shows those seven units and the settings are saved

#### Scenario: A new reader opens an article link
- **WHEN** a reader without saved settings opens `/a/2412` and closes the article
- **THEN** the article shows first and the unit picker follows

### Requirement: The stream
The stream SHALL list announcements placed on a board of a followed unit that the reader has not
hidden, newest day first, under day headings pinned while scrolling. Each item SHALL show its
source, title, summary, unit and, when withdrawn, a muted 已刪除 mark at its bottom right. Titles
and summaries SHALL be the rewrite's when one exists and the reader prefers it. Without followed
units the stream SHALL offer the unit picker.

#### Scenario: A hidden board
- **WHEN** a reader follows a unit but hid one of its boards
- **THEN** announcements placed only on that board are not shown

#### Scenario: A withdrawn announcement
- **WHEN** an announcement in the stream was withdrawn by the school
- **THEN** it stays in the stream with the 已刪除 mark

#### Scenario: No rewrite yet
- **WHEN** an announcement has no rendition
- **THEN** the item shows the school's title and no summary

#### Scenario: Nothing followed
- **WHEN** a reader unfollowed every unit
- **THEN** the stream asks them to pick units and requests no announcements

### Requirement: Topic chips and unit filter
Above the stream, topic chips SHALL filter it by one topic at a time, in the reader's topic
order, which the reader SHALL be able to change by dragging a chip or with the keyboard, here and
in the settings. A unit menu SHALL narrow the stream to one followed unit, keeping its hidden
boards hidden.

#### Scenario: Filtering by topic
- **WHEN** a reader selects the scholarships chip
- **THEN** only announcements tagged scholarships are listed

#### Scenario: Reordering topics
- **WHEN** a reader drags the free-food chip to the front
- **THEN** it stays first after a reload, in the stream and in the settings

#### Scenario: One unit with a hidden board
- **WHEN** a reader narrows the stream to a unit one of whose boards they hid
- **THEN** that board's announcements stay out

### Requirement: Paging and new announcements
Scrolling near the end SHALL load the next page by cursor until none remains, never showing an
item twice. While the tab is visible, the page SHALL check for new and changed announcements
every 5 minutes, bypassing cached answers, and put new ones in their place in the order with an
animation, without moving the item the reader is looking at.

#### Scenario: Reaching the end of a page
- **WHEN** a reader scrolls to the last of 30 items and more exist
- **THEN** the next 30 load below without a repeated item

#### Scenario: A new announcement while reading
- **WHEN** a new announcement arrives while the reader looks at an item halfway down
- **THEN** it appears in its place near the top and the item stays where it was on screen

#### Scenario: A rewrite arrives
- **WHEN** a shown announcement gets its rendition before the next check
- **THEN** the check shows its rewritten title and summary

#### Scenario: Many new announcements
- **WHEN** the tab comes back after a day with more than a page of new announcements
- **THEN** every new announcement appears, without a gap before the ones already shown

#### Scenario: A hidden tab
- **WHEN** the tab is in the background
- **THEN** no check is sent until it is visible again

### Requirement: Article view
Opening an item SHALL show the article over the stream: the rewrite by default, the school's
version from the article's menu or by the reader's setting, images where the school placed them,
every URL as a link, the day, unit, withdrawal and tag chips. Closing it with Esc, the close
button or the browser's back SHALL return to the same stream position. A link item SHALL open
its link instead.

#### Scenario: Back to the stream
- **WHEN** a reader scrolled far down, opened an article and pressed back
- **THEN** the article closes and the stream is where it was

#### Scenario: Closing after a direct link
- **WHEN** a reader opened `/a/2412` from another site and presses the close button
- **THEN** the stream shows and the reader is still on bulletin

#### Scenario: A plain-text URL
- **WHEN** the school's text holds a URL that its page does not link
- **THEN** the article shows it as a link

#### Scenario: The school's version
- **WHEN** a reader picks the school's version from the article's menu
- **THEN** the article shows the school's text and images, sanitized, without the school's styles
  or scripts

#### Scenario: A cross-post's link
- **WHEN** a reader opens the article path of a cross-post
- **THEN** the announcement it copies opens, under its own path

#### Scenario: A link item
- **WHEN** a reader clicks a link item in the stream, or opens its article path
- **THEN** its link opens and no empty article is shown

#### Scenario: An unsafe link in the rewrite
- **WHEN** the rewrite holds a link whose scheme is not http or https
- **THEN** it is shown as text, not as a link

### Requirement: Attachments
The article SHALL list its attachments by name, each a link to the school's file. A left click on
a stored image, PDF or DOCX SHALL preview it in the page: images with zoom and arrows across
the article's images, PDFs in the browser's viewer, DOCX as sanitized HTML, each with a download
of the stored copy. Where the browser shows no PDFs inline, the stored PDF SHALL open in a new tab. A
single image attachment SHALL also show at the article's end.

#### Scenario: A stored PDF
- **WHEN** a reader clicks a stored PDF's name
- **THEN** the PDF opens in an in-page preview with a download button

#### Scenario: A file kept only at the school
- **WHEN** a reader clicks an attachment without a stored file, or a stored spreadsheet
- **THEN** the school's link opens in a new tab

#### Scenario: One image attachment
- **WHEN** the attachments hold one image and two PDFs
- **THEN** the image is shown at the end of the article and all three are listed

#### Scenario: A preview that fails
- **WHEN** a stored file cannot be previewed
- **THEN** the preview says so and offers the school's link

### Requirement: Search
The header's search SHALL find announcements of every unit, followed or not, in titles and text
or in titles only, within the topic chip and unit menu in effect. It SHALL search shortly after
the reader stops typing, never while an input method is composing. The box SHALL close when
focus leaves it; the query SHALL stay applied, and in the page's address, until cleared.

#### Scenario: An unfollowed unit
- **WHEN** a reader searches for a term found only in an unfollowed unit's announcement
- **THEN** the announcement is listed

#### Scenario: Leaving the box
- **WHEN** the reader typed a query and focus leaves the box
- **THEN** the box closes and the results stay with the query shown

#### Scenario: Typing with an input method
- **WHEN** a reader types a Chinese word with zhuyin
- **THEN** one search is sent after the word is committed, none while composing

### Requirement: Context menu
Right click, a long press or the menu key on an item SHALL open a menu, on phones a bottom sheet,
to hide each followed board the item is shown through, unfollow each followed unit those boards
belong to, follow its unit when not followed, copy its link and open the school's page. Each
change SHALL apply at once with an undo in a notice.

#### Scenario: Unfollowing and undoing
- **WHEN** a reader unfollows a unit from an item's menu and then presses undo
- **THEN** the announcements shown only through that unit disappear and then return, and the
  settings match the start

#### Scenario: An item on two followed boards
- **WHEN** an item is shown through boards of two followed units
- **THEN** its menu offers to hide either board and to unfollow either unit

### Requirement: Settings
Settings SHALL be kept in the browser: theme (system, light, dark), rewrite or school version,
followed units, hidden boards and topic order. Units, boards and topics the API no longer lists
SHALL be ignored and kept. The settings sheet SHALL end with
內容轉寫自國立臺灣科技大學各單位網站，以原網頁內容為準.

#### Scenario: A board that is gone
- **WHEN** saved settings hide a board the sites list no longer holds
- **THEN** the page works as if it were not hidden, and the board is hidden again when it returns

#### Scenario: The sites list fails
- **WHEN** the sites list cannot be loaded
- **THEN** the saved settings stay as they are

#### Scenario: Dark theme
- **WHEN** a reader picks the dark theme while the system is light
- **THEN** the page is dark, also after a reload

### Requirement: Settings export and import
The settings SHALL export as copied JSON, a JSON download or a copied link carrying them after
`#s=`. Opening such a link SHALL apply them at once when the reader never saved settings, and
otherwise ask before overwriting all of them. Pasted JSON, a pasted link or a JSON file SHALL
import the same way; unreadable input SHALL show an error and change nothing.

#### Scenario: A link for a new reader
- **WHEN** a reader without saved settings opens a settings link
- **THEN** the settings apply without the first-visit picker

#### Scenario: A link for an existing reader
- **WHEN** a reader with saved settings opens a settings link and keeps their own
- **THEN** nothing changes, and reloading does not ask again

#### Scenario: Unreadable input
- **WHEN** a reader pastes text that is neither settings JSON nor a settings link
- **THEN** an error is shown and the settings stay

### Requirement: Failures
When the API cannot be reached, the stream SHALL say so with a retry button and keep what it
already shows. A search refused for its rate SHALL say so and keep the query. An unknown article
SHALL say it was not found.

#### Scenario: The API is down
- **WHEN** loading the next page fails
- **THEN** the loaded items stay and a retry button appears below them

#### Scenario: Too many searches
- **WHEN** the API answers a search with 429
- **THEN** the page says to try again shortly and keeps the query

#### Scenario: An unknown article
- **WHEN** a reader opens `/a/999999`
- **THEN** the page says the announcement was not found, over the stream

### Requirement: Narrow screens and long text
At 375 px wide and at desktop width, no page, dialog or sheet SHALL scroll sideways, also with
three-digit counts, long unbroken titles, URLs and file names. Motion SHALL stop under the
reduced-motion preference.

#### Scenario: A long file name on a phone
- **WHEN** an article with a 120-character file name opens at 375 px
- **THEN** the name wraps and nothing scrolls sideways

#### Scenario: Reduced motion
- **WHEN** the reader's system asks for reduced motion and a new announcement arrives
- **THEN** it appears without animation
