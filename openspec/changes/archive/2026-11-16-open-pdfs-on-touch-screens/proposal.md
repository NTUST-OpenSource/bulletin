# Proposal: open-pdfs-on-touch-screens

## Why

On the owner's iPhone (2026-11-16) a stored PDF's in-page preview showed a picture of its first
page, larger than the preview and beyond its zoom. iOS Safari reports an inline PDF viewer
(`navigator.pdfViewerEnabled`), so the page frames the PDF, but WebKit on iOS draws a framed PDF
as a still image of one page. Android's Chrome reports no viewer and already opens a new tab.

## What Changes

- Where the main pointer is touch (`(pointer: coarse)`), a stored PDF opens in a new tab, as it
  already does where the browser shows no PDFs inline; the phone's own viewer pages and zooms.
- Desktops keep the in-page preview. Images and DOCX keep theirs on every screen.

Out of scope: drawing PDFs in the page ourselves (pdf.js), which would keep the in-page preview on
phones at the cost of a large script.

## Capabilities

### Modified Capabilities

- `web-frontend`: "Attachments" opens stored PDFs in a new tab on touch screens.

## Impact

- `web/src/components/article/Attachments.svelte` and `web/tests/attachments.spec.ts`.
