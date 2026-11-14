# attachments

## Purpose

Keeps a record of every file an announcement links to, and a copy of small school-hosted files for
a year, as a fallback when the school's link breaks.

## ADDED Requirements

### Requirement: Attachment records
Every link in the article's attachment module (`mptattach`) and every link in the body to a file,
judged by a file extension or a `/var/file/` path, SHALL be recorded on the revision with its link
text as the name and its URL.

#### Scenario: Two PDFs
- **WHEN** an article's attachment module lists two `downloadfile` links and its body links to a
  `/var/file/` PDF and a web page
- **THEN** the revision records three attachments and not the web page

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
Attachment sizes SHALL never be read with HEAD, which the school's WAF refuses. `/var/file/`
links SHALL be read with a GET for bytes 0 to 0, taking the total from `Content-Range`.
`downloadfile` links, which ignore `Range`, SHALL be read with a GET whose `Content-Length` gives
the size, closing the connection before the body unless the file is to be stored.

#### Scenario: Range answer
- **WHEN** the range request answers 206 with `Content-Range: bytes 0-0/278993`
- **THEN** the attachment's size is 278993 bytes

#### Scenario: A module file over 5 MB
- **WHEN** a `downloadfile` link answers 200 with `Content-Length: 7900000`
- **THEN** the size is 7900000 bytes, the connection is closed and the body is not read

### Requirement: One-year file window
Nightly, the service SHALL delete each stored file that no announcement from the last 365 days
links to. The attachment records SHALL keep their name, URL, size and digest.

#### Scenario: A file shared across a year
- **WHEN** a file is linked from an announcement of 400 days ago and one of 10 days ago
- **THEN** the file stays

#### Scenario: An old file
- **WHEN** a file is linked only from an announcement of 400 days ago
- **THEN** the file is deleted and its attachment record remains
