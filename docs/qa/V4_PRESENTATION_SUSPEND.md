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

## Confirmed native RED and bounded candidate

The source hypothesis was confirmed by [PR18](https://github.com/ForceMind/ai-phone-ui/pull/18) test-only head `a439cb7c4ff83ce310e16de81c70696dc1b1af2a`, [run37738666668](https://github.com/ForceMind/ai-phone-ui/actions/runs/37738666668), Chromium143.0.7499.4. All existing suites passed; the new suite passed7/11. Both overlay-dismissal and lock/resume lost reading position: V4 360,1710→856; V4 393,904→676. V3 remained unchanged. All three photo-geometry scenarios passed. Fixed payload and zero preview executions remained intact.

Artifact11532559516 SHA256 `b96856120d66b427bec984b4c857a7673655c48eecf1975a69c088511099f27d` was downloaded and rehashed; source-head matched and all three dist files matched d856ea2. Native before/covered/after traces show the mounted body shrinking to V3 typography while covered, then regaining V4 height without its old reading offset. The actual after screenshot shows paragraph10 instead of the previously visible final local-only disclaimer.

The new production candidate separates foreground metadata from per-surface styles:
- Root still reports the visible route/sample for review controls and compatibility. It does not qualify for content-style selectors.
- Task, system home, top menu, launcher, lock, sleep, and feedback surfaces have independent `data-design-surface`, sample, route, theme, and opacity attributes. Task route changes only on a content-route event, including the existing pre-render preparation. Opening a system layer does not restyle the mounted task.
- Content selectors require `[data-design-surface][data-design-sample=true]`; rules targeting an overlay or feedback surface itself do not add a descendant space. The seven-page sample list is unchanged. Future approved sample-list extensions use the same separation.
- There is no additional reading offset, session, or persistence cache. Core gesture, confirmation, candidate, and storage implementation files are untouched.

Four unit cases cover independent task/foreground scope, non-sample task isolation, synchronous target preparation, and theme/material/V3 rollback. Native assertions additionally require covered/asleep typography, scrollHeight, and scrollTop to stay unchanged, preventing a post-dismissal offset patch from hiding reflow. Local build/static26/unit123/Python compilation pass. Candidate exact-head native CI and final pixels remain pending; the old RED and reports above are retained.
