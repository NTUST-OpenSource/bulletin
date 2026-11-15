## MODIFIED Requirements

### Requirement: Attachments
The article SHALL list its attachments by name, each a link to the school's file. A left click on
a stored image, PDF or DOCX SHALL preview it in the page: images with zoom and arrows across
the article's images, PDFs in the browser's viewer, DOCX as sanitized HTML, each with a download
of the stored copy. On touch screens, and where the browser shows no PDFs inline, the stored PDF
SHALL open in a new tab. A single image attachment SHALL also show at the article's end.

#### Scenario: A stored PDF
- **WHEN** a reader clicks a stored PDF's name
- **THEN** the PDF opens in an in-page preview with a download button

#### Scenario: A stored PDF on a touch screen
- **WHEN** a reader taps a stored PDF's name on a phone
- **THEN** the stored PDF opens in a new tab

#### Scenario: A file kept only at the school
- **WHEN** a reader clicks an attachment without a stored file, or a stored spreadsheet
- **THEN** the school's link opens in a new tab

#### Scenario: One image attachment
- **WHEN** the attachments hold one image and two PDFs
- **THEN** the image is shown at the end of the article and all three are listed

#### Scenario: A preview that fails
- **WHEN** a stored file cannot be previewed
- **THEN** the preview says so and offers the school's link
