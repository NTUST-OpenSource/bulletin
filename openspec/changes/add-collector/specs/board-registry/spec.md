# board-registry

## Purpose

The sites and boards bulletin knows about, with each board's category and tier. Boards stay in the
registry for good, so any board, off or excluded, can be turned on later.

## ADDED Requirements

### Requirement: Board identity
A board SHALL be identified by its site id and board number together. Boards with the same board
number on different sites SHALL be separate boards with their own category, tier and state.

#### Scenario: One board number on two sites
- **WHEN** the registry holds board 1927 of site 1100 and board 1927 of site 1101, and the first
  is set to P2
- **THEN** the second keeps its own tier

### Requirement: Seed import
On start, the service SHALL load `seeds/boards.json` and add every board it does not hold yet, with
its site, host, unit, name, category and tier. Boards already in the registry SHALL keep their
tier, category and review state, whatever the seed says.

#### Scenario: First start
- **WHEN** the service starts on an empty database with a seed of three boards
- **THEN** the registry holds the three boards with the seed's tiers and categories

#### Scenario: The owner's changes survive a restart
- **WHEN** a seeded board's tier was changed from P4 to P1 and the service restarts
- **THEN** the board is still P1

#### Scenario: A board added to the seed later
- **WHEN** the seed gains a fourth board and the service restarts
- **THEN** the fourth board is added and the other three are unchanged

### Requirement: Boards are kept
A board SHALL never be deleted from the registry: not when it is off, excluded, empty, or no longer
found on its site. Only its tier, category and review state change.

#### Scenario: A board that disappears from its site
- **WHEN** re-discovery no longer finds a board that the registry holds
- **THEN** the board stays in the registry with its tier

### Requirement: Board categories
Every board SHALL have one category: `announcement`, `news`, `regulation`, `course` or
`excluded`. The category only describes the board; it SHALL NOT decide whether the board is
polled, which the tier alone decides.

#### Scenario: An excluded board turned on
- **WHEN** an `excluded` board is set to P4
- **THEN** it is polled daily like any other P4 board

### Requirement: Re-discovery
Once a month, the service SHALL walk each known site's site map and the board links on its pages,
through the request queue, and add every board it has not seen as off, pending review, with a
category guessed from its name. It SHALL NOT change boards the registry already holds.

#### Scenario: A new board appears
- **WHEN** re-discovery finds a board number on a known site that the registry does not hold
- **THEN** the board is added with tier off, marked pending review, and is not polled

#### Scenario: Known boards
- **WHEN** re-discovery finds a board the registry already holds
- **THEN** the board's name, tier, category and review state are unchanged

### Requirement: Category guess
For a newly discovered board, the guessed category SHALL be `excluded` for banners, albums, videos,
FAQs and staff or profile pages, `regulation` for regulations, forms and downloads, `news` for news,
media coverage, honours and activity records, and `announcement` otherwise, judged from the board's
name.

#### Scenario: Guessing from names
- **WHEN** boards named like a banner, a forms download page, a media coverage page and a latest
  announcements page are discovered
- **THEN** they get `excluded`, `regulation`, `news` and `announcement`
