# Tasks: date-undated-articles

Each requirement gets two tasks (AGENTS.md, xfail-first): commit its failing test marked
`xfail(strict=True)`, then implement it, remove the marker and commit with the gate green.

## 1. Rendering

- [x] 1.1 Commit the xfail tests for "What gets rendered" (an old and a recent article without a list date); verify they fail for the expected reason and the gate stays green
- [x] 1.2 Commit the xfail test for "Deadlines from the text" (an article without a list date gets its nearest dated article's day); verify it fails for the expected reason and the gate stays green
- [x] 1.3 Implement both in the pick query with migration `0005`'s partial index, and remove the markers; verify their scenarios pass and the gate is green

## 2. Migration

- [x] 2.1 Add to migration `0005` the one-off removal of renditions and model tags of articles without a list date; verify with a migration test that dated articles keep theirs and manual tags stay

## 3. Verification

- [x] 3.1 Run `scripts/gate.sh`; verify it passes
- [ ] 3.2 Deploy to the owner's host and uncomment the keys; verify rendering resumes and an article without a list date whose nearest dated article is over a year old stays raw
