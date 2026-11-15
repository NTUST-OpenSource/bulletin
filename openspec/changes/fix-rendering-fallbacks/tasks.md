# Tasks: fix-rendering-fallbacks

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked to fail,
then implement it, remove the marker and commit with the gate green.

## 1. Placeholders put back

- [ ] 1.1 Commit the tests for "Text that looks like a placeholder" and for migration 0007, marked to fail; verify they fail for the expected reason and the gate stays green
- [ ] 1.2 Fail only on unknown placeholders in link or image targets, add migration 0007 dropping fallback renditions, and remove the markers; verify the gate is green

## 2. Model input

- [ ] 2.1 Commit the tests for "A scheme typed twice" and "A host Discord cannot link", marked to fail; verify they fail for the expected reason and the gate stays green
- [ ] 2.2 Repair targets that repeat their scheme and drop links and images whose host is not an ASCII host name, and remove the markers; verify the gate is green
