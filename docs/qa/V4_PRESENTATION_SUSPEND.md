# D1 presentation interruption checks

Test-only follow-up from `d856ea2f2da777a92f9a7b6d3ea5303475cf2bb1`, 2026-10-08.

## Question under test

`design-preview.js` resolves the visible route after `ui:visibility` and applies
the sample flag globally. A top system menu, lock, or sleep surface is outside
the sample list, so opening it removes V4 styling from the mounted task behind
it. The previously verified ordinary long-confirmation fixture at 360 has
scrollHeight 2207 / scrollTop 1710 in V4 and scrollHeight 1353 / scrollTop 856 in
V3. A style change could clamp the live reading offset; native scroll anchoring
may affect the outcome. This is a source-derived risk, not yet a native failure.

## Native test

Run `npm run test:presentation`. The new suite uses the existing HTTP-origin
fixture and real browser controls, with no handler, layout, scroll, or storage
patches. It checks V3 360, V4 360, and V4 393 independently:

- Read a long confirmation to the end, open the top menu with `t`, then dismiss
  it with Escape. Reading position, fixed payload, safe cancel focus, source
  route, local-only boundary, and zero preview executions must be preserved.
- Sleep and wake through the existing hardware control, unlock with Enter, and
  resume the same task cover. Apply the same assertions and then cancel, keeping
  the draft and original data.
- Select an off-center photo region, open and dismiss the top menu, and verify
  that the ring again matches image coordinates with no photo, draft, or note
  changes.

Reports, before/after screenshots, and covered/asleep geometry are isolated under
`test-results/presentation-suspend/` and carry the tested source SHA. The workflow
runs this after all existing suites. No existing assertion was removed.

## Local evidence and boundaries

Build, 26 static checks, 119 unit tests, and Python syntax compilation pass.
The test command started its loopback server, but Chromium failed before the
first case: `process_singleton_posix.cc: socket() failed: Operation not permitted`.
No OS workaround was attempted. The native outcome remains pending exact-head CI;
the local harness failure is not a product failure or a passing native test.
Runtime source and all three checked-in dist files are unchanged from d856ea2.
Physical devices, screen readers, mobile soft keyboards, OS font scaling, and
actual operating-system lock/wake are not covered.

## Separate fix proposal, only if reproduced

Keep mounted task presentation keyed to the task's content route while system
overlay/lock presentation follows its own visible route. Scope the sample
selectors or presentation marker to those surfaces rather than toggling the
hidden confirmation's typography through a single global sample flag. This
avoids adding another copy of reading/session state or changing accept/cancel
semantics. Both the underlying task and non-sample system layer should retain
their appropriate presentation; simply treating SYS-04/05/06 as migrated V4
pages would broaden the declared sample scope and is not the proposed fix.
