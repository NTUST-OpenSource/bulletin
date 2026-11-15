## MODIFIED Requirements

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
