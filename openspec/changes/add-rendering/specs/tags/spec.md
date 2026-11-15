# tags

## Purpose

Classifies announcements by the fixed taxonomy of topic, audience, nature and source, so readers
and clients can filter them, and keeps where each tag came from.

## ADDED Requirements

### Requirement: Fixed taxonomy
Tags SHALL come from the fixed taxonomy of decision E3. Topic and audience SHALL allow several tags
each; nature and source SHALL hold exactly one each. Every tag SHALL have a stable id and its
approved Traditional Chinese label. An answer with a tag outside the taxonomy, or without exactly
one nature and one source, SHALL fail the attempt.

#### Scenario: The taxonomy
- **WHEN** the taxonomy is loaded
- **THEN** it holds 20 topics, 8 audiences, 4 natures and 2 sources, each with an id and a label

#### Scenario: Two natures
- **WHEN** the answer tags an announcement both as action required and as information
- **THEN** the attempt fails

### Requirement: Tags with their source
Each tag SHALL be stored per announcement with its source, model or manual. A stored rendition
SHALL replace the announcement's model tags and SHALL keep its manual tags. A fallback rendition
SHALL leave the tags unchanged.

#### Scenario: A new rendition
- **WHEN** an announcement with a manual tag is rendered again with other model tags
- **THEN** its model tags are the new ones and its manual tag stays

#### Scenario: A fallback
- **WHEN** an announcement with model tags gets a fallback rendition
- **THEN** its tags are unchanged
