# Tasks: add-brand-intro

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing tests marked to
fail, then implement it, remove the markers and commit with the gate green.

## 1. The brand's intro

- [x] 1.1 Commit the page tests for "The intro" (the ball starts in the b's counter with the word hidden, and ends as the period) and "Reduced motion" (no intro), marked to fail; verify they fail for the expected reason and the gate stays green
- [x] 1.2 Add `Brand.svelte` with the intro's keyframes, use it in the stream's header, and remove the markers; verify the tests pass at both widths, check frames at 1280 and 375 pixels in both themes, and the gate is green
