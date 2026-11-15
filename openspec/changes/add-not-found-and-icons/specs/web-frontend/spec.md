## ADDED Requirements

### Requirement: Unknown paths
Any other path SHALL answer 404 with the page, revalidated and never framed. The page SHALL then
say that the page is not found and link back to the stream, and SHALL load no announcements and
show no first-visit picker. The API and the built files SHALL keep their own 404 answers.

#### Scenario: An unknown path
- **WHEN** a reader opens `/notices`
- **THEN** the server answers 404 with the page, which says the page is not found and links back to the stream

#### Scenario: An unknown API path
- **WHEN** a client asks for `/api/v1/notices` or `/assets/missing.js`
- **THEN** the answer is a 404 that is not the page

### Requirement: The site's icon
The page SHALL link its icon, the b of `bulletin.` holding the accent ball: an SVG that follows
the system's light or dark mode, a 32-pixel ICO and a 180-pixel home-screen PNG, each served
from the site's root and cached for a day.

#### Scenario: The icons
- **WHEN** a browser opens the page and asks for the icons it links
- **THEN** `/favicon.svg`, `/favicon.ico` and `/apple-touch-icon.png` are served
