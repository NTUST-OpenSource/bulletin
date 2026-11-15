# tier-admin Specification

## Purpose
Lets the operator change any board's tier at any time, review newly discovered boards and see who
changed what, through a CLI and an admin API that the public cannot reach.

## Requirements

### Requirement: Change a tier
The operator SHALL set a board's tier to P1, P2, P3, P4 or off through the CLI or the admin API,
naming the board by site id and board number. The change SHALL take effect at the next scheduling
pass, without a restart. An unknown board or tier SHALL be refused and change nothing.

#### Scenario: Raising a board
- **WHEN** a P4 board last polled at 09:58 on a Wednesday is set to P1 at 10:00
- **THEN** its next poll is due no later than 10:03, five minutes after its last poll

#### Scenario: Turning a board off
- **WHEN** a P2 board is set to off
- **THEN** no further poll of it is scheduled

#### Scenario: Unknown board
- **WHEN** the operator sets the tier of a board the registry does not hold
- **THEN** the command fails naming the board, and no tier changes

### Requirement: Tier audit
Every tier change SHALL be recorded with the board, the old and the new tier, who made it and when.
Who is the admin token's name for the API and the CLI's `--by` value, `cli` by default. The CLI and
the admin API SHALL list a board's changes, newest first.

#### Scenario: Two changes
- **WHEN** a board goes from P4 to P2 through the CLI and then to P1 through the API
- **THEN** its record lists P2 to P1 by the token's name, then P4 to P2 by `cli`

### Requirement: Turning a board on
A board changed from off to any tier SHALL count as not backfilled, so detection applies the
frontier rule to it, and SHALL be queued for backfill.

#### Scenario: An off board turned on
- **WHEN** an off board is set to P3
- **THEN** it is marked not backfilled and a backfill of it is queued

### Requirement: Review new boards
The operator SHALL list the boards pending review, with their site, name, guessed category and the
date they were found, and SHALL clear a board's review mark, with or without changing its tier or
category in the same command.

#### Scenario: Accepting a discovered board
- **WHEN** the operator clears the review mark of a pending board and sets it to P4 and `news`
- **THEN** the board is no longer listed as pending, is P4 and `news`, and the tier change is
  audited

### Requirement: Admin API access
The admin API SHALL listen only on the admin address, never on the public port, and SHALL require
a bearer token from configuration. A request without a valid token SHALL get 401 and change
nothing.

#### Scenario: Missing token
- **WHEN** a request to change a tier carries no token or a wrong one
- **THEN** it gets 401 and the tier is unchanged

#### Scenario: The public port
- **WHEN** an admin path is requested on the public port
- **THEN** it gets 404
