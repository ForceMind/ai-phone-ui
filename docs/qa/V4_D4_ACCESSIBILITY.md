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
  unchanged. Sample actual rendered pixels inside text rectangles (2px spacing),
  combine computed text alpha/ancestor opacity, calculate sRGB WCAG luminance.
  4.5:1 normal, 3:1 only at >=24px or >=18.667px with weight >=700.
  Rectangle sampling is conservative; anti-aliased glyph edge colors are not used.
  Filters/blend modes on the text ancestor chain explicitly fail as unverified.
  Representative semantic selectors only; this is not all-text/all-state coverage.
- Resize: snapshot every screen element's computed font-size and line-height,
  explicitly double all font sizes once (no inherited compounding), double pixel
  line-heights and retain `normal`; assert computed 2×. Device pixel ratio, zoom,
  widths and heights are not changed. Exercise end-of-message scroll/cancel,
  settings rows and task phases/footer reachability. Save start/end screenshots.
- Browser artifact includes per-sample ratios, geometry, screenshots and source SHA.

## First-pass status

Local build, 26 static checks and 129 unit tests pass. Local Chromium cannot
start: process singleton socket EPERM. No native pass or product failure inferred
from that environment blocker. New test-only CI will distinguish actual RED from
previously unmeasured gates and from harness problems before any product change.

## Still open

Physical Android/iOS, OS font scaling, native browser zoom, screen readers,
OS contrast/transparency media preferences, all 86-page certification, actual
service integration and Pages deployment are outside this bounded pass.
