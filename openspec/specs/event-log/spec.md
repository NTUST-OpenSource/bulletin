# event-log Specification

## Purpose
The ordered record of what happened to announcements, which clients read from a cursor to stay in
step with the archive without missing or repeating anything.

## Requirements

### Requirement: Events
Storing a new announcement SHALL record a published event; a new revision a revised event; a
withdrawal a withdrawn event; a restoration a restored event. Each event SHALL hold an id, the
announcement, the kind, whether it is notify-worthy and the time. Events SHALL never be changed.

#### Scenario: A full life
- **WHEN** an announcement is stored, edited, withdrawn and restored
- **THEN** its events are published, revised, withdrawn and restored, in that order

### Requirement: Gap-free order
Event ids SHALL increase, and once an event is visible to readers no event with a lower id SHALL
become visible later, so a reader that resumes after the last id it read misses nothing.

#### Scenario: Concurrent writers
- **WHEN** two transactions record events at the same time, and a reader reads after the first
  commit and again, from its last id, after the second
- **THEN** the reader has received both events once each

### Requirement: Notify flag
Only published events SHALL be notify-worthy, and only as detection decides. Revised, withdrawn
and restored events SHALL NOT be notify-worthy.

#### Scenario: A revision
- **WHEN** a revised event is recorded
- **THEN** it is not notify-worthy

### Requirement: Late discoveries are marked
A published event for a late discovery, a backfilled announcement or a cross-post SHALL say so, so
that a client mirroring the archive can store it without announcing it.

#### Scenario: Backfill
- **WHEN** backfill stores an announcement from 2019
- **THEN** its published event is marked late and not notify-worthy
