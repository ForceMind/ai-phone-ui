# D4 child-route review: task ownership and reading return

## Result

The specific [PR21 review](https://github.com/ForceMind/ai-phone-ui/pull/21#discussion_r4219363745)
was **not reproduced** on main f4a5ad0. Test-only 31fb6f9 changes no application
runtime. Run 37787714815 passes both jobs, including original D4 50/50 and the
new 8/8 probe (six presentation combinations plus page-error/outbound checks).
This is investigation/regression evidence, not a product fix or a new design.

## What actually happens

In every light/dark × glass/opaque/highcontrast case, the native cloud CLD-03
reader starts genuinely scrolled to 471 at 200% text size (percentage 144px).

1. Catalog CLD-04 follows CLD-04 → CLD-03 → CLD-02. CLD-02 is type `jobs`,
   not `job`, so `Suite.go` creates/uses `ui-CLD-02`, not the native `cloud` task.
   Its stack is the suite CLD-03 wrapper plus suite CLD-04; it has no `.job-detail`.
2. Escape returns to the suite CLD-03 wrapper, still owned by `ui-CLD-02`.
   The original cloud session retains 471. This is not the native reader at zero.
3. Returning through the original cloud activity cover restores 471 → 471,
   with the same 144px percentage font. A direct catalog CLD-04 → CLD-03 round
   trip also restores the original cloud reader to 471.
4. The actual same-cloud child is the native Pulley result page. It uses
   `pushPage`/`renderStack`, leaves the job root mounted, and Escape returns
   at 471 → 471 without changing notes, photo, job execution state or outbox.

The catalog wrapper's own `.suite-scroll` reading position is not proven here.
Neither its route ID alone nor this probe's pass is evidence that it is the same
native reader. The earlier cross-task 471 → 471 proof remains valid.

## Evidence and method

- Real Chromium 143.0.7499.4 over HTTP, synthetic data, no external requests.
- Existing D4 actual computed-font 200% rules persist through native cloud DOM
  remount; no DPR/native zoom claim and no injected scrollTop.
- Actual catalog controls, keyboard Back/Home, activity cover and Pulley actions.
- Source-head and all three artifact dist files verified; runtime/src bytes match
  f4a5ad0. ZIP artifact 11554264698 has SHA256
  `72e4dee7eddb99a395203187e148e805cfae283eb2cfd938d115c67d8b521a0e`.
- Per-stage route, task, stack, root-node presence, font and offset are preserved
  in `V4_D4_CHILD_ROUTE_EVIDENCE.json`. Actual stage screenshots were independently
  reviewed. Final documentation head and merge main still require their own CI.

## Limits and separate observation

This is not child-page typography or all-page accessibility certification.
The native result child screenshot contains visibly pale body text in light and
high-contrast modes. A separate read-only check of the existing native PNGs finds
8 fully painted pixels per sample matching source foreground #c9e0df. Against the
actual uniform #fff background, the ratio is 1.3805520821569766:1 in light and
highcontrast; dark #202327 gives 11.427409389821817:1. This ordinary 14px body needs
4.5:1. This is raster solid-foreground/background measurement, not a newly captured
computedStyle audit; anti-aliased edge colors were excluded. Exact crops, image
hashes and values are in the evidence JSON. Keep the finding separate: routing
8/8 does not mean result-child contrast passes. A narrowly scoped semantic-color
repair can be assessed separately; no product repair is made in this PR.
Physical devices, OS fonts, screen readers and unrelated routes remain untested.
No application HTML replacement is needed when its bytes have not changed.
