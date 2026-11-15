## MODIFIED Requirements

### Requirement: Model input
The model SHALL receive the article's title and the article's body and attachment module, taken
by selector and reduced to paragraphs, lists, tables, links, bold and images, as Markdown. Each
link and image SHALL be replaced by a placeholder (`L1`, `I1`, ...), so the input holds no URL. A
target that repeats its scheme, such as `http:// https://host/`, SHALL name the URL after it; a
link whose host is not an ASCII host name SHALL keep its text only, and such an image SHALL be
left out.

#### Scenario: A recorded article
- **WHEN** the recorded article with an attachment module and a body file link is rendered
- **THEN** the input holds the body text, every attachment's name and a placeholder for each link
  and image, and no URL

#### Scenario: A scheme typed twice
- **WHEN** a link's target is `http://` and a space before `https://dca.moi.gov.tw/ris`
- **THEN** its placeholder stands for `https://dca.moi.gov.tw/ris`

#### Scenario: A host Discord cannot link
- **WHEN** a link's target is `http://name@mail.ntust.edu.tw%20/`, or `http://` before Chinese
  text
- **THEN** the input holds the link's text and no placeholder for it

### Requirement: Placeholders put back
After the model answers, each placeholder the input had SHALL be replaced by the URL it stands
for. An answer that holds, in a link or image target, a placeholder the input did not have SHALL
fail the attempt; elsewhere such text, as a masked ID number, SHALL stay as written. An answer MAY
leave out images: icons and decorations are left out (owner), images with content are kept.

#### Scenario: Links restored
- **WHEN** the answer uses `L1` and `I1`
- **THEN** the stored Markdown holds their URLs and no placeholder

#### Scenario: An invented placeholder
- **WHEN** the answer links to `L9` and the input had only `L1`
- **THEN** the attempt fails

#### Scenario: Text that looks like a placeholder
- **WHEN** the answer holds the masked ID number `L125***256` outside a link
- **THEN** the stored Markdown holds it as written

#### Scenario: An image left out
- **WHEN** the input had `I1` and the answer does not
- **THEN** the rendition is stored without it
