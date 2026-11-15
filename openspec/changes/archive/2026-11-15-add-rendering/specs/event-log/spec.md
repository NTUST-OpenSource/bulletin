# event-log

## MODIFIED Requirements

### Requirement: Events
Storing a new announcement SHALL record a published event; a new revision a revised event; a
withdrawal a withdrawn event; a restoration a restored event; a stored rendition, fallback
renditions included, a rendered event. Each event SHALL hold an id, the announcement, the kind,
whether it is notify-worthy and the time. Events SHALL never be changed.

#### Scenario: A full life
- **WHEN** an announcement is stored, edited, withdrawn and restored
- **THEN** its events are published, revised, withdrawn and restored, in that order

#### Scenario: A rendition
- **WHEN** a new announcement is stored and then rendered
- **THEN** its events are published, then rendered

### Requirement: Notify flag
Only published events SHALL be notify-worthy, and only as detection decides. Revised, withdrawn,
restored and rendered events SHALL NOT be notify-worthy.

#### Scenario: A revision
- **WHEN** a revised event is recorded
- **THEN** it is not notify-worthy

#### Scenario: A rendition
- **WHEN** a rendered event is recorded
- **THEN** it is not notify-worthy
