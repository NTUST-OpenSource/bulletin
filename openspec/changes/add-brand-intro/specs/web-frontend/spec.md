## ADDED Requirements

### Requirement: The brand's intro
When the stream loads, the header's `bulletin.` SHALL start as its b with the accent ball in the
b's counter. The ball SHALL hop right in lower and lower bounces while the rest of the word
appears behind it, and SHALL settle as the period in about 1.3 seconds, once per load. With
reduced motion, or when the brand's font has not loaded within a second, the brand SHALL show at
rest.

#### Scenario: The intro
- **WHEN** a reader opens the page
- **THEN** the brand starts as its b holding the ball, and ends as `bulletin.` with the ball as its period

#### Scenario: Reduced motion
- **WHEN** a reader who prefers reduced motion opens the page
- **THEN** the brand shows at rest, without the intro
