## MODIFIED Requirements

### Requirement: The page
The public listener SHALL serve the frontend at `/` and at article paths `/a/{id}`, with the tab
title `bulletin. | 臺科公布欄`. Built files with a content hash in their names SHALL be cached as
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

#### Scenario: The tab title
- **WHEN** a reader opens the page
- **THEN** the tab reads `bulletin. | 臺科公布欄`
