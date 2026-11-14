# attachments

## Purpose

Keeps a record of every file an announcement links to, and a copy of small school-hosted files for
a year, as a fallback when the school's link breaks.

## ADDED Requirements

### Requirement: Attachment records
Every link in an article body to a file, judged by a file extension or a `/var/file/` path, SHALL be
recorded on the revision with its link text as the name and its URL.

#### Scenario: Two PDFs
- **WHEN** an article body links to two PDFs and a web page
- **THEN** the revision records the two PDFs as attachments and not the web page

### Requirement: Stored copies
For an announcement first seen or listed within the last 365 days, each attachment on a
`*.ntust.edu.tw` host SHALL have its size read and, when under 5 MB, its file downloaded and stored
once per SHA-256 digest, with the size and digest recorded. Other attachments SHALL keep their name,
URL and, when read, size.

#### Scenario: A small school file
- **WHEN** a new announcement links to a 600 KB PDF on a school host
- **THEN** the file is stored and the attachment records its size and digest

#### Scenario: A large file
- **WHEN** the attachment is 7 MB
- **THEN** only its name, URL and size are recorded

#### Scenario: A file outside the school
- **WHEN** the attachment is on a host outside `ntust.edu.tw`
- **THEN** it is neither requested nor stored

#### Scenario: The same file twice
- **WHEN** two announcements link to files with the same content
- **THEN** one copy is stored

### Requirement: Size without HEAD
Attachment sizes SHALL be read with a GET for bytes 0 to 0, taking the total from `Content-Range`,
and never with HEAD, which the school's WAF refuses.

#### Scenario: Range answer
- **WHEN** the range request answers 206 with `Content-Range: bytes 0-0/278993`
- **THEN** the attachment's size is 278993 bytes

### Requirement: One-year file window
Nightly, the service SHALL delete each stored file that no announcement from the last 365 days
links to. The attachment records SHALL keep their name, URL, size and digest.

#### Scenario: A file shared across a year
- **WHEN** a file is linked from an announcement of 400 days ago and one of 10 days ago
- **THEN** the file stays

#### Scenario: An old file
- **WHEN** a file is linked only from an announcement of 400 days ago
- **THEN** the file is deleted and its attachment record remains
