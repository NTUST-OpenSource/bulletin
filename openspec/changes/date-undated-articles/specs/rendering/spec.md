# rendering

## MODIFIED Requirements

### Requirement: What gets rendered
The service SHALL render every announcement with a revision whose day falls within the last year.
The day is the list date; for an article without one, the list date of the dated article with
the nearest article id; else the day it was first seen. Link items, which have no article page,
and older announcements SHALL stay raw. Announcements that are not late discoveries SHALL be
rendered before late ones, and within each group the most recent day first.

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

### Requirement: Deadlines from the text
A deadline SHALL be kept only when its date appears in the source text, in any of the school's
date forms: Gregorian or ROC years, numeric, Chinese or with English month names, with or without
the year. A deadline that does not appear SHALL be dropped; the rendition is stored without one.
Dates without a year SHALL be read against the announcement's day, the one that decides whether
it is rendered. The prompt SHALL give that day and today's date.

#### Scenario: An ROC date
- **WHEN** the text says the deadline is 115年12月10日 and the answer gives 2026-12-10
- **THEN** the rendition's deadline is 2026-12-10

#### Scenario: An invented date
- **WHEN** the answer gives a deadline whose date the text does not hold
- **THEN** the rendition has no deadline

#### Scenario: Both days in the prompt
- **WHEN** an announcement listed on 2026-11-03 is rendered on 2026-11-15
- **THEN** its prompt gives both days

#### Scenario: An announcement without a list date
- **WHEN** an article without a list date is rendered and its nearest dated article was listed
  on 2026-07-20
- **THEN** its prompt gives 2026-07-20

#### Scenario: No dated article at all
- **WHEN** an article without a list date is rendered and no article has a list date
- **THEN** its prompt gives the day it was first seen, in Taipei
