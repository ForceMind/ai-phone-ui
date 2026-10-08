# D4 bounded rendered contrast and 200% text resize

## Scope and method

Test-only first pass from main `8f50572631b4330ff3867c45c618e9107cd26d7c`.
This addresses the unmeasured browser portion of V4_REDESIGN_PLAN §12, not a
whole-product accessibility certification. No runtime changes in this first pass.

- Real HTTP-origin Chromium; existing synthetic fixtures; deny external requests.
- Portrait 393×852 artboard; DAY-05 long fixed confirmation, SET-01 settings,
  CLD-03 actual task detail, SYS-04 glass settings overlay.
- Light/dark × normal glass / product reduced transparency / product high contrast.
- Contrast: capture real compositor background after suppressing only target text
  glyph fill and text shadow; preserve backgrounds, pseudo-elements, borders,
  backdrop blur, ancestors, layout and scroll. Verify target geometry and scroll
  unchanged. Sample actual rendered pixels at every pixel inside visible direct-text rectangles,
  composite computed glyph alpha over that background, calculate sRGB WCAG luminance.
  Separate nested text runs use their own computed colors. Account for the phone
  frame transform when deciding whether text is large. Compare unrounded ratios.
  4.5:1 normal, 3:1 only at >=24px or >=18.667px with weight >=700.
  Rectangle sampling is conservative; anti-aliased glyph edge colors are not used.
  Group opacity, filters/blend modes, nonstandard glyph fill/stroke/text background
  explicitly fail as unverified. Actual overflow clip intersections are used;
  8px-grid hit testing guards occlusion, with saved foreground/background images
  for independent review. This is bounded measured evidence, not exhaustive
  occlusion detection for arbitrary dynamic pages.
  Representative semantic selectors only; this is not all-text/all-state coverage.
- Resize: snapshot every screen element's computed font-size and line-height,
  explicitly double all font sizes once (no inherited compounding), double pixel
  line-heights and retain `normal`; assert computed 2×. Device pixel ratio, zoom,
  widths and heights are not changed. Exercise end-of-message scroll/cancel,
  settings rows and idle-task phases/footer reachability through actual wheel input.
  Accumulate visible text lines across scroll positions, check clipping ancestors
  including the element, three-point line hit testing, header/body overlap and
  unchanged whole core/suite/fixed-payload immediately after resizing. Never use
  scrollIntoView to manufacture reachability through overflow:hidden ancestors.
  Save start/end screenshots. Frame coordinate scale is verified against PNG size.
- Independent parallel D4 CI artifact includes per-sample ratios, geometry, screenshots and source SHA.

## First-pass status

Local build, 26 static checks and 129 unit tests pass. Local Chromium cannot
start: process singleton socket EPERM. No native pass or product failure inferred
from that environment blocker. New test-only CI will distinguish actual RED from
previously unmeasured gates and from harness problems before any product change.

## Still open

Physical Android/iOS, OS font scaling, native browser zoom, screen readers,
OS contrast/transparency media preferences, all 86-page certification, actual
service integration and Pages deployment are outside this bounded pass.

## Reference criteria

- [W3C SC 1.4.3 contrast explanation](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [W3C SC 1.4.4 resize-text explanation](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html)

These browser probes support the original project criteria; they do not certify
all WCAG success criteria or substitute for the explicitly open device gates.

## Preserved first native pass (test-only dd557fac)

Run 37774131301 / artifact 11549816758 (SHA256
341686be2276d86327d2a93f77ce586f79509ab992466e0a894454949ecff7a4)
completed with 32/44 initial D4 checks passing. Six long-confirmation 200% cases
showed the body bottom at 858.827 versus hint top 850.346 in rendered coordinates:
real ~8.48px overlap, reproducible across all six presentation combinations.
Six reported contrast failures sampled beyond the paragraph's actual scroll clip;
these are harness-invalid evidence, not confirmed color defects. SET/CLD initial
resize passes used scrollIntoView and did not prove user-wheel reachability; they
are superseded by the conservative test-only pass, not accepted as product passes.

The old core suite was 9/10: backup-cancel-resume timed out waiting for filechooser
at keyboard_focus_test.py:65. No runtime bytes changed from baseline. All other
old native suites completed successfully, including 178 full-migration checks.
Keep this failure; rerun/diagnose rather than infer a production regression.

The next test-only commit separates D4 into a parallel job and fixes text-run,
clip, opacity-group, unrounded-ratio and real-wheel measurement weaknesses.

## Conservative test-only RED (69cb11f9)

Run 37775681970, independent D4 artifact 11550176376, SHA256
`dd4560ab8a1174f8e89f3bc28a5a99783039623eb769961a6426a65d31b4d062`.
Exact source-head and ZIP digest verified; actual screenshots inspected.
32/44 checks pass: all 24 contrast cases (96 semantic samples, minimum
6.373409163249365:1), six SET-01 real-wheel 200% cases, errors/outbound checks.
12 actual resize failures: six DAY-05 body/footer overlaps, six CLD-03
header/detail overlaps with unreachable footer text. No color defect established.
The separate unchanged core suite passed 10/10 on this commit. The first
filechooser timeout remains recorded; production was not changed to mask it.

## Candidate repair

Use normal flex space allocation for existing V4 confirmation regions and task
header/detail/footer. Existing scroll regions/actions/payloads remain. A visible,
actually overflowing V4 job detail can use the existing pointer scroll mode;
nonoverflow and V3 keep their original gesture selection. Three unit regressions
and a native pointer check cover that boundary. No SET-01 or color changes.
Candidate build/26 static/132 unit checks pass locally; exact candidate native
jobs and screenshots must be checked before merge.
