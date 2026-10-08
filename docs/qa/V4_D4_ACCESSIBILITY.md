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
