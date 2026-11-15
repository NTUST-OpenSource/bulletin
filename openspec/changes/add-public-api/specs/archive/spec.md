## ADDED Requirements

### Requirement: Stream day
Each announcement SHALL keep a stream day: its list date; without one, the list date of the dated
article with the nearest article id, since ids grow with time across the sites; else the day it
was first seen in Taipei. The day SHALL be set when the announcement is stored and, while it has
no list date, estimated again in the nightly upkeep.

#### Scenario: A listed announcement
- **WHEN** an announcement listed on 3 November is stored
- **THEN** its stream day is 3 November

#### Scenario: An article without a list date
- **WHEN** an article without a list date is stored between dated articles, nearest to one listed
  last week
- **THEN** its stream day is that article's list date

#### Scenario: A link item
- **WHEN** a link item without a list date or an article id is stored
- **THEN** its stream day is the day it was first seen

#### Scenario: A nearer neighbour later
- **WHEN** a dated article nearer to an undated one is stored after it, and the nightly upkeep runs
- **THEN** the undated article's stream day is the nearer article's list date
