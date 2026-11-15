# Proposal: add-brand-intro

## Why

The owner asked for the header's `bulletin.` to open each page load from the site's icon, the b
holding the accent ball, and approved the prototype on 2026-11-16 after two rounds: the ball
hops in natural, lower and lower bounces, and the word appears faster as each hop lands.

## What Changes

- On load, the stream's header shows the b with the ball in its counter. The ball hops right in
  four bounces, each lower and slower than the last, squashing as it lands, while the rest of the
  word appears behind it, catching up as each hop lands. It settles as the period after about
  1.3 seconds.
- Reduced motion, or a brand font that has not loaded within a second, shows the brand at rest.
  The intro plays once per load; the not-found view's header and the first-visit picker stay
  still.

## Capabilities

### Modified Capabilities

- `web-frontend`: adds "The brand's intro".

## Impact

- A new `web/src/components/header/Brand.svelte`, `web/src/App.svelte` and a new
  `web/tests/brand.spec.ts`.
